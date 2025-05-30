from typing import Dict, List, Tuple
from ..systems.base_layout import BaseLayout

# Format: (type_batiment, niveau, (x, y))
BASE_CONFIGURATIONS: Dict[str, List[Tuple[str, int, Tuple[int, int]]]] = {
    "Simple TH3 Par Défaut": [
        # Town Hall (centre) - size 3x3
        ("town_hall", 3, (20, 20)), # Centre (21,21)

        # Defenses
        ("cannon", 3, (15, 18)), # Canon en haut à gauche, légèrement excentré
        ("cannon", 3, (25, 18)), # Canon en haut à droite, légèrement excentré
        ("archer_tower", 2, (18, 15)), # Tour d'archer en haut, au centre
        ("mortar", 1, (20, 25)),    # Mortier en bas, au centre (protégé)

        # Resources - dispersés à l'extérieur des murs principaux
        ("gold_storage", 2, (10, 10)),
        ("elixir_storage", 2, (30, 30)),
        ("gold_mine", 3, (8, 15)),
        ("elixir_collector", 3, (32, 15)),
        ("gold_mine", 3, (15, 8)),
        ("elixir_collector", 3, (25, 8)),
        ("gold_mine", 3, (8, 25)),
        ("elixir_collector", 3, (32, 25)),


        # Army Buildings - également à l'extérieur
        ("army_camp", 3, (10, 30)),
        ("army_camp", 3, (30, 10)),
        ("barracks", 2, (5, 20)),
        ("laboratory", 1, (35, 20)),

        # Builder Huts - coins extérieurs
        ("builder_hut", 1, (2, 2)),
        ("builder_hut", 1, (38, 38)),
        
        # Walls - TH3 max 75 walls lvl 3
        # Noyau central autour de TH, Mortar, Archer Tower
        # HDV (20,20) 3x3 -> occupe 20,21,22 en x et y
        # Mortier (20,25) 3x3 -> occupe 20,21,22 en x et 25,26,27 en y
        # Tour Archer (18,15) 2x2 -> occupe 18,19 en x et 15,16 en y

        # Première enceinte (autour de TH(20,20) et Tour Archer(18,15))
        # x de 16 à 24, y de 13 à 24
        # Murs horizontaux
        ("wall", 3, (17, 13)),("wall", 3, (18, 13)),("wall", 3, (19, 13)),("wall", 3, (20, 13)),("wall", 3, (21, 13)),("wall", 3, (22, 13)), ("wall", 3, (23, 13)),
        ("wall", 3, (17, 23)),("wall", 3, (18, 23)),("wall", 3, (19, 23)),                                                        ("wall", 3, (23, 23)), 
        # Murs verticaux
        ("wall", 3, (16, 14)),("wall", 3, (16, 15)),("wall", 3, (16, 16)),("wall", 3, (16, 17)), ("wall", 3, (16, 18)), ("wall", 3, (16, 19)), ("wall", 3, (16, 20)), ("wall", 3, (16, 21)), ("wall", 3, (16, 22)),
        ("wall", 3, (24, 14)),("wall", 3, (24, 15)),("wall", 3, (24, 16)),("wall", 3, (24, 17)), ("wall", 3, (24, 18)), ("wall", 3, (24, 19)), ("wall", 3, (24, 20)), ("wall", 3, (24, 21)), ("wall", 3, (24, 22)),
        
        # Compartiment pour le Mortier (20,25) plus bas
        ("wall", 3, (19, 24)), ("wall", 3, (20, 24)), ("wall", 3, (21, 24)), ("wall", 3, (22, 24)), ("wall", 3, (23, 24)), # Ligne au dessus du mortier, connecte à l'enceinte principale
        ("wall", 3, (19, 28)), ("wall", 3, (20, 28)), ("wall", 3, (21, 28)), ("wall", 3, (22, 28)), # Ligne en dessous
        ("wall", 3, (18, 25)), ("wall", 3, (18, 26)), ("wall", 3, (18, 27)), # Côté gauche mortier
        ("wall", 3, (23, 25)), ("wall", 3, (23, 26)), ("wall", 3, (23, 27)), # Côté droit mortier
                                      
        # Compartiments pour les canons
        # Canon 1 (15,18)
        ("wall", 3, (14, 17)), ("wall", 3, (15, 17)), ("wall", 3, (16, 17)), # au dessus
        # ("wall", 3, (14, 20)), ("wall", 3, (15, 20)), ("wall", 3, (16, 20)), # en dessous (utilise mur existant (16,20))
        ("wall", 3, (13, 18)), ("wall", 3, (13, 19)), # à gauche
        ("wall", 3, (17, 18)), ("wall", 3, (17, 19)), # à droite (vers mur principal)

        # Canon 2 (25,18)
        ("wall", 3, (24, 17)), ("wall", 3, (25, 17)), ("wall", 3, (26, 17)), # au dessus
        # ("wall", 3, (24, 20)), ("wall", 3, (25, 20)), ("wall", 3, (26, 20)), # en dessous (utilise mur existant (24,20))
        ("wall", 3, (23, 18)), ("wall", 3, (23, 19)), # à gauche (vers mur principal)
        ("wall", 3, (27, 18)), ("wall", 3, (27, 19)), # à droite

        # Total murs: 7 + 4 + 9 + 9 + 5 + 4 + 3+3 + 3+2+2 + 3+2+2 = 58 murs. Il en reste pour des funnels ou renforts.
        # Ajout de quelques murs pour "fermer" des accès ou créer des funnels
        ("wall", 3, (12, 17)), ("wall", 3, (12, 20)), # Ferme un peu l'ouest
        ("wall", 3, (28, 17)), ("wall", 3, (28, 20)), # Ferme un peu l'est
        ("wall", 3, (17, 12)), ("wall", 3, (23, 12)), # Ferme un peu le nord
        ("wall", 3, (18, 29)), ("wall", 3, (22, 29)), # Ferme un peu le sud du mortier

        # Encore 58 + 8 = 66 murs. On peut en ajouter pour boucher des trous.
        ("wall", 3, (19, 18)), # Jonction interne
        ("wall", 3, (22, 18)), # Jonction interne
        ("wall", 3, (15,21)),("wall", 3, (16,21)), # Renforts
        ("wall", 3, (24,21)),("wall", 3, (25,21)), # Renforts

        # Total: 66 + 2 + 4 = 72 murs. C'est bien.
    ],
    "Base Test Minima": [
        ("town_hall", 3, (10, 10)),
        ("cannon", 2, (5, 10)),
        # Pas de murs pour simplifier le test initial
    ],
    # Vous pouvez ajouter d'autres configurations de base ici
    # "Autre Base TH3": [ ... ]
}

