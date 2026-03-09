import pygame
from td.projectile import Projectile

class Tower:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.range = 120
        self.fire_rate = 0.8
        self.timer = 0
        self.damage = 5
        self.selected = False  # 👈 added

        # -------- LOAD ATTACK SPRITE SHEET --------
        attack_sheet = pygame.image.load("assets/tower1.png").convert_alpha()
        ATTACK_FRAME_COUNT = 7
        SCALE = 1.5

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

    def update(self, dt, enemies, projectiles):
        self.timer -= dt

        # -------- TICK ANIMATION --------
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

        # -------- FIRE --------
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
        # -------- DRAW RANGE RING ONLY IF SELECTED --------
        if self.selected:
            pygame.draw.circle(screen, (60, 60, 200), self.pos, self.range, 1)

        # -------- DRAW SPRITE --------
        frames = self.attack_frames if self.is_attacking else self.idle_frames
        image = frames[self.frame_index]
        rect = image.get_rect(center=self.pos)
        screen.blit(image, rect)