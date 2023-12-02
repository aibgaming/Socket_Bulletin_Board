import socket
import threading
from datetime import date

# Server class
class Server:
    # Vector to store active clients. Vector is also flexible in size.
    active_clients = []
    # Vector to store the server messages.
    msgs = []
    # Dictionary to store 5 private boards
    private_boards = {}

    # Counter for message number
    message_id = 0

    def __init__(self):
        # Initialize 5 private boards
        for i in range(1, 6):
            board_name = f"PrivateBoard{i}"
            private_board = PrivateMessageBoard(board_name)
            # Put the PrivateMessageBoard object to the dictionary with their name as keys
            self.private_boards[board_name] = private_board

    def start_server(self):
        # Server is listening on port 1234
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('localhost', 1234))
        server_socket.listen()

        print("Server is listening for incoming connections...")

        while True:
            # Accept the incoming request
            client_socket, addr = server_socket.accept()
            print(f"New client request received from {addr}")
            
            print("Creating a new handler for this client...")
            # Create a new handler object for handling this request.
            client_handler = ClientHandler(client_socket)

            # Add this client to active clients list
            self.active_clients.append(client_handler)

            # Start a new thread for the client
            threading.Thread(target=client_handler.run).start()

# ClientHandler class
class ClientHandler:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.private_boards = {}
        self.is_logged_in = True
        self.on_board = False

        # Obtain input and output streams
        self.dis = client_socket.makefile('rb')
        self.dos = client_socket.makefile('wb')

        # Take username from the client
        self.username = self.dis.readline().decode().strip()
        print(f"Received username: {self.username}")


    def run(self):
        print(f"run is running for user {self.username}")
        while True:
            try:
                # Receive the string
                received = self.dis.readline().decode().strip()
                print(f"Received: {received}")

                if received == "%logout":
                    for mc in Server.active_clients:
                        mc.dos.write(f"{self.username} has logged out!\n".encode())
                    # Remove this client handler from the list
                    Server.active_clients.remove(self)
                    self.is_logged_in = False
                    self.client_socket.close()
                    break

                # Detect the command and run accordingly
                command, rest = received.split(" ", 1) if " " in received else (received, "")
                print('command reached')

                if command == "%join":
                    # Prints a list of users in the public board.
                    self.print_users()
                    # Alerts other members
                    for mc in Server.active_clients:
                        if mc.on_board:
                            mc.dos.write(f"{self.username} has joined the public board!\n".encode())
                    self.on_board = True
                    # Prints the last 2 messages
                    try:
                        second_last = Server.msgs[-2]
                        self.dos.write(f"{second_last.message_info()}\n".encode())
                    except IndexError:
                        pass
                    try:
                        last = Server.msgs[-1]
                        self.dos.write(f"{last.message_info()}\n".encode())
                    except IndexError:
                        self.dos.write("Message history is empty\n".encode())

                elif command == "%users":
                    self.print_users()

                elif command == "%post":
                    self.post_message(rest)

                elif command == "%leave":
                    self.on_board = False
                    for mc in Server.active_clients:
                        if mc.on_board:
                            mc.dos.write(f"{self.username} has left the public chat room!\n".encode())

                elif command == "%message":
                    self.retrieve_message(rest)

                elif command == "%help":
                    self.print_help()

                elif command == "%groups":
                    self.show_all_groups()

                elif command == "%groupjoin":
                    self.join_private_board(rest)

                elif command == "%grouppost":
                    self.post_message_to_group(rest)

                elif command == "%groupusers":
                    self.print_group_users(rest)

                elif command == "%groupleave":
                    self.leave_group(rest)

                elif command == "%groupmessage":
                    self.retrieve_group_message(rest)

                else:
                    # Invalid command
                    self.dos.write(f"{command} is invalid. Type %help to see the list of commands available\n".encode())

            except Exception as e:
                print(f"Exception in run: {e}")
                break

    def print_users(self):
        try:
            if not Server.active_clients:
                self.dos.write("You are the first user in the public board!\n".encode())
            else:
                # Otherwise print the users currently in the board
                list_of_users = "\nThe list of users in the public board:\n"
                for mc in Server.active_clients:
                    # only print the users who are on the public board
                    if mc.on_board:
                        list_of_users += mc.username + "\n"
                self.dos.write(list_of_users.encode())
        except Exception as e:
            print(e)

    def post_message(self, inline_message):
        try:
            subject, message = inline_message.split(" : ", 1)
            m = Message(subject, message, self.username, Server.message_id)
            Server.message_id += 1
            Server.msgs.append(m)

            for mc in Server.active_clients:
                if mc.on_board:
                    mc.dos.write(f"{m.message_info()}\n".encode())
        except Exception as e:
            print(e)

    def retrieve_message(self, message_id):
        try:
            message_found = False
            for msg in Server.msgs:
                if message_id == str(msg.message_id):
                    self.dos.write(f"Public: {msg.subject}: {msg.message}\n".encode())
                    message_found = True
                    break

            if not message_found:
                # The message has not been found
                self.dos.write(f"{message_id} is either not a number or there isn't any message with that value as an ID!\n".encode())
        except Exception as e:
            print(e)

    def print_help(self):
        try:
            commands = "\nList of Commands:\n" \
                       "%join - Join the public message board\n" \
                       "%post [subject] : [message] - posts the message to the public message board\n" \
                       "%users - Provides a list of users inside the public group\n" \
                       "%leave - leave the public group\n" \
                       "%message [message number (ex: 1, 100, etc.)] - retrieves message whose ID is provided\n" \
                       "%groups - retrieve a list of all groups that can be joined\n" \
                       "%groupjoin [Group name] - Provides a list of active users\n" \
                       "%grouppost [Group name] [subject] : [message] - Provides a list of active users\n" \
                       "%groupusers [Group name] - Provides a list of active users\n" \
                       "%groupleave [Group name] - Provides a list of active users\n" \
                       "%groupmessage [Group name] [MessageID] - Provides a list of active users\n" \
                       "%logout - logs you out of the server.\n"
            self.dos.write(commands.encode())
        except Exception as e:
            print(e)

    def leave_public_board(self):
        self.on_board = False
        for mc in Server.active_clients:
            if mc.on_board:
                mc.dos.write(f"{self.username} has left the public chat room!\n".encode())

    def retrieve_group_message(self, group_message_id):
        try:
            group_name, message_id = group_message_id.split(" ", 1)
            message_found = False

            for board_name, private_board in self.private_boards.items():
                if group_name == board_name:
                    if self.username in private_board.members:
                        for msg in private_board.messages:
                            if message_id == str(msg.message_id):
                                self.dos.write(f"{group_name} : {msg.subject}: {msg.message}\n".encode())
                                message_found = True
                                break

            if not message_found:
                # The message has not been found
                self.dos.write(f"{message_id} is either not a number or there isn't any message with that value as an ID!\n".encode())

        except Exception as e:
            print(e)

    def show_all_groups(self):
        try:
            # Create a new StringBuilder object that will store all the available private messaging boards
            board_list = "Available Private Boards:\n"
            # Iterate through the keySet of the private_boards dictionary to collect all board names
            # then append to board_list before converting it to String and output on the screen
            for group_name in self.private_boards.keys():
                board_list += group_name + "\n"
            self.dos.write(board_list.encode())
        except Exception as e:
            print(e)

    def join_private_board(self, private_board_name):
        try:
            if private_board_name in Server.private_boards:
                private_board = Server.private_boards[private_board_name]
                # Use add_member method inside the PrivateMessageBoard class to add a new member
                # to the list of member of the group
                private_board.add_member(self.username)
                self.private_boards[private_board_name] = private_board
                # Notify the client about the successful join
                self.group_broadcasting(f"Welcome {self.username} to {private_board_name} !", private_board)
                # Print last 2 messages
                try:
                    second_last = private_board.messages[-2]
                    self.dos.write(f"{second_last.message_info()}\n".encode())
                except IndexError:
                    pass
                try:
                    last = private_board.messages[-1]
                    self.dos.write(f"{last.message_info()}\n".encode())
                except IndexError:
                    self.dos.write("Message history is empty\n".encode())
            else:
                # Notify the client that the private board does not exist
                self.dos.write("Board does not exist! Please try again.\n".encode())

        except Exception as e:
            print(e)

    def post_message_to_group(self, inline_message):
        try:
            # %grouppost [Group name] [subject] : [message]
            # Split the arguments into sent_to_group, subject of the message, and the message ID inside the group
            sent_to_group, rest = inline_message.split(" ", 1)
            subject, message = rest.split(" : ", 1)
            
            # Iterate through all the available boards and find the board that the client wants to send to
            for group_name, private_board in self.private_boards.items():
                if sent_to_group == group_name:
                    # Logic to post a message to a group
                    # We also need to check if the username is a member of this private group or not
                    # If yes, we need to create a new message
                    if self.username in private_board.members:
                        m = Message(subject, message, self.username, private_board.group_message_id)
                        # Then add the message to the list of messages and increase the group message ID by 1
                        private_board.increase_message_id(m)
                        private_board.add_message(m)
                        # Output the message on screen
                        self.group_broadcasting(f"{group_name} : {m.message_info()}", private_board)
                    else:
                        self.dos.write("You need to join this board first!\n".encode())
                    break

        except Exception as e:
            print(e)

    def leave_group(self, group_to_leave):
        try:
            # Find the group name in the dictionary
            for group_name, private_board in self.private_boards.items():
                if group_name == group_to_leave:
                    # Check if the client is in the board or not
                    if self.username in private_board.members:
                        private_board.remove_member(self.username)
                        self.group_broadcasting(f"{self.username} has left the {group_to_leave} chat!", private_board)
                    else:
                        # If not, just inform the client
                        self.dos.write("You are not in this group!\n".encode())
        except Exception as e:
            print(e)

    def print_group_users(self, target_group):
        try:
            for group_name, private_board in self.private_boards.items():
                if target_group == group_name:
                    if private_board.members:
                        # First to join private_board.members.size() == 0
                        list_of_users = "\nThe list of users in this message board:\n"
                        for member in private_board.members:
                            list_of_users += member + "\n"
                        self.dos.write(list_of_users.encode())
                    else:
                        self.dos.write("There is no one in this chat board!\n".encode())
                    break
        except Exception as e:
            print(e)

    def group_broadcasting(self, message, private_board):
        try:
            for mc in Server.active_clients:
                if mc.username in private_board.members:
                    mc.dos.write(f"{message}\n".encode())
        except Exception as e:
            print(e)
       


# Message class
class Message:
    def __init__(self, subject, message, sender, message_id):
        self.subject = subject
        self.message = message
        self.sender = sender
        self.date_created = date.today()
        self.message_id = message_id

    def message_info(self):
        return f"#{self.message_id}, {self.sender}, {self.date_created}, {self.subject}."

# PrivateMessageBoard class
class PrivateMessageBoard:
    def __init__(self, board_name):
        self.board_name = board_name
        self.members = []
        self.messages = []
        self.group_message_id = 0

    def add_member(self, username):
        if username not in self.members:
            self.members.append(username)

    def remove_member(self, username):
        if username in self.members:
            self.members.remove(username)

    def add_message(self, message):
        self.messages.append(message)

    def increase_message_id(self, message):
        self.group_message_id += 1

if __name__ == "__main__":
    server = Server()
    server.start_server()
