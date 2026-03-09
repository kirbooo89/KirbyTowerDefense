import pygame
import math

class Projectile:
    def __init__(self, pos, target, damage):
        self.pos = pygame.Vector2(pos)
        self.target = target
        self.speed = 400
        self.damage = damage
        self.alive = True

        # -------- LOAD SPRITE SHEET --------
        sheet = pygame.image.load("assets/projectile.png").convert_alpha()

        FRAME_COUNT = 4
        SCALE = 2

        frame_width = sheet.get_width() // FRAME_COUNT
        frame_height = sheet.get_height()

        self.frames = []
        for i in range(FRAME_COUNT):
            frame = sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frame = pygame.transform.scale(
                frame,
                (int(frame_width * SCALE), int(frame_height * SCALE))
            )
            self.frames.append(frame)

        # -------- ANIMATION --------
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.08

        # -------- ROTATION --------
        self.angle = 0

        # -------- SOUND --------
        self.hit_sound = pygame.mixer.Sound("assets/hit.wav")
        self.hit_sound.set_volume(0.5)  # 0.0 to 1.0, adjust to taste

    def update(self, dt):
        if not self.target.alive:
            self.alive = False
            return

        direction = self.target.pos - self.pos

        if direction.length() < 5:
            # -------- HIT! --------
            self.target.health -= self.damage
            self.hit_sound.play()   # 👈 play sound on impact
            self.alive = False
            return

        # -------- CALCULATE ROTATION ANGLE --------
        self.angle = -math.degrees(math.atan2(direction.y, direction.x))

        self.pos += direction.normalize() * self.speed * dt

        # -------- TICK ANIMATION --------
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, screen):
        image = self.frames[self.frame_index]
        rotated = pygame.transform.rotate(image, self.angle)
        rect = rotated.get_rect(center=self.pos)
        screen.blit(rotated, rect)