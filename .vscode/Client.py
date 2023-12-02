import socket
import threading
import sys

# Client class
class Client:
    def __init__(self):
        self.server_port = 0
        self.server_ip = ""

    def main(self):
        # Get the user name first
        user_name = input("Please enter your user name: ")

        # We would only allow the user to enter %connect or %logout command
        while True:
            print("Please use %connect command to connect to the message server.")
            received = input()

            # If the command entered is "%connect ip serverport"
            if received.startswith("%connect"):
                try:
                    rest = received.split(" ", 1)[1]
                    ip, port = rest.split(" ")
                    self.server_ip = ip
                    self.server_port = int(port)
                    break
                except Exception as e:
                    print("The %connect command you have entered might be in wrong format.\n"
                          "The correct format is %connect [ip] [port]")
            elif received == "%logout":  # The command is %logout
                exit()
            else:
                print("The command you have entered is invalid currently. "
                      "Only these commands are valid at the moment:\n"
                      "%connect [ip] [port]\n%logout")

        # Establish the connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.server_ip, self.server_port))
        print("Connection is done! %help for more commands on server")

        # Obtaining input and out streams
        dis = s.makefile('rb')
        dos = s.makefile('wb')

        # Send the username to the server
        username = user_name + "\n"
        print(f"Sending username: {username}")
        dos.write(username.encode())

        # sendMessage thread
        def send_message():
            while True:
                # Read the message to deliver.
                msg = input()

                try:
                    # Write on the output stream
                    dos.write((msg + "\n").encode())
                    if msg == "%logout":
                        exit()
                except Exception as e:
                    print(f"Exception in send_message: {e}")
                    break


        # readMessage thread
        def read_message():
            print("read_message thread started")
            while True:
                try:
                    # Read the message sent to this client
                    msg = sys.stdin.readline().rstrip('\n')
                    print(f"Sending message: {msg}")
                    dos.write((msg + '\n').encode())
                    if msg == "%logout":
                        exit()
                except Exception as e:
                    print(e)
                    break



        # Start threads for sending and receiving messages
        threading.Thread(target=send_message).start()
        threading.Thread(target=read_message).start()

# Start the client
client = Client()
client.main()
