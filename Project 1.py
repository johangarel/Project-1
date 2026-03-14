import os
import sys
import pygame
from pygame.locals import*
from math import*

### Path finding
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_path(*relative_path):
    return os.path.join(BASE_DIR, "assets", *relative_path)

### Text display function 
def make_text(font,txt,color,x,y):
    t = font.render(txt, 3, color)
    tpos = t.get_rect()
    tpos.centerx = x
    tpos.centery = y
    return t, tpos

### Global variables
# General stuff
WIDTH = 960
HEIGHT = 740
DEFAULT_WINDOW_SIZE = (960,740)
PLAYER_SPEED = 500
NB_LEVELS = 10
TILE_SIZE = 40
TIMER = 0
RECALL_TIME = 0

# Menus
game_active = True
maze_active = 0
level_menu_active = 0
tutorial_fr_menu = False
tutorial_en_menu = False
victory_menu = False

# Music
play_animation = False
music_play = True
time_display = 1000

# Stable frame per second
clock = pygame.time.Clock()
fps = 240

# Level coloring
LEVEL_COLORS = [(255,0,255),
                (255,125,0),
                (0,255,0),
                (105, 230, 90), 
                (105, 155, 40), 
                (195, 55, 145), 
                (50, 185, 200), 
                (50, 50, 250), 
                (195, 50, 195), 
                (225, 150, 55)]
LEVEL_COLORS.extend([(255,255,255) for _ in range(NB_LEVELS-len(LEVEL_COLORS))])

### Initialise screen
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('MAZE 101 - v0.0.3.1')

# Additional global variables
CENTER_X, CENTER_Y = screen.get_rect().centerx, screen.get_rect().centery 
ASSETS = {"logo":pygame.image.load(get_path("images","LOGO PROJECT 1.png")),
          "winpad":pygame.image.load(get_path("images","_crown_new.png")),
          "tp1":pygame.image.load(get_path("images","_tp_new.png")),
          "tp2":pygame.image.load(get_path("images","_tp2_new.png")),
          "music_on":pygame.image.load(get_path("images","MUSIC ON.png")),
          "music_off":pygame.image.load(get_path("images","MUSIC OFF.png")),
          "home":pygame.image.load(get_path("images","THE HOUSE.png")),
          "menu_music":pygame.mixer.Sound(get_path("sounds","_cool_menu_music.mp3")),
          "music_victory":pygame.mixer.Sound(get_path("sounds","_victory.mp3")),
          "music_level1":pygame.mixer.Sound(get_path("sounds","_level1.mp3")),
          "music_level2":pygame.mixer.Sound(get_path("sounds","_level2.mp3")),
          "music_level3":pygame.mixer.Sound(get_path("sounds","_level3.mp3")),
          "music_level4":pygame.mixer.Sound(get_path("sounds","_level4.mp3")),
          "right_arrow":pygame.image.load(get_path("images","_arrow_right.png")),
          "left_arrow":pygame.image.load(get_path("images","_arrow_left.png")),
          "tutorial_fr":pygame.image.load(get_path("images","book_fr.png")),
          "tutorial_en":pygame.image.load(get_path("images","book_en.png")),
          "trap":pygame.image.load(get_path("images","trap.png")),
          "key":pygame.image.load(get_path("images","key.png")),
          "font_main":pygame.font.Font(None, 144),
          "font_small":pygame.font.Font(None, 40)
          } 

#Loading screen
loading_text, loading_textpos = make_text(pygame.font.Font(None, 144),"Loading...",(255,255,255),CENTER_X,CENTER_Y)
screen.blit(loading_text,loading_textpos)

pygame.display.set_icon(ASSETS["logo"])
pygame.display.flip()

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
        return player.y + dy > 0 and player.y + player.width + dy < HEIGHT

    def is_in_bounds_horizontal(self,dx):
        return player.x + dx > 0 and player.x + player.width + dx < WIDTH

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
        if player.win :
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
        global maze_active
        #Searching destination portal
        dest_portal = None
        for so in special_objects_list[maze_active-1]:
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
        self.img = ASSETS["winpad"]

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
        self.img = ASSETS["tp1"]
        self.img2 = ASSETS["tp2"]
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
        self.width = TILE_SIZE
        self.rect = pygame.Rect(x,y,TILE_SIZE,TILE_SIZE)
        self.img = ASSETS["trap"]
    
    def is_touched(self,player):
        assert isinstance(player,Player)
        return self.rect.colliderect(player.rect)

