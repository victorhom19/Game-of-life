import json

import pygame
import pygame_gui
import time
import tkinter as tk
from tkinter import filedialog
from utils import Button


FPS = 60
SCREEN_WIDTH = 950
SCREEN_HEIGHT = 900

UPDATE_RATE = .5  # in seconds

control_pane_height = SCREEN_HEIGHT / 5
control_pane_width = SCREEN_WIDTH
panel_x = 0
panel_y = SCREEN_HEIGHT - control_pane_height

field_size = min(SCREEN_HEIGHT, SCREEN_WIDTH) - control_pane_height

FIELD_WIDTH = 30

cell_width = field_size / FIELD_WIDTH

FIELD_OFFSET_X = (SCREEN_WIDTH - cell_width * FIELD_WIDTH) / 2

# count_fps = 0
# last_time = time.time()
# def print_fps():
#     global count_fps, last_time
#     count_fps += 1
#     curr_time = time.time()
#     if time.time() - last_time >= 1:
#         print(f"fps: {count_fps}")
#         last_time = curr_time
#         count_fps = 0

# game state:
field = [[False for _ in range(FIELD_WIDTH)] for _ in range(FIELD_WIDTH)]
moving = False

buttons = []

# Init tk for filedialogs
root = tk.Tk()
root.withdraw()

# Game params
BIRTH_PARAM = [3]
SURVIVE_PARAM = [2, 3]


def main():
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    clock = pygame.time.Clock()

    running = True
    while running:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                x -= FIELD_OFFSET_X
                if x <= field_size and y <= field_size:
                    row = int(x // cell_width)
                    column = int(y // cell_width)
                    field[column][row] = not field[column][row]

        dt = clock.tick(FPS)
        get_input(events)
        update(dt)
        draw(screen)
        # print_fps()
        pygame.display.flip()


    pygame.quit()



def get_input(events):
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            for button in buttons:
                real_rects = pygame.Rect(
                    panel_x + button.rect.left,
                    panel_y + button.rect.top,
                    button.rect.width,
                    button.rect.height
                )
                if real_rects.collidepoint(mouse_pos):
                    button.callback()
    pass


prev_update = 0


def update(dt):
    global field
    global prev_update
    if not prev_update:
        prev_update = time.time()
        return
    cur_time = time.time()
    if cur_time - prev_update >= UPDATE_RATE:
        if not moving:
            return
        step()
        prev_update = cur_time


def step():
    global field
    new_field = update_state()
    field = new_field


def update_state():
    # https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules

    new_field = [[False for _ in range(FIELD_WIDTH)]
                 for _ in range(FIELD_WIDTH)]

    def get_neighbours(x, y):
        neighbour_cells = [
            field[y - 1][x - 1],
            field[y - 1][x],
            field[y - 1][(x + 1) % FIELD_WIDTH],

            field[y][x - 1],
            field[y][(x + 1) % FIELD_WIDTH],

            field[(y + 1) % FIELD_WIDTH][x - 1],
            field[(y + 1) % FIELD_WIDTH][x],
            field[(y + 1) % FIELD_WIDTH][(x + 1) % FIELD_WIDTH]
        ]
        return sum(neighbour_cells)



    for y, row in enumerate(field):
        for x, cell in enumerate(row):
            neighbours = get_neighbours(x, y)

            # Any live cell which does not meet survive criteria dies.
            if cell and neighbours not in SURVIVE_PARAM:
                new_field[y][x] = False
                continue

            # Any live cell which meets survive criteria lives on.
            if cell and neighbours in SURVIVE_PARAM:
                new_field[y][x] = True
                continue

            # Any dead cell which meets birth criteria becomes a live cell
            if not cell and neighbours in BIRTH_PARAM:
                new_field[y][x] = True
                continue

    return new_field


def draw(screen):
    global buttons

    screen.fill((255, 255, 255))



    for y, row in enumerate(field):
        for x, cell in enumerate(row):
            rect = pygame.Rect(FIELD_OFFSET_X + x * cell_width, y *
                               cell_width, cell_width, cell_width)
            color = (0, 0, 0) if cell else (255, 255, 255)
            border_color = (160, 160, 160)
            border_width = 1
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, border_color, rect, border_width)

    # draw controls:
    panel = pygame.Surface((control_pane_width, control_pane_height))
    panel.fill((255, 255, 255))
    button_height = control_pane_height / 4
    button_width = button_height * 3


    spacing = control_pane_width / 5

    buttons = [
        Button(
            control_pane_width / 2 - button_width / 2 - 3 * spacing / 2,
            control_pane_height / 4,
            button_width,
            button_height,
            "start" if not moving else "stop",
            on_start_button
        ),
        Button(
            control_pane_width / 2 - button_width / 2 - spacing / 2,
            control_pane_height / 4,
            button_width,
            button_height,
            "step",
            on_step
        ),
        Button(
            control_pane_width / 2 - button_width / 2 + spacing / 2,
            control_pane_height / 4,
            button_width,
            button_height,
            "slower",
            on_slower
        ),
        Button(
            control_pane_width / 2 - button_width / 2 + 3 * spacing / 2,
            control_pane_height / 4,
            button_width,
            button_height,
            "faster",
            on_faster
        ),
        Button(
            control_pane_width / 2 - button_width / 2 - spacing,
            3 * control_pane_height / 4 - 20,
            button_width,
            button_height,
            "load",
            on_load
        ),
        Button(
            control_pane_width / 2 - button_width / 2,
            3 * control_pane_height / 4 - 20,
            button_width,
            button_height,
            "save",
            on_save
        ),
        Button(
            control_pane_width / 2 - button_width / 2 + spacing,
            3 * control_pane_height / 4 - 20,
            button_width,
            button_height,
            "reset",
            on_reset
        ),

    ]

    for button in buttons:
        button.draw(panel)

    screen.blit(panel, (panel_x, panel_y))
    pass


def on_start_button():
    global moving
    moving = not moving

def on_step():
    step()

def on_load():
    global field
    with filedialog.askopenfile(
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")]) as f:
        field = json.loads(f.read())

def on_save():
    with filedialog.asksaveasfile(
            initialfile='state.txt',
            defaultextension=".txt",
            filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")]) as f:
        f.write(json.dumps(field))

def on_slower():
    global UPDATE_RATE
    if UPDATE_RATE < 2:
        UPDATE_RATE += 0.05

def on_faster():
    global UPDATE_RATE
    if UPDATE_RATE > 0.05:
        UPDATE_RATE -= 0.05

def on_reset():
    global field
    field = [[False for _ in range(FIELD_WIDTH)] for _ in range(FIELD_WIDTH)]

if __name__ == '__main__':
    main()
