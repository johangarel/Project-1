
WIDTH = 960
HEIGHT = 740
HEIGHT_SETTINGS = 840

NB_LEVELS = 101
TILE_SIZE = 40

FPS = 240
FPS_PRESETS = [60,120,240]

DEFAULT_MUSIC_VOL = 0.5
DEFAULT_SFX_VOL = 0.5

PLAYER_SPEED = 400
PLAYER_WIDTH = 25
PLAYER_DEFAULT_POS = (WIDTH // 2 - PLAYER_WIDTH // 2, HEIGHT - 50)

ENEMY_SPEED_PATROL = 100
ENEMY_SPEED_CHASE = 200
ENEMY_DETECTION_RADIUS = 200

TP_WIDTH = 50
WINPAD_WIDTH = 50
VISION_RADIUS = 150

TORCH_EFFECT = 200
TORCH_TIME = 5.0

WALL_THICKNESS = 10

FADE_SPEED = {
    "slow":10,
    "normal":25,
    "fast":50
}

LEVEL_NAMES = {
    1:"Rooms", 
    2:"Trapped", 
    3:"Perfect Maze", 
    4:"Darker World",
    5:"The Heist",
    42:"The Answer",
    67:"heheheha",
    69:"Nice"
    }

LEVEL_COLORS = {
    1:(255,0,255),
    2:(255,125,0),
    3:(0,255,0),
    4:(105, 230, 90), 
    5:(40, 105, 155), 
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
    4:8,
    42:-42
}

GAME_NAME = "MAZE 101"
GAME_VERSION = "v0.5 WIP"
START_TEXT = "START"
PLAY_TEXT = "PLAY"
VICTORY_TEXT = "You win !"
LOADING_TEXT = "Loading..."
RECORD_TEXT = "New record !"
SETTINGS_TITLE = "Settings"
SAVE_TEXT = "Save changes"
RESET_TEXT = "Reset"

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

# Objects that walls shouldn't connect with
BANNED_BUILDING_CHARACTERS = ["P","V","L","S","E"]

KEY_BINDINGS_DEFAULT = {
    "up":     "K_z",
    "down":   "K_s",
    "left":   "K_q",
    "right":  "K_d",
    "music":  "K_e",
    "reset":  "K_r",
    "menu":   "K_ESCAPE",
}