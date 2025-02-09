import numpy as np
import pygame
import pygame.gfxdraw

class Obstacle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

class RectangleObstacle(Obstacle):
    def __init__(self, x, y, width, height, color, border_color=(0, 0, 0)):
        super().__init__(x, y, color)
        self.width = width
        self.height = height
        self.center = np.array([x + width / 2, y + height / 2])
        self.border_color = border_color  # Kolor obramowania

    def contains(self, pos):
        return self.x <= pos[0] <= self.x + self.width and self.y <= pos[1] <= self.y + self.height

    def closest_point(self, pos):
        closest_x = np.clip(pos[0], self.x, self.x + self.width)
        closest_y = np.clip(pos[1], self.y, self.y + self.height)
        return np.array([closest_x, closest_y])

    def draw(self, win):
        # Rysowanie obramowania
        pygame.draw.rect(win, self.border_color, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), border_radius=5)
        # Rysowanie głównego prostokąta
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.height), border_radius=5)


class CircleObstacle:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.border_color = (max(self.color[0] - 40, 0),
                             max(self.color[1] - 40, 0),
                             max(self.color[2] - 40, 0))
        self.center = np.array([x, y])

    def contains(self, pos):
        return np.linalg.norm(pos - self.center) <= self.radius

    def closest_point(self, pos):
        direction = pos - self.center
        if np.linalg.norm(direction) == 0:
            return self.center
        return self.center + direction / np.linalg.norm(direction) * self.radius

    def draw(self, surface):
        # Rysowanie obwódki (nieco większy okrąg w kolorze obramowania)
        pygame.gfxdraw.filled_circle(surface, self.x, self.y, self.radius + 2, self.border_color)

        # Rysowanie wypełnienia
        pygame.gfxdraw.filled_circle(surface, self.x, self.y, self.radius, self.color)

        # Dodatkowe wygładzanie krawędzi
        pygame.gfxdraw.aacircle(surface, self.x, self.y, self.radius, self.border_color)

class PolygonObstacle(Obstacle):
    def __init__(self, points, color, border_color=(0, 0, 0)):
        super().__init__(0, 0, color)
        self.points = np.array(points)
        self.center = np.mean(self.points, axis=0)
        self.border_color = border_color  # Kolor obramowania

    def contains(self, pos):
        n = len(self.points)
        inside = False
        x, y = pos
        p1x, p1y = self.points[0]
        for i in range(n + 1):
            p2x, p2y = self.points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def closest_point(self, pos):
        closest_point = None
        min_dist = float('inf')
        for i in range(len(self.points)):
            p1 = self.points[i]
            p2 = self.points[(i + 1) % len(self.points)]
            closest = self._closest_point_on_segment(p1, p2, pos)
            dist = np.linalg.norm(closest - pos)
            if dist < min_dist:
                closest_point = closest
                min_dist = dist
        return closest_point

    def _closest_point_on_segment(self, p1, p2, pos):
        line_vec = p2 - p1
        p1_to_pos = pos - p1
        line_len = np.dot(line_vec, line_vec)
        if line_len == 0:
            return p1
        t = np.clip(np.dot(p1_to_pos, line_vec) / line_len, 0, 1)
        return p1 + t * line_vec

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.points)

    # def draw(self, surface):
    #     # Rysowanie obramowania
    #     pygame.gfxdraw.aapolygon(surface, self.points.astype(int), self.border_color)
    #     pygame.gfxdraw.filled_polygon(surface, self.points.astype(int), self.color)
