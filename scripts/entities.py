import pygame
from .settings import TILE_SIZE, TORCH_EFFECT, KEY_COLORS, PLAYER_WIDTH


# ==================================================================
# Player class
# ==================================================================

class Player:
    def __init__(self,pos: tuple,speed: int,width: int, img):
        self.x, self.y = pos
        self.default_pos = pos
        self.respawn_pos = pos
        self.speed = speed
        self.width = width
        self.win = False
        self.keys = []
        self.rect = pygame.Rect(self.x,self.y,width,width)
        self.img = img
        self.can_teleport = False
        self.direction = "right"

    def modify_speed(self,speed: int):
        self.speed = speed
    
    def is_in_bounds_vertical(self,dy: int,game) -> bool:
        return self.y + dy > 0 and self.y + self.width + dy < game.height

    def is_in_bounds_horizontal(self,dx: int,game) -> bool:
        return self.x + dx > 0 and self.x + self.width + dx < game.width

    def can_move(self, dx: int, dy: int, walls, game) -> bool:
        future_rect = pygame.Rect(self.x + dx, self.y + dy, self.width, self.width)
        
        for wall in walls:
            if future_rect.colliderect(wall.rect):
                return False
            
        if not self.is_in_bounds_horizontal(dx, game):
            return False
        if not self.is_in_bounds_vertical(dy, game):
            return False

        return True

    def move(self,dx: int,dy: int,walls,game):
        assert isinstance(walls,list)

        if self.win :
            return
        
        # Update direction
        if  dx > 0:  self.direction = "right"
        elif  dx < 0: self.direction = "left"
        elif  dy < 0: self.direction = "up"
        elif  dy > 0: self.direction = "down"

        # horizontal
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
        self.direction = "right"

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

# ==================================================================
# Eneny class
# ==================================================================

