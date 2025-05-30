"""
Classes pour les autres types de bâtiments
"""
from typing import Tuple
from .building import Building
from .defense_buildings import Cannon, ArcherTower, Mortar

class Wall(Building):
    """Mur - bloque le passage des troupes"""
    
    def __init__(self, level: int, position: Tuple[int, int]):
        super().__init__("wall", level, position)
        
    @property
    def max_hp(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS["wall"][self.level]["hp"]
    
    @property
    def size(self) -> int:
        return 1
    
    def is_blocking(self) -> bool:
        """Les murs bloquent toujours le passage"""
        return not self.is_destroyed


class TownHall(Building):
    """Hôtel de ville - bâtiment principal"""
    
    def __init__(self, level: int, position: Tuple[int, int]):
        super().__init__("town_hall", level, position)
        
    @property
    def max_hp(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS["town_hall"][self.level]["hp"]
    
    @property
    def size(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS["town_hall"][self.level]["size"]


class ResourceBuilding(Building):
    """Classe de base pour les bâtiments de ressources"""
    
    def __init__(self, building_type: str, level: int, position: Tuple[int, int]):
        super().__init__(building_type, level, position)
        self.stored_resources = 0
        
    @property
    def max_hp(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS[self.type][self.level]["hp"]
    
    @property
    def size(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS[self.type][self.level]["size"]
    
    def is_resource_building(self) -> bool:
        return True


class ElixirCollector(ResourceBuilding):
    """Collecteur d'élixir"""
    
    def __init__(self, level: int, position: Tuple[int, int]):
        super().__init__("elixir_collector", level, position)


class ElixirStorage(ResourceBuilding):
    """Réservoir d'élixir"""
    
    def __init__(self, level: int, position: Tuple[int, int]):
        super().__init__("elixir_storage", level, position)


class GoldMine(ResourceBuilding):
    """Mine d'or"""
    
    def __init__(self, level: int, position: Tuple[int, int]):
        super().__init__("gold_mine", level, position)


class GoldStorage(ResourceBuilding):
    """Réservoir d'or"""
    
    def __init__(self, level: int, position: Tuple[int, int]):
        super().__init__("gold_storage", level, position)


class ArmyBuilding(Building):
    """Classe de base pour les bâtiments militaires"""
    
    @property
    def max_hp(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS[self.type][self.level]["hp"]
    
    @property
    def size(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS[self.type][self.level]["size"]


class Barracks(ArmyBuilding):
    """Caserne"""
    
    def __init__(self, level: int, position: Tuple[int, int]):
        super().__init__("barracks", level, position)


class ArmyCamp(ArmyBuilding):
    """Camp militaire"""
    
    def __init__(self, level: int, position: Tuple[int, int]):
        super().__init__("army_camp", level, position)
        
    @property
    def capacity(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS["army_camp"][self.level]["capacity"]


class Laboratory(ArmyBuilding):
    """Laboratoire"""
    
    def __init__(self, level: int, position: Tuple[int, int]):
        super().__init__("laboratory", level, position)


class ClanCastle(Building):
    """Château de clan"""
    
    def __init__(self, level: int, position: Tuple[int, int]):
        super().__init__("clan_castle", level, position)
        
    @property
    def max_hp(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS["clan_castle"][self.level]["hp"]
    
    @property
    def size(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS["clan_castle"][self.level]["size"]
    
    @property
    def capacity(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS["clan_castle"][self.level]["capacity"]


class BuilderHut(Building):
    """Cabane d'ouvrier"""
    
    def __init__(self, position: Tuple[int, int]):
        super().__init__("builder_hut", 1, position)
        
    @property
    def max_hp(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS["builder_hut"][1]["hp"]
    
    @property
    def size(self) -> int:
        from ..core.config import BUILDING_STATS
        return BUILDING_STATS["builder_hut"][1]["size"]


# Factory function pour créer des bâtiments
def create_building(building_type: str, level: int, position: Tuple[int, int]) -> Building:
    """Crée un bâtiment du type spécifié"""
    building_classes = {
        "wall": Wall,
        "town_hall": TownHall,
        "cannon": Cannon,
        "archer_tower": ArcherTower,
        "mortar": Mortar,
        "elixir_collector": ElixirCollector,
        "elixir_storage": ElixirStorage,
        "gold_mine": GoldMine,
        "gold_storage": GoldStorage,
        "barracks": Barracks,
        "army_camp": ArmyCamp,
        "laboratory": Laboratory,
        "clan_castle": ClanCastle,
        "builder_hut": BuilderHut
    }
    
    if building_type not in building_classes:
        raise ValueError(f"Type de bâtiment inconnu : {building_type}")
    
    cls = building_classes[building_type]
    
    # Cas spécial pour les murs et builder huts qui n'ont qu'un seul niveau
    if building_type == "wall":
        return cls(level, position)
    elif building_type == "builder_hut":
        return cls(position)
    elif building_type in ["cannon", "archer_tower", "mortar"]:
        # Les défenses attendent building_type comme premier argument
        return cls(building_type, level, position)
    else:
        # Les autres bâtiments n'attendent que level et position
        return cls(level, position) 