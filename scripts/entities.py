import pygame
from .settings import TILE_SIZE, TORCH_EFFECT, KEY_COLORS
from .assets_manager import load_assets

ASSETS = load_assets()

### PLAYER CLASS
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
        self.can_teleport = False

    def modify_speed(self,speed):
        self.speed = speed
    
    def is_in_bounds_vertical(self,dy,game):
        return self.y + dy > 0 and self.y + self.width + dy < game.height

    def is_in_bounds_horizontal(self,dx,game):
        return self.x + dx > 0 and self.x + self.width + dx < game.width

    def can_move(self, dx, dy, walls, game):
        future_rect = pygame.Rect(self.x + dx, self.y + dy, self.width, self.width)
        
        for wall in walls:
            if future_rect.colliderect(wall.rect):
                return False
            
        if not self.is_in_bounds_horizontal(dx, game):
            return False
        if not self.is_in_bounds_vertical(dy, game):
            return False

        return True

    def move(self,dx,dy,walls,game):
        assert isinstance(walls,list)
        #horizontal
        if self.win :
            return
        if dx != 0:
            if self.can_move(dx, 0, walls, game):
                self.x += dx
            else: # To stick the player to the wall
                if dx > 0 :
                    direction = 1
                else :
                    direction = -1
                while self.can_move(direction, 0, walls, game) and abs(dx) > 1:
                    self.x += direction
                    dx -= direction
            

        #vertical
        if dy != 0:
            if self.can_move(0, dy, walls, game):
                self.y += dy
            else: # To stick the player to the wall
                if dy > 0 :
                    direction = 1
                else :
                    direction = -1
                while self.can_move(0, direction, walls, game) and abs(dy) > 1:
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

    def use_portal(self, portal, objects_in_level):
        dest_portal = None
        for so in objects_in_level:
            # Searching the right portal
            if isinstance(so, Portal) and so != portal and so.id == portal.dest_id:
                dest_portal = so
                break

        if dest_portal:
            # Move player
            self.x = dest_portal.x + (dest_portal.width // 2) - (self.width // 2)
            self.y = dest_portal.y + (dest_portal.width // 2) - (self.width // 2)
            self.rect.topleft = (self.x, self.y)
    
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


### OBSTACLES CLASSES
class Wall :
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + width, y + height

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

### TRIGGERS CLASSES
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

    def move(self,x,y):
        self.x, self.y = x, y

    def is_touched(self,player):
        assert isinstance(player,Player)
        return self.x < player.x + player.width // 2 < self.x + self.width and self.y < player.y + player.width // 2 < self.y + self.width

class SubMapPortal:
    def __init__(self, x, y, target_map_index, spawn_pos):
        self.x, self.y = x, y
        self.width = 50
        self.rect = pygame.Rect(x, y, self.width, self.width)
        self.target_map_index = target_map_index #Map index in "maps" in level config
        self.spawn_pos = spawn_pos # Player spawn point in new map
        self.img = ASSETS["tp3"] 

    def is_touched(self, player):
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
        self.collected = False
        self.door_id = id
        from .utils import tint_image
        self.img = tint_image(ASSETS["key"],KEY_COLORS.get(self.door_id.lower(), (255, 255, 255)))

    def is_touched(self,player):
        assert isinstance(player,Player)
        return self.x < player.x + player.width // 2 < self.x + self.width and self.y < player.y + player.width // 2 < self.y + self.width
    
    def collect(self):
        self.collected = True
    
    def reset(self):
        self.collected = False

class Light :
    def __init__(self,x,y):
        self.x,self.y = x,y
        self.width = TILE_SIZE
        self.collected = False
        self.img = ASSETS["torch"]
        self.effect = TORCH_EFFECT
        self.cooldown = 0.0

    def is_touched(self,player):
        assert isinstance(player,Player)
        return self.x < player.x + player.width // 2 < self.x + self.width and self.y < player.y + player.width // 2 < self.y + self.width

    def collect(self):
        self.collected = True
    
    def respawn(self):
        self.collected = False

### UI CLASSES
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