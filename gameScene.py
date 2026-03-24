import pygame
import math
from td.map import Map
from td.enemy import Enemy
from td.tower import Tower
from td.mainTower import MainTower

class GameScene:
    def __init__(self):
        self.map = Map()
        self.enemies = []
        self.towers = []
        self.image = pygame.image.load("assets/ui.png").convert_alpha()
        self.font = pygame.font.SysFont(None, 24)
        self.projectiles = []
        self.main_tower = MainTower()
        self.bg_color = (20, 40, 40)
        # -------- CURRENCY --------
        self.gold = 50

        # -------- TOWER BUTTON --------
        self.tower_button_img = pygame.image.load("assets/tower1_button.png").convert_alpha()
        self.tower_button_rect = pygame.Rect(49, 417, 36, 36)
        self.tower_cost = 50
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
        self.tower_range = 120

        # -------- ERROR SOUND --------
        self.error_sound = pygame.mixer.Sound("assets/error.wav")
        self.error_sound.set_volume(0.6)

        # -------- BGM --------
        pygame.mixer.music.load("assets/bgm1.mp3")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

        # -------- FONTS --------
        self.debug_font = pygame.font.SysFont(None, 28)
        self.wave_font = pygame.font.SysFont(None, 64)
        self.result_font = pygame.font.SysFont(None, 96)

        # -------- WAVE SYSTEM --------
        self.total_waves = 30
        self.current_wave = 0           # 0 = not started yet
        self.wave_state = "countdown"   # "countdown", "spawning", "waiting", "result"
        self.countdown_timer = 5.0
        self.result = None              # "victory" or "defeat"

        # spawn queue
        self.spawn_queue = 0            # enemies left to spawn this wave
        self.spawn_interval = 0.5       # seconds between each spawn
        self.spawn_timer = 0

        # base stats (scaled per wave)
        self.base_mob_count = 20
        self.base_mob_hp = 20
        self.base_mob_speed = 80

    # --------------------------------------------------------
    #  WAVE HELPERS
    # --------------------------------------------------------

    def _wave_mob_count(self, wave):
        """20 mobs on wave 1, +50% each wave."""
        return math.ceil(self.base_mob_count * (1.5 ** (wave - 1)))

    def _wave_mob_hp(self, wave):
        """Base HP scaled by 50% per wave."""
        return math.ceil(self.base_mob_hp * (2 ** (wave - 1)))

    def _wave_mob_speed(self, wave):
        """Base speed scaled by 50% per wave."""
        return min(self.base_mob_speed * (1.5 ** (wave - 1)), 150)

    def _start_countdown(self):
        self.wave_state = "countdown"
        self.countdown_timer = 5.0

    def _start_wave(self):
        self.current_wave += 1
        self.wave_state = "spawning"
        self.spawn_queue = self._wave_mob_count(self.current_wave)
        self.spawn_timer = 0

    def _make_enemy(self):
        e = Enemy()
        e.max_health = self._wave_mob_hp(self.current_wave)
        e.health = e.max_health
        e.speed = self._wave_mob_speed(self.current_wave)
        return e

    # --------------------------------------------------------
    #  EVENTS
    # --------------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                self.placing_tower = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                self.placing_tower = False
                return

            if event.button == 1:
                if self.tower_button_rect.collidepoint(event.pos):
                    if self.gold >= self.tower_cost:
                        self.placing_tower = True
                        self._deselect_all_towers()
                    return

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

                for tower in self.towers:
                    if tower.pos.distance_to(event.pos) <= self.tower_radius + 14:
                        tower.selected = not tower.selected
                    else:
                        tower.selected = False

    def _deselect_all_towers(self):
        for tower in self.towers:
            tower.selected = False

    # --------------------------------------------------------
    #  UPDATE
    # --------------------------------------------------------

    def update(self, dt):

        # -------- RESULT SCREEN — do nothing --------
        if self.wave_state == "result":
            return None

        # -------- CHECK DEFEAT --------
        if not self.main_tower.alive:
            self.wave_state = "result"
            self.result = "defeat"
            return None

        # -------- COUNTDOWN --------
        if self.wave_state == "countdown":
            self.countdown_timer -= dt
            if self.countdown_timer <= 0:
                self._start_wave()
            return None

        # -------- SPAWNING --------
        if self.wave_state == "spawning":
            self.spawn_timer -= dt
            if self.spawn_timer <= 0 and self.spawn_queue > 0:
                self.enemies.append(self._make_enemy())
                self.spawn_queue -= 1
                self.spawn_timer = self.spawn_interval
            if self.spawn_queue == 0:
                self.wave_state = "waiting"  # all spawned, wait for clear

        # -------- WAITING (all spawned, waiting for last enemy to die) --------
        if self.wave_state == "waiting":
            if len(self.enemies) == 0:
                # wave cleared
                if self.current_wave >= self.total_waves:
                    self.wave_state = "result"
                    self.result = "victory"
                    return None
                else:
                    self._start_countdown()   # next wave countdown

        # -------- NORMAL GAME UPDATE --------
        for enemy in self.enemies:
            enemy.update(dt)

        for tower in self.towers:
            tower.update(dt, self.enemies, self.projectiles)
        for projectile in self.projectiles:
            projectile.update(dt)

        self.projectiles = [p for p in self.projectiles if p.alive]

        for enemy in self.enemies:
            if not enemy.alive:
                if enemy.reached_end:
                    self.main_tower.take_damage(enemy.damage)
                else:
                    self.gold += 5

        self.enemies = [e for e in self.enemies if e.alive]

        return None

    # --------------------------------------------------------
    #  DRAW
    # --------------------------------------------------------

    def draw(self, screen):
        screen.fill(self.bg_color)
        self.map.draw(screen)

        screen.blit(self.image, (0, 400))

        # -------- TOWER BUTTON --------
        screen.blit(self.tower_button_img, self.tower_button_rect)
        if self.placing_tower:
            pygame.draw.rect(screen, (255, 255, 0), self.tower_button_rect, 2)
        if self.gold < self.tower_cost:
            grey = pygame.Surface((36, 36), pygame.SRCALPHA)
            grey.fill((0, 0, 0, 120))
            screen.blit(grey, self.tower_button_rect)

        self.main_tower.draw(screen)

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
            circle_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            color = (0, 100, 255, 80) if buildable else (255, 0, 0, 80)
            pygame.draw.circle(circle_surf, color, (radius, radius), radius)
            screen.blit(circle_surf, circle_surf.get_rect(center=mouse_pos))

            range_surf = pygame.Surface((self.tower_range * 2, self.tower_range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, (60, 60, 200, 60),
                               (self.tower_range, self.tower_range), self.tower_range, 1)
            screen.blit(range_surf, range_surf.get_rect(center=mouse_pos))

            rect = self.tower_preview_img.get_rect(center=mouse_pos)
            screen.blit(self.tower_preview_img, rect)

        # -------- DEBUG GOLD DISPLAY --------
        gold_text = self.debug_font.render(f"Gold: {self.gold}", True, (255, 215, 0))
        screen.blit(gold_text, (10, 10))

        # -------- WAVE INFO --------
        wave_label = f"Wave: {self.current_wave} / {self.total_waves}"
        wave_text = self.debug_font.render(wave_label, True, (255, 255, 255))
        screen.blit(wave_text, (10, 30))

        # -------- COUNTDOWN OVERLAY --------
        if self.wave_state == "countdown":
            next_wave = self.current_wave + 1
            seconds_left = math.ceil(self.countdown_timer)

            title = self.wave_font.render(f"Wave {next_wave}", True, (255, 220, 50))
            subtitle = self.wave_font.render(f"Starting in {seconds_left}...", True, (255, 255, 255))

            screen.blit(title, title.get_rect(center=(320, 180)))
            screen.blit(subtitle, subtitle.get_rect(center=(320, 250)))

        # -------- VICTORY / DEFEAT OVERLAY --------
        if self.wave_state == "result":
            overlay = pygame.Surface((640, 480), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            if self.result == "victory":
                text = self.result_font.render("VICTORY!", True, (100, 255, 100))
            else:
                text = self.result_font.render("DEFEAT", True, (255, 80, 80))

            screen.blit(text, text.get_rect(center=(320, 220)))