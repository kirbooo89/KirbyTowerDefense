import pygame
from td.path import PATH

class Enemy:
    def __init__(self):
        # -------- POSITION / PATH --------
        self.pos = pygame.Vector2(PATH[0])
        self.speed = 80
        self.target_index = 1
        self.alive = True

        # -------- STATS  --------
        self.max_health = 20
        self.health = self.max_health
        self.damage = 3

        # -------- HEALTH BAR -----
        self.bar_width = 30
        self.bar_height = 5
        self.bar_offset_y = 25  # distance above enemy

        # -------- LOAD SPRITE SHEET --------
        sheet = pygame.image.load("assets/pawn.png").convert_alpha()

        FRAME_COUNT = 6   # change if your sheet has a different number
        SCALE = 0.5       # 🔴 half size

        frame_width = sheet.get_width() // FRAME_COUNT
        frame_height = sheet.get_height()

        self.frames = []
        for i in range(FRAME_COUNT):
            frame = sheet.subsurface(
                pygame.Rect(
                    i * frame_width,
                    0,
                    frame_width,
                    frame_height,
                )
            )

            # ---- SCALE FRAME TO HALF SIZE ----
            frame = pygame.transform.scale(
                frame,
                (
                    int(frame_width * SCALE),
                    int(frame_height * SCALE),
                )
            )

            self.frames.append(frame)

        # -------- ANIMATION --------
        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.12

        # -------- DIRECTION --------
        self.facing_left = False

    def update(self, dt):
        if self.health <= 0:
            self.alive = False

        if self.target_index >= len(PATH):
            self.alive = False
            return

        target = pygame.Vector2(PATH[self.target_index])
        direction = target - self.pos

        if direction.length() < 2:
            self.target_index += 1
        else:
            # ---- CHECK HORIZONTAL DIRECTION ----
            if direction.x < 0:
                self.facing_left = True
            elif direction.x > 0:
                self.facing_left = False

            self.pos += direction.normalize() * self.speed * dt

        # ---- ANIMATION ----
        self.anim_timer += dt
        if self.anim_timer >= self.anim_speed:
            self.anim_timer = 0
            self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, screen):
        image = self.frames[self.frame_index]

        # ---- FLIP ONLY WHEN MOVING LEFT ----
        if self.facing_left:
            image = pygame.transform.flip(image, True, False)

        rect = image.get_rect(center=self.pos)
        screen.blit(image, rect)

        # -------- HEALTH BAR --------
        health_ratio = self.health / self.max_health
        current_width = int(self.bar_width * health_ratio)

        bar_x = self.pos.x - self.bar_width // 2
        bar_y = self.pos.y - self.bar_offset_y

        # Red background
        pygame.draw.rect(
            screen,
            (180, 0, 0),
            (bar_x, bar_y, self.bar_width, self.bar_height),
        )

        # Green health
        pygame.draw.rect(
            screen,
            (0, 200, 0),
            (bar_x, bar_y, current_width, self.bar_height),
        )
        # Black Outline
        # pygame.draw.rect(
        #     screen,
        #     (0, 0, 0),
        #     (bar_x, bar_y, self.bar_width, self.bar_height),
        #     1
        # )

