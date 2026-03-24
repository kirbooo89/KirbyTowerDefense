import pygame

class MainTower:
    def __init__(self):
        self.pos = pygame.Vector2(342, 213)
        self.max_hp = 200
        self.hp = self.max_hp

        # -------- LOAD IMAGE --------
        self.image = pygame.image.load("assets/stone_kirby.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(342, 213))
        self.pos = pygame.Vector2(self.rect.centerx, self.rect.centery)  # pos stays at center for HP bar)

        # -------- HP BAR --------
        self.bar_width = 60
        self.bar_height = 8
        self.bar_offset_y = self.rect.height // 2 + 10

        # -------- FONT --------
        self.font = pygame.font.SysFont(None, 22)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    @property
    def alive(self):
        return self.hp > 0

    def draw(self, screen):
        # -------- SPRITE --------
        screen.blit(self.image, self.rect)

        # -------- HP BAR BACKGROUND --------
        bar_x = self.pos.x - self.bar_width // 2
        bar_y = self.pos.y + self.bar_offset_y

        pygame.draw.rect(screen, (180, 0, 0),
                         (bar_x, bar_y, self.bar_width, self.bar_height))

        # -------- HP BAR FILL --------
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, (0, 200, 0),
                         (bar_x, bar_y, int(self.bar_width * ratio), self.bar_height))

        # -------- HP TEXT --------
        text = self.font.render(f"{self.hp}/{self.max_hp}", True, (255, 255, 255))
        screen.blit(text, text.get_rect(center=(self.pos.x, bar_y + self.bar_height + 8)))