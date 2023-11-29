import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.util.Scanner;

public class Main {

    private static PrintWriter output;
    private static BufferedReader input;
    private static String clientName = "empty";
    private static boolean inGroup = false;
    private static volatile boolean exitRequested = false;

    public static void main(String[] args) {
        try (Socket socket = new Socket("localhost", 5000)){
            input = new BufferedReader(new InputStreamReader(socket.getInputStream()));
            output = new PrintWriter(socket.getOutputStream(), true);

            Scanner scanner = new Scanner(System.in);
            String userInput;

            ClientRunnable clientRun = new ClientRunnable(socket);
            Thread clientThread = new Thread(clientRun);
            clientThread.start();

            do {
                System.out.println("Enter a command:");
                userInput = scanner.nextLine();

                // Process different commands
            if (userInput.startsWith("%connect")) {
                handleConnectCommand(userInput);
            } else if (userInput.equals("%join")) {
                handleJoinCommand();
            } else if (userInput.startsWith("%post")) {
                handlePostCommand(userInput);
            } else if (userInput.equals("%users")) {
                handleUsersCommand();
            } else if (userInput.equals("%leave")) {
                handleLeaveCommand();
            } else if (userInput.startsWith("%message")) {
                handleMessageCommand(userInput);
            } else if (userInput.equals("%exit")) {
                handleExitCommand();
            } else if (userInput.equals("%groups")) {
                handleGroupsCommand();
            } else if (userInput.startsWith("%groupjoin")) {
                handleGroupJoinCommand(userInput);
            } else if (userInput.startsWith("%grouppost")) {
                handleGroupPostCommand(userInput);
            } else if (userInput.startsWith("%groupusers")) {
                handleGroupUsersCommand(userInput);
            } else if (userInput.startsWith("%groupleave")) {
                handleGroupLeaveCommand(userInput);
            } else if (userInput.startsWith("%groupmessage")) {
                handleGroupMessageCommand(userInput);
            } else {
                // Normal chat message
                sendMessage(userInput);
            }

            } while (!userInput.equals("%exit"));

            exitRequested = true; // Notify the client thread to exit
            clientThread.join(); // Wait for the client thread to finish


        } catch (Exception e) {
            System.out.println("Exception occurred in client main: " + e.getStackTrace());
        }
    }

    // Implement functions to handle each command

    private static void handleConnectCommand(String userInput) {
        // Extract address and port from the command
        // Format: %connect address port
        String[] parts = userInput.split("\\s+");
        if (parts.length == 3) {
            String address = parts[1];
            int port = Integer.parseInt(parts[2]);
            // Connect to the specified address and port
            // Update socket, input, and output accordingly
        } else {
            System.out.println("Invalid %connect command format.");
        }
    }

    private static void handleJoinCommand() {
        // Implement logic to join the message board
        // Update inGroup variable accordingly
        if(clientName.equals("empty")){
                
        }
    }

    private static void handlePostCommand(String userInput) {
        // Extract subject and content from the command
        // Format: %post subject content
        String[] parts = userInput.split("\\s+", 3);
        if (parts.length == 3) {
            String subject = parts[1];
            String content = parts[2];
            // Implement logic to post the message
            String postCommand = String.format("%post %s %s", subject, content);
            output.println(postCommand);
        } else {
            System.out.println("Invalid %post command format.");
        }
    }

    private static void handleUsersCommand() {
        // Implement logic to retrieve and display the list of users in the group
    }

    private static void handleLeaveCommand() {
        // Implement logic to leave the group
        // Update inGroup variable accordingly
    }

    private static void handleMessageCommand(String userInput) {
        // Extract message ID from the command
        // Format: %message messageID
        String[] parts = userInput.split("\\s+");
        if (parts.length == 2) {
            String messageID = parts[1];
            // Implement logic to retrieve and display the content of the message with the given ID
        } else {
            System.out.println("Invalid %message command format.");
        }
    }

    private static void handleExitCommand() {
        // Implement logic to gracefully disconnect from the server and exit the client program
    }

    private static void sendMessage(String message) {
        // Implement logic to send a normal chat message
    }

    //=============================================
    // Implement functions to handle Part 2 commands
    //=============================================

    private static void handleGroupsCommand() {
        // Implement logic to retrieve and display the list of all groups that can be joined
    }

    private static void handleGroupJoinCommand(String userInput) {
        // Extract group ID/name from the command
        // Format: %groupjoin groupID
        String[] parts = userInput.split("\\s+");
        if (parts.length == 2) {
            String groupID = parts[1];
            // Implement logic to join the specified group
        } else {
            System.out.println("Invalid %groupjoin command format.");
        }
    }

    private static void handleGroupPostCommand(String userInput) {
        // Extract group ID/name, subject, and content from the command
        // Format: %grouppost groupID subject content
        String[] parts = userInput.split("\\s+", 4);
        if (parts.length == 4) {
            String groupID = parts[1];
            String subject = parts[2];
            String content = parts[3];
            // Implement logic to post the message to the specified group
        } else {
            System.out.println("Invalid %grouppost command format.");
        }
    }

    private static void handleGroupUsersCommand(String userInput) {
        // Extract group ID/name from the command
        // Format: %groupusers groupID
        String[] parts = userInput.split("\\s+");
        if (parts.length == 2) {
            String groupID = parts[1];
            // Implement logic to retrieve and display the list of users in the specified group
        } else {
            System.out.println("Invalid %groupusers command format.");
        }
    }

    private static void handleGroupLeaveCommand(String userInput) {
        // Extract group ID/name from the command
        // Format: %groupleave groupID
        String[] parts = userInput.split("\\s+");
        if (parts.length == 2) {
            String groupID = parts[1];
            // Implement logic to leave the specified group
        } else {
            System.out.println("Invalid %groupleave command format.");
        }
    }

    private static void handleGroupMessageCommand(String userInput) {
        // Extract group ID/name and message ID from the command
        // Format: %groupmessage groupID messageID
        String[] parts = userInput.split("\\s+");
        if (parts.length == 3) {
            String groupID = parts[1];
            String messageID = parts[2];
            // Implement logic to retrieve and display the content of the message in the specified group
        } else {
            System.out.println("Invalid %groupmessage command format.");
        }
    }

    // ... (Previous code)
}
