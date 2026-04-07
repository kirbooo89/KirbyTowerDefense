import pygame
from td.projectile import Projectile

class Tower:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.range = 120
        self.fire_rate = 0.8
        self.timer = 0
        self.damage = 5
        self.selected = False

        # -------- IDENTITY --------
        self.name = "Kirby Tower"
        self.icon_path = "assets/tower1_button.png"

        # -------- UPGRADE --------
        self.level = 0
        self.max_level = 10
        self.upgrade_costs = [50, 75, 100, 130, 165, 200, 240, 285, 335, 400]
        # each entry: (damage, fire_rate)
        self.upgrade_stats = [
            (7,  0.75),
            (9,  0.70),
            (12, 0.65),
            (15, 0.60),
            (19, 0.55),
            (23, 0.50),
            (28, 0.45),
            (34, 0.40),
            (41, 0.36),
            (50, 0.32),
        ]

        # -------- LOAD ATTACK SPRITE SHEET --------
        attack_sheet = pygame.image.load("assets/tower1.png").convert_alpha()
        ATTACK_FRAME_COUNT = 7
        SCALE = 2

        frame_width = attack_sheet.get_width() // ATTACK_FRAME_COUNT
        frame_height = attack_sheet.get_height()

        self.attack_frames = []
        for i in range(ATTACK_FRAME_COUNT):
            frame = attack_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (int(frame_width * SCALE), int(frame_height * SCALE)))
            self.attack_frames.append(frame)

        # -------- LOAD IDLE SPRITE SHEET --------
        idle_sheet = pygame.image.load("assets/tower_idle.png").convert_alpha()
        IDLE_FRAME_COUNT = 5

        frame_width = idle_sheet.get_width() // IDLE_FRAME_COUNT
        frame_height = idle_sheet.get_height()

        self.idle_frames = []
        for i in range(IDLE_FRAME_COUNT):
            frame = idle_sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(frame, (int(frame_width * SCALE), int(frame_height * SCALE)))
            self.idle_frames.append(frame)

        # -------- ANIMATION STATE --------
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.1
        self.is_attacking = False

    def upgrade(self):
        if self.level >= self.max_level:
            return
        dmg, fr = self.upgrade_stats[self.level]
        self.damage = dmg
        self.fire_rate = fr
        self.level += 1

    def upgrade_cost(self):
        if self.level >= self.max_level:
            return None
        return self.upgrade_costs[self.level]

    def update(self, dt, enemies, projectiles):
        self.timer -= dt

        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.frame_index += 1
            if self.is_attacking:
                if self.frame_index >= len(self.attack_frames):
                    self.frame_index = 0
                    self.is_attacking = False
            else:
                self.frame_index = self.frame_index % len(self.idle_frames)

        if self.timer <= 0:
            for enemy in enemies:
                if enemy.alive and self.pos.distance_to(enemy.pos) <= self.range:
                    projectiles.append(Projectile(self.pos, enemy, self.damage))
                    self.timer = self.fire_rate
                    self.is_attacking = True
                    self.frame_index = 0
                    self.anim_timer = 0
                    break

    def draw(self, screen):
        if self.selected:
            pygame.draw.circle(screen, (60, 60, 200), self.pos, self.range, 1)

        frames = self.attack_frames if self.is_attacking else self.idle_frames
        image = frames[self.frame_index]
        rect = image.get_rect(center=self.pos)
        screen.blit(image, rect)