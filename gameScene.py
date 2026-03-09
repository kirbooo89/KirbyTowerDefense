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
        self.bg_color = (20, 40, 40)

        # -------- CURRENCY --------
        self.gold = 100

        # -------- TOWER BUTTON --------
        self.tower_button_img = pygame.image.load("assets/tower1_button.png").convert_alpha()
        self.tower_button_rect = pygame.Rect(49, 417, 36, 36)
        self.tower_cost = 25
        self.placing_tower = False

        # -------- PLACEMENT PREVIEW --------
        self.tower_preview_img = pygame.image.load("assets/tower_idle.png").convert_alpha()
        frame_width = self.tower_preview_img.get_width() // 5
        frame_height = self.tower_preview_img.get_height()
        frame = self.tower_preview_img.subsurface(pygame.Rect(0, 0, frame_width, frame_height))
        frame = pygame.transform.scale(frame, (int(frame_width * 1.5), int(frame_height * 1.5)))
        self.tower_preview_img = frame.copy()
        self.tower_preview_img.set_alpha(120)

        self.tower_radius = 10
        self.tower_range = 120  # must match Tower.range

        # -------- ERROR SOUND --------
        self.error_sound = pygame.mixer.Sound("assets/error.mp3")
        self.error_sound.set_volume(0.6)

        # -------- BGM --------
        pygame.mixer.music.load("assets/bgm1.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        # -------- DEBUG FONT --------
        self.debug_font = pygame.font.SysFont(None, 28)

    def handle_event(self, event):

        # -------- KEYBOARD --------
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                self.placing_tower = False  # cancel placement with X key

        if event.type == pygame.MOUSEBUTTONDOWN:

            # -------- RIGHT CLICK: cancel placement --------
            if event.button == 3:
                self.placing_tower = False
                return

            # -------- LEFT CLICK --------
            if event.button == 1:

                # -------- TOWER BUTTON CLICKED --------
                if self.tower_button_rect.collidepoint(event.pos):
                    if self.gold >= self.tower_cost:
                        self.placing_tower = True
                        self._deselect_all_towers()
                    return

                # -------- PLACE TOWER --------
                if self.placing_tower:
                    pos = event.pos
                    too_close = any(t.pos.distance_to(pos) < 32 for t in self.towers)

                    if not self.map.is_buildable(pos) or too_close:
                        self.error_sound.play()
                        return

                    self.towers.append(Tower(pos))
                    self.gold -= self.tower_cost
                    self.placing_tower = False
                    return

                # -------- SELECT / DESELECT TOWER --------
                for tower in self.towers:
                    if tower.pos.distance_to(event.pos) <= self.tower_radius + 14:
                        tower.selected = not tower.selected
                    else:
                        tower.selected = False

    def _deselect_all_towers(self):
        for tower in self.towers:
            tower.selected = False

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

        for enemy in self.enemies:
            if not enemy.alive:
                self.gold += 10

        self.enemies = [e for e in self.enemies if e.alive]

        return None

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.map.draw(screen)

        # -------- UI BAR --------
        screen.blit(self.image, (0, 400))

        # -------- TOWER BUTTON --------
        screen.blit(self.tower_button_img, self.tower_button_rect)

        if self.placing_tower:
            pygame.draw.rect(screen, (255, 255, 0), self.tower_button_rect, 2)

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

        # -------- PLACEMENT PREVIEW --------
        if self.placing_tower:
            mouse_pos = pygame.mouse.get_pos()
            too_close = any(t.pos.distance_to(mouse_pos) < 32 for t in self.towers)
            buildable = self.map.is_buildable(mouse_pos) and not too_close

            radius = self.tower_radius + 14

            # -------- PLACEMENT CIRCLE (blue = valid, red = invalid) --------
            circle_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            color = (0, 100, 255, 80) if buildable else (255, 0, 0, 80)
            pygame.draw.circle(circle_surf, color, (radius, radius), radius)
            screen.blit(circle_surf, circle_surf.get_rect(center=mouse_pos))

            # -------- RANGE PREVIEW RING --------
            range_surf = pygame.Surface((self.tower_range * 2, self.tower_range * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                range_surf,
                (60, 60, 200, 255),  # low alpha blue ring
                (self.tower_range, self.tower_range),
                self.tower_range,
                1
            )
            screen.blit(range_surf, range_surf.get_rect(center=mouse_pos))

            # -------- GHOST SPRITE --------
            rect = self.tower_preview_img.get_rect(center=mouse_pos)
            screen.blit(self.tower_preview_img, rect)

        # -------- DEBUG GOLD DISPLAY --------
        gold_text = self.debug_font.render(f"Poyo: {self.gold}", True, (255, 215, 0))
        screen.blit(gold_text, (10, 10))