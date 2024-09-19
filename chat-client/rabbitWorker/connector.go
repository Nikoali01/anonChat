package rabbitWorker

import (
	"fmt"
	"github.com/streadway/amqp"
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

	err = ch.ExchangeDeclare(
		"broadcast",
		"fanout",
		true,
		false,
		false,
		false,
		nil,
	)

	_, err = ch.QueueDeclare(
		"get_queue",
		true,  // durable
		false, // delete when unused
		false, // exclusive
		false, // no-wait
		nil,   // arguments
	)

	err = ch.QueueBind(
		"get_queue",
		"",
		"broadcast",
		false,
		nil,
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
