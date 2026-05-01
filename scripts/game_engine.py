import os
import pygame
from pygame.locals import *

from .entities import Player, Door, Key, Trap, Winpad, Portal, Button, Light, SubMapPortal
from .utils import make_text, invert_color
from .settings import (
    WIDTH, HEIGHT, NB_LEVELS, TILE_SIZE, FPS,
    PLAYER_SPEED, PLAYER_WIDTH, VISION_RADIUS,
    FADE_SPEED, LEVEL_NAMES, LEVEL_COLORS, LEVEL_REWARD,
    LEVEL_CONFIGS, TORCH_EFFECT, TORCH_TIME,
    GAME_NAME, GAME_VERSION, START_TEXT, PLAY_TEXT,
    VICTORY_TEXT, LOADING_TEXT, TUTORIAL_FR_TEXT, TUTORIAL_EN_TEXT,
    KEY_COLORS, DEFAULT_KEY_COLOR,
)
from .assets_manager import load_assets
from .audio_manager import AudioManager
from .level_manager import LevelManager
from .progress_manager import ProgressManager
from .game_state import GameState


class Game:
    """
    Main coordinator.

    Responsibilities here:
      - Main loop (run)
      - Window construction and UI widgets
      - Event dispatch to managers
      - Final rendering (relies on data exposed by managers)
    """

    def __init__(self):
        # --- Pygame ---
        pygame.init()
        self.assets = load_assets()

        # --- Dimensions ---
        self.width = WIDTH
        self.height = HEIGHT
        self.default_window_size = (WIDTH, HEIGHT)
        self.tile_size = TILE_SIZE
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(GAME_NAME)
        pygame.display.set_icon(self.assets["logo"])
        pygame.display.flip()
        self.center_x = self.screen.get_rect().centerx
        self.center_y = self.screen.get_rect().centery

        # --- Managers ---
        self.progress  = ProgressManager(NB_LEVELS)
        self.audio     = AudioManager(self.assets, {"music": self.progress.music_on})
        self.levels    = LevelManager(
            player=Player(self.center_x - PLAYER_WIDTH / 2, self.height - 50, PLAYER_SPEED, PLAYER_WIDTH),
            level_configs={k: dict(v) for k, v in LEVEL_CONFIGS.items()},
        )
        self.player = self.levels._player   # convenient shortcut

        # --- Game state ---
        self.state      = GameState.MAIN_MENU
        self.maze       = 0      # active level (1-based, 0 = menu)
        self.level_menu = 0
        self.active     = True

        # --- Timing ---
        self.clock   = pygame.time.Clock()
        self.fps     = FPS
        self.dt      = 0.0
        self.timer   = 0
        self.seconds = 0.0

        # --- UI Colors ---
        self.font_color        = (0, 0, 0)
        self.second_font_color = (255, 255, 255)
        self.fade_speed        = FADE_SPEED
        self.level_colors      = LEVEL_COLORS
        self.level_names       = LEVEL_NAMES
        self.level_stars       = LEVEL_REWARD
        self.nb_levels         = NB_LEVELS

        # --- Text & buttons ---
        self._build_ui()

    # ==================================================================
    # Main loop
    # ==================================================================

    def run(self):
        while self.active:
            self.handle_events()
            self.update()
            self.render()

    # ==================================================================
    # Events
    # ==================================================================

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.active = False

            elif event.type == KEYDOWN:
                # Music [E]
                if event.key == K_e:
                    music_on = self.audio.toggle()
                    self.progress.save_music_pref(music_on)

                # Menu return [Escape]
                elif event.key == K_ESCAPE and self.state != GameState.MAIN_MENU:
                    self._go_to_menu()

                # Level menu navigation
                elif self.state == GameState.LEVEL_MENU:
                    if event.key == K_d:
                        self._press_right()
                    elif event.key == K_q:
                        self._press_left()

                # Reset level [R]
                elif self.state == GameState.MAZE and event.key == K_r:
                    self._respawn()

            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                self._handle_click(mx, my)

    def _handle_click(self, mx, my):
        if self.state == GameState.LEVEL_MENU:
            btn = self.button_levels[self.level_menu - 1]
            if btn.is_pressed(mx, my):
                self._start_level(self.level_menu)

            if self.button_left_arrow.is_pressed(mx, my):
                self._press_left()
            if self.button_right_arrow.is_pressed(mx, my):
                self._press_right()
            if self.button_left_arrow2.is_pressed(mx, my):
                self._jump_left()
            if self.button_right_arrow2.is_pressed(mx, my):
                self._jump_right()

        elif self.state in (GameState.FRENCH_TUTORIAL, GameState.ENGLISH_TUTORIAL):
            if self.button_home.is_pressed(mx, my):
                self.state = GameState.MAIN_MENU
                self.fade_to_black(self.width, self.height, self.fade_speed["normal"])

        elif self.state == GameState.VICTORY_MENU:
            if self.button_home.is_pressed(mx, my):
                self._go_to_menu()

        elif self.state == GameState.MAIN_MENU:
            if self.button_start.is_pressed(mx, my):
                self.state = GameState.LEVEL_MENU
                self.level_menu = 1
                self.fade_to_black(self.width, self.height, self.fade_speed["normal"])
            if self.button_book_fr.is_pressed(mx, my):
                self.state = GameState.FRENCH_TUTORIAL
                self.fade_to_black(self.width, self.height, self.fade_speed["normal"])
            if self.button_book_en.is_pressed(mx, my):
                self.state = GameState.ENGLISH_TUTORIAL
                self.fade_to_black(self.width, self.height, self.fade_speed["normal"])

    # ==================================================================
    # Update
    # ==================================================================

    def update(self):
        raw_dt = self.clock.tick(self.fps) / 1000.0
        self.dt = min(raw_dt, 0.05)

        self.audio.update(self.dt)

        if self.state != GameState.MAZE:
            return

        self.seconds = round((pygame.time.get_ticks() - self.timer) / 1000, 2)
        keys = pygame.key.get_pressed()

        dx, dy = 0.0, 0.0
        dist = self.player.speed * self.dt
        if keys[K_q]: dx -= dist
        if keys[K_d]: dx += dist
        if keys[K_z]: dy -= dist
        if keys[K_s]: dy += dist

        # Obstacles = walls + closed doors
        walls = list(self.levels.walls(self.maze))
        for obj in self.levels.special_objs(self.maze):
            if isinstance(obj, Door) and not obj.opened:
                walls.append(obj)

        self.player.move(dx, dy, walls, self)
        self._process_objects()

    def _process_objects(self):
        portal_contact = False

        for obj in list(self.levels.special_objs(self.maze)):
            # Portal
            if isinstance(obj, Portal) and obj.is_touched(self.player):
                portal_contact = True
                if self.player.can_teleport:
                    if obj.dest_id is not None and obj.id != obj.dest_id:
                        self.audio.play_sfx("sfx_teleport")
                    self.player.use_portal(obj, self.levels.special_objs(self.maze))
                    self.player.can_teleport = False
                    break

            # Victory
            elif isinstance(obj, Winpad) and obj.is_touched(self.player) and not self.player.win:
                self._handle_victory()
                break

            # Key
            elif isinstance(obj, Key) and not obj.collected and obj.is_touched(self.player):
                self.audio.play_sfx("sfx_key")
                self.player.pick_up_key(obj)

            # Door
            elif isinstance(obj, Door) and not obj.opened:
                if obj.rect.inflate(10, 10).colliderect(self.player.rect):
                    if obj.id in self.player.keys:
                        self.audio.play_sfx("sfx_unlock")
                        obj.open()

            # Trap
            elif isinstance(obj, Trap) and obj.is_touched(self.player):
                self._respawn()
                break

            # Light
            elif isinstance(obj, Light):
                if obj.is_touched(self.player) and obj.cooldown == 0.0:
                    obj.collect()
                    obj.cooldown = TORCH_TIME
                    self.levels.vision_radius += TORCH_EFFECT
                if 0.0 < obj.cooldown <= TORCH_TIME:
                    obj.cooldown -= self.dt
                    if obj.cooldown <= 0.0:
                        obj.cooldown = 0.0
                        self.levels.vision_radius -= TORCH_EFFECT
                        obj.respawn()

            # Sub-map
            elif isinstance(obj, SubMapPortal) and obj.is_touched(self.player):
                layout = self.levels.load_sub_map(self.maze, obj.target_map_index, self)
                self.player.teleport(
                    obj.spawn_pos[0] + self.player.width / 2,
                    obj.spawn_pos[1] + self.player.width / 2,
                )
                self._resize_window(layout)
                self.audio.play_sfx("sfx_teleport")
                break

        if not portal_contact:
            self.player.can_teleport = True

    # ==================================================================
    # Rendering
    # ==================================================================

    def render(self):
        # Background
        if self.maze == 67 or self.level_menu == 67:
            self.screen.fill((255, 255, 255))
        else:
            self.screen.fill((0, 0, 0))

        if self.state == GameState.MAZE:
            self._render_maze()
        elif self.state == GameState.LEVEL_MENU:
            self._render_level_menu()
        elif self.state in (GameState.FRENCH_TUTORIAL, GameState.ENGLISH_TUTORIAL):
            self._render_tutorial()
        elif self.state == GameState.VICTORY_MENU:
            self._render_victory()
        elif self.state == GameState.MAIN_MENU:
            self._render_main_menu()

        # Music icon animation
        if self.audio.music_animation:
            img_key = "music_on" if self.audio.music_play else "music_off"
            self.screen.blit(self.assets[img_key], (self.width - 75, 25))

        pygame.display.flip()

    def _render_maze(self):
        objs  = self.levels.special_objs(self.maze)
        walls = self.levels.walls(self.maze)

        for obj in objs:
            if isinstance(obj, Portal):
                img = obj.img if obj.dest_id is not None else obj.img2
                self.screen.blit(img, (obj.x, obj.y))
            elif isinstance(obj, Winpad):
                self.screen.blit(obj.img, (obj.x, obj.y))
            elif isinstance(obj, Key) and not obj.collected:
                self.screen.blit(obj.img, (obj.x, obj.y))
            elif isinstance(obj, Door) and not obj.opened:
                color = KEY_COLORS.get(obj.id.lower(), DEFAULT_KEY_COLOR)
                pygame.draw.rect(self.screen, color, (obj.x1, obj.y1, obj.x2 - obj.x1, obj.y2 - obj.y1))
                pygame.draw.rect(self.screen, (0, 0, 0), obj.rect, 2)
            elif isinstance(obj, Trap):
                self.screen.blit(obj.img, (obj.x, obj.y))
            elif isinstance(obj, Light) and not obj.collected:
                self.screen.blit(obj.img, (obj.x, obj.y))
            elif isinstance(obj, SubMapPortal):
                self.screen.blit(obj.img, (obj.x, obj.y))

        pygame.draw.rect(self.screen, (255, 0, 0),
                         (self.player.x, self.player.y, self.player.width, self.player.width))

        level_color = self.level_colors.get(self.maze, (255, 255, 255))
        for wall in walls:
            pygame.draw.rect(self.screen, level_color,
                             (wall.x1, wall.y1, wall.x2 - wall.x1, wall.y2 - wall.y1))

        if self.levels.has_fow(self.maze):
            self._draw_fog()

        timer_txt, timer_pos = make_text(
            self.assets["font_small"], f"Time : {self.seconds}", (255, 255, 255),
            self.width - 100, 30,
        )
        self.screen.blit(timer_txt, timer_pos)

    def _render_level_menu(self):
        font_color = self.font_color
        if self.level_menu == 67:
            font_color = invert_color(font_color)
        inv_color = invert_color(font_color)
        level_color = self.level_colors.get(self.level_menu, self.second_font_color)

        level_btn = self.button_levels[self.level_menu - 1]
        pygame.draw.rect(self.screen, level_color,
                         (level_btn.x, level_btn.y, level_btn.width, level_btn.height))
        pygame.draw.rect(self.screen, font_color,
                         (level_btn.x + 20, level_btn.y + 20,
                          level_btn.width - 40, level_btn.height - 40))

        t, tpos = self.level_texts[self.level_menu - 1]
        self.screen.blit(t, tpos)

        play_t, play_pos = make_text(self.assets["font_main"], PLAY_TEXT, level_color,
                                     self.center_x, self.center_y)
        self.screen.blit(play_t, play_pos)

        stars = self.level_stars.get(self.level_menu, 0)
        star_txt, star_pos = make_text(self.assets["font_medium"], f": {stars}", inv_color,
                                       self.center_x + 20, self.center_y + 200)
        w, _ = star_txt.get_size()
        self.screen.blit(self.assets["star"], (self.center_x - 75, self.center_y + 175))
        self.screen.blit(star_txt, (star_pos.left + w / 2 - 25, star_pos.top))

        if self.progress.is_completed(self.level_menu):
            self.screen.blit(self.assets["completed"], (self.center_x - 75, self.center_y + 175))

        rec_txt, rec_pos = make_text(
            self.assets["font_medium"],
            f"Record : {self.progress.best_time_display(self.level_menu)}",
            inv_color, self.center_x, self.center_y + 275,
        )
        self.screen.blit(rec_txt, rec_pos)

        if self.level_menu in self.level_names:
            li_txt, li_pos = make_text(self.assets["font_small"],
                                       f"Level {self.level_menu}", inv_color,
                                       self.center_x, 100)
            self.screen.blit(li_txt, li_pos)

        for btn in (self.button_left_arrow, self.button_right_arrow,
                    self.button_left_arrow2, self.button_right_arrow2):
            self.screen.blit(btn.img, (btn.x, btn.y))

    def _render_tutorial(self):
        texts = (self.tutorial_fr if self.state == GameState.FRENCH_TUTORIAL
                 else self.tutorial_en)
        for t, tp in texts:
            self.screen.blit(t, tp)
        self.screen.blit(self.button_home.img, (self.button_home.x, self.button_home.y))

    def _render_victory(self):
        pygame.draw.rect(self.screen, (255, 255, 0), (50, 50, self.width - 100, self.height - 100))
        pygame.draw.rect(self.screen, (0, 0, 0),     (75, 75, self.width - 150, self.height - 150))
        self.screen.blit(self.victory_text, self.victory_textpos)
        self.screen.blit(self.button_home.img, (self.button_home.x, self.button_home.y))
        self.screen.blit(self.final_timer_text, self.final_timer_textpos)
        if self.display_record_txt:
            self.screen.blit(self.record_txt, self.record_pos)

    def _render_main_menu(self):
        self.screen.blit(self.name_text, self.name_textpos)
        pygame.draw.rect(self.screen, (255, 255, 0),
                         (self.button_start.x, self.button_start.y,
                          self.button_start.width, self.button_start.height))
        pygame.draw.rect(self.screen, (0, 0, 0),
                         (self.button_start.x + 10, self.button_start.y + 10,
                          self.button_start.width - 20, self.button_start.height - 20))
        self.screen.blit(self.start_text, self.start_textpos)
        self.screen.blit(self.button_book_fr.img, (self.button_book_fr.x, self.button_book_fr.y))
        self.screen.blit(self.button_book_en.img, (self.button_book_en.x, self.button_book_en.y))

        w, _ = self.stars_display.get_size()
        self.screen.blit(self.assets["star"], (25, 25))
        self.screen.blit(self.stars_display, (self.stars_displaypos.left + w / 2, self.stars_displaypos.top))
        self.screen.blit(self.v_txt, self.v_pos)

    # ==================================================================
    # Transitions & actions
    # ==================================================================

    def fade_to_black(self, width, height, speed=10):
        surf = pygame.Surface((width, height))
        surf.fill((0, 0, 0))
        for alpha in range(0, 256, speed):
            surf.set_alpha(alpha)
            self.screen.blit(surf, (0, 0))
            pygame.display.update()
            pygame.time.delay(28)

    def _draw_fog(self):
        fog = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        fog.fill((0, 0, 0, 255))
        r = self.levels.vision_radius
        for i in range(r, 0, -5):
            alpha = int(255 * (i / r))
            pygame.draw.circle(fog, (0, 0, 0, alpha), self.player.rect.center, i)
        self.screen.blit(fog, (0, 0))

    def _go_to_menu(self):
        if self.state == GameState.MAZE:
            self.levels.reset_objects(self.maze)
        self.player.reset()
        self.state = GameState.MAIN_MENU
        self.maze = 0
        self.level_menu = 0
        self.display_record_txt = False
        self.levels.reset_vision()
        self.timer = pygame.time.get_ticks()
        
        self.fade_to_black(self.width, self.height, self.fade_speed["normal"])

        self.width, self.height = self.default_window_size
        self.screen = pygame.display.set_mode(self.default_window_size)
        self.center_x = self.screen.get_rect().centerx
        self.center_y = self.screen.get_rect().centery

        self.stars_display, self.stars_displaypos = make_text(
            self.assets["font_medium"], str(self.progress.nb_stars),
            (255, 255, 255), 100, 50,
        )

        self.audio.switch_to_menu()
        self.clock.tick()

    def _respawn(self):
        self.levels.reset_objects(self.maze)
        self.levels.reset_vision()
        self.audio.play_sfx("sfx_death")
        layout = self.levels.load_sub_map(self.maze, 0, self)
        self.player.respawn()
        self._resize_window(layout)
        self.timer = pygame.time.get_ticks()
        self.clock.tick()

    def _handle_victory(self):
        self.audio.play_sfx("sfx_win")
        self.player.victory()
        self.fade_to_black(self.width, self.height, self.fade_speed["slow"])

        stars = self.level_stars.get(self.maze, 0)
        new_record = self.progress.record_victory(self.maze, stars, self.seconds)
        self.display_record_txt = new_record

        self.audio.switch_to_victory()

        self.width, self.height = self.default_window_size
        self.screen = pygame.display.set_mode(self.default_window_size)
        self.center_x = self.screen.get_rect().centerx
        self.center_y = self.screen.get_rect().centery

        self.final_timer_text, self.final_timer_textpos = make_text(
            self.assets["font_main"], f"Time : {self.seconds}",
            (255, 255, 255), self.center_x, self.center_y,
        )
        self.state = GameState.VICTORY_MENU
        self.maze = 0

    def _start_level(self, level_id: int):
        self.state      = GameState.MAZE
        self.level_menu = 0
        self.maze       = level_id
        self.display_record_txt = False

        self.audio.play_sfx("sfx_play")
        self.fade_to_black(self.width, self.height, self.fade_speed["normal"])
        self.screen.blit(self.loading_text, self.loading_textpos)
        pygame.display.flip()

        cfg = self.levels.level_configs.get(level_id)
        if cfg:
            if not cfg["loaded"] and level_id != 3:
                layout = self.levels.load_level(level_id, self)
            else:
                layout = self.levels.load_sub_map(level_id, 0, self)
            self._resize_window(layout)

        self.audio.switch_to_level(level_id)
        self.timer = pygame.time.get_ticks()
        self.clock.tick()

    def _resize_window(self, layout):
        self.fade_to_black(self.width, self.height, self.fade_speed["normal"])
        self.width  = len(layout[0]) * self.tile_size
        self.height = len(layout)    * self.tile_size
        os.environ["SDL_VIDEO_WINDOW_POS"] = "center"
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.clock.tick()

    # ==================================================================
    # Level menu navigation
    # ==================================================================

    def _press_left(self):
        self.level_menu = self.nb_levels if self.level_menu == 1 else self.level_menu - 1

    def _press_right(self):
        self.level_menu = 1 if self.level_menu == self.nb_levels else self.level_menu + 1

    def _jump_left(self):
        self.level_menu = max(1, self.level_menu - 10)

    def _jump_right(self):
        self.level_menu = min(self.nb_levels, self.level_menu + 10)

    # ==================================================================
    # UI Construction (called once in __init__)
    # ==================================================================

    def _build_ui(self):
        a = self.assets
        cx, cy = self.center_x, self.center_y

        self.name_text, self.name_textpos = make_text(
            a["font_main"], GAME_NAME, (255, 255, 255), cx, cy - 200)
        self.start_text, self.start_textpos = make_text(
            a["font_main"], START_TEXT, (255, 255, 0), cx, cy)
        self.victory_text, self.victory_textpos = make_text(
            a["font_main"], VICTORY_TEXT, (255, 255, 0), cx, cy // 2)
        self.loading_text, self.loading_textpos = make_text(
            pygame.font.Font(None, 144), LOADING_TEXT, (255, 255, 255), cx, cy)
        self.stars_display, self.stars_displaypos = make_text(
            a["font_medium"], str(self.progress.nb_stars), (255, 255, 255), 100, 50)
        self.v_txt, self.v_pos = make_text(
            a["font_small"], GAME_VERSION, (255, 255, 255),
            self.width - 25 - 6 * len(GAME_VERSION), 25)
        self.record_txt, self.record_pos = make_text(
            a["font_medium"], "New record !", (255, 255, 255), cx, cy + 75)
        self.display_record_txt = False

        # Level texts
        self.level_texts = [
            make_text(a["font_main"], f"Level {n + 1}", (255, 255, 255), cx, cy - 200)
            for n in range(NB_LEVELS)
        ]
        for lvl_id, name in LEVEL_NAMES.items():
            color = (0, 0, 0) if lvl_id == 67 else (255, 255, 255)
            self.level_texts[lvl_id - 1] = make_text(a["font_main"], name, color, cx, cy - 200)

        # Tutorials
        self.tutorial_fr = [
            make_text(a["font_small"], txt, (255, 255, 255), cx, TILE_SIZE * (i + 2))
            for i, txt in enumerate(TUTORIAL_FR_TEXT)
        ]
        self.tutorial_en = [
            make_text(a["font_small"], txt, (255, 255, 255), cx, TILE_SIZE * (i + 2))
            for i, txt in enumerate(TUTORIAL_EN_TEXT)
        ]

        # Placeholder for level end text
        self.final_timer_text, self.final_timer_textpos = make_text(
            a["font_main"], "", (255, 255, 255), cx, cy)

        # Buttons
        self.button_start        = Button(cx, cy, 400, 150, None)
        self.button_book_fr      = Button(100, self.height - 100, 100, 100, a["tutorial_fr"])
        self.button_book_en      = Button(250, self.height - 100, 100, 100, a["tutorial_en"])
        self.button_right_arrow  = Button(self.width - 100, cy - 50, 50, 50, a["right_arrow"])
        self.button_left_arrow   = Button(100, cy - 50, 50, 50, a["left_arrow"])
        self.button_right_arrow2 = Button(self.width - 100, cy + 50, 50, 50, a["right_double_arrow"])
        self.button_left_arrow2  = Button(100, cy + 50, 50, 50, a["left_double_arrow"])
        self.button_home         = Button(50, 50, 75, 75, a["home"])
        self.button_levels       = [Button(cx, cy, 400, 250, None) for _ in range(NB_LEVELS)]
