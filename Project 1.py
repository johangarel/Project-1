import os
import sys
import pygame
from pygame.locals import*
from math import*

### Path finding
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(*relative_path):
    return os.path.join(BASE_DIR, *relative_path)

### Text display function 
def make_text(font,txt,color,x,y):
    t = font.render(txt, 3, color)
    tpos = t.get_rect()
    tpos.centerx = x
    tpos.centery = y
    return t, tpos

### Game class
class Game :
    def __init__(self):
        # General stuff
        self.width = 960
        self.height = 740
        self.default_window_size = (960,740)
        self.nb_levels = 10
        self.tile_size = 40
        self.timer = 0
        self.recall_time = 0
        self.assets = {}
        # Menus
        self.active = True
        self.state = "MAIN MENU"
        self.maze = 0
        self.level_menu = 0
        # Music
        self.play_animation = False
        self.music_play = True
        self.time_display = 2.0
        self.sound_active = None
        # Frames
        self.clock = pygame.time.Clock()
        self.fps = 240
        # Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('MAZE 101 - v0.3.2')
        # More
        self.center_x, self.center_y = self.screen.get_rect().centerx, self.screen.get_rect().centery

        self.level_colors = [(255,0,255),
                             (255,125,0),
                             (0,255,0),
                             (105, 230, 90), 
                             (105, 155, 40), 
                             (195, 55, 145), 
                             (50, 185, 200), 
                             (50, 50, 250), 
                             (195, 50, 195), 
                             (225, 150, 55)]
        self.level_colors.extend([(255,255,255) for _ in range(self.nb_levels-len(self.level_colors))])
    
    def reset(self,new_maze=0):
        # Reset levels
        if self.state == "MAZE":
            for so in special_objects_list[game.maze-1]:
                if isinstance(so,Key) or isinstance(so,Door):
                    so.reset()
        if new_maze == 0:
            player.reset() #Player reset
            self.state = "MAIN MENU" #Return to main menu
        else :
            player.respawn() #Player respawn
        self.timer = pygame.time.get_ticks() #Timer reset

        # Reset menus
        self.maze = new_maze
        self.level_menu = 0

        fade_to_black(game.width,game.height,25) #Transition screen

        if new_maze == 0:
            #Window resizing
            self.width, self.height = self.default_window_size
            self.screen = pygame.display.set_mode(self.default_window_size)
            self.center_x, self.center_y = self.screen.get_rect().centerx, self.screen.get_rect().centery

            #Music
            if self.sound_active != game.assets["menu_music"] :
                if self.sound_active != None :
                    self.sound_active.stop()
                    self.sound_active.set_volume(0.5)
                self.sound_active = game.assets["menu_music"]
                self.sound_active.play()
                if not self.music_play :
                    self.sound_active.set_volume(0)
    
    def load_assets(self):
        self.assets = {"logo":pygame.image.load(get_path("assets","images","LOGO PROJECT 1.png")),
          "winpad":pygame.image.load(get_path("assets","images","_crown_new.png")),
          "tp1":pygame.image.load(get_path("assets","images","_tp_new.png")),
          "tp2":pygame.image.load(get_path("assets","images","_tp2_new.png")),
          "music_on":pygame.image.load(get_path("assets","images","MUSIC ON.png")),
          "music_off":pygame.image.load(get_path("assets","images","MUSIC OFF.png")),
          "home":pygame.image.load(get_path("assets","images","THE HOUSE.png")),
          "menu_music":pygame.mixer.Sound(get_path("assets","sounds","_cool_menu_music.mp3")),
          "music_victory":pygame.mixer.Sound(get_path("assets","sounds","_victory.mp3")),
          "music_level1":pygame.mixer.Sound(get_path("assets","sounds","_level1.mp3")),
          "music_level2":pygame.mixer.Sound(get_path("assets","sounds","_level2.mp3")),
          "music_level3":pygame.mixer.Sound(get_path("assets","sounds","_level3.mp3")),
          "music_level4":pygame.mixer.Sound(get_path("assets","sounds","_level4.mp3")),
          "right_arrow":pygame.image.load(get_path("assets","images","_arrow_right.png")),
          "left_arrow":pygame.image.load(get_path("assets","images","_arrow_left.png")),
          "tutorial_fr":pygame.image.load(get_path("assets","images","book_fr.png")),
          "tutorial_en":pygame.image.load(get_path("assets","images","book_en.png")),
          "trap":pygame.image.load(get_path("assets","images","trap.png")),
          "key":pygame.image.load(get_path("assets","images","key.png")),
          "font_main":pygame.font.Font(None, 144),
          "font_small":pygame.font.Font(None, 40)
          } 
    
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

