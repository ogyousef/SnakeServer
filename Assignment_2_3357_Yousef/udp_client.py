# Assignment: UDP Simple Chat Room - UDP Client Code Implementation

# **Libraries and Imports**:
#    - Import the required libraries and modules.
import sys
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import os.path
import threading
import time
import argparse


client_running = threading.Event()


#    Feel free to use any libraries as well.


# **Global Variables**:
#    - IF NEEDED, Define any global variables that will be used throughout the code.


# **Function Definitions**:
#    - In this section, you will implement the functions you will use in the client side.
#    - Feel free to add more other functions, and more variables.
#    - Make sure that names of functions and variables are meaningful.
#    - Take into consideration error handling, interrupts,and client shutdown.
def print_message(msg):
    sys.stdout.write("\x1b[K")  # Clear the current line
    print(msg)  # Print the received message
    sys.stdout.write(f"{clientname}:\n")  # Reprint the prompt
    sys.stdout.flush()  # Ensure it's displayed immediately


def receive_messages(clientSocket, clientname):
    global client_running
    while not client_running.is_set():
        try:
            data, addr = clientSocket.recvfrom(1024)
            print_message(data.decode("utf-8"))
        except OSError:
            break


def send_messages(clientSocket, serverAddr, serverPort, clientname):
    global client_running
    clientSocket.sendto(
        ("JOIN:" + clientname).encode("utf-8"), (serverAddr, serverPort)
    )
    while not client_running.is_set():
        # message = input(f"{clientname}:")
        message = input(f"{clientname}:\n")  # Get user input
        clientSocket.sendto(message.encode(), (serverAddr, serverPort))
        if message == "exit" or message.startswith("exit"):
            print("TESTCASE")
            client_running.set()
            clientSocket.close()
            # sys.exit(0)
            break


def run(clientSocket, clientname, serverAddr, serverPort):
    receive_thread = threading.Thread(
        target=receive_messages, args=(clientSocket, clientname)
    )
    receive_thread.start()

    send_thread = threading.Thread(
        target=send_messages, args=(clientSocket, serverAddr, serverPort, clientname)
    )
    send_thread.start()

    receive_thread.join()
    send_thread.join()
    clientSocket.close()


# **Main Code**:
if __name__ == "__main__":
    # Arguments: name address
    parser = argparse.ArgumentParser(description="argument parser")
    parser.add_argument("name")  # to use: python udp_client.py username
    args = parser.parse_args()
    clientname = args.name
    serverAddr = "127.0.0.1"
    serverPort = 9301
    clientSocket = socket(AF_INET, SOCK_DGRAM)  # UDP

    run(
        clientSocket, clientname, serverAddr, serverPort
    )  # Calling the function to start the client.
