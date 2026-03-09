import pygame

from startScene import StartScene
from mapSelectionScene import MapSelectScene
from gameScene import GameScene
from resultScene import ResultScene
from kirbySelectionScene import KirbySelectionScene

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption("Scene Transition Test")
clock = pygame.time.Clock()

SCENES = {
    "start": StartScene,
    "map_select": MapSelectScene,
    "game": GameScene,
    "result": ResultScene,
    "kirby_select": KirbySelectionScene,
}

current_scene = StartScene()

# Fade control
fade_surface = pygame.Surface((800, 600))
fade_surface.fill((0, 0, 0))
fade_alpha = 0
fade_speed = 400        # alpha per second
is_fading = False
fade_direction = 1      # 1 = fade out, -1 = fade in
next_scene_name = None

running = True
while running:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif not is_fading:
            next_scene_name = current_scene.handle_event(event)

    if not is_fading:
        scene_request = current_scene.update(dt)
        if scene_request:
            next_scene_name = scene_request

        if next_scene_name:
            is_fading = True
            fade_direction = 1
            fade_alpha = 0

    else:
        fade_alpha += fade_direction * fade_speed * dt

        if fade_alpha >= 255:
            fade_alpha = 255
            current_scene = SCENES[next_scene_name]()
            fade_direction = -1

        elif fade_alpha <= 0:
            fade_alpha = 0
            is_fading = False
            next_scene_name = None

    current_scene.draw(screen)

    if is_fading:
        fade_surface.set_alpha(int(fade_alpha))
        screen.blit(fade_surface, (0, 0))

    pygame.display.flip()

pygame.quit()
