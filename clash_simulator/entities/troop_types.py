"""
Classes pour les différents types de troupes
"""
from typing import Tuple, List
from .troop import Troop, TroopState
from ..core.config import DEFENSE_BUILDINGS, RESOURCE_BUILDINGS, PATHFINDING_CONFIG

class Barbarian(Troop):
    """Barbare - troupe de mêlée basique"""
    
    def __init__(self, level: int, position: Tuple[float, float]):
        super().__init__("barbarian", level, position)
    
    def get_target_preference_score(self, building, is_wall_blocking_path: bool = False) -> float:
        """Les barbares n'ont pas de préférence particulière, mais ne ciblent pas les murs directement."""
        if building.type == "wall":
            return float('inf') # Ne jamais cibler un mur directement
        return PATHFINDING_CONFIG["preference_multipliers"]["barbarian"]["all"]


class Archer(Troop):
    """Archer - troupe à distance"""
    
    def __init__(self, level: int, position: Tuple[float, float]):
        super().__init__("archer", level, position)
        self.is_flying = False # Les archers sont au sol mais peuvent tirer par-dessus certains murs
    
    def get_target_preference_score(self, building, is_wall_blocking_path: bool = False) -> float:
        """Les archers n'ont pas de préférence particulière, mais ne ciblent pas les murs directement."""
        if building.type == "wall":
             # Les archers peuvent tirer par-dessus les murs, donc un mur n'est jamais une cible prioritaire.
             # Sauf si c'est la seule chose qui reste.
            return float('inf')
        return PATHFINDING_CONFIG["preference_multipliers"]["archer"]["all"]


class Giant(Troop):
    """Géant - tank qui cible les défenses"""
    
    def __init__(self, level: int, position: Tuple[float, float]):
        super().__init__("giant", level, position)
    
    def get_target_preference_score(self, building, is_wall_blocking_path: bool = False) -> float:
        """Les géants préfèrent fortement les défenses, ne ciblent pas les murs directement."""
        if building.type == "wall":
            return float('inf') # Ne jamais cibler un mur directement
        
        if building.type in DEFENSE_BUILDINGS:
            return PATHFINDING_CONFIG["preference_multipliers"]["giant"]["defense"]
        else:
            return PATHFINDING_CONFIG["preference_multipliers"]["giant"]["other"]
    
    # La logique find_target spécifique aux géants reste importante
    def find_target(self, buildings: List, walls: List, current_time: float):
        """Les géants ne ciblent que les défenses s'il y en a, sinon autres bâtiments (murs en dernier recours via A*)."""
        
        active_buildings = [b for b in buildings if not b.is_destroyed]
        active_defenses = [d for d in active_buildings if d.type in DEFENSE_BUILDINGS]
        
        if active_defenses:
            # Cibler parmi les défenses actives uniquement
            return super().find_target(active_defenses, walls, current_time)
        else:
            # S'il n'y a plus de défenses, cibler n'importe quel autre bâtiment (non-mur de préférence)
            # super().find_target va déjà filtrer les murs si possible grâce aux scores de préférence.
            return super().find_target(active_buildings, walls, current_time)