class Key :
    def __init__(self,x,y,id):
        self.x,self.y = x,y
        self.width = TILE_SIZE
        self.img = ASSETS["key"]
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
    global screen
    if type == "rect" :
        obj = pygame.draw.rect(screen, color, (x, y, width, height))
        r,g,b = color
        screen.fill(pygame.Color(r,g,b),obj)

# Arrows functions in menu
def press_left_arrow():
    global NB_LEVELS, level_menu_active
    if level_menu_active == 1 :
        level_menu_active = NB_LEVELS
    else :
        level_menu_active -= 1

def press_right_arrow():
    global NB_LEVELS, level_menu_active
    if level_menu_active == NB_LEVELS :
        level_menu_active = 1
    else :
        level_menu_active += 1

# Transition screen function
def fade_to_black(width, height, speed=5):
    fade_surface = pygame.Surface((width, height))
    fade_surface.fill((0, 0, 0))
    #Modify alpha rapidly
    for alpha in range(0, 256, speed):
        fade_surface.set_alpha(alpha)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(28)

# Reset function
def reset(new_maze=0):
    global maze_active, level_menu_active, sound_active, screen, CENTER_X, CENTER_Y, WIDTH, HEIGHT, tutorial_en_menu, tutorial_fr_menu, TIMER, victory_menu

    # Reset levels
    if maze_active:
        for so in special_objects_list[maze_active-1]:
            if isinstance(so,Key) or isinstance(so,Door):
                so.reset()
    if new_maze == 0:
        player.reset() #Player reset
        TIMER = 0 #Timer reset
    else :
        player.respawn()

    # Reset menus
    maze_active = new_maze
    level_menu_active = 0
    tutorial_en_menu = False
    tutorial_fr_menu = False
    victory_menu = False

    fade_to_black(WIDTH,HEIGHT,20) #Transition screen

    if new_maze == 0:
        #Window resizing
        WIDTH, HEIGHT = DEFAULT_WINDOW_SIZE
        screen = pygame.display.set_mode(DEFAULT_WINDOW_SIZE)
        CENTER_X, CENTER_Y = screen.get_rect().centerx, screen.get_rect().centery

        #Music
        if sound_active != ASSETS["menu_music"] :
            if sound_active != None :
                sound_active.stop()
                sound_active.set_volume(0.5)
            sound_active = ASSETS["menu_music"]
            sound_active.play()
            if not music_play :
                sound_active.set_volume(0)

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
            x = col_id * TILE_SIZE
            y = row_id * TILE_SIZE

            if char == "W":  # Wall

                #Conditions (Wall nearby)
                banned_letters = ["P","V"]
                if row_id < len(layout)-1 :
                    letter = layout[row_id + 1][col_id]
                    cond_a = (letter.isupper() and not letter in banned_letters) #Down
                else :
                    cond_a = False
                if row_id > 0 :
                    letter = layout[row_id - 1][col_id]
                    cond_b = (letter.isupper() and not letter in banned_letters) #Up
                else :
                    cond_b = False
                if col_id < len(layout[0])-1 :
                    letter = layout[row_id][col_id + 1]
                    cond_c = (letter.isupper() and not letter in banned_letters) #Right
                else :
                    cond_c = False
                if col_id > 0:
                    letter = layout[row_id][col_id - 1]
                    cond_d = (letter.isupper() and not letter in banned_letters) #Left
                else :
                    cond_d = False
                

                #Connecting walls
                if cond_a :
                    walls.append(Wall(x + TILE_SIZE/2 - 5, y + TILE_SIZE/2, 10, TILE_SIZE/2))
                if cond_b :
                    walls.append(Wall(x + TILE_SIZE/2 - 5, y, 10, TILE_SIZE/2))
                if cond_c :
                    walls.append(Wall(x + TILE_SIZE/2, y + TILE_SIZE/2 - 5, TILE_SIZE/2, 10))
                if cond_d :
                    walls.append(Wall(x, y + TILE_SIZE/2 - 5, TILE_SIZE/2, 10))
                walls.append(Wall(x + TILE_SIZE/2 - 5, y + TILE_SIZE/2 - 5, 10, 10))

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
                if row_id < len(layout)-1 :
                    cond_a = (layout[row_id + 1][col_id] == 'W' ) #Down
                else :
                    cond_a = False
                if row_id > 0 :
                    cond_b = (layout[row_id - 1][col_id] == 'W' ) #Up
                else :
                    cond_b = False
                if col_id < len(layout[0])-1 :
                    cond_c = (layout[row_id][col_id + 1] == 'W' ) #Right
                else :
                    cond_c = False
                if col_id > 0:
                    cond_d = (layout[row_id][col_id - 1] == 'W' ) #Left
                else :
                    cond_d = False
                #Connect to walls
                if cond_a :
                    special_objs.append(Door(x + TILE_SIZE/2 - 5, y + TILE_SIZE/2, 10, TILE_SIZE/2,char))
                if cond_b :
                    special_objs.append(Door(x + TILE_SIZE/2 - 5, y, 10, TILE_SIZE/2,char))
                if cond_c :
                    special_objs.append(Door(x + TILE_SIZE/2, y + TILE_SIZE/2 - 5, TILE_SIZE/2, 10,char))
                if cond_d :
                    special_objs.append(Door(x, y + TILE_SIZE/2 - 5, TILE_SIZE/2, 10,char))
                
    walls = optimise_walls(walls)
    return walls, special_objs, spawn_point

