import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.ArrayList;

public class ServerThread extends Thread {
    private Socket socket;
    private ArrayList<ServerThread> threadList;
    private PrintWriter output;

    public ServerThread(Socket socket, ArrayList<ServerThread> threads) {
        this.socket = socket;
        this.threadList = threads;
    }

    @Override
    public void run() {
        try {
            // Reading the input from the client
            BufferedReader input = new BufferedReader(new InputStreamReader(socket.getInputStream()));

            // Returning the output to the client: true statement is to flush the buffer; otherwise,
            // we have to do it manually
            output = new PrintWriter(socket.getOutputStream(), true);

            // Infinite loop for the server
            while (true) {
                String command = input.readLine();

                // If user types exit command
                if (command.equals("exit")) {
                    break;
                }

                // Handle different commands
                switch (command) {
                    case "connect":
                        handleConnectCommand();
                        break;
                    case "send":
                        handleSendCommand();
                        break;
                    // Add other command handlers as needed
                }

                System.out.println("Server received " + command);
            }
        } catch (Exception e) {
            System.out.println("Error occurred " + e.getStackTrace());
        }
    }

    private void handleConnectCommand() {
        // Handle the connect command (e.g., add the user to the list)
        // ...

        // Example: send a welcome message back
        String welcomeMessage = "Welcome, user!";
        output.println(welcomeMessage);
    }

    private void handleSendCommand() {
        // Handle the send command (e.g., broadcast the message to all clients)
        // ...

        // Example: send the message back to all clients
        String broadcastMessage = "Broadcast: Hello, everyone!";
        printToAllClients(broadcastMessage);
    }

    private void printToAllClients(String outputString) {
        for (ServerThread sT : threadList) {
            sT.output.println(outputString);
        }
    }
}