class WallBreaker(Troop):
    """Casse-mur - troupe kamikaze qui cible les bâtiments, en traversant les murs aisément."""
    
    def __init__(self, level: int, position: Tuple[float, float]):
        super().__init__("wall_breaker", level, position)
        self.has_exploded = False
    
    def get_target_preference_score(self, building, is_wall_blocking_path: bool = False) -> float:
        """
        Les Wall Breakers n'ont pas de préférence de cible particulière pour les bâtiments.
        Leur faible pénalité pour les murs dans A* les guidera à travers les murs si nécessaire.
        Retourne un score neutre pour tous les types de bâtiments.
        """
        # Un score de préférence de 1.0 signifie aucune préférence particulière.
        # La clé "other" dans PATHFINDING_CONFIG est à 1.0 pour wall_breaker, ce qui est bien.
        # Si on veut qu'ils ignorent complètement les murs comme *cibles* (mais pas pour le pathfinding),
        # on pourrait mettre float('inf') pour building.type == 'wall'.
        # Mais pour l'instant, laissons-les pouvoir cibler un mur si c'est la seule chose "proche" 
        # et que le pathfinding les y amène avec une faible pénalité.
        # Le comportement "cible un bâtiment, traverse les murs" est mieux géré par A* avec faible pénalité murale.
        return PATHFINDING_CONFIG["preference_multipliers"]["wall_breaker"].get(building.type, 1.0) 

    def find_target(self, buildings: List, walls: List, current_time: float):
        """
        Les Wall Breakers ciblent n'importe quel bâtiment. Leur pathfinding 
        les fera traverser les murs avec une faible pénalité.
        """
        # Appelle la méthode find_target de la classe Troop de base, 
        # sans filtrage spécifique des cibles ici pour le WallBreaker.
        # get_target_preference_score donnera un score neutre pour tous les bâtiments.
        # La faible pénalité des murs dans A* (config.py) est cruciale.
        return super().find_target(buildings, walls, current_time)

    def get_damage_against(self, building) -> int:
        """Dégâts multipliés contre les murs s'ils finissent par en attaquer un."""
        if building.type == "wall":
            from ..core.config import TROOP_STATS
            return TROOP_STATS["wall_breaker"][self.level]["wall_damage"]
        else:
            # Les WB ne devraient pas attaquer autre chose que des murs avant d'exploser.
            # S'ils attaquent un autre bâtiment, c'est probablement après que les murs proches aient été détruits
            # et qu'ils sont sur le point d'exploser (ou bug).
            # Pour l'explosion, ils infligent leurs dégâts normaux (faibles).
            # S'ils sont forcés d'attaquer un bâtiment (pas un mur) avant d'exploser, 
            # ils font leurs dégâts de base.
            return self.damage # Dégâts de base si ce n'est pas un mur.
    
    def attack(self, building, current_time):
        """Explose au contact de sa cible (qui devrait être un mur ou un bâtiment derrière un mur)."""
        # La condition principale d'explosion est d'être à portée de la cible finale
        # trouvée par le pathfinding (qui a une très faible pénalité pour les murs).
        if self.can_attack(current_time) and self.is_in_range(building) and not self.has_exploded:
            # Appliquer des dégâts à la cible (qui est souvent un mur, mais peut être le bâtiment final)
            # Si c'est un mur, les dégâts sont majorés.
            # S'ils atteignent un bâtiment non-mur en étant "in_range" pour leur explosion,
            # ils l'endommagent avec leurs dégâts d'explosion (qui sont leurs dégâts de base).
            
            # Pour l'instant, l'explosion affecte la cible directe.
            # Une vraie explosion de zone n'est pas implémentée ici.
            damage_to_apply = self.get_damage_against(building) # Prend en compte si c'est un mur
            building.take_damage(damage_to_apply)
            
            # Le casse-mur meurt après l'explosion
            self.has_exploded = True
            self.hp = 0
            self.state = TroopState.DEAD
    
    def update(self, dt, buildings, walls, current_time):
        """Comportement de mise à jour standard. L'explosion est gérée par la méthode attack.
        La logique de ciblage des murs via faible pénalité est dans A*.
        """
        if not self.is_alive() or self.has_exploded: # Vérifier aussi has_exploded au cas où
            return
        
        # Utilise la méthode update de la classe Troop de base.
        # find_target() sera appelée, puis calculate_path(), puis move_towards() ou attack().
        # attack() gérera l'explosion.
        super().update(dt, buildings, walls, current_time)


class Goblin(Troop):
    """Gobelin - troupe rapide qui préfère les ressources"""
    
    def __init__(self, level: int, position: Tuple[float, float]):
        super().__init__("goblin", level, position)
    
    def get_target_preference_score(self, building) -> float:
        """Les gobelins préfèrent les bâtiments de ressources"""
        from ..core.config import PATHFINDING_CONFIG
        
        if building.type in RESOURCE_BUILDINGS:
            return PATHFINDING_CONFIG["preference_multipliers"]["goblin"]["resource"]
        else:
            return PATHFINDING_CONFIG["preference_multipliers"]["goblin"]["other"]
    
    def get_damage_against(self, building) -> int:
        """Dégâts doublés contre les ressources"""
        if building.type in RESOURCE_BUILDINGS:
            from ..core.config import TROOP_STATS
            return TROOP_STATS["goblin"][self.level]["resource_damage"]
        else:
            return self.damage


# Factory function pour créer des troupes
def create_troop(troop_type: str, level: int, position: Tuple[float, float]) -> Troop:
    """Crée une troupe du type spécifié"""
    troop_classes = {
        "barbarian": Barbarian,
        "archer": Archer,
        "giant": Giant,
        "wall_breaker": WallBreaker,
        "goblin": Goblin
    }
    
    if troop_type not in troop_classes:
        raise ValueError(f"Type de troupe inconnu : {troop_type}")
    
    cls = troop_classes[troop_type]
    return cls(level, position) 