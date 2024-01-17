import numpy as np
import socket
from _thread import *
from snake import SnakeGame
import uuid
import time
import rsa




server = "localhost"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))

s.listen()
print("Waiting for a connection, Server Started")

game = SnakeGame(20)
game_started = False
game_state = ""
interval = 0.2
moves_queue = set()
clients = {}  # Dictionary to hold client connections
clients_KEYS = {}
rgb_colors = {
    "red" : (255, 0, 0),
    "green" : (0, 255, 0),
    "blue" : (0, 0, 255),
    "yellow" : (255, 255, 0),
    "orange" : (255, 165, 0),
} 
rgb_colors_list = list(rgb_colors.values())

def broadcast_game_state():
    global game_state
    while True:
        game_state = game.get_state()
        for unique_id, client in list(clients.items()):  # Use list to safely modify during iteration
            try:
                # print("STATE SENT")
                client.sendall(game_state.encode())
            except:
                # Handle broken connections
                print(f"Lost connection to {unique_id}")
                client.close()
                del clients[unique_id]
                game.remove_player(unique_id)
        time.sleep(0.05)

def broadcast_message(sender_id, message):
    print(f"Message from {sender_id}: {message}")
    for unique_id, client in clients.items():
        if unique_id != sender_id:
            try:
                # print(f'key: {clients_KEYS[unique_id]}')
                encrypted_msg_send = f"MSG: {sender_id} Said: " + message
                # print(f'encrypted msg before sending: {encrypted_msg_send}')
                encrypted_msg = rsa.encrypt(encrypted_msg_send.encode(), clients_KEYS[unique_id])
                client.sendall(encrypted_msg)
            except:
                print(f"Error happned sendding the MSG")

def client_thread(conn, unique_id,priv_key):

    predefined_messages = {
    'z': "Congratulations!",
    'x': "It works!",
    'c': "Ready?"
    }

    global game, moves_queue, clients_KEYS
    while True:
        try:
            data = conn.recv(500)
            if data != 'get':
                decryptData = rsa.decrypt(data, priv_key).decode()
                # print("DECRYPTTED: "+decryptData)
                if not decryptData:
                    raise Exception("Client disconnected")
                if decryptData in ["up", "down", "left", "right"]:
                    moves_queue.add((unique_id, decryptData))
                elif decryptData == "reset":
                    game.reset_player(unique_id)
                elif decryptData in predefined_messages:
                    # print()
                    broadcast_message(unique_id,message = predefined_messages[decryptData])

        except Exception as e:

            # print(f"Error during decryption or data handling: {e}")

            # print(f"Disconnecting client: {unique_id}")
            # conn.close()
            # del clients[unique_id]
            # game.remove_player(unique_id)
            # break
            continue

def game_thread():
    global moves_queue, game_state
    while True:
        game.move(moves_queue)
        moves_queue = set()
        game_state = game.get_state()  # Update the game state here after all moves and resets
        time.sleep(interval)

def start_game():
    global game_started
    if not game_started:
        game_started = True
        start_new_thread(game_thread, ())
        start_new_thread(broadcast_game_state, ())

(pub_key, priv_key) = rsa.newkeys(2048)

# print(f'server public key{pub_key}')

# Wait for the first connection
conn, addr = s.accept()

# conn.send() server sends it public key

conn.send(pub_key.save_pkcs1())

unique_id = str(uuid.uuid4())
game.add_player(unique_id, color="color")
clients[unique_id] = conn

client_pub_key = rsa.PublicKey.load_pkcs1(conn.recv(2048))
# data = conn.recv(500).decode() server recives clients public key
clients_KEYS[unique_id] = client_pub_key # sotre 

# print("LOADED:",client_pub_key)
# print("unloaded :",clients_KEYS[unique_id])


# print(f' client: {client_pub_key}')

print("Connected to:", addr)

start_new_thread(client_thread, (conn, unique_id,priv_key))

start_game()  # Start the game after the first connection

# Handle subsequent connections
while True:
    conn, addr = s.accept()
    conn.send(pub_key.save_pkcs1())
    client_pub_key = rsa.PublicKey.load_pkcs1(conn.recv(2048))
    unique_id = str(uuid.uuid4())
    game.add_player(unique_id, color="color")
    clients[unique_id] = conn
    clients_KEYS[unique_id] = client_pub_key
    print("Connected to:", addr)
    start_new_thread(client_thread, (conn, unique_id,priv_key))
