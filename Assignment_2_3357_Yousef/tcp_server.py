# Assignment: TCP Simple Chat Room - TCP Server Code Implementation

# **Libraries and Imports**:
#    - Import the required libraries and modules.
#    You may need socket, threading, select, time libraries for the client.
#    Feel free to use any libraries as well.

# **Global Variables**:
#    - IF NEEDED, Define any global variables that will be used throughout the code.

import sys
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import os.path
import threading
import time

clients = {}


def broadcast(message, client_socket, client_name):
    message = message.decode("utf-8")
    encoded_msg = f"{client_name}: {message}".encode("utf-8")
    for client, name in clients.items():
        if client != client_socket:
            client.send(encoded_msg)
    print(f"{client_name}: {message}")


def broadcast_leave(message, client_socket, client_name):
    encoded_msg = f"{client_name}: {message}".encode("utf-8")
    for client, name in clients.items():
        if client != client_socket:
            client.send(encoded_msg)
    print(f"{client_name}: {message}")


def handle_clients(client_socket):
    client_name = client_socket.recv(1024).decode("utf-8")
    clients[client_socket] = client_name
    print(f"{client_name} has joined the chat room.")
    while True:
        try:
            message = client_socket.recv(1024)

            if message.decode("utf-8") == "exit":
                break
            else:
                broadcast(message, client_socket, client_name)

        except ConnectionResetError:
            break
    leave_msg = f"{client_name} has left the chat room."
    print(leave_msg)
    broadcast_leave(leave_msg, client_socket, client_name)
    clients.pop(client_socket, None)
    client_socket.close()


# **Function Definitions**:
#    - In this section, you will implement the functions you will use in the server side.
#    - Feel free to add more other functions, and more variables.
#    - Make sure that names of functions and variables are meaningful.
def run(serverSocket, serverPort):
    print("\n ######### Chat Room #########")
    print(f"\n Server Ready To Recive Connections On Port: {serverPort}")
    while True:
        client_socket, client_address = serverSocket.accept()
        threading.Thread(target=handle_clients, args=(client_socket,)).start()
    # The main server function.


# **Main Code**:
if __name__ == "__main__":
    server_port = 9300
    server_socket = socket(AF_INET, SOCK_STREAM)  # Creating a TCP socket.
    server_socket.bind(("127.0.0.1", server_port))
    server_socket.listen(
        3
    )  # size of the waiting_queue that stores the incoming requests to connect.

    # please note that listen() method is NOT for setting the maximum clients to connect to server.
    # didnt get it? basically, when the process (assume process is man that execute the code line by line) is executing the accept() method on the server side,
    # the process holds or waits there until a client sends a request to connect and then the process continue executing the rest of the code.
    # good! what if there is another client wants to connect and the process on the server side isnt executing the accept() method at the same time,
    # Now listen() method joins the party to solve this issue, it lets the incoming requests from the other clients to be stored in a queue or list until the process execute the accept() method.
    # the size of the queue is set using listen(size). IF YOU STILL DONT GET IT, SEND ME AN EMAIL.

    # list to add the connected client sockets , feel free to adjust it to other place
    try:
        run(server_socket, server_port)  # Calling the function to start the server.
    except KeyboardInterrupt:
        print("\nShutting down the server...")
        for client_socket in clients:
            client_socket.close()
        server_socket.close()
