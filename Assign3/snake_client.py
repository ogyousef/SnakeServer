
import socket
import pygame
import sys

# Encapsulate game settings in a class
class GameConfig:
    def __init__(self):
        self.width = 500
        self.rows = 20
        self.window = pygame.display.set_mode((self.width, self.width))
        self.red = (255, 0, 0)
        self.green = (0, 255, 0)

    def draw_grid(self):
        size_between = self.width // self.rows
        for line in range(self.rows):
            x = y = line * size_between
            pygame.draw.line(self.window, (255, 255, 255), (x, 0), (x, self.width))
            pygame.draw.line(self.window, (255, 255, 255), (0, y), (self.width, y))

    def redraw_window(self, snake_body, snacks):
        self.window.fill((0, 0, 0))
        self.draw_grid()
        self.draw_snake(snake_body)
        self.draw_snacks(snacks)
        pygame.display.update()

    def draw_snake(self, snake_body):
        dis = self.width // self.rows
        snake_segments = [tuple(map(int, segment.strip("()").split(","))) for segment in snake_body.split('*')]
        for index, (x, y) in enumerate(snake_segments):
            pygame.draw.rect(self.window, self.red, pygame.Rect(x * dis + 1, y * dis + 1, dis - 1, dis - 1))
            if index == 0:
                self.draw_snake_head(x, y, dis)

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

    running = True
    clock = pygame.time.Clock()
    old_data = ""

    while running:
        clock.tick(1000)
        try:
            client.send(str.encode('get'))
            game_state = client.recv(2048).decode()
            snake_body, snacks = game_state.split('|')
            client.send(str.encode('get'))
            new_game_state = client.recv(2048).decode()
            new_data = extract_new_data(old_data, new_game_state)
            if new_data:
                old_data = new_game_state
        except (SyntaxError, TypeError, ValueError) as e:
            print(f"Error during game state parsing or drawing: {e}")
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                client.send(str.encode('quit'))
            elif event.type == pygame.KEYDOWN:
                handle_key_event(event, client)

        game_config.redraw_window(snake_body, snacks)

    pygame.quit()
    client.close()

def handle_key_event(event, client):
    key_actions = {
        pygame.K_LEFT: 'left',
        pygame.K_RIGHT: 'right',
        pygame.K_UP: 'up',
        pygame.K_DOWN: 'down',
        pygame.K_r: 'reset',
        pygame.K_q: 'quit'
    }
    if event.key in key_actions:
        client.send(str.encode(key_actions[event.key]))
        if event.key == pygame.K_q:
            running = False

if __name__ == "__main__":
    main()
