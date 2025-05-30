"""
Classes pour les bâtiments défensifs
"""
import math
import time
from typing import Optional, List, Tuple
from .building import Building
from .troop_types import Troop
from ..core.config import DEFENSE_STATS, TILE_SIZE
from ..entities.troop import Troop as TroopEntity
from ..utils.logger import BattleLogger

class Projectile:
    """Représente un projectile (obus de mortier, etc.)"""
    def __init__(self, origin_x: float, origin_y: float, target_x: float, target_y: float, \
                 speed: float, damage: int, area_of_effect: float = 0, origin_type: str = "unknown"):
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.current_x = origin_x
        self.current_y = origin_y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.damage = damage
        self.area_of_effect = area_of_effect
        self.origin_type = origin_type

        self.total_dist = math.sqrt((target_x - origin_x)**2 + (target_y - origin_y)**2)
        self.travel_time = self.total_dist / speed if speed > 1e-6 else 0
        self.time_elapsed = 0
        self.has_impacted = False

    def update(self, dt: float) -> None:
        if self.has_impacted:
            return
        
        self.time_elapsed += dt
        if self.travel_time == 0:
            self.current_x = self.target_x
            self.current_y = self.target_y
            self.has_impacted = True
        elif self.time_elapsed >= self.travel_time:
            self.current_x = self.target_x
            self.current_y = self.target_y
            self.has_impacted = True
        else:
            ratio = self.time_elapsed / self.travel_time
            self.current_x = self.origin_x + (self.target_x - self.origin_x) * ratio
            self.current_y = self.origin_y + (self.target_y - self.origin_y) * ratio

