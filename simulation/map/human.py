import pygame
from simulation.config import constants


class Human:
    def __init__(self, x, y, size=5, color=constants.RED):
        self.x = x
        self.y = y
        self.size = size
        self.color = color

    def draw(self, surface):
        # Draw the border dark red
        pygame.draw.circle(surface, (110, 0, 0), (self.x, self.y), self.size + 2)  # Border is slightly larger
        # Draw the inner circle red
        pygame.draw.circle(surface, (255, 0, 0), (self.x, self.y), self.size)
