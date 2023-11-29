import socket
import json

def send_message(sock, message):
    json_message = json.dumps(message)
    sock.sendall(json_message.encode())

def receive_message(sock):
    data = sock.recv(4096).decode()
    return json.loads(data)

def connect_to_server(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket

def main():
    host = "localhost"
    port = 5000

    try:
        # Connect to the Java server
        client_socket = connect_to_server(host, port)

        # Example: Send a connect command
        connect_command = {"command": "connect", "address": "localhost", "port": 5000}
        send_message(client_socket, connect_command)

        # Example: Send a join command
        join_command = {"command": "join"}
        send_message(client_socket, join_command)

        # Example: Send a post command
        post_command = {"command": "post", "subject": "Hello", "content": "This is a message."}
        send_message(client_socket, post_command)

        # Example: Send a users command
        users_command = {"command": "users"}
        send_message(client_socket, users_command)

        # ... Add other commands as needed

        # Close the connection
        client_socket.close()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
