from .entities import Wall, Trap, Portal, Key, Door, Player, Winpad
from .utils import optimise_walls

class Maze :
    def __init__(self,layout,tp_order,player,game):
        assert isinstance(player,Player)
        self.walls = []
        self.special_objs = []
        self.spawn_point = player.default_pos

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
                        self.walls.append(Wall(x + game.tile_size/2 - 5, y + game.tile_size/2, 10, game.tile_size/2))
                    if cond_b :
                        self.walls.append(Wall(x + game.tile_size/2 - 5, y, 10, game.tile_size/2))
                    if cond_c :
                        self.walls.append(Wall(x + game.tile_size/2, y + game.tile_size/2 - 5, game.tile_size/2, 10))
                    if cond_d :
                        self.walls.append(Wall(x, y + game.tile_size/2 - 5, game.tile_size/2, 10))
                    self.walls.append(Wall(x + game.tile_size/2 - 5, y + game.tile_size/2 - 5, 10, 10))

                elif char == "P":  # Player Start
                    self.spawn_point = (x,y)
                elif char == "V":  # Victory
                    self.special_objs.append(Winpad(x, y))
                elif char == "T": # Trap
                    self.special_objs.append(Trap(x,y))
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
                    
        self.walls = optimise_walls(self.walls)