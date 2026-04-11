import pygame
import random
from .entities import Wall
from .assets_manager import get_path

def make_text(font,txt,color,x,y):
    if txt is None :
        txt = ""
    t = font.render(txt, 3, color)
    tpos = t.get_rect()
    tpos.centerx = x
    tpos.centery = y
    return t, tpos

def load_map(filename):
    path = get_path("levels",filename)
    level_map = []
    file = open(path,"r")
    for line in file :
        level_map.append(line.rstrip('\n'))
    return level_map

def optimise_walls(walls):
    if not walls:
        return []

    # Work on rectangles for optimization
    rects = [w.rect.copy() for w in walls]
    
    # Honrizontal fusion
    rects.sort(key=lambda r: (r.y, r.x))
    h_fused = []
    if rects:
        curr = rects[0]
        for next_r in rects[1:]:
            if next_r.y == curr.y and next_r.x == curr.x + curr.width and next_r.height == curr.height:
                curr.width += next_r.width
            else:
                h_fused.append(curr)
                curr = next_r
        h_fused.append(curr)

    # Vertical fusion
    h_fused.sort(key=lambda r: (r.x, r.y))
    v_fused = []
    if h_fused:
        curr = h_fused[0]
        for next_r in h_fused[1:]:
            if next_r.x == curr.x and next_r.y == curr.y + curr.height and next_r.width == curr.width:
                curr.height += next_r.height
            else:
                v_fused.append(curr)
                curr = next_r
        v_fused.append(curr)

    return [Wall(r.x, r.y, r.width, r.height) for r in v_fused]

def invert_color(rvb):
    r, v, b = rvb
    return (255 - r, 255 - v, 255 - b)

def tint_image(surface, color):
    """Returns a copy of the surface tinted with the given color."""
    tinted = surface.copy()
    tinted.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
    return tinted

def generate_custom_maze(width, height, entry_info, exit_info):
    """
    entry_info/exit_info : tuple (char, x, y)
    """
    # Create grid
    grid = [['W' for _ in range(width)] for _ in range(height)]

    # Create maze by DFS
    def carve(x, y):
        grid[y][x] = ' '
        directions = [(0, 2), (0, -2), (2, 0), (-2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 < nx < width-1 and 0 < ny < height-1 and grid[ny][nx] == 'W':
                grid[y + dy // 2][x + dx // 2] = ' '
                carve(nx, ny)

    carve(1, 1)

    # Entry placement
    e_char, ex, ey = entry_info
    grid[ey][ex] = e_char
    # Open the maze's entry
    if ex == 0: 
        grid[ey][ex+1] = ' '
    elif ex == width-1: 
        grid[ey][ex-1] = ' '

    # Exit(s) placement(s)
    s_char, sx, sy = exit_info
    grid[sy][sx] = s_char
    # Open the maze's exit
    if sx == 0: 
        grid[sy][sx+1] = ' '
    elif sx == width-1: 
        grid[sy][sx-1] = ' '

    return ["".join(row) for row in grid]