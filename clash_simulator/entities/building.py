"""
Classes de base pour les bâtiments
"""
import math
from abc import ABC, abstractmethod
from typing import Tuple, Optional, List

class Building(ABC):
    """Classe de base pour tous les bâtiments"""
    
    def __init__(self, building_type: str, level: int, position: Tuple[int, int]):
        self.type = building_type
        self.level = level
        self.x, self.y = position
        self.hp = self.max_hp
        self.is_destroyed = False
        self.gap = self._get_gap()
        
    @property
    @abstractmethod
    def max_hp(self) -> int:
        """Points de vie maximum du bâtiment"""
        pass
    
    @property
    @abstractmethod
    def size(self) -> int:
        """Taille du bâtiment en tuiles"""
        pass
    
    def _get_gap(self) -> float:
        """Retourne le gap autour du bâtiment"""
        from ..core.config import BUILDING_GAPS
        return BUILDING_GAPS.get(self.type, BUILDING_GAPS["default"])
    
    def take_damage(self, damage: int) -> None:
        """Inflige des dégâts au bâtiment"""
        if not self.is_destroyed:
            self.hp -= damage
            if self.hp <= 0:
                self.hp = 0
                self.is_destroyed = True
    
    def get_center(self) -> Tuple[float, float]:
        """Retourne le centre du bâtiment"""
        return (self.x + self.size / 2, self.y + self.size / 2)
    
    def get_hitbox(self) -> Tuple[float, float, float, float]:
        """Retourne la hitbox du bâtiment (incluant le gap)"""
        x1 = self.x - self.gap
        y1 = self.y - self.gap
        x2 = self.x + self.size + self.gap
        y2 = self.y + self.size + self.gap
        return (x1, y1, x2, y2)
    
    def contains_point(self, x: float, y: float) -> bool:
        """Vérifie si un point est dans le bâtiment"""
        return (self.x <= x < self.x + self.size and 
                self.y <= y < self.y + self.size)
    
    def distance_to(self, x: float, y: float) -> float:
        """Calcule la distance euclidienne à un point"""
        center_x, center_y = self.get_center()
        return math.sqrt((center_x - x) ** 2 + (center_y - y) ** 2)
    
    def _generate_points_on_line(self, start_coord: float, end_coord: float, fixed_coord: float, is_x_iter: bool, step: float) -> List[Tuple[float, float]]:
        points = []
        current = start_coord
        # Add a small epsilon to end_coord for floating point comparison to ensure end_coord is included if reachable by step
        while current <= end_coord + 1e-9:
            if is_x_iter:
                points.append((current, fixed_coord))
            else:
                points.append((fixed_coord, current))
            current += step
        return points

    def get_attack_positions(self, attack_range: float) -> List[Tuple[float, float]]:
        """Retourne les positions d'où une troupe peut attaquer ce bâtiment"""
        raw_candidate_positions: List[Tuple[float, float]] = []
        hitbox_x1, hitbox_y1, hitbox_x2, hitbox_y2 = self.get_hitbox()
        
        R = attack_range 
        step = 0.5 # Sampling step, TILE_SIZE / 2.0 essentially

        # Generate points on a rectangle surrounding the hitbox, offset by R.
        # Points on line below hitbox: y = hitbox_y1 - R, x from (hitbox_x1 - R) to (hitbox_x2 + R)
        raw_candidate_positions.extend(self._generate_points_on_line(hitbox_x1 - R, hitbox_x2 + R, hitbox_y1 - R, True, step))
        # Points on line above hitbox: y = hitbox_y2 + R, x from (hitbox_x1 - R) to (hitbox_x2 + R)
        raw_candidate_positions.extend(self._generate_points_on_line(hitbox_x1 - R, hitbox_x2 + R, hitbox_y2 + R, True, step))
        # Points on line left of hitbox: x = hitbox_x1 - R, y from (hitbox_y1 - R) to (hitbox_y2 + R)
        raw_candidate_positions.extend(self._generate_points_on_line(hitbox_y1 - R, hitbox_y2 + R, hitbox_x1 - R, False, step))
        # Points on line right of hitbox: x = hitbox_x2 + R, y from (hitbox_y1 - R) to (hitbox_y2 + R)
        raw_candidate_positions.extend(self._generate_points_on_line(hitbox_y1 - R, hitbox_y2 + R, hitbox_x2 + R, False, step))
        
        # Deduplicate raw candidates first (converting to set and back to list, then sorting for determinism)
        # Sorting helps in later selecting the 'min' distance target predictably if multiple points are equidistant.
        unique_candidate_positions = sorted(list(set(raw_candidate_positions)))

        valid_positions = []
        for pos_x, pos_y in unique_candidate_positions:
            if self._is_valid_attack_position(pos_x, pos_y, attack_range):
                valid_positions.append((pos_x, pos_y))
        
        return valid_positions
    
    def _is_valid_attack_position(self, troop_x: float, troop_y: float, troop_attack_range: float) -> bool:
        """Vérifie si une position d'attaque est valide pour une troupe."""
        from ..core.config import GRID_SIZE # TILE_SIZE is 1.0

        # 1. Check if the troop's potential position is within grid boundaries
        if not (0 <= troop_x < GRID_SIZE and 0 <= troop_y < GRID_SIZE):
            return False
        
        # 2. Check distance to building's hitbox (mimics Troop.is_in_range logic)
        bx1, by1, bx2, by2 = self.get_hitbox()

        # Closest point on building's hitbox rectangle to (troop_x, troop_y)
        closest_bx = max(bx1, min(troop_x, bx2))
        closest_by = max(by1, min(troop_y, by2))

        # Calculate squared distance from troop to this closest point on hitbox edge
        dist_sq = (troop_x - closest_bx)**2 + (troop_y - closest_by)**2
        
        # Troop is in range if distance is less than or equal to troop_attack_range.
        # Compare squared distances to avoid sqrt, add small epsilon for strict <= comparison.
        # (A + eps)^2 = A^2 + 2A*eps + eps^2. If eps is small, this is approx A^2.
        # So we compare dist_sq with (troop_attack_range^2 + some_tolerance).
        # A tolerance on the squared range handles floating point inaccuracies.
        return dist_sq <= (troop_attack_range**2 + 1e-9)
    
    def get_destruction_percentage(self) -> float:
        """Retourne le pourcentage de destruction du bâtiment"""
        return max(0, 100 * (1 - self.hp / self.max_hp))
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.type}, level={self.level}, pos=({self.x},{self.y}), hp={self.hp}/{self.max_hp})" 