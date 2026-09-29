# Pixelon

Pixelon is a Python-based playable RPG where you fight enemies across different worlds, manage an inventory, craft weapons, farm crops in real time, and progress through a leveling system. All of this runs in the terminal with custom ANSI sprite rendering.

All game content and assets live in separate data modules, so new enemies, items, recipes, or worlds can be added without touching the engine code.

## How It Works

The game is separated into multiple files, each one having a specific function:

- **`Pixelon.py`** - The main game file and engine: state machine, screen navigation, game loop
- **`Data.py`** - All game content (items, enemies, recipes, crops, worlds) as pure data
- **`Functions.py`** - Shared utilities: loot rolling, inventory management, rendering
- **`Save.py`** - JSON save/load so progress persists between sessions
- **`Sprites.py`** - All sprite designs as different character strings
- **`Mappings.py`** - Color designation of every sprite pixel

## Key Features

- **Data-driven architecture** - content separated from engine logic
- **Real-time combat** - enemies have time limits; escape if you're too slow
- **Inventory system** - stacked items with limits, rarity-based coloring
- **Crafting** - recipe validation, material consumption, weapon safety checks
- **Farming** - real-time crop growth that persists in your save file
- **World unlocks** - progression restricted by level, items, and enemies defeated

## Tech Stack

- **Python 3** - Core language
- **Colorama** - Terminal color output
- **Blessed** - Interactive terminal input and screen control
- **JSON** - Save file persistence

## Controls

Pixelon uses keyboard input directly in the terminal. Follow the in-game prompts to navigate the different screens, as each one has a different control scheme

## Getting Started

### Prerequisites

Pixelon requires Python 3.8 or later as well as the colorama and blessed libraries

To run Pixelon, run these commands in your terminal:

```bash
pip install colorama blessed
git clone https://github.com/BParniak/pixelon.git
cd pixelon
python Pixelon.py
```

After the initial setup, you only need to run:

```bash
python Pixelon.py
```

to start the game again. Your progress is saved locally and will be loaded when you return.

**Note: Pixelon currently only runs on Windows as it uses a Windows exclusive library (msvcrt)**

## What I Learned

The biggest challenge was implementing the data-driven architecture such that any new content could be added without having to touch any of the engine code. Earlier versions of the game had enemies and items hardcoded into the game logic, which meant every addition risked breaking something, and it also became clunky and inefficient very fast as more content was being added. Moving all content into separate data modules made adding new content much easier by allowing you to simply edit a dictionary, rather than the whole engine.

## Future Improvements/Additions
- More content: additional enemies, worlds, and crop types
- Quest system
- Consumable items that affect gameplay (damage/currency/xp multipliers, enemy debuffs, etc)
- Potential online connectivity, giving features such as item trading or a global marketplace
