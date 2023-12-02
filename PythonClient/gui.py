import socket
import threading
import PySimpleGUI as sg

# Client class
class Client:
    def __init__(self):
        self.server_port = 0
        self.server_ip = ""
        self.window = None

    def create_layout(self):
        layout = [
            [sg.Text("Please enter your user name:")],
            [sg.InputText(key="-USERNAME-")],
            [sg.Button("%connect"), sg.Button("%logout")],
            [sg.Multiline(size=(40, 10), key="-OUTPUT-", disabled=True)],
            [sg.InputText(key="-MESSAGE-"), sg.Button("Send")]
        ]
        return layout

    def main(self):
        self.window = sg.Window("Chat Client", self.create_layout(), finalize=True)

        while True:
            event, values = self.window.read()

            if event == sg.WIN_CLOSED or event == "%logout":
                break

            if event == "%connect":
                user_name = values["-USERNAME-"]
                self.connect_to_server(user_name)

            if event == "Send":
                msg = values["-MESSAGE-"]
                self.send_message(msg)

        self.window.close()

    def connect_to_server(self, user_name):
        # Establish the connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 1234))

        # Obtaining input and output streams
        dis = s.makefile("rb")
        dos = s.makefile("wb")

        # Send the username to the server
        username = user_name + "\n"
        dos.write(username.encode())

        # Start threads for sending and receiving messages
        threading.Thread(target=self.receive_messages, args=(dis,)).start()

    def send_message(self, msg):
        try:
            dos.write((msg + "\n").encode())
            if msg == "%logout":
                exit()
        except Exception as e:
            print(f"Exception in send_message: {e}")

    def receive_messages(self, dis):
        while True:
            try:
                # Read the message sent to this client
                msg = dis.readline().decode().strip()
                print(f"Received message: {msg}")

                # Update the GUI
                self.window["-OUTPUT-"].update(value=msg)

            except Exception as e:
                print(e)
                break

# Start the client
client = Client()
client.main()
