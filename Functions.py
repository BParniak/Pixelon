from colorama import init, Fore, Back, Style

import Mappings
init(autoreset=True)
import random

# Rarities

RARITY_COLORS = {
    "common": Fore.WHITE,
    "uncommon": Fore.LIGHTGREEN_EX,
    "rare": Fore.BLUE,
    "epic": Fore.MAGENTA,
    "legendary": Fore.RED
}

def format_item_name(item_id, ITEMS):
    item = ITEMS[item_id]
    rarity = item.get("rarity", "common")

    color = RARITY_COLORS.get(rarity, Fore.WHITE)
    name = item_id.replace("_", " ").title()

    return f"{color}{name}{Fore.RESET}"

# --- RENDER FUNCTION ---
def render(sprite, mapping=Mappings.default_mapping):
    lines = []

    for row in sprite:
        rendered_row = ""

        for char in row:
            entry = mapping.get(char, (" ", ""))

            symbol = entry[0]
            fg = entry[1] if len(entry) > 1 else ""
            bg = entry[2] if len(entry) > 2 else ""

            rendered_row += f"{fg}{bg}{symbol}{Style.RESET_ALL}"

        lines.append(rendered_row)

    return "\n".join(lines) + Style.RESET_ALL

# --- EXAMPLE SPRITE ---
sprite = [
    "..GGGG..",
    ".GRRRRG.",
    "GRRRRRRG",
    ".GRRRRG.",
    "..GGGG.."
]

def move_cursor(row, col):
    print(f"\033[{row};{col}H", end="")

class sprite:
    def __init__(self, sprite, mapping=Mappings.default_mapping):
        self.sprite = sprite
        self.mapping = mapping
    
    def render(self):
        return render(self.sprite, self.mapping)
    
    def __str__(self):
        return self.render()

def roll_loot(enemy):
    drops = []

    for reward in enemy.get("loot", []):
        if random.random() <= reward["chance"]:

            r_type = reward["type"]

            if r_type == "item":
                qty = random.randint(reward["min"], reward["max"])
                drops.append(("item", reward["id"], qty))

            elif r_type == "coins":
                qty = random.randint(reward["min"], reward["max"])
                drops.append(("coins", qty))

            elif r_type == "xp":
                qty = random.randint(reward["min"], reward["max"])
                drops.append(("xp", qty))

    return drops

def add_item(inv, item_id, qty, item_data):
    limit = item_data.get("stack_limit", None)

    if limit is None:
        inv.setdefault(item_id, []).append(qty)
        return

    inv.setdefault(item_id, [])

    for i in range(len(inv[item_id])):
        space = limit - inv[item_id][i]
        if space > 0:
            take = min(space, qty)
            inv[item_id][i] += take
            qty -= take

    while qty > 0:
        take = min(limit, qty)
        inv[item_id].append(take)
        qty -= take

def apply_loot(enemy, inventory, ITEMS, player_state):
    loot = roll_loot(enemy)

    drops = {
        "items": [],
        "coins": 0,
        "xp": 0
    }

    for drop in loot:
        if drop[0] == "item":
            _, item_id, qty = drop
            add_item(inventory, item_id, qty, ITEMS[item_id])
            drops["items"].append((item_id, qty))

        elif drop[0] == "coins":
            _, qty = drop
            player_state["coins"] += qty
            drops["coins"] += qty

        elif drop[0] == "xp":
            _, qty = drop
            player_state["xp"] += qty
            drops["xp"] += qty

    return drops