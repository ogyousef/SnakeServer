
import socket
import pygame
import sys
import time
import numpy as np
import rsa

# Encapsulate game settings in a class
class GameConfig:
    def __init__(self):
        self.width = 500
        self.rows = 20
        self.window = pygame.display.set_mode((self.width, self.width))
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)
        self.rgb_colors = {
            "red" : (255, 0, 0),
            "green" : (0, 255, 0),
            "blue" : (0, 0, 255),
            "yellow" : (255, 255, 0),
            "orange" : (255, 165, 0),
        } 
        self.rgb_colors_list = list(self.rgb_colors.values())
        self.color = self.rgb_colors_list[np.random.randint(0, len(self.rgb_colors_list))]

    def draw_grid(self):
        size_between = self.width // self.rows
        for line in range(self.rows):
            x = y = line * size_between
            pygame.draw.line(self.window, (255, 255, 255), (x, 0), (x, self.width))
            pygame.draw.line(self.window, (255, 255, 255), (0, y), (self.width, y))

    def redraw_window(self, snake_body, snacks):
        self.window.fill((0, 0, 0))
        self.draw_grid()
        self.draw_snakes(snake_body)
        self.draw_snacks(snacks)
        pygame.display.update()

    def draw_snakes(self, snakes_bodies):
        dis = self.width // self.rows
        all_snakes = snakes_bodies.split('**')
        for snake_body in all_snakes:
            try:
                snake_segments = [tuple(map(int, segment.strip("()").split(","))) for segment in snake_body.split('*')]
                for index, (x, y) in enumerate(snake_segments):
                    pygame.draw.rect(self.window, self.color, pygame.Rect(x * dis + 1, y * dis + 1, dis - 1, dis - 1))
                    if index == 0:
                        self.draw_snake_head(x, y, dis)
            except (ValueError, IndexError):
                # Handle the error or log it
                print(f' error: {ValueError}')  # Replace with error handling code


    def draw_snake_head(self, x, y, dis):
        centre = dis // 2
        radius = 3
        circle_positions = [(x * dis + centre - radius, y * dis + 8), (x * dis + dis - radius * 2, y * dis + 8)]
        for pos in circle_positions:
            pygame.draw.circle(self.window, (0, 0, 0), pos, radius)


    def draw_snacks(self, snacks):
        dis = self.width // self.rows
        snack_positions = [tuple(map(int, snack.strip("()").split(","))) for snack in snacks.split('**')]
        for x, y in snack_positions:
            pygame.draw.rect(self.window, self.green, pygame.Rect(x * dis + 1, y * dis + 1, dis - 1, dis - 1))

def connect_to_server(host='localhost', port=5555):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
        return client
    except socket.error as e:
        print(str(e))
        sys.exit()

def extract_new_data(old_data, new_data):
    diff_index = next((i for i in range(min(len(old_data), len(new_data))) if old_data[i] != new_data[i]), len(old_data))
    return new_data[diff_index:]

def main():

    pygame.init()
    game_config = GameConfig()
    client = connect_to_server()
    time.sleep(1)

    (client_pub_key, client_priv_key) = rsa.newkeys(2048)

    server_pub_key = rsa.PublicKey.load_pkcs1(client.recv(2048)) # Receive server public key

    # print(server_pub_key)

    client.send(client_pub_key.save_pkcs1())

    running = True
    clock = pygame.time.Clock()
    old_data = ""

    while running:
        clock.tick(1000)

        try:
            client.send(str.encode('get'))
            received_data = client.recv(2048)

            try:
                # print(received_data.decode())
                # First, try to decode and process as unencrypted data
                decoded_data = received_data.decode()
                game_state = decoded_data
                snake_body, snacks = game_state.split('|')
                client.send(str.encode('get'))
                new_game_state = client.recv(2048).decode()
                new_data = extract_new_data(old_data, new_game_state)

                if new_data:
                    old_data = new_game_state

                else:
                    # print("11111111111111")
                    raise ValueError("Data does not start with expected character")

            except (UnicodeDecodeError, ValueError):
                # print("222222222222")
                # If decoding fails or data doesn't start with '(', try decrypting
                decryptMsg = rsa.decrypt(received_data, client_priv_key).decode()
                # print(decryptMsg)
                # Handle the decrypted message (assuming it's a chat message)
                if decryptMsg.startswith("MSG: "):
                    handle_chat_message(decryptMsg)

        except Exception as e:
                continue




        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                client.send(str.encode('quit'))
            elif event.type == pygame.KEYDOWN:
                handle_key_event(event, client,server_pub_key)

        game_config.redraw_window(snake_body, snacks)

    pygame.quit()
    client.close()

def handle_chat_message(message):
    print(message[4:]) 

def handle_key_event(event, client,server_pub_key):
    key_actions = {
        pygame.K_LEFT: 'left',
        pygame.K_RIGHT: 'right',
        pygame.K_UP: 'up',
        pygame.K_DOWN: 'down',
        pygame.K_r: 'reset',
        pygame.K_q: 'quit',
        pygame.K_x: "x",
        pygame.K_z: "z",
        pygame.K_c: "c"
    }
    if event.key in key_actions:
        action = key_actions[event.key]
        encrypted_data = rsa.encrypt(action.encode(), server_pub_key)
        client.send(encrypted_data)
        # client.send(str.encode(key_actions[event.key]))
        if event.key == pygame.K_q:
            running = False

if __name__ == "__main__":
    main()
