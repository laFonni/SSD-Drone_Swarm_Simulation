from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List

import numpy as np
import pygame

from simulation.config.game_settings import MapEdgeBehaviour, GameSettings


class EntityAction(Enum):
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()


class Entity(ABC):
    def __init__(self, game_settings: GameSettings, controls: Dict[int, EntityAction] = None, pos=np.array([0, 0]),
                 colour=(255, 0, 0), **kwargs):
        if controls is None:
            controls = {}

        self._pos = pos
        self.color = colour
        self.controls = controls
        self.game_settings: GameSettings = game_settings

        self.kwargs = kwargs

    @abstractmethod
    def draw(self, win):
        pass

    @abstractmethod
    def update_physics(self, actions: List[EntityAction], time_elapsed):
        pass

    def check_physics(self):
        if self.pos[0] > self.game_settings.map_width:
            if self.game_settings.x_edge_behaviour == MapEdgeBehaviour.WRAP:
                self.pos[0] = self.pos[0] % self.game_settings.map_width
            if self.game_settings.x_edge_behaviour == MapEdgeBehaviour.CLAMP:
                self.pos[0] = self.game_settings.map_width

        if self.pos[0] < 0:
            if self.game_settings.x_edge_behaviour == MapEdgeBehaviour.WRAP:
                self.pos[0] = self.pos[0] % self.game_settings.map_width
            if self.game_settings.x_edge_behaviour == MapEdgeBehaviour.CLAMP:
                self.pos[0] = 0

        if self.pos[1] > self.game_settings.map_width:
            if self.game_settings.y_edge_behaviour == MapEdgeBehaviour.WRAP:
                self.pos[1] = self.pos[1] % self.game_settings.map_height
            if self.game_settings.y_edge_behaviour == MapEdgeBehaviour.CLAMP:
                self.pos[1] = self.game_settings.map_height

        if self.pos[1] < 0:
            if self.game_settings.y_edge_behaviour == MapEdgeBehaviour.WRAP:
                self.pos[1] = self.pos[1] % self.game_settings.map_width
            if self.game_settings.y_edge_behaviour == MapEdgeBehaviour.CLAMP:
                self.pos[1] = 0

    def parse_controls(self, keys):
        return [action for key, action in self.controls.items() if keys[key]]

    def get_debug_text(self):
        return f"pos:{self.pos[0]:0.1f}, {self.pos[1]:0.1f}"

    def draw_debug_info(self, win):
        font = pygame.font.SysFont("Courier New", 16)
        text_surface = font.render(self.get_debug_text(), True, self.game_settings.debug_text_colour)
        win.blit(text_surface, (self.pos[0], self.pos[1]))

    def update(self, keys, win, time_elapsed):
        self.update_physics(self.parse_controls(keys), time_elapsed)
        self.check_physics()
        self.draw(win)

        if self.game_settings.debug:
            self.draw_debug_info(win)


class CharacterEntity(Entity):
    def __init__(self, *args, width=5, v=200, **kwargs):
        super().__init__(*args, **kwargs)
        self.width = width
        self.v = v

    def draw(self, win):
        pygame.draw.circle(win, self.color, (int(self.pos[0]), int(self.pos[1])), self.width)

    def update_physics(self, actions: List[EntityAction], time_elapsed):
        for action in actions:
            if action == EntityAction.MOVE_UP:
                self.pos[1] -= self.v * time_elapsed
                continue
            if action == EntityAction.MOVE_DOWN:
                self.pos[1] += self.v * time_elapsed
                continue
            if action == EntityAction.MOVE_LEFT:
                self.pos[0] -= self.v * time_elapsed
                continue
            if action == EntityAction.MOVE_RIGHT:
                self.pos[0] += self.v * time_elapsed
                continue