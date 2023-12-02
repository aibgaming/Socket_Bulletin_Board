import threading
import socket
import json
from datetime import datetime

host = "127.0.0.1"
port = 8080
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
clients = []
names = []

# Public group
public_group_name = 'public'
groups = {
    public_group_name: {'id': 0, 'members': [], 'messages': [], 'message_id_counter': 1},
    'group1': {'id': 1, 'members': [], 'messages': [], 'message_id_counter': 1},
    'group2': {'id': 2, 'members': [], 'messages': [], 'message_id_counter': 1},
    'group3': {'id': 3, 'members': [], 'messages': [], 'message_id_counter': 1},
    'group4': {'id': 4, 'members': [], 'messages': [], 'message_id_counter': 1},
    'group5': {'id': 5, 'members': [], 'messages': [], 'message_id_counter': 1},
}


def join_public_group(client):
    group_name = public_group_name
    group_members = groups[group_name]['members']
    group_members.append(client)
    client.send(f"You have joined {group_name}.".encode('utf-8'))
    client.send("You are now connected!".encode('utf-8'))
    broadcast(f"{names[clients.index(client)]} has joined {group_name}.".encode('utf-8'), group_members)

def broadcast(message, group_members):
    for client in clients:
        if client in group_members:
            client.send(message)


def get_message_content(group_id, message_id):
    for message in groups[group_id]['messages']:
        if message['id'] == message_id:
            return message
    return None


def handle_connect_command(client, address, port):
    try:
        new_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_client.connect((address, port))
        names.append(f"{address}:{port}")
        clients.append(new_client)
        broadcast(f"{names[-1]} has joined the chat room!".encode('utf-8'), clients)
    except Exception as e:
        print(f"Error connecting to {address}:{port}: {e}")


def handle_groups_command(client):
    group_list = "\n".join([f"{group['id']}: {group_name}" for group_name, group in groups.items()])
    client.send(f"Groups available:\n{group_list}".encode('utf-8'))


def handle_groupjoin_command(client, group_name):
    if group_name in groups:
        group_members = groups[group_name]['members']
        group_members.append(client)
        client.send(f"You have joined {group_name}.".encode('utf-8'))
        client.send("You are now connected!".encode('utf-8'))
        broadcast(f"{names[clients.index(client)]} has joined {group_name}.".encode('utf-8'), group_members)
    else:
        client.send(f"Group {group_name} not found.".encode('utf-8'))


def handle_grouppost_command(client, group_name, subject, content):
    global groups
    sender = names[clients.index(client)]
    post_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = {
        'id': groups[group_name]['message_id_counter'],
        'sender': sender,
        'post_date': post_date,
        'subject': subject,
        'content': content
    }
    groups[group_name]['message_id_counter'] += 1
    groups[group_name]['messages'].append(message)
    broadcast(json.dumps(message).encode('utf-8'), groups[group_name]['members'])


def handle_groupusers_command(client, group_name):
    group_members = [names[clients.index(member)] for member in groups[group_name]['members']]
    user_list = "\n".join(group_members)
    client.send(f"Users in {group_name}:\n{user_list}".encode('utf-8'))


def handle_groupleave_command(client, group_name):
    group_members = groups[group_name]['members']
    if client in group_members:
        group_members.remove(client)
        name = names[clients.index(client)]
        client.send(f"You have left {group_name}.".encode('utf-8'))
        broadcast(f"{name} has left {group_name}.".encode('utf-8'), group_members)
    else:
        client.send("You are not a member of this group.".encode('utf-8'))


def handle_groupmessage_command(client, group_name, message_id):
    try:
        message_id = int(message_id)
        message = get_message_content(group_name, message_id)
        if message:
            client.send(json.dumps(message).encode('utf-8'))
        else:
            client.send(f"Message with ID {message_id} not found.".encode('utf-8'))
    except ValueError:
        client.send("Invalid message ID.".encode('utf-8'))


def handle_exit_command(client):
    handle_leave_command(client)
    client.close()


def handle_leave_command(client):
    index = clients.index(client)
    name = names[index]
    clients.remove(client)
    names.remove(name)
    for group_name, group in groups.items():
        if client in group['members']:
            group['members'].remove(client)
            broadcast(f"{name} has left {group_name}.".encode('utf-8'), group['members'])
    broadcast(f'{name} has left the chat room!'.encode('utf-8'), clients)


def handle_client(client):
    join_public_group(client)  # Automatically join the public group
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                break
            elif message.startswith('%'):
                print("Message")
                command, *args = message.split()
                if command == f'%connect' and len(args) == 2:
                    handle_connect_command(client, args[0], int(args[1]))
                elif command == f'%groups':
                    handle_groups_command(client)
                elif command == f'%groupjoin' and len(args) == 1:
                    handle_groupjoin_command(client, args[0])
                elif command == f'%grouppost' and len(args) >= 2:
                    handle_grouppost_command(client, args[0], args[1], ' '.join(args[2:]))
                elif command == f'%groupusers' and len(args) == 1:
                    handle_groupusers_command(client, args[0])
                elif command == f'%groupleave' and len(args) == 1:
                    handle_groupleave_command(client, args[0])
                elif command == f'%groupmessage' and len(args) == 2:
                    handle_groupmessage_command(client, args[0], args[1])
                elif command == f'%exit':
                    handle_exit_command(client)
                else:
                    client.send("Invalid command.".encode('utf-8'))
            else:
                broadcast(f'{names[clients.index(client)]}: {message}'.encode('utf-8'), groups[public_group_name]['members'])

        except ConnectionAbortedError:
            break  # Break out of the loop if the connection is aborted
        except ValueError:
            print("Client socket not found in the list.")
            break  # Break out of the loop if the client socket is not in the list
        except OSError as e:
            if e.errno == 10038:
                print("Socket operation error: Socket is not valid.")
                break  # Break out of the loop if a socket operation error occurs
            else:
                print(f"Error handling client: {e}")
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            if client in clients:
                index = clients.index(client)
                name = names[index]
                clients.remove(client)
                names.remove(name)
                broadcast(f'{name} has left the chat room!'.encode('utf-8'), groups[public_group_name]['members'])
                client.close()
                # broadcast(f'{name} has left the chat room!'.encode('utf-8'))


def receive():
    while True:
        print('Server is running and listening ...')
        client, address = server.accept()
        print(f'Connection is established with {str(address)}')
        name = client.recv(1024).decode('utf-8')
        names.append(name)
        clients.append(client)
        print(f'The name of this client is {name}')
        broadcast(f'{name} has connected to the chat room'.encode('utf-8'), clients)
        client.send('You are now connected!'.encode('utf-8'))
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()



if __name__ == "__main__":
    receive()
