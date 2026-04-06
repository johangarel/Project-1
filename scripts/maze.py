from .entities import Wall, Trap, Portal, Key, Door, Player, Winpad, Light, SubMapPortal
from .utils import optimise_walls
from .settings import WALL_THICKNESS, BANNED_BUILDING_CHARACTERS, SUBMAP_ROUTES

class Maze :
    def __init__(self,layout,tp_order,player,game, map_index=0):
        assert isinstance(player,Player)
        self.special_objs = []
        self.spawn_point = player.default_pos
        self.sub_portal_count = 0

        raw_walls = []
        wall_thickness = WALL_THICKNESS 
        offset = (game.tile_size // 2) - (wall_thickness // 2)

        for row_id, row in enumerate(layout): 
            for col_id, char in enumerate(row):
                x = col_id * game.tile_size
                y = row_id * game.tile_size

                if char == "W":  # Wall
                    banned = BANNED_BUILDING_CHARACTERS

                    # Conditions
                    down = row_id < len(layout)-1 and layout[row_id+1][col_id].isupper() and layout[row_id+1][col_id] not in banned
                    up = row_id > 0 and layout[row_id-1][col_id].isupper() and layout[row_id-1][col_id] not in banned
                    right = col_id < len(row)-1 and layout[row_id][col_id+1].isupper() and layout[row_id][col_id+1] not in banned
                    left = col_id > 0 and layout[row_id][col_id-1].isupper() and layout[row_id][col_id-1] not in banned

                    # 1. Vertical wall
                    if up or down:
                        v_start = y if up else y + offset
                        v_height = game.tile_size if (up and down) else (game.tile_size // 2 + wall_thickness // 2)
                        raw_walls.append(Wall(x + offset, v_start, wall_thickness, v_height))

                    # 2. Honrizontal wall
                    if left or right:
                        h_start = x if left else x + offset
                        h_width = game.tile_size if (left and right) else (game.tile_size // 2 + wall_thickness // 2)
                        raw_walls.append(Wall(h_start, y + offset, h_width, wall_thickness))
                    
                    # 3. Isolated wall
                    if not (up or down or left or right):
                        raw_walls.append(Wall(x + offset, y + offset, wall_thickness, wall_thickness))

                elif char == "P":  # Player Start
                    self.spawn_point = (x,y)
                elif char == "V":  # Victory
                    self.special_objs.append(Winpad(x, y))
                elif char == "T": # Trap
                    self.special_objs.append(Trap(x,y))
                elif char == "L": # Light object
                    self.special_objs.append(Light(x,y))
                elif char == "S": # Sub map portal
                    config = None
                    level_id = game.maze
                    # Search path
                    if level_id in SUBMAP_ROUTES and map_index in SUBMAP_ROUTES[level_id] and self.sub_portal_count in SUBMAP_ROUTES[level_id][map_index]:
                        config = SUBMAP_ROUTES[level_id][map_index][self.sub_portal_count]
                    # Create the portal if the path exists
                    if config:
                        portal = SubMapPortal(x, y, config["target_map"], config["spawn_pos"])
                        self.special_objs.append(portal)
                        self.sub_portal_count += 1
                elif char.isdigit(): # Teleport
                    self.special_objs.append(Portal(x,y,int(char),tp_order[int(char)]))
                elif char.islower(): # Key
                    self.special_objs.append(Key(x,y,char))
                elif char.isupper(): # Door
                    #Conditions (Wall nearby) (again)
                    cond_a = (0 < row_id < len(layout)-1) and (layout[row_id + 1][col_id] == 'W' ) and (layout[row_id - 1][col_id] == 'W' ) # Vertical
                    cond_b = (0 < col_id < len(row)-1) and (layout[row_id][col_id + 1] == 'W' ) and (layout[row_id][col_id - 1] == 'W' ) # Horizontal
                    #Connect to walls
                    if cond_a :
                        self.special_objs.append(Door(x + game.tile_size/2 - 5, y, 10, game.tile_size,char))
                    if cond_b :
                        self.special_objs.append(Door(x, y + game.tile_size/2 - 5, game.tile_size, 10,char))
                    
        self.walls = optimise_walls(raw_walls)