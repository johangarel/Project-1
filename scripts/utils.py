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