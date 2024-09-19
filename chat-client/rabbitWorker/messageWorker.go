package rabbitWorker

import (
	"encoding/json"
	"github.com/joho/godotenv"
	"github.com/streadway/amqp"
	"log"
	"time"
)

type Message struct {
	Message string    `json:"content"`
	Time    time.Time `json:"timestamp"`
}

var (
	conection *amqp.Connection
	channel   *amqp.Channel
)

func init() {
	err := godotenv.Load("./../.env")
	if err != nil {
		log.Fatal("Error loading .env file")
	}
	conn, ch, err := setupRabbitMQ()
	if err != nil {
		log.Fatalf("Failed to connect to RabbitMQ: %v", err)
	}
	conection = conn
	channel = ch
}

// Function to publish messages to RabbitMQ
func PublishMessage(message string) error {
	content := &Message{
		Message: message,
		Time:    time.Now(),
	}
	bytecontent, err := json.Marshal(content)
	if err != nil {
		return err
	}
	err = channel.Publish(
		"my_ex",
		"post_queue",
		false,
		false,
		amqp.Publishing{
			ContentType: "text/plain",
			Body:        bytecontent,
		},
	)
	return err
}

// Function to consume messages from RabbitMQ
func ConsumeMessages(messageChan chan Message) {
	msgs, err := channel.Consume(
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
		message := &Message{}
		err := json.Unmarshal(msg.Body, message)
		if err != nil {
			log.Fatalf("Failed to unmarshal message: %v", err)
		}
		messageChan <- *message
	}
}
