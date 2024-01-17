# Server
import sys
from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM
import os.path
import threading
import time


live_connections = 0  # Counter for live connections
connections_lock = threading.Lock()  # Lock to ensure thread safety


# Handles The Client Requests
def handle_client(connectionSocket, addr):
    global live_connections
    print(f"Connection Accepted from {addr} Connection Number {live_connections}")
    try:
        data = connectionSocket.recv(1024).decode("utf-8")

        filename = data
        print(f"Received request for File")

        #  If Cient is a web browser

        if filename.startswith("GET /"):
            headers = data.split("\n")
            filename = headers[0].split()[1]
            filename = filename.replace("/", "")
            print("FILE NAME:", filename)
            if os.path.isfile(filename):
                print("File exists: Sending...")
                with open(filename, "rb") as f:
                    content = f.read()

                    # Determine content type requested
                    if filename.endswith(".html"):
                        content_type = "text/html"
                    elif filename.endswith(".css"):
                        content_type = "text/css"
                    elif filename.endswith(".js"):
                        content_type = "application/javascript"
                    else:
                        content_type = "application/octet-stream"

                    response = (
                        f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n".encode()
                        + content
                    )

                    connectionSocket.send(response)

                    print("File Sent")
            #  If File does Not Exist
            else:
                print("File Does Not Exist")
                content_type = "text/html"
                response = f"HTTP/1.1 200 OK\nContent-Type: {content_type}\n\n 404 File Does Not Exist".encode()
                connectionSocket.send(response)

        # If request is from cleint.py

        else:
            _, filename = data.split(" ", 1)
            print(filename)
            if os.path.isfile(filename):
                print("File exists: Sending...")
                with open(filename, "rb") as f:
                    content = f.read()
                    connectionSocket.send(content)
                    print("File Sent")

            else:
                print("File Does Not Exist")
                error_message = "404 Not Found"
                connectionSocket.send(error_message.encode("utf-8"))

    # Handle Errors
    except Exception as e:
        print("client Discconected")
        print(f"Error: {e}")

    # Ends connection
    # un comment time.slee(20) to simulate myltiple connections
    finally:
        connectionSocket.close()
        #############
        time.sleep(20)
        #############
        print("Connection Closed")
        live_connections -= 1
        print(f"Live connections: {live_connections}")  # Debugging print statement


# @parms port
def server(ServerPort, Nclient):
    global live_connections
    serverSocket = socket(AF_INET, SOCK_STREAM)
    MaxConnections = int(Nclient)
    serverSocket.bind(("", int(ServerPort)))
    serverSocket.listen(int(MaxConnections))

    print("Server started and waiting for connections...")

    while True:
        with connections_lock:
            # Ensures that connection does not exceed The specified Max Connections
            if live_connections < MaxConnections:
                connectionSocket, addr = serverSocket.accept()
                live_connections += 1  # Increment the live connections counter
                client_thread = threading.Thread(
                    target=handle_client, args=(connectionSocket, addr)
                )
                client_thread.start()
            else:
                # If max connections reached, send a message and close the connection
                tempSocket, tempAddr = serverSocket.accept()
                error_message = "Cannot establish a connection at the moment."
                tempSocket.send(error_message.encode("utf-8"))
                tempSocket.close()

    #  Close The servers
    serverSocket.close()
    print("Server Closed")

    return 0


if __name__ == "__main__":
    server(sys.argv[1], sys.argv[2])
