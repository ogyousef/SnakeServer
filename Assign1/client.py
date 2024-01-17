# client
import sys

from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM

serverIP = "127.0.0.1"


def client(port, file):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverIP, int(port)))
    print("Connection Established")
    fileName = file
    print(f"sent request For File {fileName}")
    clientSocket.send(f"GET {fileName}".encode("utf-8"))

    data = clientSocket.recv(1024).decode("utf-8")
    if data.__contains__("404"):
        print("File not found on the server.")
    elif data.__contains__("Cannot establish a connection at the moment."):
        print("Server is Busy at The Moment Please try again later")
    else:
        with open(f"received_{fileName}", "w") as f:
            f.write(data)
        print(f"File {fileName} received and saved as received_{fileName}")
    # print(f"Received from server: {data}")

    clientSocket.close()
    print("Coneection closed")
    return 0


if __name__ == "__main__":
    client(sys.argv[1], sys.argv[2])
