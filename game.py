import random
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
        "life": 10,
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

def get_action(tank):
    return random.choice(['go_up', 'go_down', 'go_left', 'go_right', 'fire_up', 'fire_down', 'fire_left', 'fire_right'])

def move_bullets():
    for bullet in bullets:
        x, y = coords(bullet)
        bullet_hit = False
        for tank in tanks:
            if (x,y) == coords(tank):
                tank['life']-=1
                bullets.remove(bullet)
                delete(bullet)

                if tank['life'] == 0:
                    if tank == my_tank:
                        tk.destroy()
                    else:
                        delete(tank)
                        tanks.remove(tank)
                bullet_hit = True
                break
        if bullet_hit:
            continue
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
    c.after(50, move_bullets)

def move_tanks():
    for tank in tanks:
        if tank == my_tank:
            continue
        x, y = coords(tank)
        action = get_action(tank)
        if action == "go_up":
            rotate(tank, 'up')
            if is_available(x, y-1):
                move(tank, 0, -block_height)
        if action == "go_down":
            rotate(tank, 'down')
            if is_available(x, y+1):
                move(tank, 0, block_height)
        if action == "go_left":
            rotate(tank, 'left')
            if is_available(x-1, y):
                move(tank, -block_width, 0)
        if action == "go_right":
            rotate(tank, 'right')
            if is_available(x+1, y):
                move(tank, block_width, 0)
        if action == "fire_up":
            rotate(tank, 'up')
            bullets.append(get_bullet(x,y,'up'))
        if action == "fire_down":
            rotate(tank, 'down')
            bullets.append(get_bullet(x,y,'down'))
        if action == "fire_left":
            rotate(tank, 'left')
            bullets.append(get_bullet(x,y,'left'))
        if action == "fire_right":
            rotate(tank, 'right')
            bullets.append(get_bullet(x,y,'right'))

    c.after(1000, move_tanks)

# проверка доступности клетки
def is_available(i, j):
    if i < 0 or i >= 12 or j < 0 or j >= 12:
        return False
    if game_map[i][j] == 1:
        return False
    # new
    for tank in tanks:
        if coords(tank) == (i,j):
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



def start():
    tanks.append(my_tank)
    for i in range(5):
        x = 0
        y = 0
        while not is_available(x,y):
            x = random.randint(1,11)
            y = random.randint(1,11)
        tanks.append(get_tank(x,y,'up'))
    c.after(50, move_bullets)
    c.after(1000, move_tanks)

    # при нажатии любой клавишы вызываем keyDown
    tk.bind("<KeyPress>", keyDown)

    mainloop()

start()