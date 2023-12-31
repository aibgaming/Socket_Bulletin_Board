import threading
import socket
import json

alias = input('Choose an alias >>> ')
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "127.0.0.1"
port = 8080
client.connect((host, port))
current_group = None


def client_receive():
    global current_group
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith('{') and message.endswith('}'):
                handle_json_message(json.loads(message))
            else:
                print(message)

        except ConnectionResetError:
            print("Connection was forcibly closed by the remote host.")
            client.close()
            break
        except Exception as e:
            print(f'Error receiving message: {e}')
            client.close()
            break


def handle_json_message(message):
    global current_group
    if 'subject' in message:
        # Received a message
        print(f"{message['sender']} ({message['post_date']}): {message['subject']}")
        print(f"  {message['content']}")
    elif 'id' in message:
        # Received a response to %message command
        print(f"Message ID {message['id']} ({message['post_date']}): {message['subject']}")
        print(f"  {message['content']}")
    else:
        # Received other JSON messages
        print(message)


def client_send():
    while True:
        try:
            message = input("")
            if message.startswith('%'):
                handle_command(message)
            else:
                send_chat_message(message)
        except Exception as e:
            print(f'Error sending message: {e}')
            client.close()
            break


def send_chat_message(message):
    global current_group
    if current_group:
        message_data = {
            'command': 'post',
            'group_name': current_group,
            'subject': '',
            'content': message
        }
        client.send(json.dumps(message_data).encode('utf-8'))
    else:
        print("You are not in any group. Use %groupjoin to join a group.")


def handle_command(command):
    global current_group
    command, *args = command.split()
    if command == '%connect' and len(args) == 2:
        connect_to_server(args[0], int(args[1]))
    elif command == '%groups':
        get_groups()
    elif command == '%groupjoin' and len(args) == 1:
        join_group(args[0])
    elif command == '%grouppost' and len(args) >= 2:
        post_to_group(args[0], args[1], ' '.join(args[2:]))
    elif command == '%groupusers' and len(args) == 1:
        get_group_users(args[0])
    elif command == '%groupleave' and len(args) == 1:
        leave_group(args[0])
    elif command == '%groupmessage' and len(args) == 2:
        get_group_message(args[0], args[1])
    elif command == '%exit':
        exit_program()
    else:
        print("Invalid command.")


def connect_to_server(address, port):
    try:
        global client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((address, port))
        receive_thread = threading.Thread(target=client_receive)
        receive_thread.start()
        send_thread = threading.Thread(target=client_send)
        send_thread.start()
    except Exception as e:
        print(f"Error connecting to server: {e}")


def get_groups():
    client.send('%groups'.encode('utf-8'))


def join_group(group_name):
    global current_group
    client.send(f'%groupjoin {group_name}'.encode('utf-8'))
    current_group = group_name


def post_to_group(group_name, subject, content):
    client.send(f'%grouppost {group_name} {subject} {content}'.encode('utf-8'))


def get_group_users(group_name):
    client.send(f'%groupusers {group_name}'.encode('utf-8'))


def leave_group(group_name):
    global current_group
    client.send(f'%groupleave {group_name}'.encode('utf-8'))
    current_group = None


def get_group_message(group_name, message_id):
    client.send(f'%groupmessage {group_name} {message_id}'.encode('utf-8'))

def exit_program():
    client.send('%exit'.encode('utf-8'))
    client.close()
    print("Goodbye!")
    exit()


if __name__ == "__main__":
    connect_to_server(host, port)  # Change this to the actual server address and port
