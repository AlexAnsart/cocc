"""
Classe de base pour les troupes
"""
import math
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from enum import Enum

class TroopState(Enum):
    """États possibles d'une troupe"""
    IDLE = "idle"
    MOVING = "moving"
    ATTACKING = "attacking"
    DEAD = "dead"

class Troop(ABC):
    """Classe de base pour toutes les troupes"""
    
    def __init__(self, troop_type: str, level: int, position: Tuple[float, float]):
        self.type = troop_type
        self.level = level
        self.x, self.y = position
        self.hp = self.max_hp
        self.state = TroopState.IDLE
        self.target = None
        self.target_position = None
        self.path = []
        self.path_index = 0
        self.last_attack_time = 0
        self.last_retarget_time = 0
        self.last_path_calculation_time = 0
        self.spawn_time = 0
        self.is_flying = False  # Par défaut, troupes au sol
        
    @property
    def max_hp(self) -> int:
        """Points de vie maximum"""
        from ..core.config import TROOP_STATS
        return TROOP_STATS[self.type][self.level]["hp"]
    
    @property
    def damage(self) -> int:
        """Dégâts par attaque"""
        from ..core.config import TROOP_STATS
        return TROOP_STATS[self.type][self.level]["damage"]
    
    @property
    def speed(self) -> float:
        """Vitesse de déplacement (tuiles par seconde)"""
        from ..core.config import TROOP_STATS
        return TROOP_STATS[self.type][self.level]["speed"]
    
    @property
    def range(self) -> float:
        """Portée d'attaque"""
        from ..core.config import TROOP_STATS
        return TROOP_STATS[self.type][self.level]["range"]
    
    @property
    def attack_speed(self) -> float:
        """Vitesse d'attaque (secondes entre attaques)"""
        from ..core.config import TROOP_STATS
        return TROOP_STATS[self.type][self.level]["attack_speed"]
    
    @property
    def housing_space(self) -> int:
        """Espace occupé dans les camps"""
        from ..core.config import TROOP_STATS
        return TROOP_STATS[self.type][self.level]["housing"]
    
    def take_damage(self, damage: int) -> None:
        """Inflige des dégâts à la troupe"""
        if self.state != TroopState.DEAD:
            self.hp -= damage
            if self.hp <= 0:
                self.hp = 0
                self.state = TroopState.DEAD
                self.target = None
                self.path = []
    
    def is_alive(self) -> bool:
        """Vérifie si la troupe est vivante"""
        return self.hp > 0
    
    def distance_to(self, x: float, y: float) -> float:
        """Calcule la distance euclidienne à un point"""
        return math.sqrt((self.x - x) ** 2 + (self.y - y) ** 2)
    
    def distance_to_building(self, building) -> float:
        """Calcule la distance au centre d'un bâtiment"""
        center_x, center_y = building.get_center()
        return self.distance_to(center_x, center_y)
    
    def can_attack(self, current_time: float) -> bool:
        """Vérifie si la troupe peut attaquer"""
        return current_time - self.last_attack_time >= self.attack_speed
    
    def is_in_range(self, building) -> bool:
        """Vérifie si un bâtiment est à portée d'attaque (distance à la hitbox)."""
        bx1, by1, bx2, by2 = building.get_hitbox() # Hitbox includes gap
        
        # Closest point on rectangle to troop (self.x, self.y)
        closest_x = max(bx1, min(self.x, bx2))
        closest_y = max(by1, min(self.y, by2))
        
        # Distance from troop to this closest point on hitbox
        dist_x = self.x - closest_x
        dist_y = self.y - closest_y
        distance_to_hitbox_edge = math.sqrt(dist_x**2 + dist_y**2)
        
        return distance_to_hitbox_edge <= self.range
    
    @abstractmethod
    def get_target_preference_score(self, building) -> float:
        """Retourne un score de préférence pour un bâtiment (plus bas = meilleure cible)"""
        pass
    
    def find_target(self, buildings: List, walls: List, current_time: float) -> Optional[object]:
        """Trouve la meilleure cible parmi les bâtiments"""
        from ..core.config import PATHFINDING_CONFIG
        
        # Vérifier s'il faut recalculer la cible
        # Retarget if current target destroyed, or if enough time passed, or if no target
        if self.target and not self.target.is_destroyed and \
           current_time - self.last_retarget_time < PATHFINDING_CONFIG["retarget_distance_threshold"] : # This config is actually an interval in seconds
             pass # Keep current target
        else:
            # Filtrer les bâtiments valides
            valid_buildings = [b for b in buildings if not b.is_destroyed]
            if not valid_buildings:
                self.target = None
                self.path = []
                return None
            
            # Trier par distance (vol d'oiseau pour une première sélection)
            # L'A* prendra en compte les murs pour le coût réel du chemin
            buildings_by_distance = sorted(valid_buildings, 
                                         key=lambda b: self.distance_to_building(b))
            
            # Prendre les N plus proches (ou plus pour certaines troupes)
            # Ce N peut être ajusté, ou on peut évaluer plus de cibles si nécessaire
            n_closest = 4 if self.type == "wall_breaker" else 3 
            # Make sure we don't go out of bounds
            closest_buildings_to_evaluate = buildings_by_distance[:min(n_closest, len(buildings_by_distance))]
            
            best_score = float('inf')
            potential_target = None
            
            for building_candidate in closest_buildings_to_evaluate:
                # Score de base : distance (sera affiné par A* plus tard si on veut) + préférence
                # Pour l'instant, on utilise la distance directe pour la sélection de cible,
                # et A* pour le chemin vers cette cible.
                base_score = self.distance_to_building(building_candidate) 
                preference_score = self.get_target_preference_score(building_candidate)
                
                score = base_score * preference_score
                
                if score < best_score:
                    best_score = score
                    potential_target = building_candidate
            
            if potential_target != self.target:
                self.target = potential_target
                self.last_retarget_time = current_time
                self.path = [] # Forcer le recalcul du chemin vers la nouvelle cible
        
        return self.target
    
    def calculate_path(self, target_building: object, all_buildings: List, walls: List, current_time: float) -> List[Tuple[float, float]]:
        """Calcule le chemin vers une position cible en utilisant A*."""
        from ..core.config import PATHFINDING_CONFIG, TILE_SIZE
        from ..systems.pathfinding import find_path # Import A*
        
        if not target_building:
            self.path = []
            return []

        # Déterminer la position cible pour A*
        # Idéalement, une position d'attaque valide la plus proche
        attack_positions = target_building.get_attack_positions(self.range)
        if not attack_positions:
            # Si pas de positions d'attaque (ex: bâtiment très grand ou inaccessible), cibler le centre
            target_center_x, target_center_y = target_building.get_center()
            target_pos_world = (target_center_x, target_center_y)
        else:
            # Choisir la position d'attaque la plus proche de la troupe par distance directe
            current_pos_world = (self.x, self.y)
            target_pos_world = min(attack_positions, 
                                   key=lambda pos: math.sqrt((pos[0] - current_pos_world[0])**2 + (pos[1] - current_pos_world[1])**2))

        # print(f"TPW_DEBUG: Troop {self.type} -> {target_building.type if target_building else 'None'}, TargetPos: {target_pos_world if target_pos_world else 'None'}") # SIMPLIFIED DEBUG

        # Vérifier s'il faut recalculer le chemin
        # Recalculer si pas de chemin, si la cible a changé (implicite car target_pos_world dérive de target_building),
        # ou si l'intervalle de recalcul est dépassé.
        recalculation_needed = False
        if not self.path:
            recalculation_needed = True
        elif self.target_position != target_pos_world: # La position exacte sur la tuile peut changer
            recalculation_needed = True
        elif current_time - self.last_path_calculation_time >= PATHFINDING_CONFIG["path_recalculation_interval"]:
            recalculation_needed = True
        
        if not recalculation_needed:
            return self.path

        # Appeler A*
        # Note: find_path prend les bâtiments et les murs pour construire la grille
        # `all_buildings` should contain all buildings including walls for context, 
        # but find_path will differentiate them based on its `walls` parameter.
        # Let's adjust `find_path` or how we pass these.
        # For now, `find_path` expects buildings (non-walls) and walls separately.
        
        non_wall_buildings = [b for b in all_buildings if b.type != "wall"]

        
        calculated_path = find_path(
            start_pos_world=(self.x, self.y),
            end_pos_world=target_pos_world,
            buildings=non_wall_buildings, # Pass only non-wall buildings
            walls=walls,                  # Pass walls separately
            troop_type=self.type,
            troop_is_flying=self.is_flying
        )
        
        if calculated_path:
            self.path = calculated_path
            # print(f"DEBUG: Path found for {self.type}: {self.path}")
        else:
            # print(f"DEBUG: No path found for {self.type} from ({self.x:.1f},{self.y:.1f}) to {target_pos_world}")
            self.path = [] # Pas de chemin trouvé, vider le chemin

        self.path_index = 0
        self.target_position = target_pos_world # Sauvegarder la destination pour laquelle ce chemin a été calculé
        self.last_path_calculation_time = current_time
        
        return self.path
    
    def move_towards(self, target_x: float, target_y: float, dt: float) -> None:
        """Déplace la troupe vers une position cible"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            # Normaliser la direction
            dx /= distance
            dy /= distance
            
            # Calculer le déplacement
            move_distance = min(self.speed * dt, distance)
            
            # Mettre à jour la position
            self.x += dx * move_distance
            self.y += dy * move_distance
            
            self.state = TroopState.MOVING
        else:
            self.state = TroopState.IDLE
    
    def attack(self, building, current_time: float) -> None:
        """Attaque un bâtiment"""
        if self.can_attack(current_time) and self.is_in_range(building):
            damage = self.get_damage_against(building)
            building.take_damage(damage)
            self.last_attack_time = current_time
            self.state = TroopState.ATTACKING
    
    def get_damage_against(self, building) -> int:
        """Retourne les dégâts contre un type de bâtiment spécifique"""
        return self.damage
    
    def update(self, dt: float, buildings: List, walls: List, current_time: float) -> None:
        """Met à jour la troupe"""
        from ..core.config import PATHFINDING_CONFIG
        if not self.is_alive():
            return
        
        # 1. Trouver/confirmer une cible
        self.find_target(buildings, walls, current_time) # Pass all buildings including walls
        
        if not self.target:
            self.state = TroopState.IDLE
            # print(f"DEBUG: {self.type} IDLE, no target")
            return
        
        # 2. Si à portée de la cible actuelle, attaquer
        if self.is_in_range(self.target):
            self.attack(self.target, current_time)
            # print(f"DEBUG: {self.type} attacking {self.target.type}")
        else:
            # 3. Sinon, se déplacer vers la cible
            #   a. Calculer/Récupérer le chemin vers la position d'attaque de la cible
            self.calculate_path(self.target, buildings, walls, current_time) # Pass all buildings and walls
            
            #   b. Suivre le chemin
            if self.path and self.path_index < len(self.path):
                target_x, target_y = self.path[self.path_index]
                self.move_towards(target_x, target_y, dt)
                # print(f"DEBUG: {self.type} moving to {target_x:.1f},{target_y:.1f} (waypoint {self.path_index}/{len(self.path)-1}) for {self.target.type}")
                
                # Vérifier si on a atteint le waypoint actuel
                if self.distance_to(target_x, target_y) < 0.2: # Increased tolerance a bit
                    self.path_index += 1
                    # print(f"DEBUG: {self.type} reached waypoint, next index {self.path_index}")
            else:
                # Pas de chemin ou chemin terminé mais pas encore à portée (peut arriver si la cible est bloquée)
                self.state = TroopState.IDLE # Ou MOVING si on attend un recalcul? Pour l'instant IDLE.
                # print(f"DEBUG: {self.type} IDLE, no path or path ended, target: {self.target.type}, in_range: {self.is_in_range(self.target)}")
                # Potentially force a retarget or path recalculation if stuck
                if current_time - self.last_path_calculation_time > PATHFINDING_CONFIG["path_recalculation_interval"] * 0.5 : # check more frequently if stuck
                    self.path = [] # force recalculation next tick
                    # print(f"DEBUG: {self.type} forcing path recalc as it seems stuck")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(type={self.type}, level={self.level}, pos=({self.x:.1f},{self.y:.1f}), hp={self.hp}/{self.max_hp}, state={self.state.value})" 