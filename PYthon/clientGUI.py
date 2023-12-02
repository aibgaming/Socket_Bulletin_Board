import threading
import socket
import json
import PySimpleGUI as sg

layout = [
    [sg.Multiline(key='-OUTPUT-', size=(60, 20), autoscroll=True)],
    [sg.InputText(key='-INPUT-', size=(40, 1)), sg.Button('Send'), sg.Button('Connect')],
    [sg.Button('Groups'), sg.Button('Exit')]
]

window = sg.Window('Chat Client', layout, finalize=True)
host = "127.0.0.1"
port = 8080
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
current_group = None
connected = False


def client_receive():
    global current_group
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if message.startswith('{') and message.endswith('}'):
                handle_json_message(json.loads(message))
            else:
                window['-OUTPUT-'].print(message)

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
        message_text = f"{message['sender']} ({message['post_date']}): {message['subject']}\n  {message['content']}"
    elif 'id' in message:
        # Received a response to %message command
        message_text = f"Message ID {message['id']} ({message['post_date']}): {message['subject']}\n  {message['content']}"
    else:
        # Received other JSON messages
        message_text = json.dumps(message, indent=2)  # Pretty print JSON

    # Send data to the main thread for updating the GUI
    window.write_event_value('-UPDATE_OUTPUT-', message_text)




def client_send(message):
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
        window['-OUTPUT-'].print(f"You are not in any group. Use %groupjoin to join a group.")


def handle_command(command):
    global current_group, groups  
    command, *args = command.strip().split()
    print(command)
    if command == f'%connect':
        handle_connect_button()
    elif command == f'%groups':
        handle_group_button()
    elif command == f'%groupjoin' and len(args) == 1:
        join_group(args[0])
    elif command == f'%grouppost' and len(args) >= 2:
        post_to_group(args[0], args[1], ' '.join(args[2:]))
    elif command == f'%groupusers' and len(args) == 1:
        get_group_users(args[0])
    elif command == f'%groupleave' and len(args) == 1:
        leave_group(args[0])
    elif command == f'%groupmessage' and len(args) == 2:
        get_group_message(args[0], args[1])
    elif command == f'%exit':
        exit_program()
    else:
        window['-OUTPUT-'].print("Invalid command.")

def handle_group_button():
    layout = [
        [sg.Text('Enter Group ID:')],
        [sg.Input(key='-GROUP-ID-')],
        [sg.Button('Join Group'), sg.Button('Cancel')]
    ]

    window_group_input = sg.Window('Group ID Input', layout, finalize=True)

    while True:
        event, values = window_group_input.read()

        if event == sg.WINDOW_CLOSED or event == 'Cancel':
            break
        elif event == 'Join Group':
            group_id = values['-GROUP-ID-']
            if group_id.isdigit():
                join_group(int(group_id))
                break
            else:
                sg.popup_error('Invalid Group ID. Please enter a valid number.')

    window_group_input.close()





def handle_connect_button():
    global connected
    if not connected:
        address = sg.popup_get_text('Enter server address:')
        port = sg.popup_get_text('Enter server port:')
        name = sg.popup_get_text('Enter your name:')
        connect_to_server(address, int(port), name)
        join_group('public')  # Join the public group


def connect_to_server(address, port, name):
    try:
        global client
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((address, port))
        client.send(name.encode('utf-8'))  # Send the name to the server
        receive_thread = threading.Thread(target=client_receive)
        receive_thread.start()
    except Exception as e:
        print(f"Error connecting to server: {e}")

def join_group(group_id):
    global current_group
    if group_id == 'public':
        group_name = 'public'
    else:
        group_name = f'group{group_id}'
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
    client.send(f'%exit'.encode('utf-8'))
    client.close()
    window.close()


while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    elif event == 'Send':
        client_send(values['-INPUT-'])
    elif event == 'Connect':
        handle_connect_button()
    elif event == 'Groups':
        handle_group_button()
    elif event.startswith('%'):
        handle_command(values['-INPUT-'])
    elif event == '-UPDATE_OUTPUT-':
        # Update the multiline element with the received message
        window['-OUTPUT-'].print(values[event])

window.close()

