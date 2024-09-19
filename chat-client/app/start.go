package app

import (
	"chat-client/rabbitWorker"
	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/widget"
	"log"
)

func StartApp() {
	myApp := app.New()
	myWindow := myApp.NewWindow("Anonymous Chat")

	messages := widget.NewLabel("")
	input := widget.NewEntry()
	sendButton := widget.NewButton("Send", func() {
		message := input.Text
		if err := rabbitWorker.PublishMessage(message); err != nil {
			log.Printf("Failed to publish message: %v", err)
		}
		input.SetText("")
	})
	messageChan := make(chan rabbitWorker.Message)
	go rabbitWorker.ConsumeMessages(messageChan)

	// Update UI with incoming messages
	go func() {
		for msg := range messageChan {
			currentText := messages.Text
			messages.SetText(currentText + "\n" + (msg.Message + "  " + msg.Time.Format("2006-01-02 15:04:05")))
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
