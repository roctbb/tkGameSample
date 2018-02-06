import json
from tkinter import Tk, Canvas, mainloop, NW
from PIL import Image, ImageTk
import socket

# размер карты в пикселях
window_width = 600
window_height = 600

# создаем холст
tk = Tk()
c = Canvas(tk, width=window_width, height=window_height, bg='white')
c.pack()

# карта
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

images = {
    "brick": ImageTk.PhotoImage(Image.open("images/brick.jpg").resize((block_width, block_height))),
    "grass": ImageTk.PhotoImage(Image.open("images/grass.jpg").resize((block_width, block_height))),
    "bullet_up": ImageTk.PhotoImage((Image.open("images/bullet.gif").convert('RGBA').resize((10, 30)))),
    "bullet_down": ImageTk.PhotoImage((Image.open("images/bullet.gif").convert('RGBA').resize((10, 30)).rotate(180))),
    "bullet_left": ImageTk.PhotoImage((Image.open("images/bullet.gif").convert('RGBA').resize((10, 30)).rotate(90))),
    "bullet_right": ImageTk.PhotoImage((Image.open("images/bullet.gif").convert('RGBA').resize((10, 30)).rotate(270))),
    "tank_up": ImageTk.PhotoImage((Image.open("images/tank.gif").convert('RGBA').resize((block_width, block_height)))),
    "tank_down": ImageTk.PhotoImage(
        (Image.open("images/tank.gif").convert('RGBA').resize((block_width, block_height)).rotate(180))),
    "tank_left": ImageTk.PhotoImage(
        (Image.open("images/tank.gif").convert('RGBA').resize((block_width, block_height)).rotate(90))),
    "tank_right": ImageTk.PhotoImage(
        (Image.open("images/tank.gif").convert('RGBA').resize((block_width, block_height)).rotate(270)))
}

# рисуем карту
for i in range(12):
    for j in range(12):
        if game_map[i][j] == 0:
            c.create_image(i * block_width, j * block_height, image=images['grass'], anchor=NW)
        if game_map[i][j] == 1:
            c.create_image(i * block_width, j * block_height, image=images['brick'], anchor=NW)


def rotate(object, direction):
    c.itemconfigure(object['up'], state='hidden')
    c.itemconfigure(object['down'], state='hidden')
    c.itemconfigure(object['left'], state='hidden')
    c.itemconfigure(object['right'], state='hidden')
    c.itemconfigure(object[direction], state='normal')
    object['direction'] = direction



def delete(object):
    directions = ['up', 'down', 'left', 'right']
    for direction in directions:
        c.delete(object[direction])




def get_tank(x, y, direction):
    tank = {
        "direction": direction,
        "up": c.create_image(x * block_width, y * block_height, image=images['tank_up'], anchor=NW, state='normal'),
        "down": c.create_image(x * block_width, y * block_height, image=images['tank_down'], anchor=NW, state='hidden'),
        "left": c.create_image(x * block_width, y * block_height, image=images['tank_left'], anchor=NW, state='hidden'),
        "right": c.create_image(x * block_width, y * block_height, image=images['tank_right'], anchor=NW,
                                state='hidden')
    }
    rotate(tank, direction)
    return tank


def get_bullet(rx, ry, direction):
    bullet = {
        "direction": 'up',
        "up": c.create_image(rx, ry, image=images['bullet_up'], state='normal'),
        "down": c.create_image(rx, ry, image=images['bullet_down'],
                               state='hidden'),
        "left": c.create_image(rx, ry, image=images['bullet_left'],
                               state='hidden'),
        "right": c.create_image(rx, ry, image=images['bullet_right'],
                                state='hidden')
    }

    rotate(bullet, direction)

    return bullet



def loop():
    try:
        for tank in tanks:
            delete(tank)
        for bullet in bullets:
            delete(bullet)
        data = b''
        while data.decode('utf-8').count('|') < 2:
            data += s.recv(1024)
        game = json.loads(data.decode('utf-8').split('|')[1])
        for tank in game['tanks']:
            new_tank = get_tank(tank['x'], tank['y'], tank['direction'])
            tanks.append(new_tank)
        for bullet in game['bullets']:
            new_bullet = get_bullet(bullet['x'], bullet['y'], bullet['direction'])
            bullets.append(new_bullet)
    except Exception as e:
        print(e)

    c.after(25, loop)




# нажатие клавишиццы
def keyDown(key):
    if key.char == 'a':
        s.send('go_left'.encode('utf-8'))
    if key.char == 'd':
        s.send('go_right'.encode('utf-8'))
    if key.char == 'w':
        s.send('go_up'.encode('utf-8'))
    if key.char == 's':
        s.send('go_down'.encode('utf-8'))
    if key.keycode == 8320768:
        s.send('fire_up'.encode('utf-8'))
    if key.keycode == 8255233:
        s.send('fire_down'.encode('utf-8'))
    if key.keycode == 8189699:
        s.send('fire_right'.encode('utf-8'))
    if key.keycode == 8124162:
        s.send('fire_left'.encode('utf-8'))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('localhost', 8082))
print('connected')
c.after(50, loop)

# при нажатии любой клавишы вызываем keyDown
tk.bind("<KeyPress>", keyDown)

mainloop()
