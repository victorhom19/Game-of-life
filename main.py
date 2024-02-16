import pygame
import time

from utils import Button

FPS = 60
SCREEN_WIDTH = 900
SCREEN_HEIGTH = 900

UPDATE_RATE = .5  # in seconds

control_pane_height = SCREEN_HEIGTH / 5
control_pane_width = SCREEN_WIDTH
panel_x = 0
panel_y = SCREEN_HEIGTH - control_pane_height

field_size = min(SCREEN_HEIGTH, SCREEN_WIDTH) - control_pane_height

FIELD_WIDTH = 30

cell_width = field_size / FIELD_WIDTH

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

def main():
    load_initial_state()
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGTH])
    clock = pygame.time.Clock()

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                continue
        dt = clock.tick(FPS)
        get_input(events)
        update(dt)
        draw(screen)
        # print_fps()
        pygame.display.flip()

    pygame.quit()


def load_initial_state():
    # TODO: implement loading from file

    center = FIELD_WIDTH // 2
    cells = [
        (center, center),
        (center, center - 1),
        (center - 1, center),
        (center + 1, center),
    ]
    for (x, y) in cells:
        if x >= 0 and x < FIELD_WIDTH and y >= 0 and y < FIELD_WIDTH:
            field[y][x] = True

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
        neighbours = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i == 0 and j == 0):
                    continue
                new_x = x + i
                new_y = y + j
                if new_x >= 0 and new_x < FIELD_WIDTH and new_y >= 0 and new_y < FIELD_WIDTH:
                    cell = field[new_y][new_x]
                    if cell:
                        neighbours += 1
        return neighbours

    for y, row in enumerate(field):
        for x, cell in enumerate(row):
            neighbours = get_neighbours(x, y)

            # Any live cell with fewer than two live neighbors dies, as if by underpopulation.
            if cell and neighbours < 2:
                new_field[y][x] = False
                continue

            # Any live cell with two or three live neighbors lives on to the next generation.
            if cell and neighbours == 2 or neighbours == 3:
                new_field[y][x] = True
                continue

            # Any live cell with more than three live neighbors dies, as if by overpopulation.
            if cell and neighbours > 3:
                new_field[y][x] = False
                continue

            # Any dead cell with exactly three live neighbors becomes a live cell, as if by reproduction
            if not cell and neighbours == 3:
                new_field[y][x] = True
                continue

    return new_field


def draw(screen):
    global buttons

    screen.fill((255, 255, 255))

    for y, row in enumerate(field):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * cell_width, y *
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
            control_pane_width / 2 - button_width / 2 - spacing,
            control_pane_height / 2,
            button_width,
            button_height,
            "start" if not moving else "stop",
            on_start_button
        ),
        Button(
            control_pane_width / 2 - button_width / 2 + spacing,
            control_pane_height / 2,
            button_width,
            button_height,
            "step",
            on_step
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


if __name__ == '__main__':
    main()
