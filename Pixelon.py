import Data
import Functions
import Save

from colorama import init, Fore, Back, Style
init(autoreset=True)
import time
import os
import sys
import pygame
import random
import math
from datetime import datetime
from pathlib import Path
import msvcrt
from blessed import Terminal
term = Terminal()
      
def delete_lines(n):
  for _ in range(n):
    sys.stdout.write("\x1b[1A")
    sys.stdout.write("\x1b[2K")

def clear():
    sys.stdout.write("\x1b[2J\x1b[H")
    sys.stdout.flush()

def invalid_input():
    print(f"{Fore.RED}{Style.BRIGHT}Invalid input")
    time.sleep(1.5)

def flush_input():
    while True:
        key = term.inkey(timeout=0)
        if not key:
            break

def print_drops(drops):
    for item_id, qty in drops["items"]:
        print(f"+ {Functions.format_item_name(item_id, Data.ITEMS)} x {qty}")

    if drops["coins"] > 0:
        print(f"+ {Fore.YELLOW}{drops['coins']} coins{Style.RESET_ALL}")

    if drops["xp"] > 0:
        print(f"+ {Fore.LIGHTGREEN_EX}{drops['xp']} XP{Style.RESET_ALL}")

def sell_from_stack(item_id, stack_index, amount):
    global player_inventory, player_state

    stacks = player_inventory[item_id]

    # safety clamp
    amount = min(amount, stacks[stack_index])

    stacks[stack_index] -= amount

    # remove empty stack
    if stacks[stack_index] <= 0:
        stacks.pop(stack_index)

    # remove item entirely if no stacks left
    if not stacks:
        del player_inventory[item_id]

    # coins
    price = Data.ITEMS[item_id]["sell_price"]
    player_state["coins"] += price * amount

    return amount * price  # for feedback if you want

def remove_from_stack(item_id, stack_index, amount):
    global player_inventory

    stacks = player_inventory[item_id]

    amount = min(amount, stacks[stack_index])

    stacks[stack_index] -= amount

    if stacks[stack_index] <= 0:
        stacks.pop(stack_index)

    if not stacks:
        del player_inventory[item_id]

    return amount

def update_farm_growth():
    plot = farm_state["plot"]

    if plot["crop_id"] is None:
        return False

    crop = Data.CROPS[plot["crop_id"]]
    elapsed = time.time() - plot["planted_at"]

    if elapsed >= crop["growth_time"] and plot["stage"] != 1:
        plot["stage"] = 1
        return True

    return False

def get_crop_display_height():
    max_height = 0

    for crop in Data.CROPS.values():
        for stage in crop["stages"]:
            max_height = max(max_height, len(stage["sprite"]))

    return max_height

def draw_farm_plot():
    plot = farm_state["plot"]
    crop_height = get_crop_display_height()

    if plot["crop_id"] is not None:
        print(grow(plot["crop_id"], plot["stage"]))
    else:
        print("\n" * crop_height, end="")

    print(till("soil"))


def get_plantable_items():
    plantable_items = []

    for item_id, stacks in player_inventory.items():
        if Data.ITEMS[item_id].get("type") == "plantable":
            for i, qty in enumerate(stacks):
                plantable_items.append({
                    "id": item_id,
                    "qty": qty,
                    "stack_ref": i
                })

    return plantable_items

def harvest_crop(crop_id):
    crop = Data.CROPS[crop_id]

    drops = {
        "items": [],
        "coins": 0,
        "xp": 0
    }

    for reward in crop.get("loot", []):
        if random.random() <= reward["chance"]:
            qty = random.randint(reward["min"], reward["max"])

            if reward["type"] == "item":
                item_id = reward["id"]
                Functions.add_item(player_inventory, item_id, qty, Data.ITEMS[item_id])
                drops["items"].append((item_id, qty))

            elif reward["type"] == "coins":
                player_state["coins"] += qty
                drops["coins"] += qty

            elif reward["type"] == "xp":
                player_state["xp"] += qty
                drops["xp"] += qty

    return drops

def count_item_total(item_id):
    return sum(player_inventory.get(item_id, []))

def recipe_outputs_weapon(recipe_id):
    recipe = Data.RECIPES[recipe_id]

    for result in recipe["results"]:
        if is_weapon(result["id"]):
            return True

    return False

def can_craft(recipe_id, amount=1):
    recipe = Data.RECIPES[recipe_id]

    for material in recipe["materials"]:
        needed = material["qty"] * amount

        if count_item_total(material["id"]) < needed:
            return False

    if recipe_outputs_weapon(recipe_id):
        return True

    weapons_consumed = 0

    for material in recipe["materials"]:
        if is_weapon(material["id"]):
            weapons_consumed += material["qty"] * amount

    if weapons_consumed > 0 and count_weapons() - weapons_consumed < 1:
        return False

    return True