class DefenseBuilding(Building):
    """Classe de base pour les bâtiments défensifs"""
    
    def __init__(self, building_type: str, level: int, position: Tuple[int, int]):
        super().__init__(building_type, level, position)
        self.target = None
        self.last_attack_time = 0
        self.rotation = 0.0  # Rotation en radians pour l'affichage
        
    @property
    def damage(self) -> int:
        """Dégâts par attaque"""
        return DEFENSE_STATS[self.type][self.level]["damage"]
    
    @property
    def range(self) -> float:
        """Portée d'attaque"""
        return DEFENSE_STATS[self.type][self.level]["range"]
    
    @property
    def attack_speed(self) -> float:
        """Vitesse d'attaque en secondes"""
        return DEFENSE_STATS[self.type][self.level]["attack_speed"]
    
    def get_hitbox_for_range_check(self) -> Tuple[float, float, float, float]:
        # Par défaut, la hitbox pour la portée est la hitbox principale du bâtiment (self.x, self.y à self.x+size, self.y+size)
        # Cela n'inclut PAS le self.gap, car la portée est généralement mesurée depuis le bord du bâtiment.
        return (self.x, self.y, self.x + self.size, self.y + self.size)

    def is_in_range(self, troop: Troop) -> bool:
        """Vérifie si une troupe est à portée (distance au bord de la hitbox de portée)."""
        bx1, by1, bx2, by2 = self.get_hitbox_for_range_check()
        
        # Point le plus proche sur le rectangle de la hitbox de portée par rapport à la troupe (troop.x, troop.y)
        closest_x = max(bx1, min(troop.x, bx2))
        closest_y = max(by1, min(troop.y, by2))
        
        # Distance carrée de la troupe à ce point le plus proche
        dist_sq = (troop.x - closest_x)**2 + (troop.y - closest_y)**2
        
        # La troupe est à portée si la distance est <= à la portée de la défense
        # Comparaison des carrés pour éviter sqrt
        return dist_sq <= (self.range**2 + 1e-9) # Ajout d'epsilon pour la comparaison flottante

    def can_attack_time(self, current_time: float) -> bool:
        """Vérifie si la défense peut attaquer basé sur sa vitesse d'attaque."""
        return current_time - self.last_attack_time >= self.attack_speed

    def find_target(self, troops: List[Troop], logger: Optional[BattleLogger] = None) -> Optional[Troop]:
        """Trouve une cible valide parmi les troupes fournies."""
        valid_targets = []
        for troop in troops:
            if troop.is_alive() and self.can_target(troop) and self.is_in_range(troop):
                valid_targets.append(troop)
        
        if not valid_targets:
            return None
        
        # Stratégie de ciblage par défaut : la plus proche du centre de la défense
        # (pourrait être surchargé pour des comportements plus complexes)
        center_x, center_y = self.get_center()
        valid_targets.sort(key=lambda t: math.sqrt((t.x - center_x)**2 + (t.y - center_y)**2))
        
        chosen_target = valid_targets[0]
        if logger and self.target != chosen_target:
             logger.debug(f"Defense {self.type} LVL{self.level} found potential target: {chosen_target.type} LVL{chosen_target.level}", sim_time=logger.current_sim_time_for_event if hasattr(logger, 'current_sim_time_for_event') else 0.0)
        return chosen_target

    def can_target(self, troop: Troop) -> bool:
        """Vérifie si cette défense PEUT cibler ce type de troupe (ex: terrestre/aérien)."""
        return True # Par défaut, peut cibler toutes les troupes.

    def attack(self, target_troop: Troop, current_time: float, projectiles_list: List[Projectile], logger: Optional[BattleLogger] = None) -> None:
        """Logique d'attaque de base pour les défenses à tir direct (Cannon, ArcherTower)."""
        # Cette méthode sera appelée par update si une attaque doit avoir lieu.
        # can_attack_time et is_in_range devraient déjà avoir été vérifiées.
        if logger: 
            log_tick = getattr(logger, 'current_tick_for_event', None)
            log_sim_time = getattr(logger, 'current_sim_time_for_event', current_time)
            logger.info(f"{self.type} LVL{self.level} at ({self.x},{self.y}) attacks {target_troop.type} LVL{target_troop.level} at ({target_troop.x:.1f},{target_troop.y:.1f}) for {self.damage} damage.", 
                        tick=log_tick, sim_time=log_sim_time)
        
        target_troop.take_damage(self.damage)
        self.last_attack_time = current_time 
        
        # Rotation pour l'affichage
        dx = target_troop.x - (self.x + self.size / 2)
        dy = target_troop.y - (self.y + self.size / 2)
        self.rotation = math.atan2(dy, dx)
        
        if not target_troop.is_alive() and logger:
            log_tick_destroyed = getattr(logger, 'current_tick_for_event', None)
            log_sim_time_destroyed = getattr(logger, 'current_sim_time_for_event', current_time)
            logger.info(f"Troop {target_troop.type} LVL{target_troop.level} destroyed by {self.type} LVL{self.level}.", 
                        tick=log_tick_destroyed, sim_time=log_sim_time_destroyed)

    def update(self, dt: float, troops: List[Troop], current_time: float, projectiles_list: List[Projectile], logger: Optional[BattleLogger] = None) -> None:
        """Met à jour l'état de la défense (ciblage, attaque)."""
        if self.is_destroyed:
            return

        # Passer le temps actuel au logger pour qu'il puisse l'utiliser pour les messages de log de cet update
        if logger:
            logger.current_tick_for_event = getattr(logger, 'simulator_current_tick', None) # Attribut à setter par le simulateur
            logger.current_sim_time_for_event = current_time

        # Vérifier si la cible actuelle est toujours valide
        if self.target:
            if not self.target.is_alive() or not self.can_target(self.target) or not self.is_in_range(self.target):
                if logger: 
                    logger.debug(f"Defense {self.type} LVL{self.level} lost target {self.target.type if self.target else 'None'} (dead, out of range/sight, or invalid type).", sim_time=current_time)
                self.target = None

        # Si pas de cible, en trouver une nouvelle
        if not self.target:
            self.target = self.find_target(troops, logger) # Passer logger à find_target
            if self.target and logger:
                logger.info(f"Defense {self.type} LVL{self.level} acquired new target: {self.target.type} LVL{self.target.level} at ({self.target.x:.1f},{self.target.y:.1f}).", sim_time=current_time)

        # Si une cible valide est présente et que la défense peut tirer
        if self.target and self.can_attack_time(current_time):
            # Re-vérifier is_in_range juste avant d'attaquer, car la cible a pu bouger
            if self.is_in_range(self.target):
                self.attack(self.target, current_time, projectiles_list, logger)
            else:
                # La cible a bougé hors de portée entre le find_target/début du tick et le moment de l'attaque
                if logger: 
                    logger.debug(f"Defense {self.type} LVL{self.level} target {self.target.type} LVL{self.target.level} moved out of range before attack could occur.", sim_time=current_time)
                self.target = None # Forcer la recherche d'une nouvelle cible

