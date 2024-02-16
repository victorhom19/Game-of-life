import pygame

class Button:
    def __init__(self, x, y, width, height, text, f = None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.f = f

    def draw(self, surface):
        text_color = (0, 0, 0)
        button_color = (160, 160, 160)
        pygame.draw.rect(surface, button_color, self.rect)
        font = pygame.font.Font(None, 24)
        text = font.render(self.text, True, text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
    
    def callback(self):
        if self.f is None:
            return
        self.f()
