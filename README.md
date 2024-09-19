# anonymousChat

## Server
located in ./backend:
1) rabbit.py is the realization of rabbitmq worker from the server side
2) controller.py fastapi application that retrieves the amount of sent messages
3) builded with docker

## Client
located in ./chat-client
1) rabbitWorker package with all producer-consumer logic
2) app package with desktop app logic
3) builded as binary executable

## Database
mongodb(works in docker)

## Message broker
rabbitmq(works in docker)