class Cannon(DefenseBuilding):
    """Canon - attaque uniquement les troupes au sol"""
    
    @property
    def max_hp(self) -> int:
        return DEFENSE_STATS["cannon"][self.level]["hp"]
    
    @property
    def size(self) -> int:
        return 3
    
    def can_target(self, troop: Troop) -> bool:
        """Le canon ne peut cibler que les troupes au sol"""
        return not getattr(troop, 'is_flying', False)

    def attack(self, target: Troop, current_time: float, projectiles_list: List[Projectile], logger: Optional[BattleLogger] = None) -> None:
        if self.can_target(target) and self.is_in_range(target):
            if logger: 
                logger.info(f"{self.type} LVL{self.level} at ({self.x},{self.y}) attacks {target.type} LVL{target.level} at ({target.x:.1f},{target.y:.1f}) for {self.damage} damage.", 
                            sim_time=current_time)
            target.take_damage(self.damage)
            self.last_attack_time = current_time
            if not target.is_alive() and logger:
                logger.info(f"Troop {target.type} LVL{target.level} destroyed by {self.type} LVL{self.level}.", 
                            sim_time=current_time)


class ArcherTower(DefenseBuilding):
    """Tour d'archer - attaque sol et air"""
    
    @property
    def max_hp(self) -> int:
        return DEFENSE_STATS["archer_tower"][self.level]["hp"]
    
    @property
    def size(self) -> int:
        return 3
    
    def can_target(self, troop: Troop) -> bool:
        """La tour d'archer peut cibler toutes les troupes"""
        return True

    def attack(self, target: Troop, current_time: float, projectiles_list: List[Projectile], logger: Optional[BattleLogger] = None) -> None:
        if self.can_target(target) and self.is_in_range(target):
            if logger: 
                logger.info(f"{self.type} LVL{self.level} at ({self.x},{self.y}) attacks {target.type} LVL{target.level} at ({target.x:.1f},{target.y:.1f}) for {self.damage} damage.", 
                            sim_time=current_time)
            target.take_damage(self.damage)
            self.last_attack_time = current_time
            if not target.is_alive() and logger:
                logger.info(f"Troop {target.type} LVL{target.level} destroyed by {self.type} LVL{self.level}.", 
                            sim_time=current_time)


