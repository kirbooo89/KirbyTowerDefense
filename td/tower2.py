import pygame

class Tower2:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.range = 120
        self.fire_rate = 0.8        # seconds between AOE bursts
        self.timer = 0
        self.damage = 12             # AOE damage per burst
        self.selected = False

        # -------- LOAD IDLE SPRITE SHEET (48x48, 6 frames) --------
        idle_sheet = pygame.image.load("assets/spark_tower_idle.png").convert_alpha()
        IDLE_FRAMES = 6
        IDLE_FRAME_SIZE = 48
        SCALE = 2

        self.idle_frames = []
        for i in range(IDLE_FRAMES):
            frame = idle_sheet.subsurface(pygame.Rect(i * IDLE_FRAME_SIZE, 0, IDLE_FRAME_SIZE, IDLE_FRAME_SIZE))
            frame = pygame.transform.scale(frame, (IDLE_FRAME_SIZE * SCALE, IDLE_FRAME_SIZE * SCALE))
            self.idle_frames.append(frame)

        # -------- LOAD ATTACK SPRITE SHEET (64x64, 7 frames) --------
        attack_sheet = pygame.image.load("assets/spark_tower_attack.png").convert_alpha()
        ATTACK_FRAMES = 7
        ATTACK_FRAME_SIZE = 64

        self.attack_frames = []
        for i in range(ATTACK_FRAMES):
            frame = attack_sheet.subsurface(pygame.Rect(i * ATTACK_FRAME_SIZE, 0, ATTACK_FRAME_SIZE, ATTACK_FRAME_SIZE))
            frame = pygame.transform.scale(frame, (ATTACK_FRAME_SIZE * SCALE, ATTACK_FRAME_SIZE * SCALE))
            self.attack_frames.append(frame)

        # -------- ANIMATION STATE --------
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.1
        self.is_attacking = False

        # -------- AOE RADIUS --------
        # idle sprite is 48px, attack sprite is 64px
        # the extra 16px (8 on each side) defines the AOE damage zone
        self.aoe_radius = (IDLE_FRAME_SIZE // 2 + 16) * SCALE   # = 40px scaled

    def update(self, dt, enemies, projectiles):
        self.timer -= dt

        # -------- TICK ANIMATION --------
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.frame_index += 1

            if self.is_attacking:
                # -------- DEAL AOE DAMAGE ON FIRST FRAME --------
                if self.frame_index == 1:
                    for enemy in enemies:
                        if enemy.alive and self.pos.distance_to(enemy.pos) <= self.aoe_radius:
                            enemy.health -= self.damage
                            enemy.flash()

                if self.frame_index >= len(self.attack_frames):
                    self.frame_index = 0
                    self.is_attacking = False
            else:
                self.frame_index = self.frame_index % len(self.idle_frames)

        # -------- TRIGGER ATTACK --------
        if self.timer <= 0:
            # only attack if at least one enemy is in range
            for enemy in enemies:
                if enemy.alive and self.pos.distance_to(enemy.pos) <= self.aoe_radius:
                    self.is_attacking = True
                    self.frame_index = 0
                    self.anim_timer = 0
                    self.timer = self.fire_rate
                    break

    def draw(self, screen):
        # -------- RANGE RING ONLY IF SELECTED --------
        if self.selected:
            pygame.draw.circle(screen, (200, 100, 255), self.pos, self.aoe_radius, 1)

        # -------- DRAW SPRITE --------
        frames = self.attack_frames if self.is_attacking else self.idle_frames
        image = frames[self.frame_index]
        rect = image.get_rect(center=self.pos)
        screen.blit(image, rect)