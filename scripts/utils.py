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

def invert_color(rvb):
    r, v, b = rvb
    return (255 - r, 255 - v, 255 - b)