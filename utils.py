"""
Utilities module of cellular automata simulation program.
Provides classes for better building of UI components.
"""
from typing import Tuple

import pygame

class Button:
    """
    Button class provides rectangle-shaped button component
    for pygame UI as well as assignment onclick callback function.
    """

    def __init__(self, position: Tuple[float, float], size: Tuple[float, float], text, f=None):
        """ Button initialization """
        x, y = position
        width, height = size
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.f = f

    def draw(self, surface):
        """ Draws button on UI surface """

        text_color = (0, 0, 0)
        button_color = (160, 160, 160)
        pygame.draw.rect(surface, button_color, self.rect)
        font = pygame.font.Font(None, 24)
        text = font.render(self.text, True, text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

    def callback(self):
        """ Executes callback function provided on init phase """
        if self.f is None:
            return
        self.f()
