from pathlib import Path
import json

SAVE_FILE = "save.json"

script_dir = Path(__file__).parent
file_path = script_dir / SAVE_FILE

def save_game(player_state, player_inventory, current_weapon, farm_state=None):
    data = {
        "player_state": player_state,
        "player_inventory": player_inventory,
        "current_weapon": current_weapon,
        "farm_state": farm_state
    }
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def load_game():
    if not file_path.exists():
        return None
    
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return None