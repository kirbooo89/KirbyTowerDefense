import pygame

class TowerStatsWindow:
    def __init__(self):
        # -------- BACKGROUND --------
        self.bg_img = pygame.image.load("../assets/tower_stats.png").convert_alpha()
        self.bg_pos = (10, 114)     # topleft

        # -------- UPGRADE BUTTON IMAGES --------
        self.btn_released    = pygame.image.load("../assets/upgrade_released.png").convert_alpha()
        self.btn_pressed     = pygame.image.load("../assets/upgrade_pressed.png").convert_alpha()
        self.btn_unavailable = pygame.image.load("../assets/upgrade_unavailable.png").convert_alpha()

        self.btn_released    = pygame.transform.scale(self.btn_released,    (32, 32))
        self.btn_pressed     = pygame.transform.scale(self.btn_pressed,     (32, 32))
        self.btn_unavailable = pygame.transform.scale(self.btn_unavailable, (32, 32))

        # button topleft is x:97 y:128 in screen space
        self.btn_rect = pygame.Rect(
            self.bg_pos[0] + 97,
            self.bg_pos[1] + 128,    # local y:128 relative to window
            32, 32
        )

        # -------- FONT --------
        self.font = pygame.font.Font("../assets/BoldPixels.ttf", 12)

        # -------- BUTTON STATE --------
        self.btn_is_pressed = False

        # cached icon surface
        self._icon_cache = {}

    # ----------------------------------------------------------------
    #  helpers
    # ----------------------------------------------------------------

    def _get_icon(self, path):
        if path not in self._icon_cache:
            img = pygame.image.load(path).convert_alpha()
            # crop first 36x36 frame and keep as-is
            img = img.subsurface(pygame.Rect(0, 0, 36, 36)).copy()
            self._icon_cache[path] = img
        return self._icon_cache[path]

    def _win_x(self, local_x):
        return self.bg_pos[0] + local_x

    def _win_y(self, local_y):
        return self.bg_pos[1] + local_y

    # ----------------------------------------------------------------
    #  public API
    # ----------------------------------------------------------------

    def handle_event(self, event, tower, gold):
        """
        Call from GameScene.handle_event when a tower is selected.
        Returns new gold value after potential upgrade purchase.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if tower.level < tower.max_level:
                cost = tower.upgrade_cost()
                if cost is not None and gold >= cost:
                    if self.btn_rect.collidepoint(event.pos):
                        self.btn_is_pressed = True
                        tower.upgrade()
                        gold -= cost
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.btn_is_pressed = False

        return gold

    def draw(self, screen, tower, gold):
        # -------- BACKGROUND --------
        screen.blit(self.bg_img, self.bg_pos)

        # -------- ICON --------
        icon = self._get_icon(tower.icon_path)
        screen.blit(icon, (self._win_x(24), self._win_y(24)))

        # -------- NAME --------
        name_surf = self.font.render(tower.name, True, (255, 255, 255))
        screen.blit(name_surf, (self._win_x(80), self._win_y(40)))

        # -------- ATK --------
        atk_surf = self.font.render(f"ATK: {tower.damage}", True, (255, 255, 255))
        screen.blit(atk_surf, (self._win_x(19), self._win_y(90)))

        # -------- FIRE RATE --------
        fr_surf = self.font.render(f"FR: {tower.fire_rate:.2f}", True, (255, 255, 255))
        screen.blit(fr_surf, (self._win_x(19), self._win_y(108)))

        # -------- LEVEL --------
        lvl_label = "MAX" if tower.level >= tower.max_level else str(tower.level)
        lvl_surf = self.font.render(f"LVL: {lvl_label}", True, (255, 255, 255))
        screen.blit(lvl_surf, (self._win_x(19), self._win_y(126)))

        # -------- UPGRADE SECTION (hidden at max level) --------
        if tower.level < tower.max_level:
            cost = tower.upgrade_cost()

            # price text
            cost_surf = self.font.render(f"{cost} POYO", True, (255, 215, 0))
            screen.blit(cost_surf, (self._win_x(19), self._win_y(144)))

            # button state
            can_afford = gold >= cost
            if not can_afford:
                btn_img = self.btn_unavailable
            elif self.btn_is_pressed:
                btn_img = self.btn_pressed
            else:
                btn_img = self.btn_released

            screen.blit(btn_img, self.btn_rect)