class Enemy:

    def __init__(self, x, y, patrol_path: list, speed_patrol: int, speed_chase: int, detection_radius: int, img, map_index: int):
        self.x, self.y = float(x), float(y)
        self.spawn_pos = (float(x), float(y))
        self.width = PLAYER_WIDTH
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.width)

        # Patrol
        self.waypoints   = patrol_path   # list of (px_x, px_y)
        self.patrol_index  = 0
        self._was_chasing = False
        self._patrol_path = []         # list of pixel (x, y) waypoints
        self._patrol_path_timer = 0.0  # countdown to next recalculation
        self.PATROL_PATH_REFRESH = 0.6 # seconds between A* recalculations

        # A* chase path
        self._chase_path  = []   # list of pixel (x, y) waypoints
        self._path_timer  = 0.0  # countdown to next recalculation
        self.PATH_REFRESH = 0.6  # seconds between A* recalculations
        self._path_computed_this_cycle = False

        # Stats
        self.speed_patrol      = speed_patrol
        self.speed_chase       = speed_chase
        self.detection_radius  = detection_radius

        # Rendering
        self.img       = img
        self.direction = "right"
        self.map_index = map_index

        self.state = "patrol"  # "patrol" | "chase"
 
    def update(self, player, walls: list, dt: float, layout: list, tile_size: int) -> None:
        dist = self._distance_to(player)

        if self.state == "patrol":
            if dist <= self.detection_radius:
                self.state = "chase"
        else:  # chase
            if dist > self.detection_radius * 1.2:
                self.state = "patrol"

        if self.state == "chase":
            self._update_chase(player, walls, dt, layout, tile_size)
            self._was_chasing = True
        else:
            self._chase_path = []
            self._path_timer = 0.0
            if not self.waypoints:
                self._was_chasing = False
                return

            if self._was_chasing:
                self._patrol_path = []
                self._patrol_path_timer = 0.0
            self._was_chasing = False

            self._update_patrol(walls, dt, layout, tile_size)

    def _update_chase(self, player, walls: list, dt: float, layout: list, tile_size: int) -> None:
        """Follow the player using A* pathfinding."""
        from .utils import astar

        dist = self._distance_to(player)
        # Short distance chase
        if dist < 34.5:
            self._chase_path = []
            self._path_timer = self.PATH_REFRESH # reset timer
            self._path_computed_this_cycle = False
            self._move_towards(player.x, player.y, self.speed_chase, walls, dt)
            return

        self._path_timer -= dt
        if self._path_timer <= 0:
            start_col = int(self.x // tile_size)
            start_row = int(self.y // tile_size)
            start_snapped = (
                start_col * tile_size + tile_size // 2,
                start_row * tile_size + tile_size // 2,
            )
            self._chase_path = astar(
                layout,
                start_snapped,
                (player.x, player.y),
                tile_size,
            )
            self._path_timer = self.PATH_REFRESH

        if not self._chase_path and not self._path_computed_this_cycle:
            start_col = int(self.x // tile_size)
            start_row = int(self.y // tile_size)
            start_snapped = (
                start_col * tile_size + tile_size // 2,
                start_row * tile_size + tile_size // 2,
            )
            self._chase_path = astar(
                layout,
                start_snapped,
                (player.x, player.y),
                tile_size,
            )
            self._path_computed_this_cycle = True

        if self._chase_path:
            cx = self._chase_path[0][0] + tile_size // 2 - self.width // 2
            cy = self._chase_path[0][1] + tile_size // 2 - self.width // 2
            self._move_towards(cx, cy, self.speed_chase, walls, dt)
            if abs(self.x - cx) < 4 and abs(self.y - cy) < 4:
                self._chase_path.pop(0)
        else:
            self._update_patrol(walls, dt, layout, tile_size)

    def _update_patrol(self, walls: list, dt: float, layout: list, tile_size: int) -> None:
        from .utils import astar

        tx, ty = self.waypoints[self.patrol_index]

        # Waypoints
        if abs(self.x - tx) < 4 and abs(self.y - ty) < 4:
            self.patrol_index = (self.patrol_index + 1) % len(self.waypoints)
            self._patrol_path = []
            self._patrol_path_timer = 0.0
            tx, ty = self.waypoints[self.patrol_index]

        # A*
        self._patrol_path_timer -= dt
        if self._patrol_path_timer <= 0 or not self._patrol_path:
            self._patrol_path = astar(layout, (self.x, self.y), (tx, ty), tile_size)
            self._patrol_path_timer = self.PATROL_PATH_REFRESH

        if self._patrol_path:
            cx = self._patrol_path[0][0] + tile_size // 2 - self.width // 2
            cy = self._patrol_path[0][1] + tile_size // 2 - self.width // 2
            self._move_towards(cx, cy, self.speed_patrol, walls, dt)
            if abs(self.x - cx) < 4 and abs(self.y - cy) < 4:
                self._patrol_path.pop(0)
        else:
            # Fallback
            self._move_towards(tx, ty, self.speed_patrol, walls, dt)

    def is_touching(self, player) -> bool:
        return self.rect.colliderect(player.rect)

    def reset(self) -> None:
        self.x, self.y    = self.spawn_pos
        self.patrol_index = 0
        self.state        = "patrol"
        self._chase_path  = []
        self._path_timer  = 0.0
        self.rect         = pygame.Rect(int(self.x), int(self.y), self.width, self.width)
        self._was_chasing = False
        self._patrol_path = []
        self._patrol_path_timer = 0.0

    def _distance_to(self, player) -> float:
        dx = (self.x + self.width / 2) - (player.x + player.width / 2)
        dy = (self.y + self.width / 2) - (player.y + player.width / 2)
        return (dx ** 2 + dy ** 2) ** 0.5

    def _move_towards(self, tx: float, ty: float, speed: int, walls: list, dt: float) -> None:
        """Move toward (tx, ty) at given speed, sliding along walls."""
        dx = tx - self.x
        dy = ty - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist < 1:
            return

        step      = speed * dt
        norm_dx   = dx / dist * min(step, dist)
        norm_dy   = dy / dist * min(step, dist)

        # Update sprite direction
        if abs(norm_dx) > abs(norm_dy):
            self.direction = "right" if norm_dx > 0 else "left"
        else:
            self.direction = "down" if norm_dy > 0 else "up"

        # Move axes independently so the enemy slides along walls
        future_x = pygame.Rect(int(self.x + norm_dx), int(self.y), self.width, self.width)
        future_y = pygame.Rect(int(self.x), int(self.y + norm_dy), self.width, self.width)

        if not any(future_x.colliderect(w.rect) for w in walls):
            self.x += norm_dx
        if not any(future_y.colliderect(w.rect) for w in walls):
            self.y += norm_dy

        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.width)

    def _nearest_patrol_index(self) -> int:
        best_idx = self.patrol_index
        best_dist = float("inf")
        for i, (px, py) in enumerate(self.waypoints):
            d = (self.x - px) ** 2 + (self.y - py) ** 2
            if d < best_dist:
                best_dist = d
                best_idx = i
        return best_idx

# ==================================================================
# Obstacles classes
# ==================================================================

class Wall :
    def __init__(self, x, y, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + width, y + height

class Door :
    def __init__(self,x,y,width: int,height: int,id=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x + width, y + height
        self.opened = False
        self.id = id.lower()
    
    def open(self):
        self.opened = True
    
    def reset(self):
        self.opened = False

# ==================================================================
# Triggers classes
# ==================================================================

class Winpad:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.width = 50
        self.rect = pygame.Rect(x, y, self.width, self.width)
        self.img = img

    def move(self,x,y):
        self.x = x
        self.y = y

    def is_touched(self,player: Player) -> bool:
        return self.x < player.x + player.width // 2 < self.x + self.width and self.y < player.y + player.width // 2 < self.y + self.width

class Portal:
    def __init__(self,x,y,id, destination_id, img, img2):
        self.x, self.y = x,y
        self.width = 50
        self.rect = pygame.Rect(x, y, self.width, self.width)
        self.img = img
        self.img2 = img2
        self.id = id
        self.dest_id = destination_id

    def move(self,x,y):
        self.x, self.y = x, y

    def is_touched(self,player: Player):
        return self.x < player.x + player.width // 2 < self.x + self.width and self.y < player.y + player.width // 2 < self.y + self.width

class SubMapPortal:
    def __init__(self, x, y, target_map_index, spawn_pos, img):
        self.x, self.y = x, y
        self.width = 50
        self.rect = pygame.Rect(x, y, self.width, self.width)
        self.target_map_index = target_map_index #Map index in "maps" in level config
        self.spawn_pos = spawn_pos # Player spawn point in new map
        self.img = img

    def is_touched(self, player: Player) -> bool:
        return self.x < player.x + player.width // 2 < self.x + self.width and self.y < player.y + player.width // 2 < self.y + self.width

class Trap :
    def __init__(self,x,y,img):
        self.x,self.y = x,y
        self.width = TILE_SIZE
        self.rect = pygame.Rect(x,y,TILE_SIZE,TILE_SIZE)
        self.img = img
    
    def is_touched(self,player: Player) -> bool:
        return self.rect.colliderect(player.rect)

class Key :
    def __init__(self,x,y,id,img):
        self.x,self.y = x,y
        self.width = TILE_SIZE
        self.collected = False
        self.door_id = id
        from .utils import tint_image
        self.img = tint_image(img,KEY_COLORS.get(self.door_id.lower(), (255, 255, 255)))

    def is_touched(self,player: Player) -> bool:
        return self.x < player.x + player.width // 2 < self.x + self.width and self.y < player.y + player.width // 2 < self.y + self.width
    
    def collect(self):
        self.collected = True
    
    def reset(self):
        self.collected = False

class Light :
    def __init__(self,x,y,img):
        self.x,self.y = x,y
        self.width = TILE_SIZE
        self.collected = False
        self.img = img
        self.effect = TORCH_EFFECT
        self.cooldown = 0.0

    def is_touched(self,player: Player) -> bool:
        return self.x < player.x + player.width // 2 < self.x + self.width and self.y < player.y + player.width // 2 < self.y + self.width

    def collect(self):
        self.collected = True
    
    def respawn(self):
        self.collected = False

# ==================================================================
# UI classes
# ==================================================================

class ButtonUI:
    def __init__(self,x,y,width: int,height: int,img):
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

    def is_pressed(self,x,y) -> bool:
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

class TextUI:
    def __init__(self,x,y,font,txt,color):
        if txt is None :
            txt = ""
        self.centerx = x
        self.centery = y
        self.font = font
        self.txt = font.render(txt, 3, color)
        self.color = color
        self.pos = self.txt.get_rect(center=(x,y))