### Text display 

gamename_text, gamename_textpos = make_text(ASSETS["font_main"],"MAZE 101",(255, 255, 255),CENTER_X,CENTER_Y - 200)
levels_text = [make_text(ASSETS["font_main"],"Level "+str(nb+1),(255, 255, 255),CENTER_X,CENTER_Y - 200) for nb in range(NB_LEVELS)]
start_text, start_textpos = make_text(ASSETS["font_main"],"START",(255, 255, 0),CENTER_X,CENTER_Y)
victory_text, victory_textpos = make_text(ASSETS["font_main"],"You win !",(255, 255, 0),CENTER_X,CENTER_Y//2)

# Tutorial (both languages)
tutorial_fr = [make_text(ASSETS["font_small"],"Se déplacer : ZQSD",(255,255,255),CENTER_X,TILE_SIZE*2),
               make_text(ASSETS["font_small"],"Couper/Réactiver la musique : E",(255,255,255),CENTER_X,TILE_SIZE*3),
               make_text(ASSETS["font_small"],"Revenir au menu principal : Echap",(255,255,255),CENTER_X,TILE_SIZE*4),
               make_text(ASSETS["font_small"],"Changer le niveau dans le menu : Q/D",(255,255,255),CENTER_X,TILE_SIZE*5)]

tutorial_en = [make_text(ASSETS["font_small"],"Move : ZQSD",(255,255,255),CENTER_X,TILE_SIZE*2),
               make_text(ASSETS["font_small"],"Mute/Unmute the music : E",(255,255,255),CENTER_X,TILE_SIZE*3),
               make_text(ASSETS["font_small"],"Go back to the main menu : Escape",(255,255,255),CENTER_X,TILE_SIZE*4),
               make_text(ASSETS["font_small"],"Change level in menu : Q/D",(255,255,255),CENTER_X,TILE_SIZE*5)]

### Objects
# Player
player = Player(CENTER_X - 25/2, HEIGHT - 50, PLAYER_SPEED, 25)

# Maze building
''' 
How does it work :
Firstly, create a map of the new level and put the corresponding letter for each object. W for Wall, V for Winpad, P for Player Spawn Location, Space for nothing and a number for a portal.
Secondly, indicate where a portal leads by putting it's id (number on the map) on the the level tp list. For exemple, if tp 0 leads to tp 1, then on the tp list, the number in index 0 will be 1. Put None if the portal is exit only.
Finally, add a variable where you use the function build_level with parameters the map and the tp list. After that, add the level to wall_list (id 0), to special_objects_list (id 1) and spawn_point_list (id 2) and add the map to the level map list.
'''

LEVEL_1_MAP = [
            "                           ",
            " 0     3  WWWWWWWWWWWWWWWWW",
            " WWWWWWWWWW  2  W   W W4  W",
            " W1       W  WWWWW  W WWW W",
            " W   WWW  W  W      W   W W",
            " W  VW    W     WW  WWW W W",
            " WWWWW  WWWWWWWWW   W   W W",
            "WW       W      W  WW WWW W",
            "W  WWWWWWWWW   WW  W      W",
            "W  W     W WW   W  WWWW W W",
            "W    WWW W         W    W W",
            "WWWWWW     WWWWWW  WW WWW W",
            "W          W            W W",
            "WWWWWWWWWWWWWWWWWWWWWWWWW W",
            "W5W P W    W W W   W  W   W",
            "W   W   W   W W       W W W",
            "WWWWWWWWWWWWWWWW  WWWWWWW W",
            "                   W       ",
            "  WWWW WWWWW WWWWWWWWWWW   ",
            "     WWW   WWW             ",
            "                           "]

LEVEL_1_TP = [1,None,3,None,5,None]
LEVEL_1 = build_level(LEVEL_1_MAP,LEVEL_1_TP)

LEVEL_2_MAP = [
    "                         ",
    "WWWWWWWWWWWWWWWWWWWWWWWWW",
    "WP    aW V   TT   T     T",
    "WWWWAWWWWWWT TT T   T   T",
    "W1W  W  WTTT TT TTTTT   T",
    "W   W   WTTT    T   T  TT",
    "WWW WWW WWWWWW  T 0 T   T",
    "W     W      W  T   T   T",
    "WWW WWWWWWWW W  TTTTTTW T",
    "W   W        W        W T",
    "W WWWWWW WWWWWTTTTTTT W T",
    "W W5W        W        W T",
    "W W W WWWWWWWW  TTTTTTW T",
    "W W W W W W  W          T",
    "W W    W W  4WTTTTTTTT  T",
    "W W WWWWWWWWWW   W   W  T",
    "WbW   W      B W   W    T",
    "WWW 2 W  3   WTTTTTTTTTTT",
    "  WWWWWWWWWWWW           "]

LEVEL_2_TP = [None,0,1,0,3,0]
LEVEL_2 = build_level(LEVEL_2_MAP,LEVEL_2_TP)

wall_list = [LEVEL_1[0],LEVEL_2[0]]
wall_list.extend([[] for _ in range(NB_LEVELS-len(wall_list))])

special_objects_list = [LEVEL_1[1],LEVEL_2[1]]
special_objects_list.extend([[] for _ in range(NB_LEVELS-len(special_objects_list))])

spawn_point_list = [LEVEL_1[2],LEVEL_2[2]]
spawn_point_list.extend([(None,None) for _ in range(NB_LEVELS-len(spawn_point_list))])

LEVEL_MAP_LIST = [LEVEL_1_MAP,LEVEL_2_MAP]
LEVEL_MAP_LIST.extend(None for _ in range(NB_LEVELS-len(LEVEL_MAP_LIST)))

# Buttons (Menu)
start = Button(CENTER_X, CENTER_Y, 400, 150,None)
book_fr = Button(100, HEIGHT -100, 100, 100, ASSETS["tutorial_fr"])
book_en = Button(250, HEIGHT -100, 100, 100, ASSETS["tutorial_en"])
right_arrow = Button(WIDTH - 100, CENTER_Y, 50, 50, ASSETS["right_arrow"])
left_arrow = Button(100, CENTER_Y, 50, 50, ASSETS["left_arrow"])
home = Button(50, 50, 75, 75, ASSETS["home"])
level_buttons = [Button(CENTER_X,CENTER_Y, 400, 250,None) for _ in range(NB_LEVELS)]

### Music 
sound_active = ASSETS["menu_music"]
sound_list = [ASSETS["music_level1"], ASSETS["music_level2"], ASSETS["music_level3"], ASSETS["music_level4"]]
sound_list.extend([None for _ in range(NB_LEVELS-len(sound_list))])

sound_active.set_volume(0.5)
for s in sound_list :
    if s != None :
        s.set_volume(0.5)

sound_active.play()

### EVENT LOOP
while game_active:
    dt = clock.tick(fps) / 1000.0 #Time tracking

    for event in pygame.event.get():
        # Quit
        if event.type == QUIT:
            game_active = False
        elif event.type == KEYDOWN:
            # Music activate/desactivate [E]
            if sound_active != None and event.key == K_e:
                if music_play:
                    music_play = False
                    sound_active.set_volume(0)
                else:
                    music_play = True
                    sound_active.set_volume(0.5)
                play_animation = True
            # Game reset [ESCAPE]
            elif event.key == K_ESCAPE and (maze_active or level_menu_active or tutorial_fr_menu or tutorial_en_menu or victory_menu) :
                reset()

            # Arrows (left and right) : change the current level selected in the menu
            elif level_menu_active and event.key == K_d:
                press_right_arrow()

            elif level_menu_active and event.key == K_q:
                press_left_arrow()

        #Buttons
        elif event.type == MOUSEBUTTONDOWN :
            if event.button == 1 :
                MOUSE_X, MOUSE_Y = pygame.mouse.get_pos() #Mouse position

                if level_menu_active: #Buttons in levels menu
                    
                    # Play button : Transfer the player to the right selected level from the menu
                    for level_id in range(len(level_buttons)) :
                        if level_buttons[level_id].is_pressed(MOUSE_X,MOUSE_Y) and level_menu_active == level_id+1:
                            level_menu_active = 0
                            maze_active = level_id + 1

                            fade_to_black(WIDTH, HEIGHT, 20) #Transition screen

                            # Window dimension updating
                            if LEVEL_MAP_LIST[maze_active-1] != None :
                                WIDTH, HEIGHT = len(LEVEL_MAP_LIST[maze_active-1][0])*TILE_SIZE, len(LEVEL_MAP_LIST[maze_active-1])*TILE_SIZE
                                screen = pygame.display.set_mode((WIDTH, HEIGHT))
                                CENTER_X, CENTER_Y = screen.get_rect().centerx, screen.get_rect().centery
                                
                                # Move player
                                if spawn_point_list[maze_active-1][0] != None :
                                    x,y = spawn_point_list[maze_active-1]
                                    player.move_spawn(x,y)

                            #Timer starting
                            TIMER = pygame.time.get_ticks()
                            
                            # Music
                            sound_active.stop()
                            sound_active.set_volume(0.5)
                            sound_active = sound_list[level_id]
                            if sound_active != None :
                                sound_active.play()
                                if not music_play :
                                    sound_active.set_volume(0)
                    
                    # Arrows (left and right) : change the current level selected in the menu
                    if level_menu_active and right_arrow.is_pressed(MOUSE_X,MOUSE_Y):
                        press_right_arrow()

                    if level_menu_active and left_arrow.is_pressed(MOUSE_X,MOUSE_Y):
                        press_left_arrow()
                        

                elif maze_active: # Buttons when a level is being played
                    pass
                
                elif tutorial_fr_menu :
                    if home.is_pressed(MOUSE_X,MOUSE_Y):
                        tutorial_fr_menu = False
                        fade_to_black(WIDTH,HEIGHT,20)
                
                elif tutorial_en_menu :
                    if home.is_pressed(MOUSE_X,MOUSE_Y):
                        tutorial_en_menu = False
                        fade_to_black(WIDTH,HEIGHT,20)

                elif victory_menu :
                    if home.is_pressed(MOUSE_X,MOUSE_Y):
                        victory_menu = False
                        fade_to_black(WIDTH,HEIGHT,20)
                        reset()

                else : # Buttons in start menu
                    # Start button : goes to the level menu
                    if start.is_pressed(MOUSE_X, MOUSE_Y):
                        level_menu_active = 1
                        fade_to_black(WIDTH,HEIGHT,20)
                    
                    if book_fr.is_pressed(MOUSE_X,MOUSE_Y):
                        tutorial_fr_menu = True
                        fade_to_black(WIDTH, HEIGHT, 20) 
                    
                    if book_en.is_pressed(MOUSE_X,MOUSE_Y):
                        tutorial_en_menu = True
                        fade_to_black(WIDTH, HEIGHT, 20) 



    ### PLAYER MOVEMENT AND INTERACTIONS
    if maze_active :
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
        obstacles = list(wall_list[maze_active-1])
        for so in special_objects_list[maze_active-1]:
            if isinstance(so,Door) and not so.opened:
                obstacles.append(so)

        #Moves the player only when it doesn't collide with a wall, closed door or the window border
        player.move(dx, dy, obstacles) 

        #Interacting with a special object
        for so in special_objects_list[maze_active-1]:
            if isinstance(so,Portal) and so.is_touched(player): # Use portal
                if RECALL_TIME == 0:
                    player.use_portal(so)
                    RECALL_TIME = 200
            if isinstance(so,Winpad) and so.is_touched(player) and not player.win: # Win
                player.victory()
                # Music
                if sound_active != None :
                    sound_active.stop()
                sound_active = ASSETS["music_victory"]
                sound_active.set_volume(0.5)
                sound_active.play()
                if not music_play :
                    sound_active.set_volume(0)

                fade_to_black(WIDTH,HEIGHT,1)

                #Window resizing
                WIDTH, HEIGHT = DEFAULT_WINDOW_SIZE
                screen = pygame.display.set_mode(DEFAULT_WINDOW_SIZE)
                CENTER_X, CENTER_Y = screen.get_rect().centerx, screen.get_rect().centery

                # Menu update
                maze_active = 0
                victory_menu = True
                
                # Text
                final_timer_text, final_timer_textpos = make_text(ASSETS["font_main"],"Time : "+str(seconds),(255,255,255),CENTER_X,CENTER_Y)

            if isinstance(so,Key) and not so.collected and so.is_touched(player): #Collect key
                player.pick_up_key(so)
            if isinstance(so,Door) and not so.opened and so.rect.inflate(10,10).colliderect(player.rect): # Open door
                if so.id in player.keys :
                    so.open()
            if isinstance(so,Trap) and so.is_touched(player):
                reset(maze_active)
        

    ### VISUALS
    screen.fill(pygame.Color(0,0,0))
    #Levels
    if maze_active :

        #Objects underneath the player
        for so in special_objects_list[maze_active-1]:
            if isinstance(so,Portal):
                if so.dest_id == None :
                    screen.blit(so.img2,(so.x, so.y))
                else :
                    screen.blit(so.img,(so.x, so.y))
            elif isinstance(so,Winpad):
                screen.blit(so.img,(so.x,so.y))
            elif isinstance(so,Key) and not so.collected:
                screen.blit(so.img,(so.x,so.y))
            elif isinstance(so,Door) and not so.opened:
                create("rect",so.x1, so.y1, so.x2-so.x1, so.y2-so.y1,(255,255,0))
            elif isinstance(so,Trap):
                screen.blit(so.img,(so.x,so.y))

        #The player
        create("rect",player.x, player.y, player.width, player.width,(255,0,0))

        #Objects above the player
        # Walls
        for wall in wall_list[maze_active-1]:
            create("rect",wall.x1, wall.y1, wall.x2-wall.x1, wall.y2-wall.y1,LEVEL_COLORS[maze_active-1])
        # Timer
        else :
            seconds = (pygame.time.get_ticks() - TIMER) / 1000
            timer_text, timer_pos = make_text(ASSETS["font_small"],"Time : "+str(seconds),(255,255,255),WIDTH-100,30)
            screen.blit(timer_text,timer_pos)

    #Level selecting menu
    elif level_menu_active :
        for k in range(NB_LEVELS + 1) :
            if k == level_menu_active :
                #Current level
                level = level_buttons[k-1]
                #Center play button
                create("rect",level.x, level.y, level.width, level.height,LEVEL_COLORS[k-1])
                create("rect",level.x + 20, level.y + 20, level.width - 40, level.height - 40,(0,0,0))
                #Display the right level text
                t, tpos = levels_text[k-1]
                screen.blit(t, tpos)
                #Create the "PLAY" text here matching with the current level color
                play_text, play_textpos = make_text(ASSETS["font_main"],"PLAY",LEVEL_COLORS[k-1],CENTER_X,CENTER_Y)
        #Display arrows
        screen.blit(left_arrow.img,(left_arrow.x,left_arrow.y))
        screen.blit(right_arrow.img,(right_arrow.x,right_arrow.y))
        #Play text in the center
        screen.blit(play_text,play_textpos)

    #Tutorial menus
    elif tutorial_fr_menu :
        for text, textpos in tutorial_fr :
            screen.blit(text,textpos)
            screen.blit(home.img, (home.x,home.y))
    
    elif tutorial_en_menu :
        for text, textpos in tutorial_en :
            screen.blit(text,textpos)
            screen.blit(home.img, (home.x,home.y))

    #Victory menu
    elif victory_menu :
        create("rect",50,50,WIDTH-100,HEIGHT-100,(255,255,0))
        create("rect",75,75,WIDTH-150,HEIGHT-150,(0,0,0))
        screen.blit(victory_text,victory_textpos)
        screen.blit(home.img, (home.x,home.y))
        screen.blit(final_timer_text,final_timer_textpos)

    #Start menu
    else :
        #The game name
        screen.blit(gamename_text, gamename_textpos)
        #Start button visual 
        create("rect",start.x, start.y, start.width, start.height,(255,255,0))
        create("rect",start.x + 10, start.y + 10, start.width - 20, start.height - 20,(0,0,0))
        screen.blit(start_text,start_textpos)

        #Tutorial menus
        screen.blit(book_fr.img,(book_fr.x,book_fr.y))
        screen.blit(book_en.img,(book_en.x,book_en.y))

    #Music display
    if play_animation:
        if music_play :
            screen.blit(ASSETS["music_on"],(WIDTH - 75, 25))
        else :
            screen.blit(ASSETS["music_off"],(WIDTH - 75, 25))
        time_display -= 1
        if time_display <= 0 :
            play_animation = False
    elif time_display != 100 :
        time_display = 100
    
    pygame.display.flip()
    if RECALL_TIME > 0:
        RECALL_TIME -= 1

pygame.quit()