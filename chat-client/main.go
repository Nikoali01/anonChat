package main

import (
	"fmt"
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
	"github.com/joho/godotenv"
	"github.com/streadway/amqp"
	"log"
	"os"
)

// RabbitMQ connection and channel setup
func setupRabbitMQ() (*amqp.Connection, *amqp.Channel, error) {
	connString := fmt.Sprintf("amqp://%s:%s@%s:%s", os.Getenv("RABBITMQ_DEFAULT_USER"), os.Getenv("RABBITMQ_DEFAULT_PASS"), os.Getenv("RABBITMQ_HOST"), os.Getenv("RABBITMQ_PORT"))
	conn, err := amqp.Dial(connString)
	if err != nil {
		return nil, nil, err
	}

	ch, err := conn.Channel()
	if err != nil {
		return nil, nil, err
	}

	_, err = ch.QueueDeclare(
		"get_queue",
		true,  // durable
		false, // delete when unused
		false, // exclusive
		false, // no-wait
		nil,   // arguments
	)
	_, err = ch.QueueDeclare(
		"post_queue",
		true,  // durable
		false, // delete when unused
		false, // exclusive
		false, // no-wait
		nil,   // arguments
	)
	if err != nil {
		return nil, nil, err
	}

	return conn, ch, nil
}

// Function to publish messages to RabbitMQ
func publishMessage(ch *amqp.Channel, message string) error {
	err := ch.Publish(
		"",
		"post_queue",
		false,
		false,
		amqp.Publishing{
			ContentType: "text/plain",
			Body:        []byte(message),
		},
	)
	return err
}

// Function to consume messages from RabbitMQ
func consumeMessages(ch *amqp.Channel, messageChan chan string) {
	msgs, err := ch.Consume(
		"get_queue",
		"",
		true,  // auto-ack (set to false to manually acknowledge)
		false, // exclusive
		false, // no-local
		false, // no-wait
		nil,   // args
	)
	if err != nil {
		log.Fatalf("Failed to start consuming messages: %v", err)
	}

	for msg := range msgs {
		messageChan <- string(msg.Body)
	}
}

func main() {
	err := godotenv.Load("./../.env")
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	myApp := app.New()
	myWindow := myApp.NewWindow("Anonymous Chat")

	// Setup RabbitMQ
	conn, ch, err := setupRabbitMQ()
	if err != nil {
		log.Fatalf("Failed to connect to RabbitMQ: %v", err)
	}
	defer conn.Close()
	defer ch.Close()

	// Create UI elements
	messages := widget.NewLabel("")
	input := widget.NewEntry()
	sendButton := widget.NewButton("Send", func() {
		message := input.Text
		if err := publishMessage(ch, message); err != nil {
			log.Printf("Failed to publish message: %v", err)
		}
		input.SetText("")
	})

	// Create a channel to receive messages
	messageChan := make(chan string)
	go consumeMessages(ch, messageChan)

	// Update UI with incoming messages
	go func() {
		for msg := range messageChan {
			currentText := messages.Text
			messages.SetText(currentText + "\n" + msg)
		}
	}()

	// Layout
	myWindow.SetContent(container.NewBorder(
		messages,
		input,
		nil,
		sendButton,
	))

	myWindow.Resize(fyne.NewSize(400, 300))
	myWindow.ShowAndRun()
}
