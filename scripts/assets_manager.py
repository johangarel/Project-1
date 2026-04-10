import pygame
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_path(*relative_path):
    return os.path.join(BASE_DIR, *relative_path)

def load_assets():
    pygame.mixer.init()
    pygame.font.init()
    assets = {"logo":pygame.image.load(get_path("assets","images","LOGO PROJECT 1.png")),
            "winpad":pygame.image.load(get_path("assets","images","_crown_new.png")),
            "tp1":pygame.image.load(get_path("assets","images","_tp_new.png")),
            "tp2":pygame.image.load(get_path("assets","images","_tp2_new.png")),
            "tp3":pygame.image.load(get_path("assets","images","_tp3_new.png")),
            "music_on":pygame.image.load(get_path("assets","images","MUSIC ON.png")),
            "music_off":pygame.image.load(get_path("assets","images","MUSIC OFF.png")),
            "home":pygame.image.load(get_path("assets","images","THE HOUSE.png")),
            "right_arrow":pygame.image.load(get_path("assets","images","_arrow_right.png")),
            "right_double_arrow":pygame.image.load(get_path("assets","images","_arrow_righter.png")),
            "left_arrow":pygame.image.load(get_path("assets","images","_arrow_left.png")),
            "left_double_arrow":pygame.image.load(get_path("assets","images","_arrow_lefter.png")),
            "tutorial_fr":pygame.image.load(get_path("assets","images","book_fr.png")),
            "tutorial_en":pygame.image.load(get_path("assets","images","book_en.png")),
            "trap":pygame.image.load(get_path("assets","images","trap.png")),
            "key":pygame.image.load(get_path("assets","images","key.png")),
            "star":pygame.image.load(get_path("assets","images","STAR.png")),
            "completed":pygame.image.load(get_path("assets","images","YES.png")),
            "torch":pygame.image.load(get_path("assets","images","Light.png")),

            "menu_music":pygame.mixer.Sound(get_path("assets","sounds","_cool_menu_music.mp3")),
            "music_victory":pygame.mixer.Sound(get_path("assets","sounds","_victory.mp3")),
            "music_level1":pygame.mixer.Sound(get_path("assets","sounds","_level1.mp3")),
            "music_level2":pygame.mixer.Sound(get_path("assets","sounds","_level2.mp3")),
            "music_level3":pygame.mixer.Sound(get_path("assets","sounds","_level3.mp3")),
            "music_level4":pygame.mixer.Sound(get_path("assets","sounds","_level4.mp3")),
            "music_level42":pygame.mixer.Sound(get_path("assets","sounds","_level42.mp3")),

            "sfx_death":pygame.mixer.Sound(get_path("assets","sounds","sfx","sfx_reset.ogg")),
            "sfx_teleport":pygame.mixer.Sound(get_path("assets","sounds","sfx","sfx_teleport.ogg")),
            "sfx_win":pygame.mixer.Sound(get_path("assets","sounds","sfx","sfx_win.ogg")),
            "sfx_unlock":pygame.mixer.Sound(get_path("assets","sounds","sfx","sfx_unlock.ogg")),
            "sfx_play":pygame.mixer.Sound(get_path("assets","sounds","sfx","sfx_play.ogg")),
            "sfx_key":pygame.mixer.Sound(get_path("assets","sounds","sfx","sfx_key.ogg")),
            
            "font_main":pygame.font.Font(None, 144),
            "font_medium":pygame.font.Font(None, 64),
            "font_small":pygame.font.Font(None, 40)
            } 
    return assets