"""
Système de gestion des bases TH3
"""
import json
from typing import List, Dict, Tuple, Optional
from ..entities.defense_buildings import Cannon, ArcherTower, Mortar
from ..entities.other_buildings import (
    Wall, TownHall, ResourceBuilding, ArmyBuilding,
    ElixirCollector, ElixirStorage, GoldMine, GoldStorage,
    Barracks, ArmyCamp, Laboratory, ClanCastle, BuilderHut,
    create_building
)
from ..core.config import TH3_BUILDING_LIMITS, GRID_SIZE

class BaseLayout:
    """Représente une base TH3 avec tous ses bâtiments"""
    
    def __init__(self, name: str = "Base TH3"):
        self.name = name
        self.buildings = []
        self.walls = []
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.building_counts = {building_type: 0 for building_type in TH3_BUILDING_LIMITS}
        
    def add_building(self, building_type: str, level: int, position: Tuple[int, int]) -> bool:
        """Ajoute un bâtiment à la base"""
        x, y = position
        
        # Vérifier les limites
        if not self._can_add_building(building_type):
            print(f"Limite atteinte pour {building_type}")
            return False
        
        # Créer le bâtiment
        try:
            building = create_building(building_type, level, position)
        except Exception as e:
            print(f"Erreur lors de la création du bâtiment : {e}")
            return False
        
        # Vérifier la position
        if not self._is_valid_position(building):
            print(f"Position invalide pour {building_type} à {position}")
            return False
        
        # Ajouter le bâtiment
        if building_type == "wall":
            self.walls.append(building)
        else:
            self.buildings.append(building)
        
        # Mettre à jour la grille
        self._place_on_grid(building)
        
        # Mettre à jour les compteurs
        self.building_counts[building_type] += 1
        
        return True
    
    def remove_building(self, building) -> bool:
        """Retire un bâtiment de la base"""
        if building in self.buildings:
            self.buildings.remove(building)
        elif building in self.walls:
            self.walls.remove(building)
        else:
            return False
        
        # Retirer de la grille
        self._remove_from_grid(building)
        
        # Mettre à jour les compteurs
        self.building_counts[building.type] -= 1
        
        return True
    
    def _can_add_building(self, building_type: str) -> bool:
        """Vérifie si on peut ajouter ce type de bâtiment"""
        current_count = self.building_counts.get(building_type, 0)
        max_count = TH3_BUILDING_LIMITS.get(building_type, 0)
        return current_count < max_count
    
    def _is_valid_position(self, building) -> bool:
        """Vérifie si la position est valide pour ce bâtiment"""
        # Vérifier les limites de la carte
        if (building.x < 0 or building.y < 0 or 
            building.x + building.size > GRID_SIZE or 
            building.y + building.size > GRID_SIZE):
            return False
        
        # Vérifier les collisions avec d'autres bâtiments
        for y in range(building.y, building.y + building.size):
            for x in range(building.x, building.x + building.size):
                if self.grid[y][x] is not None:
                    return False
        
        # Vérifier les gaps (sauf pour les murs)
        if building.type != "wall":
            gap = int(building.gap)
            for y in range(max(0, building.y - gap), 
                          min(GRID_SIZE, building.y + building.size + gap)):
                for x in range(max(0, building.x - gap), 
                              min(GRID_SIZE, building.x + building.size + gap)):
                    if self.grid[y][x] is not None and self.grid[y][x].type != "wall":
                        return False
        
        return True
    
    def _place_on_grid(self, building) -> None:
        """Place le bâtiment sur la grille"""
        for y in range(building.y, building.y + building.size):
            for x in range(building.x, building.x + building.size):
                self.grid[y][x] = building
    
    def _remove_from_grid(self, building) -> None:
        """Retire le bâtiment de la grille"""
        for y in range(building.y, building.y + building.size):
            for x in range(building.x, building.x + building.size):
                if self.grid[y][x] == building:
                    self.grid[y][x] = None
    
    def save_to_dict(self) -> Dict:
        """Sauvegarde la base sous forme de dictionnaire"""
        data = {
            "name": self.name,
            "buildings": [],
            "walls": []
        }
        
        for building in self.buildings:
            data["buildings"].append({
                "type": building.type,
                "level": building.level,
                "x": building.x,
                "y": building.y
            })
        
        for wall in self.walls:
            data["walls"].append({
                "level": wall.level,
                "x": wall.x,
                "y": wall.y
            })
        
        return data
    
    def load_from_dict(self, data: Dict) -> None:
        """Charge une base depuis un dictionnaire"""
        self.name = data.get("name", "Base TH3")
        self.buildings.clear()
        self.walls.clear()
        self.grid = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.building_counts = {building_type: 0 for building_type in TH3_BUILDING_LIMITS}
        
        # Charger les bâtiments
        for building_data in data.get("buildings", []):
            self.add_building(
                building_data["type"],
                building_data["level"],
                (building_data["x"], building_data["y"])
            )
        
        # Charger les murs
        for wall_data in data.get("walls", []):
            self.add_building(
                "wall",
                wall_data["level"],
                (wall_data["x"], wall_data["y"])
            )
    
    def save_to_file(self, filename: str) -> None:
        """Sauvegarde la base dans un fichier JSON"""
        with open(filename, 'w') as f:
            json.dump(self.save_to_dict(), f, indent=2)
    
    def load_from_file(self, filename: str) -> None:
        """Charge une base depuis un fichier JSON"""
        with open(filename, 'r') as f:
            data = json.load(f)
            self.load_from_dict(data)
    
    def get_all_buildings(self) -> List:
        """Retourne tous les bâtiments (incluant les murs)"""
        return self.buildings + self.walls
    
    def get_defenses(self) -> List:
        """Retourne uniquement les défenses"""
        return [b for b in self.buildings if isinstance(b, (Cannon, ArcherTower, Mortar))]
    
    def get_resource_buildings(self) -> List:
        """Retourne uniquement les bâtiments de ressources"""
        return [b for b in self.buildings if isinstance(b, ResourceBuilding)]
    
    def get_total_hp(self) -> int:
        """Calcule les HP totaux de la base"""
        total = 0
        for building in self.get_all_buildings():
            if not building.is_destroyed:
                total += building.hp
        return total
    
    def get_destruction_percentage(self) -> float:
        """Calcule le pourcentage de destruction de la base"""
        all_buildings = self.get_all_buildings()
        if not all_buildings:
            return 0.0
            
        total_buildings = len(all_buildings)
        destroyed_buildings = sum(1 for b in all_buildings if b.is_destroyed)
        
        return (destroyed_buildings / total_buildings) * 100
    
    def get_stars(self) -> int:
        """Calcule le nombre d'étoiles obtenues"""
        destruction = self.get_destruction_percentage()
        town_hall_destroyed = any(
            isinstance(b, TownHall) and b.is_destroyed 
            for b in self.buildings
        )
        
        stars = 0
        if destruction >= 50:
            stars = 1
        if town_hall_destroyed:
            stars = max(stars, 1)
        if destruction == 100:
            stars = 3
        elif destruction >= 50 and town_hall_destroyed:
            stars = 2
        
        return stars
    
    def reset(self) -> None:
        """Réinitialise tous les bâtiments à leur état initial"""
        for building in self.get_all_buildings():
            building.hp = building.max_hp
            building.is_destroyed = False
            if hasattr(building, 'target'):
                building.target = None
            if hasattr(building, 'last_attack_time'):
                building.last_attack_time = 0
    
    def __repr__(self) -> str:
        return (f"BaseLayout(name='{self.name}', "
                f"buildings={len(self.buildings)}, "
                f"walls={len(self.walls)}, "
                f"destruction={self.get_destruction_percentage():.1f}%)")


class BaseBuilder:
    """Classe utilitaire pour aider à construire des bases complexes.
       Actuellement, les configurations de base sont gérées dans data/base_configs.py
    """
    # La méthode create_simple_th3_base() a été déplacée vers base_configs.py
    # Cette classe est conservée pour une utilisation future potentielle.
    pass 