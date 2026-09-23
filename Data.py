import Mappings
import Sprites

ITEMS = {
    "stick": {
        "sprite": Sprites.stick_sprite,
        "mapping": Mappings.stick_mapping,
        "type": "weapon",
        "damage": 1,
        "sell_price": 10,
        "stack_limit": 1,
        "rarity": "common"
    },
    "cudgel": {
        "sprite": Sprites.cudgel_sprite,
        "mapping": Mappings.cudgel_mapping,
        "type": "weapon",
        "damage": 2,
        "sell_price": 25,
        "stack_limit": 1,
        "rarity": "common"
    },
    "wooden_sword": {
        "sprite": Sprites.wooden_sword_sprite,
        "mapping": Mappings.wooden_sword_mapping,
        "type": "weapon",
        "damage": 3,
        "sell_price": 50,
        "stack_limit": 1,
        "rarity": "common"
    },
    "stone_sword": {
        "sprite": Sprites.stone_sword_sprite,
        "mapping": Mappings.stone_sword_mapping,
        "type": "weapon",
        "damage": 5,
        "sell_price": 100,
        "stack_limit": 1,
        "rarity": "common"
    },
    "syringe": {
        "sprite": Sprites.syringe_sprite,
        "mapping": Mappings.syringe_mapping,
        "type": "weapon",
        "damage": 10,
        "sell_price": 100,
        "stack_limit": 1,
        "rarity": "uncommon"
    },

    "knife": {
        "sprite": Sprites.knife_sprite,
        "mapping": Mappings.knife_mapping,
        "type": "weapon",
        "damage": 15,
        "sell_price": 150,
        "stack_limit": 1,
        "rarity": "epic"
    },
    "gel": {
        "sprite": None,
        "mapping": None,
        "type": "material",
        "sell_price": 5,
        "stack_limit": 99,
        "rarity": "common"
    },
    "plastic": {
        "sprite": None,
        "mapping": None,
        "type": "material",
        "sell_price": 25,
        "stack_limit": 99,
        "rarity": "common"
    },
    "wheat_seeds": {
        "sprite": None,
        "mapping": None,
        "type": "plantable",
        "crop_id": "wheat_crop",
        "sell_price": 5,
        "stack_limit": 99,
        "rarity": "common"
    },
    "wheat": {
        "sprite": None,
        "mapping": None,
        "type": "material",
        "sell_price": 5,
        "stack_limit": 99,
        "rarity": "common"
    },
    "strawberry_seeds": {
        "sprite": None,
        "mapping": None,
        "type": "plantable",
        "crop_id": "strawberry_crop",
        "sell_price": 5,
        "stack_limit": 99,
        "rarity": "common"
    },
    "strawberry": {
        "sprite": None,
        "mapping": None,
        "type": "material",
        "sell_price": 5,
        "stack_limit": 99,
        "rarity": "common"
    },
    "gel_ball": {
        "sprite": None,
        "mapping": None,
        "type": "material",
        "sell_price": 25,
        "stack_limit": 99,
        "rarity": "common"
    },
    "green_gel_ball": {
        "sprite": None,
        "mapping": None,
        "type": "material",
        "sell_price": 25,
        "stack_limit": 99,
        "rarity": "common"
    },
    "blue_gel_ball": {
        "sprite": None,
        "mapping": None,
        "type": "material",
        "sell_price": 25,
        "stack_limit": 99,
        "rarity": "common"
    },
    "cheese": {
        "sprite": None,
        "mapping": None,
        "type": "material",
        "sell_price": 50,
        "stack_limit": 99,
        "rarity": "uncommon"
    }

}

ITEM_ACTIONS = {
    "weapon": ["equip"],
    "consumable": ["consume"],
    "plantable": ["plant"],
    "material": [],
    "accessory": ["equip"],
    "special": ["use"]
}

RECIPES = {
    "plastic": {
        "results": [
            {
                "id": "plastic",
                "qty": 1
            }
        ],
        "materials": [
            {
                "id": "gel",
                "qty": 5
            }
        ]
    },
    "syringe": {
        "results": [
            {
                "id": "syringe",
                "qty": 1
            }
        ],
        "materials": [
            {
                "id": "plastic",
                "qty": 8
            },
            {
                "id": "gel",
                "qty": 5
            }
        ]
    }
}

CROPS = {
    "wheat_crop": {
        "growth_time": 20,  # seconds
        "stages": [
            {
                "sprite": Sprites.wheat_seeds_planted_sprite,
                "mapping": Mappings.wheat_seeds_planted_mapping
            },
            {
                "sprite": Sprites.wheat_crop_sprite,
                "mapping": Mappings.wheat_crop_mapping
            }
        ],
        "loot": [
            {
                "type": "item",
                "id": "wheat",
                "chance": 1.0,
                "min": 1,
                "max": 1
            },
            {
                "type": "xp",
                "chance": 1.0,
                "min": 2,
                "max": 2
            }
        ]
    }
}

