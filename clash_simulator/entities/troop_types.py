"""
Classes pour les différents types de troupes
"""
from typing import Tuple
from .troop import Troop, TroopState
from ..core.config import DEFENSE_BUILDINGS, RESOURCE_BUILDINGS

class Barbarian(Troop):
    """Barbare - troupe de mêlée basique"""
    
    def __init__(self, level: int, position: Tuple[float, float]):
        super().__init__("barbarian", level, position)
    
    def get_target_preference_score(self, building) -> float:
        """Les barbares n'ont pas de préférence particulière"""
        from ..core.config import PATHFINDING_CONFIG
        return PATHFINDING_CONFIG["preference_multipliers"]["barbarian"]["all"]


class Archer(Troop):
    """Archer - troupe à distance"""
    
    def __init__(self, level: int, position: Tuple[float, float]):
        super().__init__("archer", level, position)
    
    def get_target_preference_score(self, building) -> float:
        """Les archers n'ont pas de préférence particulière"""
        from ..core.config import PATHFINDING_CONFIG
        return PATHFINDING_CONFIG["preference_multipliers"]["archer"]["all"]


class Giant(Troop):
    """Géant - tank qui cible les défenses"""
    
    def __init__(self, level: int, position: Tuple[float, float]):
        super().__init__("giant", level, position)
    
    def get_target_preference_score(self, building) -> float:
        """Les géants préfèrent fortement les défenses"""
        from ..core.config import PATHFINDING_CONFIG
        
        if building.type in DEFENSE_BUILDINGS:
            return PATHFINDING_CONFIG["preference_multipliers"]["giant"]["defense"]
        else:
            return PATHFINDING_CONFIG["preference_multipliers"]["giant"]["other"]
    
    def find_target(self, buildings, walls, current_time):
        """Les géants ne ciblent que les défenses s'il y en a"""
        # Filtrer pour ne garder que les défenses actives
        defenses = [b for b in buildings if b.type in DEFENSE_BUILDINGS and not b.is_destroyed]
        
        if defenses:
            # Ne considérer que les défenses
            return super().find_target(defenses, walls, current_time)
        else:
            # S'il n'y a plus de défenses, cibler n'importe quoi
            return super().find_target(buildings, walls, current_time)


class WallBreaker(Troop):
    """Casse-mur - troupe kamikaze qui cible les murs"""
    
    def __init__(self, level: int, position: Tuple[float, float]):
        super().__init__("wall_breaker", level, position)
        self.has_exploded = False
    
    def get_target_preference_score(self, building) -> float:
        """Les casse-murs préfèrent les bâtiments derrière des murs"""
        from ..core.config import PATHFINDING_CONFIG
        
        # Pour l'instant, préférence simple
        # TODO: Implémenter la détection de murs sur le chemin
        if building.type == "wall":
            return PATHFINDING_CONFIG["preference_multipliers"]["wall_breaker"]["wall"]
        else:
            return PATHFINDING_CONFIG["preference_multipliers"]["wall_breaker"]["other"]
    
    def get_damage_against(self, building) -> int:
        """Dégâts multipliés contre les murs"""
        if building.type == "wall":
            from ..core.config import TROOP_STATS
            return TROOP_STATS["wall_breaker"][self.level]["wall_damage"]
        else:
            return self.damage
    
    def attack(self, building, current_time):
        """Explose au contact"""
        if self.can_attack(current_time) and self.is_in_range(building) and not self.has_exploded:
            damage = self.get_damage_against(building)
            building.take_damage(damage)
            
            # Le casse-mur meurt après l'explosion
            self.has_exploded = True
            self.hp = 0
            self.state = TroopState.DEAD
    
    def update(self, dt, buildings, walls, current_time):
        """Mise à jour spéciale pour gérer l'explosion sur les murs rencontrés"""
        if not self.is_alive() or self.has_exploded:
            return
        
        # Vérifier s'il y a un mur très proche
        for wall in walls:
            if not wall.is_destroyed and self.distance_to_building(wall) <= 0.5:
                # Exploser sur le mur
                self.target = wall
                self.attack(wall, current_time)
                return
        
        # Comportement normal sinon
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