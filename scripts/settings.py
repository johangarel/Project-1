
WIDTH = 960
HEIGHT = 740

NB_LEVELS = 101
TILE_SIZE = 40

FPS = 240

PLAYER_SPEED = 500
PLAYER_WIDTH = 25

TP_WIDTH = 50
WINPAD_WIDTH = 50
VISION_RADIUS = 150

TORCH_EFFECT = 200
TORCH_TIME = 5.0

WALL_THICKNESS = 10

LEVEL_NAMES = {
    1:"Rooms", 
    2:"Trapped", 
    3:"Perfect Maze", 
    4:"Darker World",
    42:"The Answer",
    67:"heheheha",
    69:"Nice"
    }

LEVEL_COLORS = {
    1:(255,0,255),
    2:(255,125,0),
    3:(0,255,0),
    4:(105, 230, 90), 
    5:(105, 155, 40), 
    6:(195, 55, 145), 
    7:(50, 185, 200), 
    8:(50, 50, 250), 
    9:(195, 50, 195), 
    10:(225, 150, 55),
    42:(0,0,0),
    67:(0,0,0)
}

LEVEL_REWARD = {
    1:1,
    2:4,
    3:2,
    4:10,
    42:-42
}

GAME_NAME = "MAZE 101"
GAME_TITLE = "MAZE 101 - v0.4"
START_TEXT = "START"
PLAY_TEXT = "PLAY"
VICTORY_TEXT = "You win !"
LOADING_TEXT = "Loading ..."

TUTORIAL_FR_TEXT = [
    "Se déplacer : ZQSD",
    "Couper/Réactiver la musique : E",
    "Revenir au menu principal : Echap",
    "Changer le niveau dans le menu : Q/D",
    "Réinitialiser le labyrinthe : R"
]

TUTORIAL_EN_TEXT = [
    "Move : ZQSD",
    "Mute/Unmute the music : E",
    "Go back to the main menu : Escape",
    "Change level in menu : Q/D",
    "Reset maze : R"
]

KEY_COLORS = {
    'a': (255, 50, 50),   
    'b': (50, 255, 50),   
    'c': (50, 50, 255),   
    'd': (255, 255, 50),  
    'e': (255, 50, 255)
}

DEFAULT_KEY_COLOR = (200, 200, 200)

# Mandatory step if you want to create a new level
LEVEL_CONFIGS = {
    1: {"file": ["level1.txt"], "tps": [1, None, 3, None, 5, None], "fow":False},
    2: {"file": ["level2.txt"], "tps": [None, 0, 1, 0, 3, 0], "fow":False},
    3: {"file": ["level3_1.txt","level3_2.txt","level3_3.txt"], "tps": [1, 0, 5, 4, None, None], "fow":False},
    4: {"file": ["level4.txt","level4_2.txt","level4_3.txt","level4_4.txt"], "tps": [1,None,3,None,5,None], "fow":True},
    42: {"file": ["level42.txt"], "tps":[], "fow":False}
}

# Optional step : create a sub map portal system
SUBMAP_ROUTES = {
    3: { # For level 3
        0: { # For level3_1.txt (Index 0)
            0:{"target_map": 1, "spawn_pos": (TILE_SIZE,TILE_SIZE)} # The 1st 'S' leads to map index 1
            },
        1: { # For level3_2.txt (Index 1)
            0:{"target_map": 2, "spawn_pos": (TILE_SIZE,TILE_SIZE)}, # The 1st 'S' leads to map index 2
            1:{"target_map": 0, "spawn_pos": (TILE_SIZE, TILE_SIZE)}
            },  
    },
    4: {
        0: {
            1:{"target_map":3, "spawn_pos": (3*TILE_SIZE,13*TILE_SIZE)},
            0:{"target_map":1, "spawn_pos": (12*TILE_SIZE,12*TILE_SIZE)}
        },
        1: {
            0:{"target_map":1, "spawn_pos": (12*TILE_SIZE,12*TILE_SIZE)},
            1:{"target_map":3, "spawn_pos": (3*TILE_SIZE,13*TILE_SIZE)},
            2:{"target_map":0, "spawn_pos": (TILE_SIZE,11*TILE_SIZE)},
            3:{"target_map":2, "spawn_pos": (15*TILE_SIZE,7*TILE_SIZE)},
            4:{"target_map":0, "spawn_pos": (TILE_SIZE,11*TILE_SIZE)},
        },
        2: {
            0:{"target_map":3, "spawn_pos": (25*TILE_SIZE,13*TILE_SIZE)}
        },
        3: {
            0:{"target_map":0, "spawn_pos": (TILE_SIZE,11*TILE_SIZE)}
        }
    }
}

# Objects that walls shouldn't connect with
BANNED_BUILDING_CHARACTERS = ["P","V","L","S"]