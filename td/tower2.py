import pygame

class Tower2:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.range = 120
        self.fire_rate = 1.0
        self.timer = 0
        self.damage = 8
        self.selected = False

        # -------- IDENTITY --------
        self.name = "Spark Tower"
        self.icon_path = "assets/tower2_button.png"

        # -------- UPGRADE --------
        self.level = 0
        self.max_level = 10
        self.upgrade_costs = [50, 70, 95, 125, 160, 200, 245, 295, 350, 415]
        # each entry: (damage, fire_rate)
        self.upgrade_stats = [
            (11, 0.95),
            (15, 0.90),
            (19, 0.85),
            (24, 0.80),
            (30, 0.75),
            (37, 0.70),
            (45, 0.65),
            (54, 0.60),
            (65, 0.55),
            (78, 0.50),
        ]

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
        self.aoe_radius = (IDLE_FRAME_SIZE // 2 + 16) * SCALE

        # -------- ATTACK SOUND --------
        self.attack_sound = pygame.mixer.Sound("assets/spark_tower_attack.mp3")
        self.attack_sound.set_volume(0.6)

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

        if self.timer <= 0:
            for enemy in enemies:
                if enemy.alive and self.pos.distance_to(enemy.pos) <= self.aoe_radius:
                    self.is_attacking = True
                    self.frame_index = 0
                    self.anim_timer = 0
                    self.timer = self.fire_rate
                    self.attack_sound.play()
                    break

    def draw(self, screen):
        if self.selected:
            pygame.draw.circle(screen, (200, 100, 255), self.pos, self.aoe_radius, 1)

        frames = self.attack_frames if self.is_attacking else self.idle_frames
        image = frames[self.frame_index]
        rect = image.get_rect(center=self.pos)
        screen.blit(image, rect)