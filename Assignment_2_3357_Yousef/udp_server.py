# Assignment: UDP Simple Chat Room - UDP Server Code Implementation

# **Libraries and Imports**:
#    - Import the required libraries and modules.
import sys
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import os.path
import threading
import time


# **Global Variables**:
#    - IF NEEDED, Define any global variables that will be used throughout the code.
active_clients = {}


# **Function Definitions**:
#    - In this section, you will implement the functions you will use in the server side.
#    - Feel free to add more other functions, and more variables.
#    - Make sure that names of functions and variables are meaningful.
def run(serverSocket, serverPort):
    serverSocket.bind(("", serverPort))
    print("\n ######### Chat Room #########")
    print(f"\n Server Ready To Recive Connections On Port: {serverPort}")

    # serverSocket.listen()
    while True:
        data, addr = serverSocket.recvfrom(1024)

        if data.startswith(b"JOIN:"):
            username = data[5:].decode("utf-8")
            active_clients[addr] = username
            print(f"User {username} joined from adress:{addr}")

        if data.startswith(b"exit"):
            print(f"User {username} Left from adress:{addr}")
            active_clients.pop(addr)
            # username = data[5:].decode("utf-8")
            # active_clients[addr] = username
        if not data.startswith(b"JOIN:") and not data.startswith(b"exit"):
            print(
                f"Message Recived From {addr} {active_clients[addr]}: {data.decode('utf-8')}"
            )
        for client_addr in active_clients:
            if (
                client_addr != addr
                and not data.startswith(b"JOIN:")
                and not data.startswith(b"exit")
            ):
                message_to_broadcast = (
                    f"{active_clients[addr]}: {data.decode('utf-8')}".encode("utf-8")
                )
                serverSocket.sendto(message_to_broadcast, client_addr)


# **Main Code**:
if __name__ == "__main__":
    serverPort = 9301  # Set the `serverPort` to the desired port number (e.g., 9301).
    serverSocket = socket(AF_INET, SOCK_DGRAM)  # Creating a UDP socket.
    run(serverSocket, serverPort)  # Calling the function to start the server.
    try:
        run(serverSocket, serverPort)  # Calling the function to start the server.
    except KeyboardInterrupt:
        print("\nShutting down the server...")
    serverSocket.close()