class Mortar(DefenseBuilding):
    """Mortier - attaque de zone avec zone morte"""
    
    def __init__(self, building_type: str, level: int, position: Tuple[int, int]):
        super().__init__(building_type, level, position)
        self.projectiles = []  # Pour l'animation des projectiles
        self.projectile_speed = DEFENSE_STATS["mortar"][self.level].get("projectile_speed", 3) # Tuiles/sec, ajusté
        self.area_of_effect = DEFENSE_STATS["mortar"][self.level].get("splash_radius", 1.5) # Rayon AoE
    
    @property
    def max_hp(self) -> int:
        return DEFENSE_STATS["mortar"][self.level]["hp"]
    
    @property
    def size(self) -> int:
        return 4
    
    @property
    def range_min(self) -> float:
        """Portée minimale (zone morte)"""
        return DEFENSE_STATS["mortar"][self.level]["range_min"]
    
    @property
    def range_max(self) -> float:
        """Portée maximale"""
        return DEFENSE_STATS["mortar"][self.level]["range_max"]
    
    @property
    def splash_radius(self) -> float:
        """Rayon des dégâts de zone"""
        return DEFENSE_STATS["mortar"][self.level]["splash_radius"]
    
    @property
    def range(self) -> float:
        """Portée effective pour la recherche de cible"""
        return self.range_max
    
    def can_target(self, troop: Troop) -> bool:
        """Le mortier ne peut cibler que les troupes au sol dans sa zone de tir"""
        if getattr(troop, 'is_flying', False):
            return False
        
        distance = self.distance_to(troop.x, troop.y)
        return self.range_min <= distance <= self.range_max
    
    def find_target(self, troops: List[Troop], logger: Optional[BattleLogger] = None) -> Optional[Troop]:
        """Trouve la meilleure cible (groupe de troupes)"""
        best_target = None
        best_score = 0
        
        for troop in troops:
            if troop.hp <= 0 or not self.can_target(troop):
                continue
            
            # Compter les troupes dans le rayon de splash
            troops_in_splash = 0
            for other_troop in troops:
                if other_troop.hp > 0:
                    dx = other_troop.x - troop.x
                    dy = other_troop.y - troop.y
                    if math.sqrt(dx*dx + dy*dy) <= self.splash_radius:
                        troops_in_splash += 1
            
            # Score basé sur le nombre de troupes touchées
            score = troops_in_splash
            
            if score > best_score:
                best_score = score
                best_target = troop
        
        # Log si une nouvelle cible est trouvée (similaire à DefenseBuilding.find_target)
        if logger and best_target and (self.target != best_target):
             # Pour sim_time, on pourrait essayer d'obtenir l'heure actuelle si le logger est configuré pour l'avoir
             current_sim_time_for_log = getattr(logger, 'current_sim_time_for_event', 0.0)
             current_tick_for_log = getattr(logger, 'current_tick_for_event', None)
             logger.debug(f"Mortar {self.type} LVL{self.level} found potential target: {best_target.type} LVL{best_target.level} (Score: {best_score})", 
                          tick=current_tick_for_log, sim_time=current_sim_time_for_log)

        return best_target
    
    def attack(self, target: Troop, current_time: float, projectiles_list: List[Projectile], logger: Optional[BattleLogger] = None) -> None:
        if self.can_target(target) and self.is_in_range(target):
            # Mortier crée un projectile
            projectile = Projectile(
                origin_x=self.get_center()[0],
                origin_y=self.get_center()[1],
                target_x=target.x, # Cible le centre de la troupe pour le projectile
                target_y=target.y,
                speed=self.projectile_speed,
                damage=self.damage,
                area_of_effect=self.area_of_effect,
                origin_type=self.type
            )
            projectiles_list.append(projectile)
            self.last_attack_time = current_time
            if logger: 
                logger.info(f"{self.type} LVL{self.level} at ({self.x},{self.y}) fires projectile at ({target.x:.1f},{target.y:.1f}) (Troop: {target.type} LVL{target.level}).", 
                            sim_time=current_time)
    
    def apply_splash_damage(self, impact_x: float, impact_y: float, troops: List[Troop]) -> None:
        """Applique les dégâts de zone"""
        for troop in troops:
            if troop.hp > 0:
                dx = troop.x - impact_x
                dy = troop.y - impact_y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance <= self.splash_radius:
                    # Dégâts complets au centre, réduits sur les bords
                    damage_ratio = 1.0 - (distance / self.splash_radius) * 0.5
                    damage = int(self.damage * damage_ratio)
                    troop.take_damage(damage)
    
    def update(self, dt: float, troops: List[Troop], current_time: float, projectiles_list: List[Projectile], logger: Optional[BattleLogger] = None) -> None:
        """Met à jour le mortier et ses projectiles"""
        super().update(dt, troops, current_time, projectiles_list, logger)
        
        # Gérer les projectiles
        projectiles_to_remove = []
        for projectile in self.projectiles:
            if current_time >= projectile['impact_time']:
                # Le projectile a atteint sa cible
                self.apply_splash_damage(
                    projectile['target_x'],
                    projectile['target_y'],
                    troops
                )
                projectiles_to_remove.append(projectile)
        
        # Retirer les projectiles qui ont explosé
        for projectile in projectiles_to_remove:
            self.projectiles.remove(projectile) 