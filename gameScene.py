import pygame
from td.map import Map
from td.enemy import Enemy
from td.tower import Tower

class GameScene:
    def __init__(self):
        self.map = Map()
        self.enemies = [Enemy()]
        self.towers = []
        self.spawn_timer = 2.0
        self.image = pygame.image.load("assets/ui.png").convert_alpha()
        self.font = pygame.font.SysFont(None, 24)
        self.projectiles = []

        # -------- CURRENCY --------
        self.gold = 100  # starting gold, adjust to taste

        # -------- TOWER BUTTON --------
        self.tower_button_img = pygame.image.load("assets/tower1_button.png").convert_alpha()
        self.tower_button_rect = pygame.Rect(49, 417, 36, 36)
        self.tower_cost = 25  # gold cost per tower, adjust to taste
        self.placing_tower = False  # True when player has clicked the button

        # -------- BGM --------
        pygame.mixer.music.load("assets/bgm1.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        # -------- DEBUG FONT --------
        self.debug_font = pygame.font.SysFont(None, 28)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:

            # -------- TOWER BUTTON CLICKED --------
            if self.tower_button_rect.collidepoint(event.pos):
                if self.gold >= self.tower_cost:
                    self.placing_tower = True   # arm placement mode
                return

            # -------- PLACE TOWER --------
            if self.placing_tower:
                pos = event.pos
                if not self.map.is_buildable(pos):
                    return
                for tower in self.towers:
                    if tower.pos.distance_to(pos) < 32:
                        return
                self.towers.append(Tower(pos))
                self.gold -= self.tower_cost
                self.placing_tower = False      # disarm after one placement

    def update(self, dt):
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.enemies.append(Enemy())
            self.spawn_timer = 3

        for enemy in self.enemies:
            enemy.update(dt)

        for tower in self.towers:
            tower.update(dt, self.enemies, self.projectiles)
        for projectile in self.projectiles:
            projectile.update(dt)

        self.projectiles = [p for p in self.projectiles if p.alive]

        # -------- CHECK FOR KILLS & AWARD GOLD --------
        for enemy in self.enemies:
            if not enemy.alive:
                self.gold += 10  # gold per kill, adjust to taste

        self.enemies = [e for e in self.enemies if e.alive]

        return None

    def draw(self, screen):
        self.map.draw(screen)

        # -------- UI BAR --------
        screen.blit(self.image, (0, 400))

        # -------- TOWER BUTTON --------
        screen.blit(self.tower_button_img, self.tower_button_rect)

        # -------- HIGHLIGHT BUTTON WHEN ACTIVE --------
        if self.placing_tower:
            pygame.draw.rect(screen, (255, 255, 0), self.tower_button_rect, 2)  # yellow outline

        # -------- GREY OUT BUTTON IF NOT ENOUGH GOLD --------
        if self.gold < self.tower_cost:
            grey = pygame.Surface((36, 36), pygame.SRCALPHA)
            grey.fill((0, 0, 0, 120))
            screen.blit(grey, self.tower_button_rect)

        for tower in self.towers:
            tower.draw(screen)
        for projectile in self.projectiles:
            projectile.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)

        # -------- DEBUG GOLD DISPLAY --------
        gold_text = self.debug_font.render(f"Gold: {self.gold}", True, (255, 215, 0))
        screen.blit(gold_text, (10, 10))