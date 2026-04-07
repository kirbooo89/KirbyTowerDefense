import pygame
import math
from td.map import Map
from td.enemy import Enemy
from td.tower import Tower
from td.tower2 import Tower2
from td.mainTower import MainTower
from td.towerStatsWindow import TowerStatsWindow      # 👈

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

        # -------- TOWER 1 BUTTON --------
        self.tower_button_img = pygame.image.load("assets/tower1_button.png").convert_alpha()
        self.tower_button_rect = pygame.Rect(49, 417, 36, 36)
        self.tower1_cost = 75

        # -------- TOWER 2 BUTTON --------
        self.tower2_button_img = pygame.image.load("assets/tower2_button.png").convert_alpha()
        t2_frame = self.tower2_button_img.subsurface(pygame.Rect(0, 0, 36, 36))
        self.tower2_button_img = pygame.transform.scale(t2_frame, (36, 36))
        self.tower2_button_rect = pygame.Rect(133, 417, 36, 36)
        self.tower2_cost = 50

        # -------- PLACEMENT STATE --------
        self.placing_tower = None

        # -------- PLACEMENT PREVIEW — TOWER 1 --------
        t1_idle = pygame.image.load("assets/tower_idle.png").convert_alpha()
        frame_width = t1_idle.get_width() // 5
        frame_height = t1_idle.get_height()
        frame = t1_idle.subsurface(pygame.Rect(0, 0, frame_width, frame_height))
        self.tower1_preview_img = pygame.transform.scale(frame, (int(frame_width * 1.5), int(frame_height * 1.5))).copy()
        self.tower1_preview_img.set_alpha(120)

        # -------- PLACEMENT PREVIEW — TOWER 2 --------
        t2_idle = pygame.image.load("assets/spark_tower_idle.png").convert_alpha()
        t2_frame = t2_idle.subsurface(pygame.Rect(0, 0, 48, 48))
        self.tower2_preview_img = pygame.transform.scale(t2_frame, (96, 96)).copy()
        self.tower2_preview_img.set_alpha(120)

        self.tower_radius = 10
        self.tower1_range = 120
        self.tower2_aoe = 40

        # -------- TOWER STATS WINDOW --------
        self.stats_window = TowerStatsWindow()          # 👈

        # -------- SOUNDS --------
        self.error_sound = pygame.mixer.Sound("assets/error.wav")
        self.error_sound.set_volume(0.6)

        self.tower_select_sound = pygame.mixer.Sound("assets/tower_select.wav")
        self.tower_select_sound.set_volume(0.6)

        self.tower_cancel_sound = pygame.mixer.Sound("assets/tower_cancel.wav")
        self.tower_cancel_sound.set_volume(0.6)

        self.tower_placement_sound = pygame.mixer.Sound("assets/tower_placement.mp3")
        self.tower_placement_sound.set_volume(0.6)

        self.gameover_sound = pygame.mixer.Sound("assets/gameover.mp3")
        self.gameover_sound.set_volume(0.8)
        self.gameover_played = False

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
        self.current_wave = 0
        self.wave_state = "countdown"
        self.countdown_timer = 5.0
        self.result = None

        self.spawn_queue = 0
        self.spawn_interval = 0.5
        self.spawn_timer = 0

        self.base_mob_count = 20
        self.base_mob_hp = 20
        self.base_mob_speed = 80

    # --------------------------------------------------------
    #  WAVE HELPERS
    # --------------------------------------------------------

    def _wave_mob_count(self, wave):
        return math.ceil(self.base_mob_count * (1.5 ** (wave - 1)))

    def _wave_mob_hp(self, wave):
        return math.ceil(self.base_mob_hp * (2 ** (wave - 1)))

    def _wave_mob_speed(self, wave):
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

    def _cancel_placement(self):
        if self.placing_tower is not None:
            self.tower_cancel_sound.play()
        self.placing_tower = None

    def _selected_tower(self):
        """Returns the currently selected tower, or None."""
        for tower in self.towers:
            if tower.selected:
                return tower
        return None

    # --------------------------------------------------------
    #  EVENTS
    # --------------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                self._cancel_placement()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:
                self._cancel_placement()
                return

            if event.button == 1:

                # -------- STATS WINDOW UPGRADE BUTTON (checked first) --------
                selected = self._selected_tower()
                if selected is not None:
                    self.gold = self.stats_window.handle_event(event, selected, self.gold)  # 👈
                    if self.stats_window.btn_rect.collidepoint(event.pos):
                        return  # consumed by stats window, don't fall through

                # -------- TOWER 1 BUTTON --------
                if self.tower_button_rect.collidepoint(event.pos):
                    if self.gold >= self.tower1_cost:
                        self.placing_tower = "tower1"
                        self._deselect_all_towers()
                        self.tower_select_sound.play()
                    return

                # -------- TOWER 2 BUTTON --------
                if self.tower2_button_rect.collidepoint(event.pos):
                    if self.gold >= self.tower2_cost:
                        self.placing_tower = "tower2"
                        self._deselect_all_towers()
                        self.tower_select_sound.play()
                    return

                # -------- PLACE TOWER --------
                if self.placing_tower:
                    pos = event.pos
                    too_close = any(t.pos.distance_to(pos) < 32 for t in self.towers)
                    if not self.map.is_buildable(pos) or too_close:
                        self.error_sound.play()
                        return
                    if self.placing_tower == "tower1":
                        self.towers.append(Tower(pos))
                        self.gold -= self.tower1_cost
                    elif self.placing_tower == "tower2":
                        self.towers.append(Tower2(pos))
                        self.gold -= self.tower2_cost
                    self.tower_placement_sound.play()
                    self.placing_tower = None
                    return

                # -------- SELECT / DESELECT TOWER --------
                for tower in self.towers:
                    if tower.pos.distance_to(event.pos) <= self.tower_radius + 14:
                        tower.selected = not tower.selected
                    else:
                        tower.selected = False

        # -------- MOUSE BUTTON UP — reset pressed state --------
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            selected = self._selected_tower()
            if selected is not None:
                self.stats_window.handle_event(event, selected, self.gold)  # 👈 for btn release

    def _deselect_all_towers(self):
        for tower in self.towers:
            tower.selected = False

    # --------------------------------------------------------
    #  UPDATE
    # --------------------------------------------------------

    def update(self, dt):
        if self.wave_state == "result":
            return None

        if not self.main_tower.alive:
            self.wave_state = "result"
            self.result = "defeat"
            if not self.gameover_played:
                pygame.mixer.music.stop()
                self.gameover_sound.play()
                self.gameover_played = True
            return None

        if self.wave_state == "countdown":
            self.countdown_timer -= dt
            if self.countdown_timer <= 0:
                self._start_wave()
            return None

        if self.wave_state == "spawning":
            self.spawn_timer -= dt
            if self.spawn_timer <= 0 and self.spawn_queue > 0:
                self.enemies.append(self._make_enemy())
                self.spawn_queue -= 1
                self.spawn_timer = self.spawn_interval
            if self.spawn_queue == 0:
                self.wave_state = "waiting"

        if self.wave_state == "waiting":
            if len(self.enemies) == 0:
                if self.current_wave >= self.total_waves:
                    self.wave_state = "result"
                    self.result = "victory"
                    return None
                else:
                    self._start_countdown()

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

        # -------- TOWER 1 BUTTON --------
        screen.blit(self.tower_button_img, self.tower_button_rect)
        if self.placing_tower == "tower1":
            pygame.draw.rect(screen, (255, 255, 0), self.tower_button_rect, 2)
        if self.gold < self.tower1_cost:
            grey = pygame.Surface((36, 36), pygame.SRCALPHA)
            grey.fill((0, 0, 0, 120))
            screen.blit(grey, self.tower_button_rect)

        # -------- TOWER 2 BUTTON --------
        screen.blit(self.tower2_button_img, self.tower2_button_rect)
        if self.placing_tower == "tower2":
            pygame.draw.rect(screen, (255, 255, 0), self.tower2_button_rect, 2)
        if self.gold < self.tower2_cost:
            grey = pygame.Surface((36, 36), pygame.SRCALPHA)
            grey.fill((0, 0, 0, 120))
            screen.blit(grey, self.tower2_button_rect)

        self.main_tower.draw(screen)

        for tower in self.towers:
            tower.draw(screen)
        for projectile in self.projectiles:
            projectile.draw(screen)
        for enemy in self.enemies:
            enemy.draw(screen)

        # -------- TOWER STATS WINDOW --------
        selected = self._selected_tower()
        if selected is not None:                                    # 👈
            self.stats_window.draw(screen, selected, self.gold)

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

            if self.placing_tower == "tower1":
                preview_range = self.tower1_range
                range_color = (60, 60, 200, 60)
                preview_img = self.tower1_preview_img
            else:
                preview_range = self.tower2_aoe
                range_color = (200, 60, 255, 60)
                preview_img = self.tower2_preview_img

            range_surf = pygame.Surface((preview_range * 2, preview_range * 2), pygame.SRCALPHA)
            pygame.draw.circle(range_surf, range_color,
                               (preview_range, preview_range), preview_range, 1)
            screen.blit(range_surf, range_surf.get_rect(center=mouse_pos))

            rect = preview_img.get_rect(center=mouse_pos)
            screen.blit(preview_img, rect)

        # -------- DEBUG GOLD DISPLAY --------
        gold_text = self.debug_font.render(f"Gold: {self.gold}", True, (255, 215, 0))
        screen.blit(gold_text, (10, 10))

        wave_text = self.debug_font.render(f"Wave: {self.current_wave} / {self.total_waves}", True, (255, 255, 255))
        screen.blit(wave_text, (10, 30))

        if self.wave_state == "countdown":
            next_wave = self.current_wave + 1
            seconds_left = math.ceil(self.countdown_timer)
            title = self.wave_font.render(f"Wave {next_wave}", True, (255, 220, 50))
            subtitle = self.wave_font.render(f"Starting in {seconds_left}...", True, (255, 255, 255))
            screen.blit(title, title.get_rect(center=(320, 180)))
            screen.blit(subtitle, subtitle.get_rect(center=(320, 250)))

        if self.wave_state == "result":
            overlay = pygame.Surface((640, 480), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            if self.result == "victory":
                text = self.result_font.render("VICTORY!", True, (100, 255, 100))
            else:
                text = self.result_font.render("DEFEAT", True, (255, 80, 80))
            screen.blit(text, text.get_rect(center=(320, 220)))