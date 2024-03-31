"""
Main module of cellular automata simulation program.
Provides basic types and functions for configuring and running 2D cellular automata.
See Conway "Game of Life" for more details:
https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life#Rules
"""
import os.path
import time
import json
import tkinter as tk
from tkinter import filedialog
from typing import List

import pygame

from utils import Button

# Init tk for filedialogs
root = tk.Tk()
root.withdraw()

# ----- Screen params -----
SCREEN_WIDTH = 950
SCREEN_HEIGHT = 900

FPS = 60

# ----- Panel sizes -----
CONTROL_PANE_HEIGHT = SCREEN_HEIGHT / 5
CONTROL_PANE_WIDTH = SCREEN_WIDTH
PANEL_X = 0
PANEL_Y = SCREEN_HEIGHT - CONTROL_PANE_HEIGHT

# ----- Field size and offset -----
FIELD_WIDTH = min(SCREEN_HEIGHT, SCREEN_WIDTH) - CONTROL_PANE_HEIGHT
FIELD_OFFSET_X = (SCREEN_WIDTH - FIELD_WIDTH) / 2

# ----- Epsilon value for floating-point comparison -----
EPS = 10e-3

class CellularAutomata:
    """
    Cellular automata class.
    Provides functions for configuring and running 2D cellular automata.
    """

    class Params:
        """ Container for main game parameters"""

        def __init__(self, field_size=None, birth_param=None, survive_param=None):
            """ Init params """

            if field_size is None:
                self.field_size = 30
            else:
                self.field_size = field_size

            if birth_param is None:
                self.birth_param = [3]
            else:
                self.birth_param = birth_param

            if survive_param is None:
                self.survive_param = [2, 3]
            else:
                self.survive_param = survive_param

        def set(self, field_size, birth_param, survive_param):
            """ Set params """

            self.field_size = field_size
            self.birth_param = birth_param
            self.survive_param = survive_param

        def default(self):
            """ Set default params """

            self.field_size = 30
            self.birth_param = [3]
            self.survive_param = [2, 3]

    def __init__(self):
        """ Init with default params """

        # Set default game params
        self.params = CellularAutomata.Params()

        # Game State:
        self.field = [
            [False for _ in range(self.params.field_size)] for _ in range(self.params.field_size)
        ]
        self.moving = False

        self.buttons = []
        self.prev_update = 0

        self.update_rate = .5  # in seconds

        self.cell_width = FIELD_WIDTH / self.params.field_size

    def main(self):
        """ Provides main pygame running loop """

        pygame.init()
        screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])

        self.running = True
        while self.running:
            events = pygame.event.get()
            self.get_input(events)
            self.update()
            self.draw(screen)
            pygame.display.flip()

        pygame.quit()

    def get_input(self, events):
        """ Listens for user input and executes callback function when user clicks on button """
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                x -= FIELD_OFFSET_X
                if x <= FIELD_WIDTH and y <= FIELD_WIDTH:
                    cell_width = FIELD_WIDTH / self.params.field_size
                    row = int(x // cell_width)
                    column = int(y // cell_width)
                    self.field[column][row] = not self.field[column][row]

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    real_rects = pygame.Rect(
                        PANEL_X + button.rect.left,
                        PANEL_Y + button.rect.top,
                        button.rect.width,
                        button.rect.height
                    )
                    if real_rects.collidepoint(mouse_pos):
                        button.callback()

    def update(self):
        """ Provides update of pygame screen state with given rate """
        if not self.prev_update:
            self.prev_update = time.time()
            return
        cur_time = time.time()
        if cur_time - self.prev_update >= self.update_rate:
            if not self.moving:
                return
            self.step()
            self.prev_update = cur_time

    def step(self):
        """
        Does single evolution step according to
        current CA state and provided rules
        """
        new_field = [[False for _ in range(self.params.field_size)]
                     for _ in range(self.params.field_size)]

        for row in self.field:
            for el in row:
                if type(el) is not bool:
                    raise TypeError("Field values should be booleans")

        for y, row in enumerate(self.field):
            for x, cell in enumerate(row):
                neighbours = self.get_neighbours(x, y)

                # Any live cell which meets survive criteria lives on.
                if cell and neighbours in self.params.survive_param:
                    new_field[y][x] = True
                    continue

                # Any dead cell which meets birth criteria becomes a live cell
                if not cell and neighbours in self.params.birth_param:
                    new_field[y][x] = True
                    continue

        self.field = new_field

    def set_params(self, grid_size: int, birth_param: List[int], survive_param: List[int]):
        """ Sets provided game parameters, such as grid size and birth/survive rules """
        if grid_size < 1:
            raise ValueError(
                "Grid size should be positive integer value"
            )
        for el in birth_param:
            if el < 0 or el > 8:
                raise ValueError(
                    "Birth param should include only "
                    "non-negative integer values between 0 and 8"
                )
        for el in birth_param:
            if el < 0 or el > 8:
                raise ValueError(
                    "Survive param should include only "
                    "non-negative integer values between 0 and 8"
                )
        self.params.set(grid_size, birth_param, survive_param)

    
    def get_neighbours(self, x, y):
        neighbour_cells = [
            self.field[y - 1][x - 1],
            self.field[y - 1][x],
            self.field[y - 1][(x + 1) % self.params.field_size],

            self.field[y][x - 1],
            self.field[y][(x + 1) % self.params.field_size],

            self.field[(y + 1) % self.params.field_size][x - 1],
            self.field[(y + 1) % self.params.field_size][x],
            self.field[(y + 1) % self.params.field_size][(x + 1) % self.params.field_size]
        ]
        return sum(neighbour_cells)

    def draw(self, screen):
        """ Draws current CA state on pygame screen """

        screen.fill((255, 255, 255))

        for y, row in enumerate(self.field):
            for x, cell in enumerate(row):
                rect = pygame.Rect(FIELD_OFFSET_X + x * self.cell_width, y *
                                   self.cell_width, self.cell_width, self.cell_width)
                color = (0, 0, 0) if cell else (255, 255, 255)
                border_color = (160, 160, 160)
                border_width = 1
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, border_color, rect, border_width)

        # draw controls:
        panel = pygame.Surface((CONTROL_PANE_WIDTH, CONTROL_PANE_HEIGHT))
        panel.fill((255, 255, 255))
        button_height = CONTROL_PANE_HEIGHT / 4
        button_width = button_height * 3

        spacing = CONTROL_PANE_WIDTH / 5

        self.buttons = [
            Button(
                position=(
                    CONTROL_PANE_WIDTH / 2 - button_width / 2 - 3 * spacing / 2,
                    CONTROL_PANE_HEIGHT / 4
                ),
                size=(button_width, button_height),
                text="start" if not self.moving else "stop",
                f=self.on_switch_mode
            ),
            Button(
                position=(
                    CONTROL_PANE_WIDTH / 2 - button_width / 2 - spacing / 2,
                    CONTROL_PANE_HEIGHT / 4
                ),
                size=(button_width, button_height),
                text="step",
                f=self.on_step
            ),
            Button(
                position=(
                    CONTROL_PANE_WIDTH / 2 - button_width / 2 + spacing / 2,
                    CONTROL_PANE_HEIGHT / 4
                ),
                size=(button_width, button_height),
                text="slower",
                f=self.on_slower
            ),
            Button(
                position=(
                    CONTROL_PANE_WIDTH / 2 - button_width / 2 + 3 * spacing / 2,
                    CONTROL_PANE_HEIGHT / 4
                ),
                size=(button_width, button_height),
                text="faster",
                f=self.on_faster
            ),
            Button(
                position=(
                    CONTROL_PANE_WIDTH / 2 - button_width / 2 - spacing,
                    3 * CONTROL_PANE_HEIGHT / 4 - 20
                ),
                size=(button_width, button_height),
                text="load",
                f=self.on_load
            ),
            Button(
                position=(
                    CONTROL_PANE_WIDTH / 2 - button_width / 2,
                    3 * CONTROL_PANE_HEIGHT / 4 - 20
                ),
                size=(button_width, button_height),
                text="save",
                f=self.on_save
            ),
            Button(
                position=(
                    CONTROL_PANE_WIDTH / 2 - button_width / 2 + spacing,
                    3 * CONTROL_PANE_HEIGHT / 4 - 20
                ),
                size=(button_width, button_height),
                text="reset",
                f=self.on_reset
            ),

        ]

        for button in self.buttons:
            button.draw(panel)

        screen.blit(panel, (PANEL_X, PANEL_Y))

    def on_switch_mode(self):
        """ Start button callback function """
        self.moving = not self.moving

    def on_step(self):
        """ Step button callback function """
        self.step()

    def on_load(self, path_to_file=None):
        """ Load button callback function """
        if path_to_file is None:
            with filedialog.askopenfile(
                    defaultextension=".txt",
                    filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")]) as f:
                self.field = json.loads(f.read())
        else:
            with open(path_to_file) as f:
                self.field = json.loads(f.read())

    def on_save(self, path_to_file=None):
        """ Save button callback function """
        if path_to_file is None:
            with filedialog.asksaveasfile(
                    initialfile='state.txt',
                    defaultextension=".txt",
                    filetypes=[("All Files", "*.*"), ("Text Documents", "*.txt")]) as f:
                f.write(json.dumps(self.field))
        else:
            with open(path_to_file, "w") as f:
                f.write(json.dumps(self.field))

    def on_slower(self):
        """ Slower button callback function """
        if abs(self.update_rate - 1) > EPS:
            self.update_rate += 0.05

    def on_faster(self):
        """ Faster button callback function """
        if abs(self.update_rate - 0.05) > EPS:
            self.update_rate -= 0.05

    def on_reset(self):
        """ Reset button callback function """
        self.field = [
            [False for _ in range(self.params.field_size)] for _ in range(self.params.field_size)
        ]
        self.moving = False
        self.update_rate = 0.5


if __name__ == '__main__':
    cellular_automata = CellularAutomata()
    cellular_automata.main()
