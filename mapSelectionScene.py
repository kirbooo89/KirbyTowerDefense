import pygame

class MapSelectScene:
    def __init__(self):
        self.bg_color = (30, 80, 40)
        self.button = pygame.Rect(300, 260, 200, 80)
        self.font = pygame.font.SysFont(None, 36)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button.collidepoint(event.pos):
                return "kirby_select"

    def update(self, dt):
        return None

    def draw(self, screen):
        screen.fill(self.bg_color)
        pygame.draw.rect(screen, (200, 200, 200), self.button)
        text = self.font.render("PLAY MAP", True, (0, 0, 0))
        screen.blit(text, text.get_rect(center=self.button.center))
