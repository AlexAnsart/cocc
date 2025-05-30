"""
Configuration principale pour le simulateur Clash of Clans TH3
Contient toutes les constantes et paramètres du jeu
"""

# Paramètres de la grille de jeu
GRID_SIZE = 44  # Taille de la carte en tuiles
TICK_RATE = 10  # Ticks par seconde
TILE_SIZE = 1.0  # Taille d'une tuile en unités
MAX_BATTLE_DURATION = 180.0 # Durée maximale d'une bataille en secondes (3 minutes)

# Statistiques des troupes par niveau
TROOP_STATS = {
    "barbarian": {
        1: {"hp": 45, "dps": 8, "damage": 8, "speed": 16, "range": 0.4, "housing": 1, "cost": 25, "attack_speed": 1.0},
        2: {"hp": 54, "dps": 11, "damage": 11, "speed": 16, "range": 0.4, "housing": 1, "cost": 40, "attack_speed": 1.0}
    },
    "archer": {
        1: {"hp": 20, "dps": 7, "damage": 7, "speed": 24, "range": 3.5, "housing": 1, "cost": 50, "attack_speed": 1.0},
        2: {"hp": 23, "dps": 9, "damage": 9, "speed": 24, "range": 3.5, "housing": 1, "cost": 80, "attack_speed": 1.0}
    },
    "giant": {
        1: {"hp": 300, "dps": 11, "damage": 11, "speed": 12, "range": 1.0, "housing": 5, "cost": 250, "attack_speed": 1.0}
    },
    "wall_breaker": {
        1: {"hp": 20, "dps": 6, "damage": 6, "wall_damage": 60, "speed": 24, "range": 0.1, "housing": 2, "cost": 750, "attack_speed": 1.0}
    },
    "goblin": {
        1: {"hp": 25, "dps": 11, "damage": 11, "resource_damage": 22, "speed": 32, "range": 0.4, "housing": 1, "cost": 25, "attack_speed": 1.0},
        2: {"hp": 30, "dps": 14, "damage": 14, "resource_damage": 28, "speed": 32, "range": 0.4, "housing": 1, "cost": 40, "attack_speed": 1.0}
    }
}

# Statistiques des bâtiments défensifs
DEFENSE_STATS = {
    "cannon": {
        1: {"hp": 420, "dps": 7, "damage": 7, "range": 9, "attack_speed": 0.8},
        2: {"hp": 470, "dps": 9, "damage": 9, "range": 9, "attack_speed": 0.8},
        3: {"hp": 520, "dps": 11, "damage": 11, "range": 9, "attack_speed": 0.8},
        4: {"hp": 570, "dps": 15, "damage": 15, "range": 9, "attack_speed": 0.8}
    },
    "archer_tower": {
        1: {"hp": 380, "dps": 11, "damage": 11, "range": 10, "attack_speed": 0.5},
        2: {"hp": 420, "dps": 13, "damage": 13, "range": 10, "attack_speed": 0.5},
        3: {"hp": 460, "dps": 16, "damage": 16, "range": 10, "attack_speed": 0.5}
    },
    "mortar": {
        1: {"hp": 400, "dps": 4, "damage": 20, "range_min": 4, "range_max": 11, "splash_radius": 1.5, "attack_speed": 5.0}
    }
}

# Statistiques des autres bâtiments
BUILDING_STATS = {
    "town_hall": {
        3: {"hp": 1400, "size": 4}
    },
    "clan_castle": {
        1: {"hp": 700, "size": 3, "capacity": 10}
    },
    "army_camp": {
        1: {"hp": 250, "size": 5, "capacity": 35}
    },
    "barracks": {
        1: {"hp": 250, "size": 3},
        2: {"hp": 275, "size": 3},
        3: {"hp": 300, "size": 3}
    },
    "elixir_collector": {
        1: {"hp": 400, "size": 3},
        2: {"hp": 450, "size": 3},
        3: {"hp": 500, "size": 3},
        4: {"hp": 550, "size": 3}
    },
    "elixir_storage": {
        1: {"hp": 400, "size": 3},
        2: {"hp": 500, "size": 3},
        3: {"hp": 600, "size": 3}
    },
    "gold_mine": {
        1: {"hp": 400, "size": 3},
        2: {"hp": 450, "size": 3},
        3: {"hp": 500, "size": 3},
        4: {"hp": 550, "size": 3}
    },
    "gold_storage": {
        1: {"hp": 400, "size": 3},
        2: {"hp": 500, "size": 3},
        3: {"hp": 600, "size": 3}
    },
    "laboratory": {
        1: {"hp": 250, "size": 3}
    },
    "builder_hut": {
        1: {"hp": 250, "size": 2}
    },
    "wall": {
        1: {"hp": 300},
        2: {"hp": 500},
        3: {"hp": 700}
    }
}

