import pygame
import os

class StartScene:
    def __init__(self):

        # Base path for assets
        base_path = os.path.join("assets", "startScene")

        self.kirby_img = pygame.image.load(
            os.path.join(base_path, "kirbyimage.png")
        ).convert_alpha()

        self.title_img = pygame.image.load(
            os.path.join(base_path, "kirbytitle.png")
        ).convert_alpha()

        self.start_img = pygame.image.load(
            os.path.join(base_path, "button.png")
        ).convert_alpha()

        self.button = self.start_img.get_rect(topleft=(12, 328))

        self.start_screen_img = pygame.image.load(
            os.path.join(base_path, "start_screen.png")
        ).convert_alpha()

        self.towerdefense_img = pygame.image.load(
            os.path.join(base_path, "towerdefense.png")
        ).convert_alpha()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button.collidepoint(event.pos):
                return "map_select"

    def update(self, dt):
        return None

    def draw(self, screen):


        # Starscreem (background)
        screen.blit(self.start_screen_img, (0, 0))

        # Title image (top center)
        screen.blit(self.title_img, (0, 0))

        # Kirby image
        screen.blit(self.kirby_img, (0, 0))

        # Towerdefense (text)
        screen.blit(self.towerdefense_img, (0, 0))

        # start (button)
        screen.blit(self.start_img, (12, 328))







