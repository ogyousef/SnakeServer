import socket
import pygame
import sys
import re
from snake import snake

# Set up the client's socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = 'localhost'  # The server's hostname or IP address
port = 5555         # The port used by the server

# Connect to the server
try:
    client.connect(("127.0.0.1", port))
except socket.error as e:
    print(str(e))
    sys.exit()

def drawGrid(w, rows, surface):
    sizeBtwn = w // rows

    x = 0
    y = 0
    for l in range(rows):
        x = x + sizeBtwn
        y = y + sizeBtwn

        pygame.draw.line(surface, (255,255,255), (x,0),(x,w))
        pygame.draw.line(surface, (255,255,255), (0,y),(w,y))




def redrawWindow(surface,snake_body,snacks):
    global rows, width, s, snack
    surface.fill((0,0,0))
    drawGrid(width,rows, surface)
    draw_snake(snake_body, surface)
    draw_snacks(snacks,surface)
    pygame.display.update()



# Initialize Pygame
pygame.init()


global width, rows, s, snack
width = 500
rows = 20

win = pygame.display.set_mode((width, width))

red = (255, 0, 0)
green = (0, 255, 0)

def draw_snake(snake_body, surface):
    dis = width // rows

    # print("snake_body: " , snake_body)

    snake_body = snake_body.split('*')

    for index,segment in enumerate(snake_body):
        segment = segment.replace(")","").replace("(","").split(",")
        pygame.draw.rect(surface, red, pygame.Rect(int(segment[0])*dis+1, int(segment[1])*dis+1 , dis-1, dis-1))
        if index == 0:
            centre = dis//2
            radius = 3
            circleMiddle = (int(segment[0])*dis+centre-radius,int(segment[1])*dis+8)
            circleMiddle2 = (int(segment[0])*dis + dis -radius*2, int(segment[1])*dis+8)
            pygame.draw.circle(surface, (0,0,0), circleMiddle, radius)
            pygame.draw.circle(surface, (0,0,0), circleMiddle2, radius)

def draw_snacks(snacks, surface):
    dis = width // rows


    snacks = snacks.split('**')

    for snack in snacks:
        snack = snack.replace(")","").replace("(","").split(",")
        # x, y = snack
        pygame.draw.rect(surface, green, pygame.Rect(int(snack[0])*dis+1, int(snack[1])*dis+1, dis-1, dis-1))


flag = True

clock = pygame.time.Clock()

def extract_new_data(old_data, new_data):
    min_length = min(len(old_data), len(new_data))
    diff_index = next((i for i in range(min_length) if old_data[i] != new_data[i]), len(old_data))
    return new_data[diff_index:]



while flag:
    clock.tick(1000)

    
    
    try:

        client.send(str.encode('get'))
        game_state = client.recv(2048).decode()
        old_data = game_state

        # Process the initial data
        snake_body_str, snacks_str = game_state.split('|')

        # Subsequent request to the server
        client.send(str.encode('get'))
        new_game_state = client.recv(2048).decode()

        # Extract new data
        new_data = extract_new_data(old_data, new_game_state)

        # If there's new data, process it
        if new_data:
            new_snake_body_str, new_snacks_str = new_data.split('|')
            # Update old data for the next comparison
            old_data = new_game_state

    except (SyntaxError, TypeError, ValueError) as e:
        print(f"Error during game state parsing or drawing: {e}")
        
        continue

    
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            client.send(str.encode('quit'))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                client.send(str.encode('left'))
            elif event.key == pygame.K_RIGHT:
                client.send(str.encode('right'))
            elif event.key == pygame.K_UP:
                client.send(str.encode('up'))
            elif event.key == pygame.K_DOWN:
                client.send(str.encode('down'))
            elif event.key == pygame.K_r:
                client.send(str.encode('reset'))
            elif event.key == pygame.K_q:
                run = False
                client.send(str.encode('quit'))
    redrawWindow(win,snake_body_str,snacks_str)

pygame.quit()
client.close()
