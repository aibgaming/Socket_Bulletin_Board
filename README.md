
# Socket Bulletin Board

## Description

This project implements a simple chat application with a server and client components using sockets. It provides both a public message board and multiple private message boards for users to interact with.

## Features

- **Public Message Board**
  - Joining a single message board
  - Posting messages
  - Retrieving user list
  - Leaving the group
  - Retrieving message content
  - Exiting the program

- **Private Message Boards**
  - Joining multiple private groups
  - Posting messages to specific groups
  - Retrieving user list in a group
  - Leaving a specific group
  - Retrieving message content in a group

## Requirements

- Java
- Any Java IDE (IntelliJ, Eclipse, etc.)

## Usage

### Server

```bash
# Navigate to the server directory
cd server

# Compile and run the server
javac Server.java
java Server
```

The server will start running and listening for client connections.

### Command-Line Client

```bash
# Navigate to the client directory
cd client

# Compile and run the client
javac Client.java
java Client
```

Follow the prompts to connect to the server and interact with the message boards.

## Commands

- `%connect <address> <port>`: Connect to the server.
- `%groups`: Retrieve a list of all groups.
- `%groupjoin <group_id>`: Join a specific group.
- `%grouppost <group_id> <subject> <content>`: Post a message to a specific group.
- `%groupusers <group_id>`: Retrieve a list of users in a given group.
- `%groupleave <group_id>`: Leave a specific group.
- `%groupmessage <group_id> <message_id>`: Retrieve the content of a message posted in a specific group.
- `%logout`: Disconnect from the server and exit the program.

## Contributing

- Autri Ilesh Banerjee
- Anay Joshi
- Sethu Kruthin Nagari
```
