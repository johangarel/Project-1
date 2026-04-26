import json
import os
from .assets_manager import get_path

SAVE_FILE = "save.json"

def get_default_save():
    return {
        "total_stars": 0,
        "levels": {}
    }

def save_game(data):
    path = get_path(SAVE_FILE)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def load_game():
    path = get_path(SAVE_FILE) 
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return get_default_save()