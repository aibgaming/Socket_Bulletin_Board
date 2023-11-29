import socket
import threading
import PySimpleGUI as sg

MAX_BUFFER_SIZE = 4096
HOST_ADDR = "localhost"
HOST_PORT = 5000
msgs = []

sg.theme("DarkTeal5")
sg.set_options(font=("Helvetica", 13))
layout = [
    [sg.Text("Name:"), sg.InputText(key="-NAME-", size=(30, 1)),
     sg.Button("Connect", key="-CONNECT-", size=(15, 1)),
     sg.Button("Stop", key="-STOP1-", size=(15, 1))],
    [sg.Multiline(key="-DISPLAY-", size=(70, 23), disabled=True,
                  autoscroll=True)],
    [sg.InputText(key="-MESSAGE-", size=(55, 1)),
     sg.Button("Send", key="-SEND-", bind_return_key=True, size=(15, 1))],
]

window = sg.Window("Client", layout, size=(600, 425))
client = None
username = ""

def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    print(10)
    try:
        print(20)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        print(client)
        send_message(client, f"connect:{name}")
        window["-NAME-"].update(disabled=True)
        window["-CONNECT-"].update(disabled=True)
        window["-MESSAGE-"].update(disabled=False)

        thread = threading.Thread(target=receive_message_from_server, args=(client,))
        thread.start()
    except Exception as e:
        sg.popup_error(f"Cannot connect to host: {HOST_ADDR} on port: {HOST_PORT}. Server may be unavailable. Try again later.")

def send_message(sock, message):
    sock.sendall(message.encode())

def receive_message(sock):
    data = sock.recv(MAX_BUFFER_SIZE).decode()
    return data

def receive_message_from_server(sck):
    try:
        while True:
            message = receive_message(sck)
            handle_message(message)
    except OSError:
        exit()

def handle_message(message):
    # Process the received message as needed
    sender, content = message.split(":", 1)
    msgs.append(f"{sender} -> {content}")
    text = "\n".join(msgs)
    window["-DISPLAY-"].update(f"{text}\n")

def main():
    global username
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == "-CONNECT-":

            if len(values["-NAME-"]) < 1:
                sg.popup_error("Enter a valid name.")
            else:
                username = values["-NAME-"]
                connect_to_server(username)
        elif event == "-STOP1-":
            if client:
                client.close()
            window.close()
            exit()
        elif event == "-SEND-":
            msg = values["-MESSAGE-"].replace('\n', '')
            if msg:
                send_message(client, f"send:{username}:{msg}")
                msgs.append(f"You -> {msg}")
                text = "\n".join(msgs)
                window["-DISPLAY-"].update(f"{text}\n")
                window["-MESSAGE-"].update(value="")
                window["-MESSAGE-"].set_focus()

if __name__ == "__main__":
    main()
