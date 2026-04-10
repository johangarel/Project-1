import os
import pygame
from pygame.locals import*
from .entities import Player, Door, Key, Trap, Winpad, Portal, Button, Light, SubMapPortal
from .utils import make_text, load_map, invert_color
from .settings import*
from .assets_manager import load_assets
from .maze import Maze

class Game :
    def __init__(self):
        # General stuff
        self.width = WIDTH
        self.height = HEIGHT
        self.default_window_size = (WIDTH,HEIGHT)
        self.nb_levels = NB_LEVELS
        self.tile_size = TILE_SIZE
        self.timer = 0
        self.recall_time = 0
        # Menus
        self.active = True
        self.state = "MAIN MENU"
        self.maze = 0
        self.level_menu = 0
        self.font_color = (0,0,0)
        self.second_font_color = (255,255,255)
        # Pygame
        pygame.init()
        self.assets = load_assets()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(GAME_TITLE)
        pygame.display.set_icon(self.assets["logo"])
        pygame.display.flip()
        # Music
        self.music_animation = False
        self.music_play = True
        self.time_display = 2.0
        self.sound_active = self.assets["menu_music"]
        self.sound_list = [self.assets["music_level1"], self.assets["music_level2"], self.assets["music_level3"], self.assets["music_level4"]]
        self.sound_list.extend([None for _ in range(self.nb_levels-len(self.sound_list))])
        self.sound_list[41] = self.assets["music_level42"]
        # Frames
        self.clock = pygame.time.Clock()
        self.fps = FPS
        self.seconds = 0
        # Levels
        self.wall_list = [[] for _ in range(self.nb_levels)]
        self.special_objects_list = [[] for _ in range(self.nb_levels)]
        self.spawn_point_list = [(None,None) for _ in range(self.nb_levels)]
        self.level_map_list = [None for _ in range(self.nb_levels)]
        self.level_names = LEVEL_NAMES
        self.level_colors = LEVEL_COLORS
        self.level_stars = LEVEL_REWARD
        self.level_configs = LEVEL_CONFIGS
        for level_nb in self.level_configs :
            self.level_configs[level_nb]["loaded"] = False # No level is loaded by default
        self.vision_radius = VISION_RADIUS
        # Progression
        self.nb_stars = 0
        self.level_time = ["--.--" for _ in range(self.nb_levels)]
        self.reward_collected = [False for _ in range(self.nb_levels)]
        # More
        self.center_x, self.center_y = self.screen.get_rect().centerx, self.screen.get_rect().centery
        # Text
        self.name_text, self.name_textpos = make_text(self.assets["font_main"],GAME_NAME,(255, 255, 255),self.center_x,self.center_y - 200)

        self.level_texts = [make_text(self.assets["font_main"],"Level "+str(nb+1),(255, 255, 255),self.center_x,self.center_y - 200) for nb in range(self.nb_levels)]
        for nb in range(self.nb_levels) :
            if nb in self.level_names :
                self.level_texts[nb-1] = make_text(self.assets["font_main"],self.level_names[nb],(255, 255, 255),self.center_x,self.center_y - 200)
        self.level_texts[66] = make_text(self.assets["font_main"],self.level_names[67],(0, 0, 0),self.center_x,self.center_y - 200)

        self.start_text, self.start_textpos = make_text(self.assets["font_main"],START_TEXT,(255, 255, 0),self.center_x,self.center_y)
        self.victory_text, self.victory_textpos = make_text(self.assets["font_main"],VICTORY_TEXT,(255, 255, 0),self.center_x,self.center_y//2)
        self.loading_text, self.loading_textpos = make_text(pygame.font.Font(None, 144),LOADING_TEXT,(255,255,255),self.center_x,self.center_y)
        self.stars_display, self.stars_displaypos = make_text(self.assets["font_medium"],str(self.nb_stars),(255,255,255),100,50)
        self.tutorial_fr, self.tutorial_en = [], []
        for i in range(len(TUTORIAL_FR_TEXT)):
            self.tutorial_fr.append(make_text(self.assets["font_small"],TUTORIAL_FR_TEXT[i],(255,255,255),self.center_x,self.tile_size*(i+2)))
        for i in range(len(TUTORIAL_EN_TEXT)):
            self.tutorial_en.append(make_text(self.assets["font_small"],TUTORIAL_EN_TEXT[i],(255,255,255),self.center_x,self.tile_size*(i+2)))
        # Player
        self.player = Player(self.center_x - 25/2, self.height - 50, PLAYER_SPEED, PLAYER_WIDTH)
        # Buttons
        self.button_start = Button(self.center_x, self.center_y, 400, 150,None)
        self.button_book_fr = Button(100, self.height -100, 100, 100, self.assets["tutorial_fr"])
        self.button_book_en = Button(250, self.height -100, 100, 100, self.assets["tutorial_en"])
        self.button_right_arrow = Button(self.width - 100, self.center_y-50, 50, 50, self.assets["right_arrow"])
        self.button_left_arrow = Button(100, self.center_y-50, 50, 50, self.assets["left_arrow"])
        self.button_right_arrow2 = Button(self.width - 100, self.center_y+50, 50, 50, self.assets["right_double_arrow"])
        self.button_left_arrow2 = Button(100, self.center_y+50, 50, 50, self.assets["left_double_arrow"])
        self.button_home = Button(50, 50, 75, 75, self.assets["home"])
        self.button_levels = [Button(self.center_x,self.center_y, 400, 250,None) for _ in range(self.nb_levels)]
        # Music play
        self.sound_active.set_volume(0.5)
        for s in self.sound_list :
            if s != None :
                s.set_volume(0.5)
        self.sound_active.play(loops=-1)

    
    def reset(self,new_maze=0):
        # Reset levels
        if self.state == "MAZE":
            for so in self.special_objects_list[self.maze-1]:
                if isinstance(so,Key) or isinstance(so,Door):
                    so.reset()
        if new_maze == 0:
            self.player.reset() #Player reset
            self.state = "MAIN MENU" #Return to main menu
            self.fade_to_black(self.width,self.height,25) #Transition screen
        else :
            self.assets["sfx_death"].play()
            self.load_sub_map(0)
        if self.vision_radius != VISION_RADIUS :
            self.vision_radius = VISION_RADIUS
        self.timer = pygame.time.get_ticks() #Timer reset

        # Reset menus
        self.maze = new_maze
        self.level_menu = 0

        if new_maze == 0:
            #Window resizing
            self.width, self.height = self.default_window_size
            self.screen = pygame.display.set_mode(self.default_window_size)
            self.center_x, self.center_y = self.screen.get_rect().centerx, self.screen.get_rect().centery
            #Refresh star counter
            self.stars_display, self.stars_displaypos = make_text(self.assets["font_medium"],str(self.nb_stars),(255,255,255),100,50)

            #Music
            if self.sound_active != self.assets["menu_music"] :
                if self.sound_active != None :
                    self.sound_active.stop()
                    self.sound_active.set_volume(0.5)
                self.sound_active = self.assets["menu_music"]
                self.sound_active.play(loops=-1)
                if not self.music_play :
                    self.sound_active.set_volume(0)
        else :
            self.player.respawn() #Player respawn

        # Time (reset finished)
        self.clock.tick()

    def press_left_arrow(self):
        if self.level_menu == 1 :
            self.level_menu = self.nb_levels
        else :
            self.level_menu -= 1

    def press_right_arrow(self):
        if self.level_menu == self.nb_levels :
            self.level_menu = 1
        else :
            self.level_menu += 1

    def create(self,type,x,y,width,height,color):
        if type == "rect" :
            obj = pygame.draw.rect(self.screen, color, (x, y, width, height))
            r,g,b = color
            self.screen.fill(pygame.Color(r,g,b),obj)
    
    def fade_to_black(self, width, height, speed=5):
        fade_surface = pygame.Surface((width, height))
        fade_surface.fill((0, 0, 0))
        #Modify alpha rapidly
        for alpha in range(0, 256, speed):
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.delay(28)

    def draw_fog(self):
            fog_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            fog_surf.fill((0, 0, 0, 255)) 

            for i in range(self.vision_radius, 0, -5):
                alpha = int(255 * (i / self.vision_radius)) # Visibility is better in the center
                pygame.draw.circle(fog_surf, (0, 0, 0, alpha), self.player.rect.center, i)
            
            self.screen.blit(fog_surf, (0, 0))

    def load_sub_map(self, map_index):
        config = self.level_configs[self.maze]
        map_file = config["file"][map_index]
        
        # Change layout
        layout = load_map(map_file)
        # Create maze
        current_maze = Maze(layout, config["tps"], self.player, self, map_index=map_index)
        
        # Modify global game values
        self.level_map_list[self.maze-1] = layout
        self.wall_list[self.maze-1] = current_maze.walls
        self.special_objects_list[self.maze-1] = current_maze.special_objs
        if self.vision_radius != VISION_RADIUS :
            self.vision_radius = VISION_RADIUS

        self.fade_to_black(self.width, self.height, 25) #Transition screen
        
        # Window dimension updating
        self.width = len(layout[0]) * self.tile_size
        self.height = len(layout) * self.tile_size
        os.environ['SDL_VIDEO_WINDOW_POS'] = "center"
        self.screen = pygame.display.set_mode((self.width, self.height))

        # Time
        self.clock.tick()

    def handle_events(self):
        for event in pygame.event.get():
            # Quit
            if event.type == QUIT:
                self.active = False
            elif event.type == KEYDOWN:
                # Music activate/desactivate [E]
                if self.sound_active != None and event.key == K_e:
                    self.time_display = 2.0
                    if self.music_play:
                        self.music_play = False
                        self.sound_active.set_volume(0)
                    else:
                        self.music_play = True
                        self.sound_active.set_volume(0.5)
                    self.music_animation = True
                
                # Game reset [ESCAPE]
                elif event.key == K_ESCAPE and not self.state == "MAIN MENU" :
                    self.reset()

                # Arrows (left and right) : change the current level selected in the menu
                elif self.state == "LEVEL MENU" :
                    if event.key == K_d:
                        self.press_right_arrow()
                    elif event.key == K_q:
                        self.press_left_arrow()

                # Restart run
                elif self.state == "MAZE" and event.key == K_r :
                    self.reset(self.maze)

            #Buttons
            elif event.type == MOUSEBUTTONDOWN :
                if event.button == 1 :
                    MOUSE_X, MOUSE_Y = pygame.mouse.get_pos() #Mouse position

                    if self.state == "LEVEL MENU": #Buttons in levels menu
                        
                        # Play button : Transfer the self.player to the right selected level from the menu
                        for level_id in range(len(self.button_levels)) :
                            if self.button_levels[level_id].is_pressed(MOUSE_X,MOUSE_Y) and self.level_menu == level_id+1:

                                # Game state changes
                                self.state = "MAZE"
                                self.level_menu = 0
                                self.maze = level_id + 1

                                self.assets["sfx_play"].play()

                                # Loading + Transition screen
                                self.fade_to_black(self.width, self.height, 25)
                                self.screen.blit(self.loading_text,self.loading_textpos)
                                pygame.display.flip()

                                if level_id+1 in self.level_configs : # Level needs to be not empty

                                    if not self.level_configs[level_id+1]["loaded"]: # When the level is not loaded
                                        # Create maze
                                        config = self.level_configs[level_id+1]
                                        layout = load_map(config["file"][0]) #The first map is being loaded                            
                                        current_maze = Maze(layout,config["tps"],self.player,self)

                                        # Modify global game values
                                        self.level_map_list[level_id] = layout
                                        self.wall_list[level_id] = current_maze.walls
                                        self.special_objects_list[level_id] = current_maze.special_objs
                                        self.spawn_point_list[level_id] = current_maze.spawn_point

                                        self.level_configs[level_id+1]["loaded"] = True # Level has been loaded

                                        self.fade_to_black(self.width, self.height, 25)

                                        # Time
                                        self.clock.tick()
                                    
                                    else : # When a level is loaded
                                        self.load_sub_map(0)

                                # Window dimension updating
                                if self.level_map_list[self.maze-1] != None :
                                    self.width, self.height = len(self.level_map_list[self.maze-1][0])*self.tile_size, len(self.level_map_list[self.maze-1])*self.tile_size
                                    os.environ['SDL_VIDEO_WINDOW_POS'] = "center"
                                    self.screen = pygame.display.set_mode((self.width, self.height))
                                    self.center_x, self.center_y = self.screen.get_rect().centerx, self.screen.get_rect().centery
                                    
                                    # Move player
                                    if self.spawn_point_list[self.maze-1][0] != None :
                                        x,y = self.spawn_point_list[self.maze-1]
                                        self.player.move_spawn(x,y)

                                #Timer starting
                                self.timer = pygame.time.get_ticks()
                                
                                # Music
                                self.sound_active.stop()
                                self.sound_active.set_volume(0.5)
                                self.sound_active = self.sound_list[level_id]
                                if self.sound_active != None :
                                    self.sound_active.play(loops=-1)
                                    if not self.music_play :
                                        self.sound_active.set_volume(0)
                        
                        # Arrows (left and right) : change the current level selected in the menu
                        if self.state == "LEVEL MENU" :
                            if self.button_right_arrow.is_pressed(MOUSE_X,MOUSE_Y):
                                self.press_right_arrow()
                            if self.button_left_arrow.is_pressed(MOUSE_X,MOUSE_Y):
                                self.press_left_arrow()
                            if self.button_right_arrow2.is_pressed(MOUSE_X,MOUSE_Y):
                                for _ in range(10):
                                    self.press_right_arrow()
                            if self.button_left_arrow2.is_pressed(MOUSE_X,MOUSE_Y):
                                for _ in range(10):
                                    self.press_left_arrow()
                            

                    elif self.state == "MAZE": # Buttons when a level is being played
                        pass # No buttons for now
                    
                    # Tutorial and victory menus : Home buttons
                    elif self.state == "FRENCH TUTORIAL" :
                        if self.button_home.is_pressed(MOUSE_X,MOUSE_Y):
                            self.state = "MAIN MENU"
                            self.fade_to_black(self.width,self.height,25)
                    
                    elif self.state == "ENGLISH TUTORIAL":
                        if self.button_home.is_pressed(MOUSE_X,MOUSE_Y):
                            self.state = "MAIN MENU"
                            self.fade_to_black(self.width,self.height,25)

                    elif self.state == "VICTORY MENU" :
                        if self.button_home.is_pressed(MOUSE_X,MOUSE_Y):
                            self.state = "MAIN MENU"
                            self.fade_to_black(self.width,self.height,25)
                            self.reset()

                    elif self.state == "MAIN MENU":
                        # Start button : goes to the level menu
                        if self.button_start.is_pressed(MOUSE_X, MOUSE_Y):
                            self.state = "LEVEL MENU"
                            self.level_menu = 1
                            self.fade_to_black(self.width,self.height,25)
                        
                        # "Book" buttons goes to their respectives menus
                        if self.button_book_fr.is_pressed(MOUSE_X,MOUSE_Y):
                            self.state = "FRENCH TUTORIAL"
                            self.fade_to_black(self.width, self.height, 25) 
                        
                        if self.button_book_en.is_pressed(MOUSE_X,MOUSE_Y):
                            self.state = "ENGLISH TUTORIAL"
                            self.fade_to_black(self.width, self.height, 25) 

    def update(self):
        raw_dt = self.clock.tick(self.fps) / 1000.0
        self.dt = min(raw_dt, 0.05) #Time tracking
        self.seconds = round((pygame.time.get_ticks() - self.timer) / 1000, 2)
        if self.state == "MAZE" :
            keys = pygame.key.get_pressed()

            #Basic movement
            dx, dy = 0, 0
            distance = self.player.speed * self.dt
            if keys[pygame.K_q] :
                dx -= distance
            if keys[pygame.K_d] :
                dx += distance
            if keys[pygame.K_z] :
                dy -= distance
            if keys[pygame.K_s] :
                dy += distance
            
            # Obstacles are walls and closed doors
            obstacles = list(self.wall_list[self.maze-1])
            for so in self.special_objects_list[self.maze-1]:
                if isinstance(so,Door) and not so.opened:
                    obstacles.append(so)

            #Moves the player only when it doesn't collide with a wall, closed door or the window border
            self.player.move(dx, dy, obstacles, self) 

            #Interacting with a special object
            portal_contact = False
            for so in self.special_objects_list[self.maze-1]:
                if isinstance(so,Portal) and so.is_touched(self.player): # Use portal
                    portal_contact = True
                    if self.player.can_teleport : # To prevent infinite teleportations
                        if so.dest_id != None and so.id != so.dest_id:
                            self.assets["sfx_teleport"].play()
                        self.player.use_portal(so,self.special_objects_list[self.maze-1])
                        self.player.can_teleport = False
                        break # To prevent errors

                if isinstance(so,Winpad) and so.is_touched(self.player) and not self.player.win: # Win
                    self.assets["sfx_win"].play()
                    self.player.victory()
                    self.fade_to_black(self.width,self.height,25) # Transition screen

                    # Stars
                    if not self.reward_collected[self.maze-1]:
                        self.reward_collected[self.maze-1] = True
                        self.nb_stars += self.level_stars[self.maze]

                    # Timer
                    if self.level_time[self.maze-1] == "--.--" or self.seconds < self.level_time[self.maze-1]: #Record
                        self.level_time[self.maze-1] = self.seconds

                    # Music
                    if self.sound_active != None :
                        self.sound_active.stop()
                    self.sound_active = self.assets["music_victory"]
                    self.sound_active.set_volume(0.5)
                    self.sound_active.play(loops=-1)
                    if not self.music_play :
                        self.sound_active.set_volume(0)

                    # Window resizing
                    self.width, self.height = self.default_window_size
                    self.screen = pygame.display.set_mode(self.default_window_size)
                    self.center_x, self.center_y = self.screen.get_rect().centerx, self.screen.get_rect().centery

                    # Game state update
                    self.state = "VICTORY MENU"
                    self.maze = 0

                    # Text
                    self.final_timer_text, self.final_timer_textpos = make_text(self.assets["font_main"],"Time : "+str(self.seconds),(255,255,255),self.center_x,self.center_y)

                if isinstance(so,Key) and not so.collected and so.is_touched(self.player): #Collect key
                    self.assets["sfx_key"].play()
                    self.player.pick_up_key(so)

                if isinstance(so,Door) and not so.opened and so.rect.inflate(10,10).colliderect(self.player.rect): # Open door if player has the keys 
                    if so.id in self.player.keys :
                        self.assets["sfx_unlock"].play() 
                        so.open()

                if isinstance(so,Trap) and so.is_touched(self.player): # Kill player and reset maze
                    self.reset(self.maze)
                    break # Map possibly changed

                if isinstance(so,Light) : # Increase player vision
                    if so.is_touched(self.player) and so.cooldown == 0.0: # Collect temporary torch
                        so.collect()
                        so.cooldown = TORCH_TIME
                        self.vision_radius += TORCH_EFFECT
                    # Update cooldown
                    if 0.0 < so.cooldown <= TORCH_TIME :
                        so.cooldown -= self.dt
                        if so.cooldown <= 0.0 :
                            so.cooldown = 0.0
                            self.vision_radius -= TORCH_EFFECT
                            so.respawn()

                if isinstance(so, SubMapPortal) and so.is_touched(self.player): # Load another sub map in the level
                    self.load_sub_map(so.target_map_index)
                    # Teleport player
                    self.assets["sfx_teleport"].play()
                    self.player.teleport(so.spawn_pos[0] + (self.player.width/2), so.spawn_pos[1] + (self.player.width/2))
                    break # Level updated, special_objects_list changed
        
            # Player exited a portal, he can now reenter one
            if not portal_contact :
                self.player.can_teleport = True
        
        # Update music animation
        if self.music_animation and self.time_display <= 0 :
                self.music_animation = False
        if not self.music_animation and self.time_display != 2.0 :
            self.time_display = 2.0

    def render(self):
        # Font color
        if self.maze == 67 or self.level_menu == 67:
            self.screen.fill(pygame.Color(255,255,255))
        else :
            self.screen.fill(pygame.Color(0,0,0))
        
        #Levels
        if self.state == "MAZE" :
            objs = self.special_objects_list[self.maze-1]
            walls = self.wall_list[self.maze-1]

            #Objects underneath the player
            for so in objs:
                if isinstance(so,Portal):
                    if so.dest_id == None : # Tp goes nowhere -> image gets darker
                        self.screen.blit(so.img2,(so.x, so.y))
                    else : 
                        self.screen.blit(so.img,(so.x, so.y))
                elif isinstance(so,Winpad):
                    self.screen.blit(so.img,(so.x,so.y))
                elif isinstance(so,Key) and not so.collected: #Display key if not collected
                    self.screen.blit(so.img, (so.x, so.y))
                elif isinstance(so,Door) and not so.opened: #Display door if not opened
                    color = KEY_COLORS.get(so.id.lower(), DEFAULT_KEY_COLOR)
                    self.create("rect",so.x1, so.y1, so.x2-so.x1, so.y2-so.y1,color)
                    pygame.draw.rect(self.screen, (0,0,0), so.rect, 2)
                elif isinstance(so,Trap):
                    self.screen.blit(so.img,(so.x,so.y))
                elif isinstance(so,Light) :
                    if not so.collected:
                        self.screen.blit(so.img,(so.x,so.y))
                elif isinstance(so,SubMapPortal):
                    self.screen.blit(so.img,(so.x,so.y))

            #The player
            self.create("rect",self.player.x, self.player.y, self.player.width, self.player.width,(255,0,0))

            #Objects above the player
            # Walls
            level_color = self.level_colors[self.maze]
            for wall in walls :
                self.create("rect",wall.x1, wall.y1, wall.x2-wall.x1, wall.y2-wall.y1,level_color)
            # Activate fog of war (if needed)
            if self.maze in self.level_configs and self.level_configs[self.maze]["fow"]:
                self.draw_fog()
            # Timer
            timer_text, timer_pos = make_text(self.assets["font_small"],"Time : "+str(self.seconds),(255,255,255),self.width-100,30)
            self.screen.blit(timer_text,timer_pos)

        #Level selecting menu
        elif self.state == "LEVEL MENU" :

            #Level font color
            if self.level_menu == 67 :
                font_color = invert_color(font_color)
            else :
                font_color = self.font_color
            inv_font_color = invert_color(font_color)
            #Current level color
            if self.level_menu in self.level_colors :
                level_color = self.level_colors[self.level_menu]
            else :
                level_color = self.second_font_color
            
            level = self.button_levels[self.level_menu-1]

            # Center play button
            self.create("rect",level.x, level.y, level.width, level.height,level_color)
            self.create("rect",level.x + 20, level.y + 20, level.width - 40, level.height - 40,font_color)

            # Level text display
            t, tpos = self.level_texts[self.level_menu-1]
            self.screen.blit(t, tpos)
            
            # PLAY text display
            play_text, play_textpos = make_text(self.assets["font_main"],PLAY_TEXT,level_color,self.center_x,self.center_y)
            self.screen.blit(play_text,play_textpos)

            # Stars
            if self.level_menu in self.level_stars :
                stars = self.level_stars[self.level_menu]
            else :
                stars = 0
            star_txt, star_pos = make_text(self.assets["font_medium"],": "+str(stars),inv_font_color,self.center_x + 20,self.center_y + 200)
            star_txt_width, _ = star_txt.get_size()
            self.screen.blit(self.assets["star"],(self.center_x-75,self.center_y+175))
            self.screen.blit(star_txt,(star_pos.left + star_txt_width/2 -25, star_pos.top))

            if self.reward_collected[self.level_menu-1]: #Checkmark
                self.screen.blit(self.assets["completed"],(self.center_x-75,self.center_y+175))

            # Timer
            rec_txt, rec_pos = make_text(self.assets["font_medium"],"Record : "+str(self.level_time[self.level_menu-1]),inv_font_color,self.center_x,self.center_y + 275)
            self.screen.blit(rec_txt,rec_pos)

            # Additional level text if level has a name
            if self.level_menu in self.level_names:
                levelindex_text, levelindex_textpos = make_text(self.assets["font_small"],"Level "+str(self.level_menu),inv_font_color,self.center_x,100)
                self.screen.blit(levelindex_text,levelindex_textpos)
            
            # Arrows
            for btn in [self.button_left_arrow, self.button_right_arrow, self.button_left_arrow2, self.button_right_arrow2]:
                self.screen.blit(btn.img, (btn.x, btn.y))

        #Tutorial menus
        elif self.state in ["FRENCH TUTORIAL", "ENGLISH TUTORIAL"]:
            texts = self.tutorial_fr if "FRENCH" in self.state else self.tutorial_en
            for t, tp in texts: self.screen.blit(t, tp)
            self.screen.blit(self.button_home.img, (self.button_home.x, self.button_home.y))

        #Victory menu
        elif self.state == "VICTORY MENU":
            self.create("rect",50,50,self.width-100,self.height-100,(255,255,0))
            self.create("rect",75,75,self.width-150,self.height-150,(0,0,0))
            self.screen.blit(self.victory_text,self.victory_textpos)
            self.screen.blit(self.button_home.img, (self.button_home.x,self.button_home.y))
            self.screen.blit(self.final_timer_text,self.final_timer_textpos)

        #Start menu
        elif self.state == "MAIN MENU":
            #The game name
            self.screen.blit(self.name_text, self.name_textpos)
            #Start button visual 
            self.create("rect",self.button_start.x, self.button_start.y, self.button_start.width, self.button_start.height,(255,255,0))
            self.create("rect",self.button_start.x + 10, self.button_start.y + 10, self.button_start.width - 20, self.button_start.height - 20,(0,0,0))
            self.screen.blit(self.start_text,self.start_textpos)

            #Tutorial menus
            self.screen.blit(self.button_book_fr.img,(self.button_book_fr.x,self.button_book_fr.y))
            self.screen.blit(self.button_book_en.img,(self.button_book_en.x,self.button_book_en.y))

            # Star counter
            stars_text_width, _ = self.stars_display.get_size()
            self.screen.blit(self.assets["star"],(25,25))
            self.screen.blit(self.stars_display,(self.stars_displaypos.left + stars_text_width/2, self.stars_displaypos.top))

        #Music display animation
        if self.music_animation:
            if self.music_play :
                self.screen.blit(self.assets["music_on"],(self.width - 75, 25))
            else :
                self.screen.blit(self.assets["music_off"],(self.width - 75, 25))
            self.time_display -= self.dt
        
        pygame.display.flip()