# Limites de bâtiments pour TH3
TH3_BUILDING_LIMITS = {
    "town_hall": 1,
    "cannon": 2,
    "archer_tower": 1,
    "mortar": 1,
    "clan_castle": 1,
    "army_camp": 2,
    "barracks": 2,
    "elixir_collector": 3,
    "elixir_storage": 2,
    "gold_mine": 3,
    "gold_storage": 2,
    "laboratory": 1,
    "builder_hut": 5,
    "wall": 50
}

# Configuration du pathfinding et de l'IA
PATHFINDING_CONFIG = {
    # Pénalités de mur par type de troupe
    "wall_penalties": {
        "barbarian": 15.0,
        "archer": 15.0,
        "giant": 10.0,
        "wall_breaker": 0.1,
        "goblin": 20.0,
    },
    
    # Multiplicateurs de préférence
    "preference_multipliers": {
        "giant": {"defense": 0.3, "other": 1.0},
        "wall_breaker": {"wall": 0.2, "other": 1.0},
        "goblin": {"resource": 0.4, "other": 1.0},
        "barbarian": {"all": 0.8},
        "archer": {"all": 0.8}
    },
    
    # Autres paramètres
    "retarget_distance_threshold": 3.0,
    "path_recalculation_interval": 5,
    "wall_break_time_estimation": 5.0,
    "compartment_preference": 0.8,
}

# Types de bâtiments par catégorie
DEFENSE_BUILDINGS = ["cannon", "archer_tower", "mortar"]
RESOURCE_BUILDINGS = ["elixir_collector", "elixir_storage", "gold_mine", "gold_storage"]
ARMY_BUILDINGS = ["barracks", "army_camp", "laboratory"]
OTHER_BUILDINGS = ["town_hall", "clan_castle", "builder_hut"]

# Gaps autour des bâtiments (en tuiles)
BUILDING_GAPS = {
    "default": 0.5,
    "army_camp": 1.0,
    "wall": 0.0
}

# Couleurs pour l'affichage (codes ANSI)
COLORS = {
    "reset": "\033[0m",
    "red": "\033[91m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "blue": "\033[94m",
    "magenta": "\033[95m",
    "cyan": "\033[96m",
    "white": "\033[97m",
    "gray": "\033[90m",
    "orange": "\033[38;5;208m",
    "dark_green": "\033[38;5;22m",
    "brown": "\033[38;5;94m"
}

# Symboles et couleurs pour l'affichage
DISPLAY_CONFIG = {
    "buildings": {
        "town_hall": {"symbol": "T", "color": "yellow"},
        "cannon": {"symbol": "C", "color": "red"},
        "archer_tower": {"symbol": "A", "color": "magenta"},
        "mortar": {"symbol": "M", "color": "orange"},
        "clan_castle": {"symbol": "Ç", "color": "cyan"},
        "army_camp": {"symbol": "∏", "color": "green"},
        "barracks": {"symbol": "B", "color": "blue"},
        "elixir_collector": {"symbol": "E", "color": "magenta"},
        "elixir_storage": {"symbol": "Ê", "color": "magenta"},
        "gold_mine": {"symbol": "G", "color": "yellow"},
        "gold_storage": {"symbol": "Ĝ", "color": "yellow"},
        "laboratory": {"symbol": "L", "color": "cyan"},
        "builder_hut": {"symbol": "h", "color": "brown"},
        "wall": {"symbol": "█", "color": "gray"}
    },
    "troops": {
        "barbarian": {"symbol": "b", "color": "yellow"},
        "archer": {"symbol": "a", "color": "magenta"},
        "giant": {"symbol": "G", "color": "orange"},
        "wall_breaker": {"symbol": "w", "color": "red"},
        "goblin": {"symbol": "g", "color": "green"}
    },
    "terrain": {
        "empty": {"symbol": "·", "color": "dark_green"},
        "spawn": {"symbol": "×", "color": "blue"}
    }
} 