from tkinter import Tk, Canvas, mainloop, NW
from PIL import Image, ImageTk

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


def move(object, dx, dy):
    directions = ['up', 'down', 'left', 'right']
    for direction in directions:
        c.move(object[direction], dx, dy)


def delete(object):
    directions = ['up', 'down', 'left', 'right']
    for direction in directions:
        c.delete(object[direction])


def coords(object):
    x, y = c.coords(object['up'])
    return (int(x // block_width), int(y // block_height))


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


my_tank = get_tank(6, 6, 'up')


def loop():
    for bullet in bullets:
        x, y = coords(bullet)
        if not is_available(x, y):
            delete(bullet)
            bullets.remove(bullet)
            continue
        if bullet['direction'] == 'up':
            move(bullet, 0, -20)
        if bullet['direction'] == 'down':
            move(bullet, 0, 20)
        if bullet['direction'] == 'left':
            move(bullet, -20, 0)
        if bullet['direction'] == 'right':
            move(bullet, 20, 0)
    c.after(50, loop)


# проверка доступности клетки
def is_available(i, j):
    if i < 0 or i >= 12 or j < 0 or j >= 12:
        return False
    if game_map[i][j] == 1:
        return False
    return True


# нажатие клавишиццы
def keyDown(key):
    dx = 0
    dy = 0
    x, y = coords(my_tank)
    if key.char == 'a':
        rotate(my_tank, 'left')
        if is_available(x - 1, y):
            dx = -1
    if key.char == 'd':
        rotate(my_tank, 'right')
        if is_available(x + 1, y):
            dx = 1
    if key.char == 'w':
        rotate(my_tank, 'up')
        if is_available(x, y - 1):
            dy = -1
    if key.char == 's':
        rotate(my_tank, 'down')
        if is_available(x, y + 1):
            dy = 1
    if key.keycode == 8320768:
        rotate(my_tank, 'up')
        bullets.append(get_bullet(x, y, 'up'))
    if key.keycode == 8255233:
        rotate(my_tank, 'down')
        bullets.append(get_bullet(x, y, 'down'))
    if key.keycode == 8189699:
        rotate(my_tank, 'right')
        bullets.append(get_bullet(x, y, 'right'))
    if key.keycode == 8124162:
        rotate(my_tank, 'left')
        bullets.append(get_bullet(x, y, 'left'))
    move(my_tank, dx * block_width, dy * block_height)


c.after(50, loop)

# при нажатии любой клавишы вызываем keyDown
tk.bind("<KeyPress>", keyDown)

mainloop()