### Player class
class Player:
    def __init__(self,x,y,speed,width):
        self.x = x
        self.y = y
        self.default_pos = (x,y)
        self.respawn_pos = (x,y)
        self.speed = speed
        self.width = width
        self.win = False
        self.keys = []
        self.rect = pygame.Rect(x,y,width,width)

    def modify_speed(self,speed):
        self.speed = speed
    
    def is_in_bounds_vertical(self,dy):
        return self.y + dy > 0 and self.y + self.width + dy < game.height

    def is_in_bounds_horizontal(self,dx):
        return self.x + dx > 0 and self.x + self.width + dx < game.width

    def can_move(self, dx, dy, walls):
        future_rect = pygame.Rect(self.x + dx, self.y + dy, self.width, self.width)
        
        for wall in walls:
            if future_rect.colliderect(wall.rect):
                return False
            
        if not self.is_in_bounds_horizontal(dx):
            return False
        if not self.is_in_bounds_vertical(dy):
            return False

        return True

    def move(self,dx,dy,walls):
        assert isinstance(walls,list)
        #horizontal
        if self.win :
            return
        if dx != 0:
            if self.can_move(dx, 0, walls):
                self.x += dx
            else: # To stick the player to the wall
                if dx > 0 :
                    direction = 1
                else :
                    direction = -1
                while self.can_move(direction, 0, walls) and abs(dx) > 1:
                    self.x += direction
                    dx -= direction
            

        #vertical
        if dy != 0:
            if self.can_move(0, dy, walls):
                self.y += dy
            else: # To stick the player to the wall
                if dy > 0 :
                    direction = 1
                else :
                    direction = -1
                while self.can_move(0, direction, walls) and abs(dy) > 1:
                    self.y += direction
                    dy -= direction
        
        self.rect = pygame.Rect(self.x,self.y,self.width,self.width)
    
    def get_pos(self):
        print(self.x,self.y)

    def move_spawn(self,x,y):
        if x != None and y != None :
            self.x = x
            self.y = y
            self.respawn_pos = (x,y)
            self.rect = pygame.Rect(self.x,self.y,self.width,self.width)

    def teleport(self,x,y):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x,self.y,self.width,self.width)

    def use_portal(self,portal):
        assert isinstance(portal,Portal)
        #Searching destination portal
        dest_portal = None
        for so in special_objects_list[game.maze-1]:
            if isinstance(so,Portal) :
                if portal.id != so.id and so.id == portal.dest_id :
                    dest_portal = so
                    break
        #Using the portal
        if dest_portal != None :
            self.x = dest_portal.x + portal.width // 2 - player.width//2
            self.y = dest_portal.y + portal.width // 2 - player.width//2
            self.rect = pygame.Rect(self.x,self.y,self.width,self.width)
    
    def victory(self):
        self.win = True

    def reset(self):
        self.win = False
        x,y = self.default_pos
        self.x = x
        self.y = y
        self.respawn_pos = (x,y)
        self.keys = []
        self.rect = pygame.Rect(self.x,self.y,self.width,self.width)

    def respawn(self):
        x,y = self.respawn_pos
        self.x = x
        self.y = y
        self.keys = []
        self.rect = pygame.Rect(self.x,self.y,self.width,self.width)

    def pick_up_key(self,key):
        assert isinstance(key,Key)
        self.keys.append(key.door_id)
        key.collect()
        

