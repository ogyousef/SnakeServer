import sys
from socket import socket, AF_INET, SOCK_STREAM
import threading
import argparse
import time

# Flag to determine if the client is running
client_running = True


def print_message(msg):
    sys.stdout.write("\x1b[A")
    sys.stdout.write("\x1b[K")
    # sys.stdout.write("\x1b[K")
    print(msg)  # Print the received message
    sys.stdout.write(f"{client_name}:\n")  # Reprint the prompt
    sys.stdout.flush()  # Ensure it's displayed immediately


def receive_messages(client_socket, client_name):
    global client_running
    while client_running:
        # try:
        data = client_socket.recv(1024).decode("utf-8")
        # print(data)
        # client_running = False
        print_message(data)
    # except:
    #     print("An error occurred while receiving data.")
    #     client_running = False
    #     break


def send_messages(client_socket, client_name):
    global client_running
    client_socket.send(client_name.encode("utf-8"))
    while client_running:
        message = input(f"{client_name}:\n")
        try:
            client_socket.send(message.encode("utf-8"))
            if message == "exit":
                # Giving a little time for the server to process the 'exit' message
                # time.sleep(1)
                client_running = False
                break
                sys.exit(0)
        except:
            print("An error occurred while sending data.")
            client_running = False
            break


def run(client_socket, client_name):
    receive_thread = threading.Thread(
        target=receive_messages, args=(client_socket, client_name)
    )
    receive_thread.start()

    send_thread = threading.Thread(
        target=send_messages, args=(client_socket, client_name)
    )
    send_thread.start()

    receive_thread.join()
    send_thread.join()
    client_socket.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Argument Parser")
    parser.add_argument("name")  # Usage: python tcp_client.py username
    args = parser.parse_args()
    client_name = args.name
    server_addr = "127.0.0.1"
    server_port = 9300

    client_socket = socket(AF_INET, SOCK_STREAM)  # TCP
    client_socket.connect((server_addr, server_port))

    run(client_socket, client_name)
