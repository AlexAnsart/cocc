from typing import Dict, List, Tuple
from ..entities.troop_types import Troop, create_troop # Import Troop for type hinting

# Format: (type_troupe, niveau, (spawn_x, spawn_y))
ARMY_CONFIGURATIONS: Dict[str, List[Tuple[str, int, Tuple[float, float]]]] = {
    "Armée Mixte TH3 (Main)": [
        # Capacité TH3: 70 places. Géant=5, Barb=1, Arch=1, WB=2, Gob=1
        # Nouvelle composition: 4 Géants (20), 12 Barbares (12), 18 Archers (18), 5 Sapeurs (10), 10 Gobelins (10) = 70 places

        # 4 Géants pour tanker, déployés sur deux points d'attaque principaux
        ("giant", 1, (5, 10)),  # Point d'attaque Nord-Ouest
        ("giant", 1, (5, 30)),  # Point d'attaque Sud-Ouest
        ("giant", 1, (35, 10)), # Point d'attaque Nord-Est (un peu plus centré)
        #("giant", 1, (35, 30)), # Point d'attaque Sud-Est (un peu plus centré)
        
        # 5 Sapeurs pour ouvrir les brèches, près des groupes de géants
        ("wall_breaker", 1, (6, 9)),
        ("wall_breaker", 1, (6, 31)),
        ("wall_breaker", 1, (34, 9)),
        ("wall_breaker", 1, (34, 31)),
        ("wall_breaker", 1, (20, 5)), # Un sapeur pour le nord, au cas où.

        # 12 Barbares, pour suivre les géants et aider au nettoyage
        # Vague 1 (derrière les géants)
        ("barbarian", 2, (7, 11)), ("barbarian", 2, (7, 29)),
        ("barbarian", 2, (33, 11)), ("barbarian", 2, (33, 29)),
        # Vague 2 (un peu plus tard ou plus large)
        ("barbarian", 2, (4, 15)), ("barbarian", 2, (4, 25)),
        ("barbarian", 2, (36, 15)), ("barbarian", 2, (36, 25)),
        ("barbarian", 2, (10, 5)), ("barbarian", 2, (30, 5)),
        #("barbarian", 2, (10, 35)), ("barbarian", 2, (30, 35)),
        
        # 18 Archers, en soutien derrière les barbares/géants et pour bâtiments à distance
        # Soutien direct
        ("archer", 2, (8, 12)), ("archer", 2, (8, 28)),
        ("archer", 2, (32, 12)), ("archer", 2, (32, 28)),
        # Flancs / nettoyage extérieur
        ("archer", 2, (3, 5)), ("archer", 2, (3, 35)),
        ("archer", 2, (37, 5)), ("archer", 2, (37, 35)),
        ("archer", 2, (15, 3)), #("archer", 2, (25, 3)),
        #("archer", 2, (15, 37)), ("archer", 2, (25, 37)),
        # Réserve
        #("archer", 2, (1, 20)), ("archer", 2, (39, 20)),
        #("archer", 2, (20, 1)), ("archer", 2, (20, 39)),
        #("archer", 2, (5, 5)), ("archer", 2, (35, 35)),

        # 10 Gobelins pour les ressources, déploiement large pour diversifier les points d'entrée sur les collecteurs/mines externes
        ("goblin", 2, (1, 2)), ("goblin", 2, (2, 1)), # Coin Nord-Ouest
        ("goblin", 2, (39, 2)), ("goblin", 2, (38, 1)), # Coin Nord-Est
        #("goblin", 2, (1, 38)) # Coin Sud-Ouest
        #("goblin", 2, (39, 38)), ("goblin", 2, (38, 39)), # Coin Sud-Est
        #("goblin", 2, (15, 5)), # Nord centre
        #("goblin", 2, (25, 35)),# Sud centre
    ],
    "Armée Démo Visuelle": [
        ("giant", 1, (10, 15)),
        ("giant", 1, (30, 15)),
        ("barbarian", 2, (8, 10)), ("barbarian", 2, (9, 10)), ("barbarian", 2, (10, 10)), ("barbarian", 2, (11, 10)), ("barbarian", 2, (12, 10)),
        ("barbarian", 2, (28, 10)), ("barbarian", 2, (29, 10)), ("barbarian", 2, (30, 10)), ("barbarian", 2, (31, 10)), ("barbarian", 2, (32, 10)),
        ("archer", 2, (12, 5)), ("archer", 2, (14, 5)), ("archer", 2, (16, 5)), ("archer", 2, (18, 5)), ("archer", 2, (20, 5)), ("archer", 2, (22, 5)),
        ("wall_breaker", 1, (20, 15)),
        ("wall_breaker", 1, (22, 15)),
        ("goblin", 2, (5, 20)),
        ("goblin", 2, (35, 20)),
    ],
    "Petite Armée Test Vitesse": [
        ("barbarian", 2, (10, 20)),
        ("barbarian", 2, (11, 20)),
        ("archer", 2, (30, 20)),
        ("archer", 2, (31, 20))
    ],
    "Petite Armée Custom Battle": [
        ("giant", 1, (10, 20)),
        ("barbarian", 2, (11, 20)),
        ("barbarian", 2, (12, 20)),
        ("archer", 2, (13, 20)),
        ("archer", 2, (14, 20)),
        ("wall_breaker", 1, (15, 20)),
    ],
    "Armée Test Minima": [
        ("barbarian", 2, (0, 10)),
        ("archer", 2, (0, 11)),
    ],
    # Ajoutez d'autres configurations d'armées ici
}

def get_army_from_config(name: str, army_configs_dict: Dict = ARMY_CONFIGURATIONS) -> List[Troop]:
    """
    Crée et retourne une liste d'objets Troop basés sur une configuration nommée.
    """
    config = army_configs_dict.get(name)
    if not config:
        raise ValueError(f"Configuration d'armée nommée '{name}' non trouvée.")
    
    troops_list = []
    for troop_type, level, position in config:
        try:
            troops_list.append(create_troop(troop_type, level, position))
        except Exception as e:
            # Gérer l'erreur ou la logger, ou la lever plus haut
            print(f"AVERTISSEMENT: Impossible de créer la troupe {troop_type} Lvl {level} à {position} pour l'armée '{name}'. Erreur: {e}")
            # raise Exception(f"Échec critique de la création de l'armée: {e}")
    return troops_list

if __name__ == '__main__':
    # Test de la création d'armée
    try:
        test_army = get_army_from_config("Armée Mixte TH3 (Main)")
        print(f"Armée '{'Armée Mixte TH3 (Main)'}' créée avec {len(test_army)} troupes.")
        for troop in test_army:
            print(f"  - {troop.type} Lvl {troop.level} à ({troop.x}, {troop.y})")
        
        test_army_2 = get_army_from_config("Petite Armée Test Vitesse")
        print(f"Armée '{'Petite Armée Test Vitesse'}' créée avec {len(test_army_2)} troupes.")

    except ValueError as e:
        print(e) 