### Other objects classes
class Wall :
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + width, y + height

class Winpad:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.width = 50
        self.rect = pygame.Rect(x, y, self.width, self.width)
        self.img = game.assets["winpad"]

    def move(self,x,y):
        self.x = x
        self.y = y

    def is_touched(self,player):
        assert isinstance(player,Player)
        return self.x < player.x + player.width // 2 < self.x + self.width and self.y < player.y + player.width // 2 < self.y + self.width
    
class Portal:
    def __init__(self,x,y,id,destination_id):
        self.x, self.y = x,y
        self.width = 50
        self.rect = pygame.Rect(x, y, self.width, self.width)
        self.img = game.assets["tp1"]
        self.img2 = game.assets["tp2"]
        self.id = id
        self.dest_id = destination_id

    def move_tp_1(self,x,y):
        self.x, self.y = x, y

    def is_touched(self,player):
        assert isinstance(player,Player)
        return self.x < player.x + player.width // 2 < self.x + self.width and self.y < player.y + player.width // 2 < self.y + self.width

class Trap :
    def __init__(self,x,y):
        self.x,self.y = x,y
        self.width = game.tile_size
        self.rect = pygame.Rect(x,y,game.tile_size,game.tile_size)
        self.img = game.assets["trap"]
    
    def is_touched(self,player):
        assert isinstance(player,Player)
        return self.rect.colliderect(player.rect)

class Key :
    def __init__(self,x,y,id):
        self.x,self.y = x,y
        self.width = game.tile_size
        self.img = game.assets["key"]
        self.collected = False
        self.door_id = id

    def is_touched(self,player):
        assert isinstance(player,Player)
        return self.x < player.x + player.width // 2 < self.x + self.width and self.y < player.y + player.width // 2 < self.y + self.width
    
    def collect(self):
        self.collected = True
    
    def reset(self):
        self.collected = False

