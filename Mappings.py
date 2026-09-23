from colorama import Fore, Back, Style

# Item mappings

default_mapping = {
    ".": (" ", ""),  # (character, color/style)
    "G": ("█", Fore.GREEN),
    "g": ("█", Fore.LIGHTGREEN_EX),
    "R": ("█", Fore.RED),
    "r": ("█", Fore.LIGHTRED_EX),
    "B": ("█", Fore.BLUE),
    "b": ("█", Fore.LIGHTBLUE_EX),
    "Y": ("█", Fore.YELLOW),
    "y": ("█", Fore.LIGHTYELLOW_EX),
    "M": ("█", Fore.MAGENTA),
    "m": ("█", Fore.LIGHTMAGENTA_EX),
    "C": ("█", Fore.CYAN),
    "c": ("█", Fore.LIGHTCYAN_EX),
    "W": ("█", Fore.WHITE),
    "w": ("█", Fore.LIGHTWHITE_EX),
    "D": ("█", Fore.BLACK),
    "d": ("█", Fore.LIGHTBLACK_EX),
    "O": ("█", "\033[38;2;255;165;0m"), # Orange color
    "P": ("█", "\033[38;2;128;0;128m"), # Purple color
    "p": ("█", "\033[38;2;255;192;203m"), # Pink color
    "$": ("█", "\033[38;2;150;75;0m"), # Brown color
    "#": ("█", "\033[38;2;128;128;128m"), # Gray color
}

stick_mapping = {
    **default_mapping,
    "!": ("─", "\033[38;2;150;75;0m"),
    "@": ("┐", "\033[38;2;150;75;0m"),
    "%": ("└", "\033[38;2;150;75;0m")
}

cudgel_mapping = {
    **default_mapping,
    "@": ("▀", "\033[38;2;150;75;0m"),
    ",": ("▄", "\033[38;2;150;75;0m")
}

wooden_sword_mapping = {
    **default_mapping,
    "#": ("█", "\033[38;2;193;154;107m"), # Wood brown color
    "^": ("┃", "\033[38;2;193;154;107m"), # Wood brown color
    "@": ("▀", "\033[38;2;150;75;0m"), # Brown color
}

stone_sword_mapping = {
    **default_mapping,
    "^": ("┃", "\033[38;2;128;128;128m"), # Gray color
    "@": ("▀", "\033[38;2;58;58;58m"), # Dark gray color
    "&": ("█", "\033[38;2;58;58;58m") # Dark gray color
}

syringe_mapping = {
    **default_mapping,
    "@": ("▀", Fore.WHITE),
    "^": ("┃", "\033[38;2;128;128;128m"),
    "*": ("▀", Fore.WHITE, Back.LIGHTBLUE_EX),
    ",": ("▄", Fore.WHITE, Back.LIGHTBLUE_EX)
}

knife_mapping = {
    **default_mapping,
    "*": ("▀", "\033[38;2;150;75;0m") # Brown color
}

#Enemy mappings

green_slime_mapping = {
    **default_mapping,
    "@": ("▀", Fore.GREEN),
    "!": ("▄", Fore.GREEN),
    "*": ("▀", Fore.LIGHTGREEN_EX, Back.BLACK),
    ",": ("▄", Fore.LIGHTGREEN_EX, Back.BLACK)
}

blue_slime_mapping = {
    **default_mapping,
    "@": ("▀", Fore.BLUE),
    "!": ("▄", Fore.BLUE),
    "*": ("▀", Fore.LIGHTBLUE_EX, Back.BLACK),
    ",": ("▄", Fore.LIGHTBLUE_EX, Back.BLACK)
}

red_slime_mapping = {
    **default_mapping,
    "@": ("▀", Fore.RED),
    "!": ("▄", Fore.RED),
    "*": ("▀", Fore.LIGHTRED_EX, Back.BLACK),
    ",": ("▄", Fore.LIGHTRED_EX, Back.BLACK)
}

cheese_slime_mapping = {
    **default_mapping,
    "1": ("█", "\033[38;2;255;215;0m"), # Gold color
    "@": ("▀", "\033[38;2;255;215;0m"),
    "!": ("▄", "\033[38;2;255;215;0m"),
    "2": ("▀", "\033[38;2;255;215;0m", Back.LIGHTYELLOW_EX),
    "3": ("▄", "\033[38;2;255;215;0m", Back.LIGHTYELLOW_EX),
    "*": ("▀", Fore.LIGHTYELLOW_EX, Back.BLACK),
    ",": ("▄", Fore.LIGHTYELLOW_EX, Back.BLACK)
}

zombie_mapping = {
    **default_mapping,
    "@": ("▀", Fore.LIGHTBLACK_EX, Back.GREEN),
    "!": ("▄", Fore.GREEN),
    ",": ("▄", "\033[38;2;150;75;0m"),
    "(": ("▄", Fore.GREEN, Back.WHITE),
    ")": ("▄", Fore.GREEN, Back.RED),
    "*": ("▀", Fore.GREEN),
    "^": ("▀", Fore.GREEN, "\033[48;2;150;75;0m"), # Background brown color
    "-": ("▀", "\033[38;2;150;75;0m"),
    "_": ("▄", Fore.LIGHTBLACK_EX),
    "+": ("▀", "\033[38;2;150;75;0m", Back.LIGHTBLACK_EX)
}

knife_zombie_mapping = {
    **zombie_mapping,
    "`": ("▀", "\033[38;2;128;128;128m", "\033[48;2;150;75;0m")
}

# Farm mappings

soil_mapping = default_mapping

wheat_crop_mapping = {
    "|": ("█", "\033[38;2;245;222;179m"), # Wheat colour
    "<": ("▟", "\033[38;2;245;222;179m"),
    ">": ("▙", "\033[38;2;245;222;179m"),
    ",": ("▜", "\033[38;2;245;222;179m"),
    "/": ("▛", "\033[38;2;245;222;179m")
}

wheat_seeds_planted_mapping = wheat_crop_mapping