import json
import random
import select, socket, sys, queue
from threading import Thread

import time

window_width = 600
window_height = 600

game_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# размеры блока
block_width = window_width // 12
block_height = window_height // 12

bullets = []
tanks = []
lifes = {}


def get_empty_place():
    while True:
        x = random.randint(1, 10)
        y = random.randint(1, 10)
        if is_available(x, y):
            return x, y


def coords(object):
    x, y = object['x'], object['y']
    return (int(x // block_width), int(y // block_height))


def rotate(object, direction):
    object['direction'] = direction


def move(object, dx, dy):
    object['x'] += dx
    object['y'] += dy


def delete(object):
    if object in tanks:
        tanks.remove(object)
    if object in bullets:
        bullets.remove(object)


def get_tank(x, y, direction):
    tank = {
        "direction": direction,
        "x": x,
        "y": y,
        "life": 5
    }
    return tank


def get_bullet(x, y, direction):
    if direction == 'left':
        rx = block_width * x - 10
        ry = block_height * y + block_height // 2
    elif direction == 'right':
        rx = block_width * (x + 1) + 10
        ry = block_height * y + block_height // 2
    elif direction == 'up':
        rx = block_width * x + block_width // 2
        ry = block_height * y - 10
    else:
        rx = block_width * x + block_width // 2
        ry = block_height * (y + 1) + 10

    bullet = {
        "direction": direction,
        "x": rx,
        "y": ry
    }
    return bullet

def is_collided(tank, bullet):
    x,y = coords(bullet)
    if x == tank['x'] and y == tank['y']:
        return True
    return False

def is_available(i, j):
    if i < 0 or i >= 12 or j < 0 or j >= 12:
        return False
    if game_map[i][j] == 1:
        return False
    for tank in tanks:
        x, y = tank['x'], tank['y']
        if x == i and y == j:
            return False
    return True


def loop():
    while True:
        for bullet in bullets:
            x, y = coords(bullet)

            for tank in tanks:
                if is_collided(tank, bullet):
                    tanks.remove(tank)
                    tank['life']-= 1
                    if tank['life'] > 0:
                        tanks.append(tank)

            if not is_available(x, y):
                delete(bullet)
                continue
            if bullet['direction'] == 'up':
                move(bullet, 0, -20)
            if bullet['direction'] == 'down':
                move(bullet, 0, 20)
            if bullet['direction'] == 'left':
                move(bullet, -20, 0)
            if bullet['direction'] == 'right':
                move(bullet, 20, 0)


        time.sleep(0.05)

def process_command(tank, command):
    dx = 0
    dy = 0
    if command == 'go_up':
        rotate(tank, 'up')
        if is_available(tank['x'], tank['y'] - 1):
            dy = -1
    if command == 'go_down':
        rotate(tank, 'down')
        if is_available(tank['x'], tank['y'] + 1):
            dy = 1
    if command == 'go_left':
        rotate(tank, 'left')
        if is_available(tank['x'] - 1, tank['y']):
            dx = -1
    if command == 'go_right':
        rotate(tank, 'right')
        if is_available(tank['x'] + 1, tank['y']):
            dx = 1
    if command == 'fire_up':
        rotate(tank, 'up')
        new_bullet = get_bullet(tank['x'], tank['y'], 'up')
        bullets.append(new_bullet)
    if command == 'fire_down':
        rotate(tank, 'down')
        new_bullet = get_bullet(tank['x'], tank['y'], 'down')
        bullets.append(new_bullet)
    if command == 'fire_left':
        rotate(tank, 'left')
        new_bullet = get_bullet(tank['x'], tank['y'], 'left')
        bullets.append(new_bullet)
    if command == 'fire_right':
        rotate(tank, 'right')
        new_bullet = get_bullet(tank['x'], tank['y'], 'right')
        bullets.append(new_bullet)
    move(tank, dx, dy)
    return tank



server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setblocking(0)
server.bind(('localhost', 8082))
server.listen(5)
inputs = [server]
outputs = []
message_queues = {}

thread = Thread(target=loop)
thread.start()

while inputs:
    readable, writable, exceptional = select.select(inputs, outputs, inputs)
    for s in readable:
        if s is server:
            print("accepting connection")
            connection, client_address = s.accept()
            connection.setblocking(0)
            inputs.append(connection)
            outputs.append(connection)
            x,y = get_empty_place()
            new_tank = get_tank(x,y,'up')
            message_queues[connection] = new_tank
            tanks.append(new_tank)
            print('accepted')
        else:
            data = s.recv(11024)
            if data:
                command = data.decode('utf-8')
                print("received", command)
                tank = message_queues[connection]
                print(tank)
                tanks.remove(tank)
                tank = process_command(tank, command)
                print(tank)
                tanks.append(tank)

                if s not in outputs:
                    outputs.append(s)
            else:
                if s in outputs:
                    outputs.remove(s)
                inputs.remove(s)
                s.close()
                del message_queues[s]

    for s in writable:
            tank = message_queues[connection]
            if tank not in tanks:
                s.close()
            response = '|' + json.dumps({
                "me": tank,
                "tanks": tanks,
                "bullets": bullets
            })
            s.sendall(response.encode('utf-8'))

    for s in exceptional:
        inputs.remove(s)
        if s in outputs:
            outputs.remove(s)
        s.close()
        del message_queues[s]
    time.sleep(0.025)