class Door :
    def __init__(self,x,y,width,height,id=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + width, y + height
        self.opened = False
        self.id = id.lower()
    
    def open(self):
        self.opened = True
    
    def reset(self):
        self.opened = False

class Button:
    def __init__(self,x,y,width,height,img):
        self.centerx = x
        self.centery = y
        self.width = width
        self.height = height
        self.x = self.centerx - self.width/2
        self.y = self.centery - self.height/2
        self.img = img
    
    def move(self,x,y):
        self.centerx = x
        self.centery = y
        self.x = self.centerx - self.width/2
        self.y = self.centery - self.height/2

    def is_pressed(self,x,y):
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

### Additional functions
# Function to place objects
def create(type,x,y,width,height,color):
    if type == "rect" :
        obj = pygame.draw.rect(game.screen, color, (x, y, width, height))
        r,g,b = color
        game.screen.fill(pygame.Color(r,g,b),obj)

# Transition screen function
def fade_to_black(width, height, speed=5):
    fade_surface = pygame.Surface((width, height))
    fade_surface.fill((0, 0, 0))
    #Modify alpha rapidly
    for alpha in range(0, 256, speed):
        fade_surface.set_alpha(alpha)
        game.screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(28)

# Load level from file
def load_map(filename):
    path = get_path("levels",filename)
    level_map = []
    file = open(path,"r")
    for line in file :
        level_map.append(line.rstrip('\n'))
    return level_map

# Optimise walls function
def optimise_walls(walls):
    if not walls:
        return [] #When a level is empty

    #Extract rectangles
    rects = [w.rect.copy() for w in walls]

    #Honrizontal wall fusion
    fusion_h = True
    while fusion_h:
        fusion_h = False
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                r1 = rects[i]
                r2 = rects[j]
                if r1.y == r2.y and r1.height == r2.height: #Same Y level and same height
                    if r1.x + r1.width == r2.x or r2.x + r2.width == r1.x: #Walls colliding each other
                        new_rect = r1.union(r2)
                        rects.pop(j)
                        rects.pop(i)
                        rects.append(new_rect)
                        fusion_h = True
                        break
            if fusion_h: 
                break

    #Vertical wall fusion
    fusion_v = True
    while fusion_v:
        fusion_v = False
        for i in range(len(rects)):
            for j in range(i + 1, len(rects)):
                r1 = rects[i]
                r2 = rects[j]
                if r1.x == r2.x and r1.width == r2.width: #Same X level and same width
                    if r1.y + r1.height == r2.y or r2.y + r2.height == r1.y: #Walls colliding each other
                        new_rect = r1.union(r2)
                        rects.pop(j)
                        rects.pop(i)
                        rects.append(new_rect)
                        fusion_v = True
                        break
            if fusion_v: 
                break

    #New walls into a new list
    return [Wall(r.x, r.y, r.width, r.height) for r in rects]

#Build level function
def build_level(layout,tp_order):
    walls = []
    special_objs = []
    spawn_point = player.default_pos

    for row_id, row in enumerate(layout): 
        for col_id, char in enumerate(row):
            x = col_id * game.tile_size
            y = row_id * game.tile_size

            if char == "W":  # Wall

                #Conditions (Wall nearby)
                banned_letters = ["P","V"]
                cond_a = row_id < len(layout)-1 and layout[row_id + 1][col_id].isupper() and not layout[row_id + 1][col_id] in banned_letters # Down
                cond_b = row_id > 0 and layout[row_id - 1][col_id].isupper() and not layout[row_id - 1][col_id] in banned_letters # Up
                cond_c = col_id < len(row)-1 and layout[row_id][col_id + 1].isupper() and not layout[row_id][col_id + 1] in banned_letters # Right
                cond_d = col_id > 0 and layout[row_id][col_id - 1].isupper() and not layout[row_id][col_id - 1] in banned_letters # Right

                #Connecting walls
                if cond_a :
                    walls.append(Wall(x + game.tile_size/2 - 5, y + game.tile_size/2, 10, game.tile_size/2))
                if cond_b :
                    walls.append(Wall(x + game.tile_size/2 - 5, y, 10, game.tile_size/2))
                if cond_c :
                    walls.append(Wall(x + game.tile_size/2, y + game.tile_size/2 - 5, game.tile_size/2, 10))
                if cond_d :
                    walls.append(Wall(x, y + game.tile_size/2 - 5, game.tile_size/2, 10))
                walls.append(Wall(x + game.tile_size/2 - 5, y + game.tile_size/2 - 5, 10, 10))

            elif char == "P":  # Player Start
                spawn_point = (x,y)
            elif char == "V":  # Victory
                special_objs.append(Winpad(x, y))
            elif char == "T": # Trap
                special_objs.append(Trap(x,y))
            elif char.isdigit(): # Teleport
                special_objs.append(Portal(x,y,int(char),tp_order[int(char)]))
            elif char.islower(): # Key
                special_objs.append(Key(x,y,char))
            elif char.isupper(): # Door
                #Conditions (Wall nearby) (again)
                cond_a = (0 < row_id < len(layout)-1) and (layout[row_id + 1][col_id] == 'W' ) and (layout[row_id - 1][col_id] == 'W' ) # Vertical
                cond_b = (0 < col_id < len(row)-1) and (layout[row_id][col_id + 1] == 'W' ) and (layout[row_id][col_id - 1] == 'W' ) # Horizontal
                #Connect to walls
                if cond_a :
                    special_objs.append(Door(x + game.tile_size/2 - 5, y, 10, game.tile_size,char))
                if cond_b :
                    special_objs.append(Door(x, y + game.tile_size/2 - 5, game.tile_size, 10,char))
                
    walls = optimise_walls(walls)
    return walls, special_objs, spawn_point

### Initialise game
game = Game()
game.load_assets()

loading_text, loading_textpos = make_text(pygame.font.Font(None, 144),"Loading...",(255,255,255),game.center_x,game.center_y)
game.screen.blit(loading_text,loading_textpos) # Loading screen

pygame.display.set_icon(game.assets["logo"])
pygame.display.flip()

### Text display 
gamename_text, gamename_textpos = make_text(game.assets["font_main"],"MAZE 101",(255, 255, 255),game.center_x,game.center_y - 200)
levels_text = [make_text(game.assets["font_main"],"Level "+str(nb+1),(255, 255, 255),game.center_x,game.center_y - 200) for nb in range(game.nb_levels)]
start_text, start_textpos = make_text(game.assets["font_main"],"START",(255, 255, 0),game.center_x,game.center_y)
victory_text, victory_textpos = make_text(game.assets["font_main"],"You win !",(255, 255, 0),game.center_x,game.center_y//2)

# Tutorial (both languages)
tutorial_fr = [make_text(game.assets["font_small"],"Se déplacer : ZQSD",(255,255,255),game.center_x,game.tile_size*2),
               make_text(game.assets["font_small"],"Couper/Réactiver la musique : E",(255,255,255),game.center_x,game.tile_size*3),
               make_text(game.assets["font_small"],"Revenir au menu principal : Echap",(255,255,255),game.center_x,game.tile_size*4),
               make_text(game.assets["font_small"],"Changer le niveau dans le menu : Q/D",(255,255,255),game.center_x,game.tile_size*5),
               make_text(game.assets["font_small"],"Réinitialiser le labyrinthe : R",(255,255,255),game.center_x,game.tile_size*6)]

tutorial_en = [make_text(game.assets["font_small"],"Move : ZQSD",(255,255,255),game.center_x,game.tile_size*2),
               make_text(game.assets["font_small"],"Mute/Unmute the music : E",(255,255,255),game.center_x,game.tile_size*3),
               make_text(game.assets["font_small"],"Go back to the main menu : Escape",(255,255,255),game.center_x,game.tile_size*4),
               make_text(game.assets["font_small"],"Change level in menu : Q/D",(255,255,255),game.center_x,game.tile_size*5),
               make_text(game.assets["font_small"],"Reset maze : R",(255,255,255),game.center_x,game.tile_size*6)]

### Objects
# Player
player = Player(game.center_x - 25/2, game.height - 50, 500, 25)

# Maze building

LEVEL_1_MAP = load_map("level1.txt")
LEVEL_1_TP = [1,None,3,None,5,None]
LEVEL_1 = build_level(LEVEL_1_MAP,LEVEL_1_TP)

LEVEL_2_MAP = load_map("level2.txt")
LEVEL_2_TP = [None,0,1,0,3,0]
LEVEL_2 = build_level(LEVEL_2_MAP,LEVEL_2_TP)

wall_list = [LEVEL_1[0],LEVEL_2[0]]
wall_list.extend([[] for _ in range(game.nb_levels-len(wall_list))])

special_objects_list = [LEVEL_1[1],LEVEL_2[1]]
special_objects_list.extend([[] for _ in range(game.nb_levels-len(special_objects_list))])

spawn_point_list = [LEVEL_1[2],LEVEL_2[2]]
spawn_point_list.extend([(None,None) for _ in range(game.nb_levels-len(spawn_point_list))])

LEVEL_MAP_LIST = [LEVEL_1_MAP,LEVEL_2_MAP]
LEVEL_MAP_LIST.extend(None for _ in range(game.nb_levels-len(LEVEL_MAP_LIST)))

# Buttons (Menu)
start = Button(game.center_x, game.center_y, 400, 150,None)
book_fr = Button(100, game.height -100, 100, 100, game.assets["tutorial_fr"])
book_en = Button(250, game.height -100, 100, 100, game.assets["tutorial_en"])
right_arrow = Button(game.width - 100, game.center_y, 50, 50, game.assets["right_arrow"])
left_arrow = Button(100, game.center_y, 50, 50, game.assets["left_arrow"])
home = Button(50, 50, 75, 75, game.assets["home"])
level_buttons = [Button(game.center_x,game.center_y, 400, 250,None) for _ in range(game.nb_levels)]

### Music 
game.sound_active = game.assets["menu_music"]
sound_list = [game.assets["music_level1"], game.assets["music_level2"], game.assets["music_level3"], game.assets["music_level4"]]
sound_list.extend([None for _ in range(game.nb_levels-len(sound_list))])

game.sound_active.set_volume(0.5)
for s in sound_list :
    if s != None :
        s.set_volume(0.5)

game.sound_active.play()

### EVENT LOOP
while game.active:
    dt = game.clock.tick(game.fps) / 1000.0 #Time tracking

    for event in pygame.event.get():
        # Quit
        if event.type == QUIT:
            game.active = False
        elif event.type == KEYDOWN:
            # Music activate/desactivate [E]
            if game.sound_active != None and event.key == K_e:
                if game.music_play:
                    game.music_play = False
                    game.sound_active.set_volume(0)
                else:
                    game.music_play = True
                    game.sound_active.set_volume(0.5)
                game.play_animation = True
            
            # Game reset [ESCAPE]
            elif event.key == K_ESCAPE and not game.state == "MAIN MENU" :
                game.reset()

            # Arrows (left and right) : change the current level selected in the menu
            elif game.state == "LEVEL MENU" :
                if event.key == K_d:
                    game.press_right_arrow()
                elif event.key == K_q:
                    game.press_left_arrow()

            elif game.state == "MAZE" and event.key == K_r :
                game.reset(game.maze)

        #Buttons
        elif event.type == MOUSEBUTTONDOWN :
            if event.button == 1 :
                MOUSE_X, MOUSE_Y = pygame.mouse.get_pos() #Mouse position

                if game.state == "LEVEL MENU": #Buttons in levels menu
                    
                    # Play button : Transfer the player to the right selected level from the menu
                    for level_id in range(len(level_buttons)) :
                        if level_buttons[level_id].is_pressed(MOUSE_X,MOUSE_Y) and game.level_menu == level_id+1:
                            game.state = "MAZE"
                            game.level_menu = 0
                            game.maze = level_id + 1

                            fade_to_black(game.width, game.height, 25) #Transition screen

                            # Window dimension updating
                            if LEVEL_MAP_LIST[game.maze-1] != None :
                                game.width, game.height = len(LEVEL_MAP_LIST[game.maze-1][0])*game.tile_size, len(LEVEL_MAP_LIST[game.maze-1])*game.tile_size
                                game.screen = pygame.display.set_mode((game.width, game.height))
                                game.center_x, game.center_y = game.screen.get_rect().centerx, game.screen.get_rect().centery
                                
                                # Move player
                                if spawn_point_list[game.maze-1][0] != None :
                                    x,y = spawn_point_list[game.maze-1]
                                    player.move_spawn(x,y)

                            #Timer starting
                            game.timer = pygame.time.get_ticks()
                            
                            # Music
                            game.sound_active.stop()
                            game.sound_active.set_volume(0.5)
                            game.sound_active = sound_list[level_id]
                            if game.sound_active != None :
                                game.sound_active.play()
                                if not game.music_play :
                                    game.sound_active.set_volume(0)
                    
                    # Arrows (left and right) : change the current level selected in the menu
                    if game.state == "LEVEL MENU" :
                        if right_arrow.is_pressed(MOUSE_X,MOUSE_Y):
                            game.press_right_arrow()
                        if left_arrow.is_pressed(MOUSE_X,MOUSE_Y):
                            game.press_left_arrow()
                        

                elif game.state == "MAZE": # Buttons when a level is being played
                    pass
                
                elif game.state == "FRENCH TUTORIAL" :
                    if home.is_pressed(MOUSE_X,MOUSE_Y):
                        game.state = "MAIN MENU"
                        fade_to_black(game.width,game.height,25)
                
                elif game.state == "ENGLISH TUTORIAL":
                    if home.is_pressed(MOUSE_X,MOUSE_Y):
                        game.state = "MAIN MENU"
                        fade_to_black(game.width,game.height,25)

                elif game.state == "VICTORY MENU" :
                    if home.is_pressed(MOUSE_X,MOUSE_Y):
                        game.state = "MAIN MENU"
                        fade_to_black(game.width,game.height,25)
                        game.reset()

                elif game.state == "MAIN MENU":
                    # Start button : goes to the level menu
                    if start.is_pressed(MOUSE_X, MOUSE_Y):
                        game.state = "LEVEL MENU"
                        game.level_menu = 1
                        fade_to_black(game.width,game.height,25)
                    
                    if book_fr.is_pressed(MOUSE_X,MOUSE_Y):
                        game.state = "FRENCH TUTORIAL"
                        fade_to_black(game.width, game.height, 25) 
                    
                    if book_en.is_pressed(MOUSE_X,MOUSE_Y):
                        game.state = "FRENCH TUTORIAL"
                        fade_to_black(game.width, game.height, 25) 



    ### PLAYER MOVEMENT AND INTERACTIONS
    if game.state == "MAZE" :
        keys = pygame.key.get_pressed()

        #Basic movement
        dx, dy = 0, 0
        distance = player.speed * dt
        if keys[pygame.K_q] :
            dx -= distance
        if keys[pygame.K_d] :
            dx += distance
        if keys[pygame.K_z] :
            dy -= distance
        if keys[pygame.K_s] :
            dy += distance
        
        # Obstacles are walls and closed doors
        obstacles = list(wall_list[game.maze-1])
        for so in special_objects_list[game.maze-1]:
            if isinstance(so,Door) and not so.opened:
                obstacles.append(so)

        #Moves the player only when it doesn't collide with a wall, closed door or the window border
        player.move(dx, dy, obstacles) 

        #Interacting with a special object
        for so in special_objects_list[game.maze-1]:
            if isinstance(so,Portal) and so.is_touched(player): # Use portal
                if game.recall_time <= 0:
                    player.use_portal(so)
                    game.recall_time = 1.0
            if isinstance(so,Winpad) and so.is_touched(player) and not player.win: # Win
                player.victory()
                fade_to_black(game.width,game.height,25)

                # Music
                if game.sound_active != None :
                    game.sound_active.stop()
                game.sound_active = game.assets["music_victory"]
                game.sound_active.set_volume(0.5)
                game.sound_active.play()
                if not game.music_play :
                    game.sound_active.set_volume(0)

                #Window resizing
                game.width, game.height = game.default_window_size
                game.screen = pygame.display.set_mode(game.default_window_size)
                game.center_x, game.center_y = game.screen.get_rect().centerx, game.screen.get_rect().centery

                # Menu update
                game.state = "VICTORY MENU"
                game.maze = 0

                # Text
                final_timer_text, final_timer_textpos = make_text(game.assets["font_main"],"Time : "+str(seconds),(255,255,255),game.center_x,game.center_y)

            if isinstance(so,Key) and not so.collected and so.is_touched(player): #Collect key
                player.pick_up_key(so)
            if isinstance(so,Door) and not so.opened and so.rect.inflate(10,10).colliderect(player.rect): # Open door
                if so.id in player.keys :
                    so.open()
            if isinstance(so,Trap) and so.is_touched(player):
                game.reset(game.maze)
        

    ### VISUALS
    game.screen.fill(pygame.Color(0,0,0))
    #Levels
    if game.state == "MAZE" :

        #Objects underneath the player
        for so in special_objects_list[game.maze-1]:
            if isinstance(so,Portal):
                if so.dest_id == None :
                    game.screen.blit(so.img2,(so.x, so.y))
                else :
                    game.screen.blit(so.img,(so.x, so.y))
            elif isinstance(so,Winpad):
                game.screen.blit(so.img,(so.x,so.y))
            elif isinstance(so,Key) and not so.collected:
                game.screen.blit(so.img,(so.x,so.y))
            elif isinstance(so,Door) and not so.opened:
                create("rect",so.x1, so.y1, so.x2-so.x1, so.y2-so.y1,(255,255,0))
            elif isinstance(so,Trap):
                game.screen.blit(so.img,(so.x,so.y))

        #The player
        create("rect",player.x, player.y, player.width, player.width,(255,0,0))

        #Objects above the player
        # Walls
        for wall in wall_list[game.maze-1]:
            create("rect",wall.x1, wall.y1, wall.x2-wall.x1, wall.y2-wall.y1,game.level_colors[game.maze-1])
        # Timer
        else :
            seconds = round((pygame.time.get_ticks() - game.timer) / 1000, 2)
            timer_text, timer_pos = make_text(game.assets["font_small"],"Time : "+str(seconds),(255,255,255),game.width-100,30)
            game.screen.blit(timer_text,timer_pos)

    #Level selecting menu
    elif game.state == "LEVEL MENU" :
        for k in range(game.nb_levels + 1) :
            if k == game.level_menu :
                #Current level
                level = level_buttons[k-1]
                #Center play button
                create("rect",level.x, level.y, level.width, level.height,game.level_colors[k-1])
                create("rect",level.x + 20, level.y + 20, level.width - 40, level.height - 40,(0,0,0))
                #Display the right level text
                t, tpos = levels_text[k-1]
                game.screen.blit(t, tpos)
                #Create the "PLAY" text here matching with the current level color
                play_text, play_textpos = make_text(game.assets["font_main"],"PLAY",game.level_colors[k-1],game.center_x,game.center_y)
        #Display arrows
        game.screen.blit(left_arrow.img,(left_arrow.x,left_arrow.y))
        game.screen.blit(right_arrow.img,(right_arrow.x,right_arrow.y))
        #Play text in the center
        game.screen.blit(play_text,play_textpos)

    #Tutorial menus
    elif game.state == "FRENCH TUTORIAL" :
        for text, textpos in tutorial_fr :
            game.screen.blit(text,textpos)
            game.screen.blit(home.img, (home.x,home.y))
    
    elif game.state == "ENGLISH TUTORIAL" :
        for text, textpos in tutorial_en :
            game.screen.blit(text,textpos)
            game.screen.blit(home.img, (home.x,home.y))

    #Victory menu
    elif game.state == "VICTORY MENU":
        create("rect",50,50,game.width-100,game.height-100,(255,255,0))
        create("rect",75,75,game.width-150,game.height-150,(0,0,0))
        game.screen.blit(victory_text,victory_textpos)
        game.screen.blit(home.img, (home.x,home.y))
        game.screen.blit(final_timer_text,final_timer_textpos)

    #Start menu
    elif game.state == "MAIN MENU":
        #The game name
        game.screen.blit(gamename_text, gamename_textpos)
        #Start button visual 
        create("rect",start.x, start.y, start.width, start.height,(255,255,0))
        create("rect",start.x + 10, start.y + 10, start.width - 20, start.height - 20,(0,0,0))
        game.screen.blit(start_text,start_textpos)

        #Tutorial menus
        game.screen.blit(book_fr.img,(book_fr.x,book_fr.y))
        game.screen.blit(book_en.img,(book_en.x,book_en.y))

    #Music display
    if game.play_animation:
        if game.music_play :
            game.screen.blit(game.assets["music_on"],(game.width - 75, 25))
        else :
            game.screen.blit(game.assets["music_off"],(game.width - 75, 25))
        game.time_display -= dt
        if game.time_display <= 0 :
            game.play_animation = False
    elif game.time_display != 100 :
        game.time_display = 2.0
    
    pygame.display.flip()
    if game.recall_time > 0:
        game.recall_time -= dt

pygame.quit()