def get_base_layout_from_config(name: str, base_configs_dict: Dict = BASE_CONFIGURATIONS) -> BaseLayout:
    """
    Crée et retourne un objet BaseLayout basé sur une configuration nommée.
    """
    config = base_configs_dict.get(name)
    if not config:
        raise ValueError(f"Configuration de base nommée '{name}' non trouvée.")
    
    base = BaseLayout(name=name)
    for building_type, level, position in config:
        if not base.add_building(building_type, level, position):
            print(f"AVERTISSEMENT: Impossible d'ajouter {building_type} Lvl {level} à {position} pour la base '{name}'. Vérifiez les limites ou la position.")
            # Vous pourriez choisir de lever une exception ici si l'ajout est critique
            # raise Exception(f"Échec critique de la création de la base : Impossible d'ajouter {building_type} Lvl {level} à {position} pour la base '{name}'.")
    return base

if __name__ == '__main__':
    # Test de la création de base à partir de la configuration
    try:
        default_base = get_base_layout_from_config("Simple TH3 Par Défaut")
        print(f"Base '{default_base.name}' créée avec succès.")
        print(f"Nombre de bâtiments: {len(default_base.buildings)}")
        print(f"Nombre de murs: {len(default_base.walls)}")
        # Afficher la base (nécessite TerminalDisplay)
        # from ..visualization.terminal_display import TerminalDisplay
        # display = TerminalDisplay()
        # display.render_base(default_base)
    except ValueError as e:
        print(e) 