SOILS = {
    "soil": {
        "sprite": Sprites.soil_sprite,
        "mapping": Mappings.soil_mapping
    }
}

STORE_ITEMS = {
    "wheat_seeds": {
        "results": [
            {
                "id": "wheat_seeds",
                "qty": 1
            }
        ],
        "price": 5
    },
    "cudgel": {
        "results": [
            {
                "id": "cudgel",
                "qty": 1
            }
        ],
        "price": 25
    },
    "wooden_sword": {
        "results": [
            {
                "id": "wooden_sword",
                "qty": 1
            }
        ],
        "price": 50
    },
    "stone_sword": {
        "results": [
            {
                "id": "stone_sword",
                "qty": 1
            }
        ],
        "price": 100
    },
}

ENEMIES = {
    "green_slime": {
        "sprite": Sprites.green_slime_sprite,
        "mapping": Mappings.green_slime_mapping,
        "health": 10,
        "time_limit": 8,
        "loot": [
            {
                "type": "item",
                "id": "gel",
                "chance": 75,
                "min": 2,
                "max": 2
            },
            {
                "type": "item",
                "id": "wheat_seeds",
                "chance": 0.25,
                "min": 1,
                "max": 1
            },
            {
                "type": "coins",
                "chance": 1.0,
                "min": 5,
                "max": 5
            },
            {
                "type": "xp",
                "chance": 1.0,
                "min": 5,
                "max": 5
            }
        ]
    },

    "blue_slime": {
        "sprite": Sprites.blue_slime_sprite,
        "mapping": Mappings.blue_slime_mapping,
        "health": 10,
        "loot": [
            {
                "type": "item",
                "id": "gel",
                "chance": 100,
                "min": 1,
                "max": 2
            },
            {
                "type": "coins",
                "chance": 1.0,
                "min": 5,
                "max": 5
            },
            {
                "type": "xp",
                "chance": 1.0,
                "min": 5,
                "max": 5
            }
        ]
    },

    "red_slime": {
        "sprite": Sprites.red_slime_sprite,
        "mapping": Mappings.red_slime_mapping,
        "health": 15,
        "loot": [
            {
                "type": "item",
                "id": "gel",
                "chance": 0.50,
                "min": 3,
                "max": 3
            },
            {
                "type": "coins",
                "chance": 1.0,
                "min": 5,
                "max": 5
            },
            {
                "type": "xp",
                "chance": 1.0,
                "min": 5,
                "max": 5
            }
        ]
    },

    "cheese_slime": {
        "sprite": Sprites.cheese_slime_sprite,
        "mapping": Mappings.cheese_slime_mapping,
        "health": 10,
        "time_limit": None,
        "loot": [
            {
                "type": "item",
                "id": "cheese",
                "chance": 1.0,
                "min": 1,
                "max": 1
            },
            {
                "type": "coins",
                "chance": 1.0,
                "min": 5,
                "max": 5
            },
            {
                "type": "xp",
                "chance": 1.0,
                "min": 5,
                "max": 5
            }
        ]
    },

    "zombie": {
        "sprite": Sprites.zombie_sprite,
        "mapping": Mappings.zombie_mapping,
        "health": 20,
        "time_limit": None,
        "loot": [
            {
                "type": "coins",
                "chance": 1.0,
                "min": 30,
                "max": 30
            },
            {
                "type": "xp",
                "chance": 1.0,
                "min": 25,
                "max": 25
            }
        ]
    },

    "knife_zombie": {
        "sprite": Sprites.knife_zombie_sprite,
        "mapping": Mappings.knife_zombie_mapping,
        "health": 30,
        "time_limit": None,
        "loot": [
            {
                "type": "item",
                "id": "knife",
                "chance": 0.1,
                "min": 1,
                "max": 1
            },
            {
                "type": "coins",
                "chance": 1.0,
                "min": 35,
                "max": 37
            },
            {
                "type": "xp",
                "chance": 1.0,
                "min": 30,
                "max": 35
            }
        ]
    }
}

WORLDS = {
    "slime_fields": {
        "name": "Slime Fields",
        "unlocked_by_default": True,
        "enemies": {
            "green_slime": 30,
            "blue_slime": 30,
            "red_slime": 30,
            "cheese_slime": 10
        },
        "music": None
    },

    "dark-forest": {
        "name": "Dark Forest",
        "unlocked_by_default": False,
        "unlock_conditions": {
            "level": 2,
            "coins": 50,
            "items": {
                "wheat": 3
            },
            "enemies_defeated": {
                "green_slime": 5
            },
            "worlds": ["slime_fields"]
        },
        "enemies": {
            "zombie": 50,
            "knife_zombie": 50
        },
        "music": None
    }
}