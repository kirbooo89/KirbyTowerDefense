import pygame
from td.path import PATH

class Map:
    def __init__(self):
        self.image = pygame.image.load("assets/map.png").convert_alpha()
        self.path_width = 30
        self.tower_radius = 20  # 👈 added
        self.ui_height = 400

    def draw(self, screen):
        screen.blit(self.image, (0, 0))

    def is_buildable(self, pos):
        x, y = pos

        # -------- BLOCK UI AREA --------
        if y >= self.ui_height:
            return False

        # -------- BLOCK PATH (including tower radius) --------
        clearance = self.path_width // 2 + self.tower_radius  # 15 + 10 = 25
        for i in range(len(PATH) - 1):
            if self._point_near_segment(x, y, PATH[i], PATH[i + 1], clearance):
                return False

        return True

    def _point_near_segment(self, px, py, a, b, radius):
        ax, ay = a
        bx, by = b

        dx = bx - ax
        dy = by - ay
        seg_len_sq = dx * dx + dy * dy

        if seg_len_sq == 0:
            dist_sq = (px - ax) ** 2 + (py - ay) ** 2
            return dist_sq <= radius * radius

        t = ((px - ax) * dx + (py - ay) * dy) / seg_len_sq
        t = max(0.0, min(1.0, t))

        closest_x = ax + t * dx
        closest_y = ay + t * dy

        dist_sq = (px - closest_x) ** 2 + (py - closest_y) ** 2
        return dist_sq <= radius * radius