def max_craftable_amount(recipe_id):
    recipe = Data.RECIPES[recipe_id]
    max_amount = None

    for material in recipe["materials"]:
        owned = count_item_total(material["id"])
        possible = owned // material["qty"]

        if max_amount is None:
            max_amount = possible
        else:
            max_amount = min(max_amount, possible)

    if max_amount is None:
        max_amount = 0

    if recipe_outputs_weapon(recipe_id):
        return max_amount

    weapons_consumed_per_craft = 0

    for material in recipe["materials"]:
        if is_weapon(material["id"]):
            weapons_consumed_per_craft += material["qty"]

    if weapons_consumed_per_craft > 0:
        max_by_weapon_safety = max(0, (count_weapons() - 1) // weapons_consumed_per_craft)
        max_amount = min(max_amount, max_by_weapon_safety)

    return max_amount

def remove_item_amount(item_id, amount):
    remaining = amount

    while remaining > 0 and item_id in player_inventory:
        take = min(player_inventory[item_id][0], remaining)
        remove_from_stack(item_id, 0, take)
        remaining -= take

def unequip_if_removing_current_weapon(item_id, amount):
        global current_weapon

        if item_id == current_weapon and amount > 0:
            current_weapon = None

def craft_recipe(recipe_id, amount):
    recipe = Data.RECIPES[recipe_id]

    if not can_craft(recipe_id, amount):
        return False

    for material in recipe["materials"]:
        remove_amount = material["qty"] * amount
        unequip_if_removing_current_weapon(material["id"], remove_amount)
        remove_item_amount(material["id"], remove_amount)

    for result in recipe["results"]:
        Functions.add_item(player_inventory, result["id"], result["qty"] * amount, Data.ITEMS[result["id"]])

    Save.save_game(player_state, player_inventory, current_weapon, farm_state)

    return True

def format_recipe_result(recipe_id, amount=1):
    recipe = Data.RECIPES[recipe_id]
    parts = []

    for result in recipe["results"]:
        name = Functions.format_item_name(result["id"], Data.ITEMS)
        qty = result["qty"] * amount
        parts.append(f"{name} x {qty}")

    return ", ".join(parts)

def format_recipe_materials(recipe_id):
    recipe = Data.RECIPES[recipe_id]
    parts = []

    for material in recipe["materials"]:
        owned = count_item_total(material["id"])
        needed = material["qty"]
        name = Functions.format_item_name(material["id"], Data.ITEMS)
        parts.append(f"{name} x {needed} ({owned})")

    return ", ".join(parts)

def format_store_product(store_id, amount=1):
    product = Data.STORE_ITEMS[store_id]
    parts = []

    for result in product["results"]:
        name = Functions.format_item_name(result["id"], Data.ITEMS)
        qty = result["qty"] * amount
        parts.append(f"{name} x {qty}")

    return ", ".join(parts)

def format_store_price(store_id, amount=1):
    price = Data.STORE_ITEMS[store_id]["price"] * amount
    return f"{price} coins"

def max_buyable_amount(store_id):
    price = Data.STORE_ITEMS[store_id]["price"]

    if price <= 0:
        return 0

    return player_state["coins"] // price

def buy_store_item(store_id, amount):
    total_price = Data.STORE_ITEMS[store_id]["price"] * amount

    if amount <= 0:
        return False

    if player_state["coins"] < total_price:
        return False

    player_state["coins"] -= total_price

    for result in Data.STORE_ITEMS[store_id]["results"]:
        Functions.add_item(
            player_inventory,
            result["id"],
            result["qty"] * amount,
            Data.ITEMS[result["id"]]
        )

    Save.save_game(player_state, player_inventory, current_weapon, farm_state)

    return True

player_inventory = {}

player_state = {
    "coins": 0,
    "xp": 0,
    "level": 1,
    "unlocked_worlds": [],
    "enemies_defeated": {}
}

inventory_message = ""

farm_state = {
    "plot": {
        "crop_id": None,
        "planted_at": None,
        "stage": None
    }
}

def summon(name):
    data = Data.ENEMIES[name]
    return Functions.sprite(data["sprite"], data["mapping"])

def make(name):
    data = Data.ITEMS[name]
    return Functions.sprite(data["sprite"], data["mapping"])

def grow(crop_id, stage):
    data = Data.CROPS[crop_id]["stages"][stage]
    return Functions.sprite(data["sprite"], data["mapping"])

def till(soil_id):
    data = Data.SOILS[soil_id]
    return Functions.sprite(data["sprite"], data["mapping"])

def is_weapon(item_id):
    return item_id in Data.ITEMS and Data.ITEMS[item_id].get("type") == "weapon"

def count_item(item_id):
    return sum(player_inventory.get(item_id, []))

def count_weapons():
    total = 0

    for item_id, stacks in player_inventory.items():
        if is_weapon(item_id):
            total += sum(stacks)

    return total

def find_first_weapon():
    for item_id, stacks in player_inventory.items():
        if is_weapon(item_id) and sum(stacks) > 0:
            return item_id

    return None

def ensure_weapon_safety():
    global current_weapon

    if count_weapons() <= 0:
        Functions.add_item(player_inventory, "stick", 1, Data.ITEMS["stick"])

    if current_weapon is None:
        return

    if not is_weapon(current_weapon):
        current_weapon = None
        return

    if count_item(current_weapon) <= 0:
        current_weapon = None

def has_equipped_weapon():
    return current_weapon is not None and is_weapon(current_weapon) and count_item(current_weapon) > 0


def max_removable_amount(item_id, replacement_item_id=None):
    owned = count_item(item_id)

    if not is_weapon(item_id):
        return owned

    if replacement_item_id and is_weapon(replacement_item_id):
        return owned

    weapons_total = count_weapons()

    return max(0, weapons_total - 1)

def choose_enemy(world_id):
    world = Data.WORLDS[world_id]

    enemy_ids = list(world["enemies"].keys())
    weights = list(world["enemies"].values())

    return random.choices(enemy_ids, weights=weights, k=1)[0]

def is_world_unlocked(world_id):
    return world_id in player_state["unlocked_worlds"]

def get_world_unlock_message(world_id):
    world = Data.WORLDS[world_id]
    conditions = world.get("unlock_conditions", {})

    requirements = []

    if "level" in conditions:
        current = player_state["level"]
        req = conditions["level"]
        met = current >= req
        color = Fore.GREEN if met else Fore.RED
        requirements.append(f"{color}Level {req} ({current}/{req}){Fore.RESET}")

    if "coins" in conditions:
        current = player_state["coins"]
        req = conditions["coins"]
        met = current >= req
        color = Fore.GREEN if met else Fore.RED
        requirements.append(f"{color}{req} coins ({current}/{req}){Fore.RESET}")

    for item_id, required_qty in conditions.get("items", {}).items():
        current_qty = count_item_total(item_id)
        met = current_qty >= required_qty
        color = Fore.GREEN if met else Fore.RED
        name = Functions.format_item_name(item_id, Data.ITEMS)
        requirements.append(f"{name} {color}x {required_qty} ({current_qty}/{required_qty}){Fore.RESET}")

    for enemy_id, required_count in conditions.get("enemies_defeated", {}).items():
        current_kills = player_state["enemies_defeated"].get(enemy_id, 0)
        met = current_kills >= required_count
        color = Fore.GREEN if met else Fore.RED
        enemy_name = format_enemy_name(enemy_id)
        requirements.append(f"{color}Defeat {enemy_name} x {required_count} ({current_kills}/{required_count}){Fore.RESET}")

    for required_world_id in conditions.get("worlds", []):
        met = required_world_id in player_state["unlocked_worlds"]
        color = Fore.GREEN if met else Fore.RED
        world_name = Data.WORLDS[required_world_id]["name"]
        status = "(Unlocked)" if met else "(Locked)"
        requirements.append(f"{color}Unlock {world_name} {status}{Fore.RESET}")

    if not requirements:
        return "This world is locked"

    return f"{Fore.RESET}Requires " + ", ".join(requirements)

def initialize_unlocked_worlds():
    for world_id, world in Data.WORLDS.items():
        if world.get("unlocked_by_default"):
            if world_id not in player_state["unlocked_worlds"]:
                player_state["unlocked_worlds"].append(world_id)

def world_requirements_met(world_id):
    world = Data.WORLDS[world_id]
    conditions = world.get("unlock_conditions", {})

    if player_state["level"] < conditions.get("level", 1):
        return False

    if player_state["coins"] < conditions.get("coins", 0):
        return False

    for item_id, required_qty in conditions.get("items", {}).items():
        if count_item_total(item_id) < required_qty:
            return False

    for enemy_id, required_count in conditions.get("enemies_defeated", {}).items():
        defeated_count = player_state["enemies_defeated"].get(enemy_id, 0)

        if defeated_count < required_count:
            return False

    for required_world_id in conditions.get("worlds", []):
        if required_world_id not in player_state["unlocked_worlds"]:
            return False

    return True

def update_world_unlocks():
    unlocked_any = False

    for world_id in Data.WORLDS:
        if is_world_unlocked(world_id):
            continue

        if world_requirements_met(world_id):
            player_state["unlocked_worlds"].append(world_id)
            unlocked_any = True

    if unlocked_any:
        Save.save_game(player_state, player_inventory, current_weapon, farm_state)

def record_enemy_defeat(enemy_id):
    defeated = player_state["enemies_defeated"]
    defeated[enemy_id] = defeated.get(enemy_id, 0) + 1

def health_bar(current_health, max_health, width=15):
    current_health = max(0, current_health)
    filled = round((current_health / max_health) * width)
    empty = width - filled

    if current_health / max_health > 0.5:
        color = Fore.GREEN
    elif current_health / max_health > 0.25:
        color = Fore.YELLOW
    else:
        color = Fore.RED

    bar = f"{color}{'█' * filled}{Fore.LIGHTBLACK_EX}{'░' * empty}{Style.RESET_ALL}"

    return f"{bar} {current_health}/{max_health} {Fore.RED}✚"

def format_enemy_name(enemy_id):
    return enemy_id.replace("_", " ").title()

def get_enemy_time_left(enemy_state):
    if enemy_state["time_limit"] is None:
        return None

    elapsed = time.time() - enemy_state["spawned_at"]
    return enemy_state["time_limit"] - elapsed

def time_bar(time_left, max_time, width=15):
    time_left = max(0, time_left)

    filled = round((time_left / max_time) * width)
    empty = width - filled

    bar = f"{Fore.BLUE}{'█' * filled}{Fore.LIGHTBLACK_EX}{'░' * empty}{Style.RESET_ALL}"

    return f"{bar} {time_left:.1f}s {Fore.BLUE}⏱︎"

def create_enemy_state(enemy_id):
    enemy_data = Data.ENEMIES[enemy_id]
    time_limit = enemy_data.get("time_limit")

    return {
        "id": enemy_id,
        "health": enemy_data["health"],
        "max_health": enemy_data["health"],
        "time_limit": time_limit,
        "spawned_at": time.time() if time_limit is not None else None
    }

def print_enemy_header(enemy_state):
    print(f"{Style.BRIGHT}{format_enemy_name(enemy_state['id'])}")
    print(health_bar(enemy_state["health"], enemy_state["max_health"]))

    if enemy_state["time_limit"] is not None:
        time_left = get_enemy_time_left(enemy_state)
        print(time_bar(time_left, enemy_state["time_limit"]))

def enemy_escaped(enemy_state):
    time_left = get_enemy_time_left(enemy_state)

    return (
        enemy_state["time_limit"] is not None
        and time_left <= 0
        and enemy_state["health"] > 0
    )

def wait_for_combat_input(enemy_state):
    while True:
        if enemy_escaped(enemy_state):
            return "escape"

        if msvcrt.kbhit():
            key = msvcrt.getwch()

            if key == "\r":
                return ""

            if key.lower() == "b":
                return "b"

            return "invalid"

        time.sleep(0.05)

def xp_required_for_level(level):
    if level <= 1:
        return 0

    total_xp = 0

    for current_level in range(2, level + 1):
        total_xp += 100 * (1.2 ** (current_level - 2))

    return round(total_xp)

def xp_bar(width=15):
    current_xp = player_state["xp"]
    current_level = player_state["level"]

    current_level_required_xp = xp_required_for_level(current_level)
    next_level_required_xp = xp_required_for_level(current_level + 1)

    xp_into_current_level = current_xp - current_level_required_xp
    xp_needed_for_next_level = next_level_required_xp - current_level_required_xp

    xp_into_current_level = max(0, xp_into_current_level)

    progress = xp_into_current_level / xp_needed_for_next_level
    progress = max(0, min(progress, 1))

    filled = round(progress * width)
    empty = width - filled

    bar = f"\033[38;2;57;255;20m{'█' * filled}{Fore.LIGHTBLACK_EX}{'░' * empty}{Style.RESET_ALL}" # Neon green color

    return f"Level {current_level} {bar} {xp_into_current_level}/{xp_needed_for_next_level} XP"

def update_player_level():
    while player_state["xp"] >= xp_required_for_level(player_state["level"] + 1):
        player_state["level"] += 1

current_weapon = "stick"
current_enemy = "green_slime"
current_world = None

data = Save.load_game()

if data:
    player_state = data.get("player_state", player_state)
    player_inventory = data.get("player_inventory", {})
    current_weapon = data.get("current_weapon", current_weapon)
    farm_state = data.get("farm_state", farm_state)

ensure_weapon_safety()
initialize_unlocked_worlds()

clear()
print(f"{Style.BRIGHT}Welcome to Pixelon!")
time.sleep(2)
clear()

def main_menu():
    global player_state, player_inventory, current_weapon
    while True:
        clear()
        print(f"{Style.BRIGHT}Pixelon\n")
        print("1. Start Game 🎮")
        print("2. Inventory 🧰")
        print("3. Crafting 🛠")
        print("4. Farm 🌾")
        print("5. Store 🛒")
        print("6. Save and Exit ❌")
        print("7. Delete Save 🗑")
        print("")
        choice = input("Enter the number of your choice to select: ").lower()

        if choice == "1":
            ensure_weapon_safety()
            if not has_equipped_weapon():
                print(f"{Fore.RED}{Style.BRIGHT}You must equip a weapon")
                time.sleep(2)
                continue
            return "world_selection"
        elif choice == "2":
            return "inventory"
        elif choice == "3":
            return "crafting"
        elif choice == "4":
            return "farm"
        elif choice == "5":
            return "store"
        elif choice == "6":
            Save.save_game(player_state, player_inventory, current_weapon, farm_state)
            print(f"{Fore.GREEN}{Style.BRIGHT}Game saved successfully. Exiting...")
            time.sleep(1)
            return "exit"
        elif choice == "7":
            clear()
            confirm = input(f"{Fore.RED}{Style.BRIGHT}Are you sure you want to delete your save? This action cannot be undone. (y/n): {Style.RESET_ALL}").lower()
            if confirm == "y":
                player_state = {
                    "coins": 0,
                    "xp": 0,
                    "level": 1,
                    "unlocked_worlds": [],
                    "enemies_defeated": {}
                }

                player_inventory = {}
                current_weapon = "stick"

                ensure_weapon_safety()
                initialize_unlocked_worlds()
                if Save.file_path.exists():
                    Save.file_path.unlink()
                print("Save deleted")
                time.sleep(2)
                return "main_menu"
            else:
                print("Save deletion cancelled")
                time.sleep(2)
        else:
            invalid_input()

def world_selection():
    global current_world

    error_message = ""

    while True:
        update_world_unlocks()
        clear()
        print(f"{Style.BRIGHT}World Selection\n")

        world_ids = list(Data.WORLDS.keys())

        for i, world_id in enumerate(world_ids, start=1):
            world = Data.WORLDS[world_id]
            name = world["name"]

            if is_world_unlocked(world_id):
                print(f"{i}. {name}")
            else:
                print(f"{i}. {Fore.LIGHTBLACK_EX}{name} (Locked){Style.RESET_ALL}")

        if error_message:
            print(f"\nEnter the number of your choice or \"b\" to go back: \n{Fore.RED}{Style.BRIGHT}{error_message}")
            time.sleep(1.5)
            error_message = ""
            continue

        choice = input("\nEnter the number of your choice or \"b\" to go back: ").lower()

        if choice == "b":
            return "main_menu"

        try:
            choice_index = int(choice) - 1
        except:
            error_message = "Invalid input"
            continue

        if choice_index < 0 or choice_index >= len(world_ids):
            error_message = "Invalid input"
            continue

        selected_world = world_ids[choice_index]

        if not is_world_unlocked(selected_world):
            error_message = get_world_unlock_message(selected_world)
            continue

        current_world = selected_world
        return "game"

def game():
    global current_world
    ensure_weapon_safety()

    if not has_equipped_weapon():
        clear()
        print(f"{Fore.RED}{Style.BRIGHT}You must equip a weapon")
        time.sleep(2)
        return "main_menu"
    
    if current_world is None:
        return "world_selection"

    enemy_id = choose_enemy(current_world)
    enemy_data = Data.ENEMIES[enemy_id]
    enemy_state = create_enemy_state(enemy_id)

    drops = []

    while True:
        clear()
        print(f"{Style.BRIGHT}{Data.WORLDS[current_world]['name']}          {xp_bar()}\n")
        print_enemy_header(enemy_state)
        print()
        print(summon(enemy_state["id"]))
        print("\n")
        print(make(current_weapon))
        print()
        print("Press \"Enter\" to attack or \"b\" to go back: ")

        cmd = wait_for_combat_input(enemy_state)

        if cmd == "escape":
            clear()

            enemy_display_height = len(enemy_data["sprite"])

            if enemy_state["time_limit"] is not None:
                enemy_display_height += 1

            enemy_display_height += 2  # enemy name + health bar

            print(f"{Style.BRIGHT}{Data.WORLDS[current_world]['name']}          {xp_bar()}\n")
            sys.stdout.write("\n" * enemy_display_height)
            print(make(current_weapon))
            print()
            print("Press \"Enter\" to attack or \"b\" to go back: ")
            print(f"{Fore.BLUE}{Style.BRIGHT}{format_enemy_name(enemy_state['id'])} has escaped")

            time.sleep(1.5)

            enemy_id = choose_enemy(current_world)
            enemy_data = Data.ENEMIES[enemy_id]
            enemy_state = create_enemy_state(enemy_id)
            continue

        if cmd == "":
            clear()

            damage = Data.ITEMS[current_weapon].get("damage", 0)
            enemy_state["health"] -= damage

            print(f"{Style.BRIGHT}{Data.WORLDS[current_world]['name']}          {xp_bar()}\n")
            print_enemy_header(enemy_state)
            print()
            print(summon(enemy_state["id"]))
            print(make(current_weapon))
            print("\n\n")
            print("Press \"Enter\" to attack or \"b\" to go back: ")

            drops = []

            if enemy_state["health"] <= 0:
                record_enemy_defeat(enemy_state["id"])
                drops = Functions.apply_loot(
                    enemy_data,
                    player_inventory,
                    Data.ITEMS,
                    player_state
                )
                
                update_player_level()
                update_world_unlocks()
                Save.save_game(player_state, player_inventory, current_weapon, farm_state)

                height = len(enemy_data["sprite"])

                print_drops(drops)

                time.sleep(0.5)

                clear()
                print(f"{Style.BRIGHT}{Data.WORLDS[current_world]['name']}          {xp_bar()}\n")
                print_enemy_header(enemy_state)
                sys.stdout.write("\n" * height)
                print("\n\n")
                print(make(current_weapon))
                print()
                print("Press \"Enter\" to attack or \"b\" to go back: ")

                print_drops(drops)

                time.sleep(0.2)

                enemy_id = choose_enemy(current_world)
                enemy_data = Data.ENEMIES[enemy_id]
                enemy_state = create_enemy_state(enemy_id)

                continue

            time.sleep(0.5)

        elif cmd == "b":
            return go_back()

        else:
            invalid_input()

def inventory():
    global inventory_message

    page = 0
    selected = 0
    error_message = ""
    error_time = 0
    show_error_frame = False
    needs_redraw = True

    with term.cbreak():
        while True:

            flat_inventory = []
            for item_id, stacks in player_inventory.items():
                for i, qty in enumerate(stacks):
                    flat_inventory.append({
                        "id": item_id,
                        "qty": qty,
                        "stack_ref": i,
                        "rarity": Data.ITEMS[item_id]["rarity"],
                    })

            height = term.height
            page_size = max(1, height - 7)

            total_pages = max(1, math.ceil(len(flat_inventory) / page_size))
            page = max(0, min(page, total_pages - 1))

            start = page * page_size
            end = start + page_size

            page_items = flat_inventory[start:end]

            if flat_inventory:
                selected = max(0, min(selected, len(page_items) - 1))

            if error_message:
                clear()
                print(f"{Style.BRIGHT}Inventory\n")

                for item in page_items:
                    print(f"  {Functions.format_item_name(item['id'], Data.ITEMS)} x {item['qty']}")

                print(f"\nPage {page + 1}/{total_pages}")
                print("← prev | → next | ⇅ up/down | ↵ select | b back")
                print(f"{Fore.RED}{Style.BRIGHT}{error_message}")

                time.sleep(1)

                flush_input()

                error_message = ""
                clear()
                needs_redraw = True
                continue

            if inventory_message:
                clear()
                print(f"{Style.BRIGHT}Inventory\n")

                if flat_inventory:
                    for i, item in enumerate(page_items):
                        prefix = "▶ " if i == selected else "  "
                        print(f"{prefix}{Functions.format_item_name(item['id'], Data.ITEMS)} x {item['qty']}")

                    print(f"\nPage {page + 1}/{total_pages}")
                    print("← prev | → next | ⇅ up/down | ↵ select | b back")
                else:
                    print("Inventory is empty\n")
                    print("Press 'b' to go back")

                print(f"{Fore.YELLOW}{Style.BRIGHT}{inventory_message}")

                time.sleep(1)

                flush_input()

                inventory_message = ""
                clear()
                needs_redraw = True
                continue

            if not flat_inventory:
                clear()
                print(f"{Style.BRIGHT}Inventory\n")
                print("Inventory is empty\n")
                print("Press 'b' to go back")

                key = term.inkey()
                if key.lower() == "b":
                    return go_back()
                continue

            if needs_redraw:
                clear()
                print(f"{Style.BRIGHT}Inventory\n")

                for i, item in enumerate(page_items):
                    prefix = "▶ " if i == selected else "  "
                    print(f"{prefix}{Functions.format_item_name(item['id'], Data.ITEMS)} x {item['qty']}")

                print(f"\nPage {page + 1}/{total_pages}")
                print("← prev | → next | ⇅ up/down | ↵ select | b back")

                needs_redraw = False

            key = term.inkey()

            if not key:
                continue

            if key.name == "KEY_UP":
                if selected > 0:
                    selected -= 1
                    needs_redraw = True

            elif key.name == "KEY_DOWN":
                if selected < len(page_items) - 1:
                    selected += 1
                    needs_redraw = True

            elif key.name == "KEY_LEFT":
                if page > 0:
                    page -= 1
                    selected = 0
                    needs_redraw = True

            elif key.name == "KEY_RIGHT":
                if page < total_pages - 1:
                    page += 1
                    selected = 0
                    needs_redraw = True

            elif key.name == "KEY_ENTER" or key == "\n":
                selected_item = page_items[selected]
                return ("item_selection", selected_item)

            elif key.lower() == "b":
                return go_back()

            else:
                error_message = "Invalid input"
                needs_redraw = True

def item_selection(item=None):
    global inventory_message, current_weapon

    sale_message = ""

    def get_stack():
        stacks = player_inventory.get(item["id"], [])
        if item["stack_ref"] >= len(stacks):
            return None, stacks
        return stacks[item["stack_ref"]], stacks

    while True:

        if sale_message:
            clear()
            print(f"{Style.BRIGHT}Item Selection\n")

            if not item:
                print("No item selected.")
            else:
                name = Functions.format_item_name(item["id"], Data.ITEMS)
                print(f"{name} x {item['qty']}\n")

            item_data = Data.ITEMS[item["id"]]
            item_type = item_data.get("type", "material")
            actions = Data.ITEM_ACTIONS.get(item_type, [])

            option_number = 1

            for action in actions:
                print(f"{option_number}. {action.capitalize()}")
                option_number += 1

            print(f"{option_number}. Sell 1")
            option_number += 1

            print(f"{option_number}. Sell stack")
            option_number += 1

            print(f"{option_number}. Sell all")
            option_number += 1

            print(f"{option_number}. Sell custom amount")
            option_number += 1

            print("b. Back\n")
            print(sale_message)

            time.sleep(1)
            flush_input()

            sale_message = ""
            clear()

        clear()
        print(f"{Style.BRIGHT}Item Selection\n")

        if not item:
            print("No item selected.")
            time.sleep(1)
            return "inventory"

        name = Functions.format_item_name(item["id"], Data.ITEMS)
        print(f"{name} x {item['qty']}\n")

        item_data = Data.ITEMS[item["id"]]
        item_type = item_data.get("type", "material")
        actions = Data.ITEM_ACTIONS.get(item_type, [])

        option_map = {}
        option_number = 1

        for action in actions:
            print(f"{option_number}. {action.capitalize()}")
            option_map[str(option_number)] = action
            option_number += 1

        print(f"{option_number}. Sell 1")
        option_map[str(option_number)] = "sell_1"
        option_number += 1

        print(f"{option_number}. Sell stack")
        option_map[str(option_number)] = "sell_stack"
        option_number += 1

        print(f"{option_number}. Sell all")
        option_map[str(option_number)] = "sell_all"
        option_number += 1

        print(f"{option_number}. Sell custom amount")
        option_map[str(option_number)] = "sell_custom"
        option_number += 1

        print("b. Back\n")

        choice = input("> ").lower()

        if choice == "b":
            return "inventory"

        action = option_map.get(choice)

        if not action:
            invalid_input()
            continue

        if action == "equip":
            current_weapon = item["id"]
            Save.save_game(player_state, player_inventory, current_weapon, farm_state)
            sale_message = f">\n{Fore.GREEN}{Style.BRIGHT}You have equipped {name}"
            continue

        elif action == "consume":
            print("Consume logic here")
            time.sleep(1)
            continue

        elif action == "plant":
            plot = farm_state["plot"]

            if plot["crop_id"] is not None:
                sale_message = f">\n{Fore.RED}{Style.BRIGHT}Something is already planted"
                continue

            crop_id = Data.ITEMS[item["id"]].get("crop_id")

            if crop_id is None:
                sale_message = f">\n{Fore.RED}{Style.BRIGHT}This item cannot be planted"
                continue

            remove_from_stack(item["id"], item["stack_ref"], 1)

            plot["crop_id"] = crop_id
            plot["planted_at"] = time.time()
            plot["stage"] = 0

            Save.save_game(player_state, player_inventory, current_weapon, farm_state)

            return "farm"

        elif action == "use":
            print("Use logic here")
            time.sleep(1)
            continue

        elif action == "sell_1":
            max_sellable = max_removable_amount(item["id"])

            if max_sellable < 1:
                sale_message = f">\n{Fore.RED}{Style.BRIGHT}You must keep at least one weapon"
                continue

            sold_whole_stack = item["qty"] <= 1

            unequip_if_removing_current_weapon(item["id"], 1)
            coins_gained = sell_from_stack(item["id"], item["stack_ref"], 1)
            Save.save_game(player_state, player_inventory, current_weapon, farm_state)

            if sold_whole_stack:
                inventory_message = f"+ {coins_gained} coins"
                return "inventory"

            sale_message = f">\n{Fore.YELLOW}{Style.BRIGHT}+ {coins_gained} coins"

            stack, stacks = get_stack()

            if not stacks or stack is None:
                inventory_message = f"+ {coins_gained} coins"
                return "inventory"

            item["qty"] = stack

        elif action == "sell_stack":
            max_sellable = max_removable_amount(item["id"])
            amount = min(item["qty"], max_sellable)

            if amount <= 0:
                sale_message = f">\n{Fore.RED}{Style.BRIGHT}You must keep at least one weapon"
                continue

            unequip_if_removing_current_weapon(item["id"], amount)
            coins_gained = sell_from_stack(item["id"], item["stack_ref"], amount)
            Save.save_game(player_state, player_inventory, current_weapon, farm_state)

            if amount >= item["qty"]:
                inventory_message = f"+ {coins_gained} coins"
                return "inventory"

            sale_message = f">\n{Fore.YELLOW}{Style.BRIGHT}+ {coins_gained} coins"

            stack, stacks = get_stack()

            if not stacks or stack is None:
                inventory_message = f"+ {coins_gained} coins"
                return "inventory"

            item["qty"] = stack

        elif action == "sell_all":
            max_sellable = max_removable_amount(item["id"])

            if max_sellable <= 0:
                sale_message = f">\n{Fore.RED}{Style.BRIGHT}You must keep at least one weapon"
                continue

            price = Data.ITEMS[item["id"]]["sell_price"]
            coins_gained = 0
            remaining = max_sellable

            unequip_if_removing_current_weapon(item["id"], max_sellable)

            stacks = player_inventory[item["id"]]

            i = 0
            while i < len(stacks) and remaining > 0:
                take = min(stacks[i], remaining)
                stacks[i] -= take
                remaining -= take
                coins_gained += take * price

                if stacks[i] <= 0:
                    stacks.pop(i)
                else:
                    i += 1

            if not stacks:
                del player_inventory[item["id"]]

            player_state["coins"] += coins_gained
            Save.save_game(player_state, player_inventory, current_weapon, farm_state)

            inventory_message = f"+ {coins_gained} coins"
            return "inventory"

        elif action == "sell_custom":
            try:
                amount = int(input("Enter amount: "))
            except:
                invalid_input()
                continue

            if amount <= 0:
                print(f"{Fore.RED}{Style.BRIGHT}Enter a positive amount")
                time.sleep(1.5)
                continue

            max_sellable = max_removable_amount(item["id"])

            if amount > max_sellable:
                print(f"{Fore.RED}{Style.BRIGHT}The most you can sell is {max_sellable}")
                time.sleep(2)
                continue

            exit_after = amount >= item["qty"]

            price = Data.ITEMS[item["id"]]["sell_price"]
            coins_gained = amount * price
            player_state["coins"] += coins_gained

            unequip_if_removing_current_weapon(item["id"], amount)

            remaining = amount
            stacks = player_inventory[item["id"]]

            i = 0
            while i < len(stacks) and remaining > 0:
                take = min(stacks[i], remaining)
                stacks[i] -= take
                remaining -= take

                if stacks[i] <= 0:
                    stacks.pop(i)
                else:
                    i += 1

            Save.save_game(player_state, player_inventory, current_weapon, farm_state)

            if not stacks:
                del player_inventory[item["id"]]
                inventory_message = f"+ {coins_gained} coins"
                return "inventory"

            stack, stacks = get_stack()

            if not stacks or stack is None:
                inventory_message = f"+ {coins_gained} coins"
                return "inventory"

            item["qty"] = stack

            if exit_after:
                inventory_message = f"+ {coins_gained} coins"
                return "inventory"

            sale_message = f">\n{Fore.YELLOW}{Style.BRIGHT}+ {coins_gained} coins"

def crafting():
    page = 0
    selected = 0
    error_message = ""
    needs_redraw = True

    with term.cbreak():
        while True:
            recipe_ids = list(Data.RECIPES.keys())

            if not recipe_ids:
                clear()
                print(f"{Style.BRIGHT}Crafting\n")
                print("You have no recipes\n")
                print("Press 'b' to go back")

                key = term.inkey()
                if key.lower() == "b":
                    return go_back()
                continue

            height = term.height
            page_size = max(1, (height - 7) // 3)

            total_pages = max(1, math.ceil(len(recipe_ids) / page_size))
            page = max(0, min(page, total_pages - 1))

            start = page * page_size
            end = start + page_size
            page_recipes = recipe_ids[start:end]

            selected = max(0, min(selected, len(page_recipes) - 1))

            if needs_redraw:
                clear()
                print(f"{Style.BRIGHT}Crafting\n")

                for i, recipe_id in enumerate(page_recipes):
                    prefix = "▶ " if i == selected else "  "
                    print(f"{prefix}{format_recipe_result(recipe_id)}")
                    print(f"    Ingredients: {format_recipe_materials(recipe_id)}\n")

                print(f"Page {page + 1}/{total_pages}")
                print("← prev | → next | ⇅ up/down | ↵ select | b back")

                needs_redraw = False

            if error_message:
                clear()
                print(f"{Style.BRIGHT}Crafting\n")

                for i, recipe_id in enumerate(page_recipes):
                    prefix = "▶ " if i == selected else "  "
                    print(f"{prefix}{format_recipe_result(recipe_id)}")
                    print(f"    Ingredients: {format_recipe_materials(recipe_id)}\n")

                print(f"Page {page + 1}/{total_pages}")
                print("← prev | → next | ⇅ up/down | ↵ select | b back")
                print(f"{Fore.RED}{Style.BRIGHT}{error_message}")

                time.sleep(1)
                error_message = ""
                flush_input()
                needs_redraw = True
                continue

            key = term.inkey()

            if not key:
                continue

            if key.name == "KEY_UP":
                if selected > 0:
                    selected -= 1
                    needs_redraw = True

            elif key.name == "KEY_DOWN":
                if selected < len(page_recipes) - 1:
                    selected += 1
                    needs_redraw = True

            elif key.name == "KEY_LEFT":
                if page > 0:
                    page -= 1
                    selected = 0
                    needs_redraw = True

            elif key.name == "KEY_RIGHT":
                if page < total_pages - 1:
                    page += 1
                    selected = 0
                    needs_redraw = True

            elif key.name == "KEY_ENTER" or key == "\n":
                selected_recipe = page_recipes[selected]
                return ("craft_item", selected_recipe)

            elif key.lower() == "b":
                return go_back()

            else:
                error_message = "Invalid input"
                needs_redraw = True

def craft_item(recipe_id=None):
    message = ""

    while True:
        clear()
        print(f"{Style.BRIGHT}Craft Item\n")

        if recipe_id is None:
            print("No recipe selected.")
            time.sleep(1)
            return "crafting"

        print(format_recipe_result(recipe_id))
        print(f"Needs: {format_recipe_materials(recipe_id)}\n")

        max_amount = max_craftable_amount(recipe_id)

        print("1. Craft 1")
        print("2. Craft max")
        print("3. Craft custom amount")
        print("b. Back\n")

        if message:
            print(message)
            time.sleep(1.5)
            message = ""
            continue

        choice = input("> ").lower()

        if choice == "1":
            if not craft_recipe(recipe_id, 1):
                message = f"{Fore.RED}{Style.BRIGHT}Not enough materials"
                continue

            message = f"> \n{Fore.YELLOW}{Style.BRIGHT}Crafted {format_recipe_result(recipe_id, 1)}"

        elif choice == "2":
            if max_amount <= 0:
                message = f"{Fore.RED}{Style.BRIGHT}Not enough materials"
                continue

            craft_recipe(recipe_id, max_amount)
            message = f"> \n{Fore.YELLOW}{Style.BRIGHT}Crafted {format_recipe_result(recipe_id, max_amount)}"

        elif choice == "3":
            try:
                amount = int(input("Enter amount: "))
            except:
                message = f"{Fore.RED}{Style.BRIGHT}Invalid input"
                continue

            if amount <= 0:
                message = f"{Fore.RED}{Style.BRIGHT}Enter a positive amount"
                continue

            if amount > max_amount:
                message = f"{Fore.RED}{Style.BRIGHT}The most you can craft is {max_amount}"
                continue

            craft_recipe(recipe_id, amount)
            message = f"{Fore.YELLOW}{Style.BRIGHT}Crafted {format_recipe_result(recipe_id, amount)}"

        elif choice == "b":
            return "crafting"

        else:
            message = f"{Fore.RED}{Style.BRIGHT}Invalid input"

def farm():
    message = ""
    message_color = Fore.RED
    needs_redraw = True

    def draw_farm_screen():
        clear()
        print(f"{Style.BRIGHT}Farm          {xp_bar()}\n")

        draw_farm_plot()

        print("\n1. Plant")
        print("2. Harvest")
        print("b. Back\n")
        print("Select:")

    with term.cbreak():
        while True:
            grew = update_farm_growth()

            if grew:
                Save.save_game(player_state, player_inventory, current_weapon, farm_state)
                needs_redraw = True

            if needs_redraw:
                draw_farm_screen()
                needs_redraw = False

            if message:
                print(f"{message_color}{Style.BRIGHT}{message}")
                time.sleep(1.5)
                message = ""
                needs_redraw = True
                flush_input()
                continue

            key = term.inkey(timeout=0.2)

            if not key:
                continue

            choice = key.lower()

            if choice == "1":
                if farm_state["plot"]["crop_id"] is not None:
                    message = "Something is already planted"
                    message_color = Fore.RED
                    continue

                return "plant_selection"

            elif choice == "2":
                plot = farm_state["plot"]

                if plot["crop_id"] is None:
                    message = "There is nothing to harvest"
                    message_color = Fore.RED
                    continue

                if plot["stage"] != 1:
                    message = "This crop is still growing"
                    message_color = Fore.RED
                    continue

                drops = harvest_crop(plot["crop_id"])

                plot["crop_id"] = None
                plot["planted_at"] = None
                plot["stage"] = None

                update_player_level()
                update_world_unlocks()
                Save.save_game(player_state, player_inventory, current_weapon, farm_state)

                if drops:
                    drop_lines = []

                    for item_id, qty in drops["items"]:
                        drop_lines.append(f"+ {Functions.format_item_name(item_id, Data.ITEMS)} x {qty}")

                    if drops["coins"] > 0:
                        drop_lines.append(f"+ {Fore.YELLOW}{drops['coins']} coins{Style.RESET_ALL}")

                    if drops["xp"] > 0:
                        drop_lines.append(f"+ {Fore.LIGHTGREEN_EX}{drops['xp']} XP{Style.RESET_ALL}")

                    if drop_lines:
                        message = "\n".join(drop_lines)
                    else:
                        message = "Harvested"

                message_color = Fore.RESET
                needs_redraw = True
                continue

            elif choice == "b":
                return go_back()

            else:
                message = "Invalid input"
                message_color = Fore.RED
                continue

def plant_selection():
    page = 0
    selected = 0
    error_message = ""
    needs_redraw = True

    with term.cbreak():
        while True:
            plantable_items = get_plantable_items()

            if not plantable_items:
                clear()
                print(f"{Style.BRIGHT}Plant Selection\n")
                print("You have nothing to plant\n")
                print("Press 'b' to go back")

                key = term.inkey()
                if key.lower() == "b":
                    return "farm"
                continue

            height = term.height
            page_size = max(1, height - 7)

            total_pages = max(1, math.ceil(len(plantable_items) / page_size))
            page = max(0, min(page, total_pages - 1))

            start = page * page_size
            end = start + page_size
            page_items = plantable_items[start:end]

            selected = max(0, min(selected, len(page_items) - 1))

            if needs_redraw:
                clear()
                print(f"{Style.BRIGHT}Plant Selection\n")

                for i, item in enumerate(page_items):
                    prefix = "▶ " if i == selected else "  "
                    print(f"{prefix}{Functions.format_item_name(item['id'], Data.ITEMS)} x {item['qty']}")

                print(f"\nPage {page + 1}/{total_pages}")
                print("← prev | → next | ⇅ up/down | ↵ plant | b back")

                needs_redraw = False

            if error_message:
                clear()
                print(f"{Style.BRIGHT}Plant Selection\n")

                for i, item in enumerate(page_items):
                    prefix = "▶ " if i == selected else "  "
                    print(f"{prefix}{Functions.format_item_name(item['id'], Data.ITEMS)} x {item['qty']}")

                print(f"\nPage {page + 1}/{total_pages}")
                print("← prev | → next | ⇅ up/down | ↵ plant | b back")
                print(f"{Fore.RED}{Style.BRIGHT}{error_message}")

                time.sleep(1)
                error_message = ""
                flush_input()
                needs_redraw = True
                continue

            key = term.inkey()

            if not key:
                continue

            if key.name == "KEY_UP":
                if selected > 0:
                    selected -= 1
                    needs_redraw = True

            elif key.name == "KEY_DOWN":
                if selected < len(page_items) - 1:
                    selected += 1
                    needs_redraw = True

            elif key.name == "KEY_LEFT":
                if page > 0:
                    page -= 1
                    selected = 0
                    needs_redraw = True

            elif key.name == "KEY_RIGHT":
                if page < total_pages - 1:
                    page += 1
                    selected = 0
                    needs_redraw = True

            elif key.name == "KEY_ENTER" or key == "\n":
                selected_item = page_items[selected]
                crop_id = Data.ITEMS[selected_item["id"]]["crop_id"]

                remove_from_stack(selected_item["id"], selected_item["stack_ref"], 1)

                farm_state["plot"]["crop_id"] = crop_id
                farm_state["plot"]["planted_at"] = time.time()
                farm_state["plot"]["stage"] = 0

                Save.save_game(player_state, player_inventory, current_weapon, farm_state)

                return "farm"

            elif key.lower() == "b":
                return "farm"

            else:
                error_message = "Invalid input"
                needs_redraw = True

def store():
    page = 0
    selected = 0
    error_message = ""
    needs_redraw = True

    with term.cbreak():
        while True:
            store_ids = list(Data.STORE_ITEMS.keys())

            if not store_ids:
                clear()
                print(f"{Style.BRIGHT}Store")
                print(f"Coins: {player_state['coins']}\n")
                print("There is nothing for sale\n")
                print("Press 'b' to go back")

                key = term.inkey()
                if key.lower() == "b":
                    return go_back()
                continue

            height = term.height
            page_size = max(1, (height - 7) // 3)

            total_pages = max(1, math.ceil(len(store_ids) / page_size))
            page = max(0, min(page, total_pages - 1))

            start = page * page_size
            end = start + page_size
            page_items = store_ids[start:end]

            selected = max(0, min(selected, len(page_items) - 1))

            if needs_redraw:
                clear()
                print(f"{Style.BRIGHT}Store   Coins: {player_state['coins']}\n")

                for i, store_id in enumerate(page_items):
                    prefix = "▶ " if i == selected else "  "
                    print(f"{prefix}{format_store_product(store_id)}")
                    print(f"    Price: {format_store_price(store_id)}\n")

                print(f"Page {page + 1}/{total_pages}")
                print("← prev | → next | ⇅ up/down | ↵ select | b back")

                needs_redraw = False

            if error_message:
                clear()
                print(f"{Style.BRIGHT}Store   Coins: {player_state['coins']}\n")

                for i, store_id in enumerate(page_items):
                    prefix = "▶ " if i == selected else "  "
                    print(f"{prefix}{format_store_product(store_id)}")
                    print(f"    Price: {format_store_price(store_id)}\n")

                print(f"Page {page + 1}/{total_pages}")
                print("← prev | → next | ⇅ up/down | ↵ select | b back")
                print(f"{Fore.RED}{Style.BRIGHT}{error_message}")

                time.sleep(1)
                error_message = ""
                flush_input()
                needs_redraw = True
                continue

            key = term.inkey()

            if not key:
                continue

            if key.name == "KEY_UP":
                if selected > 0:
                    selected -= 1
                    needs_redraw = True

            elif key.name == "KEY_DOWN":
                if selected < len(page_items) - 1:
                    selected += 1
                    needs_redraw = True

            elif key.name == "KEY_LEFT":
                if page > 0:
                    page -= 1
                    selected = 0
                    needs_redraw = True

            elif key.name == "KEY_RIGHT":
                if page < total_pages - 1:
                    page += 1
                    selected = 0
                    needs_redraw = True

            elif key.name == "KEY_ENTER" or key == "\n":
                selected_store_item = page_items[selected]
                return ("buy_item", selected_store_item)

            elif key.lower() == "b":
                return go_back()

            else:
                error_message = "Invalid input"
                needs_redraw = True

def buy_item(store_id=None):
    message = ""

    while True:
        clear()
        print(f"{Style.BRIGHT}Buy Item   Coins: {player_state['coins']}\n")

        if store_id is None:
            print("No item selected.")
            time.sleep(1)
            return "store"

        print(format_store_product(store_id))
        print(f"Price: {format_store_price(store_id)}\n")

        max_amount = max_buyable_amount(store_id)

        print("1. Buy 1")
        print("2. Buy 10")
        print("3. Buy max")
        print("4. Buy custom amount")
        print("b. Back\n")

        if message:
            print(message)
            time.sleep(1.5)
            message = ""
            continue

        choice = input("> ").lower()

        if choice == "1":
            amount = 1

            if not buy_store_item(store_id, amount):
                message = f"{Fore.RED}{Style.BRIGHT}Not enough coins"
                continue

            message = f"{Fore.YELLOW}{Style.BRIGHT}Bought {format_store_product(store_id, amount)}"

        elif choice == "2":
            amount = 10

            if not buy_store_item(store_id, amount):
                message = f"{Fore.RED}{Style.BRIGHT}Not enough coins"
                continue

            message = f"{Fore.YELLOW}{Style.BRIGHT}Bought {format_store_product(store_id, amount)}"

        elif choice == "3":
            amount = max_amount

            if amount <= 0:
                message = f"{Fore.RED}{Style.BRIGHT}Not enough coins"
                continue

            buy_store_item(store_id, amount)
            message = f"{Fore.YELLOW}{Style.BRIGHT}Bought {format_store_product(store_id, amount)}"

        elif choice == "4":
            try:
                amount = int(input("Enter amount: "))
            except:
                message = f"{Fore.RED}{Style.BRIGHT}Invalid input"
                continue

            if amount <= 0:
                message = f"{Fore.RED}{Style.BRIGHT}Enter a positive amount"
                continue

            if amount > max_amount:
                message = f"{Fore.RED}{Style.BRIGHT}The most you can buy is {max_amount}"
                continue

            buy_store_item(store_id, amount)
            message = f"{Fore.YELLOW}{Style.BRIGHT}Bought {format_store_product(store_id, amount)}"

        elif choice == "b":
            return "store"

        else:
            message = f"{Fore.RED}{Style.BRIGHT}Invalid input"

def xp_store():
    while True:
        clear()
        print(f"{Style.BRIGHT}XP Store")
        print("Type 'back' to return")

        choice = input("Enter the number of your choice to select or type \"b\" to go back: ").lower()

        if choice == "b":
            return "store"
        else:
            invalid_input()

def go_back():
    return "main_menu"

screens = {
    "main_menu": main_menu,
    "world_selection": world_selection,
    "game": game,
    "inventory": inventory,
    "item_selection": lambda: item_selection(selected_item),
    "crafting": crafting,
    "craft_item": lambda: craft_item(selected_recipe),
    "farm": farm,
    "plant_selection": plant_selection,
    "store": store,
    "buy_item": lambda: buy_item(selected_store_item),
    "xp_store": xp_store
}

current = "main_menu"

selected_item = None
selected_recipe = None
selected_store_item = None

while current != "exit":
    if current in screens:
        result = screens[current]()

        if isinstance(result, tuple):
            current = result[0]

            if current == "item_selection":
                selected_item = result[1]
            elif current == "craft_item":
                selected_recipe = result[1]
            elif current == "buy_item":
                selected_store_item = result[1]
        else:
            current = result
    else:
        print(f"{Fore.RED}{Style.BRIGHT}Error: Screen '{current}' not found.")
        current = "main_menu"