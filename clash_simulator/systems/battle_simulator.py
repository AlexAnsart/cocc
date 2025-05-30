"""
Moteur de simulation de bataille
"""
import time
from typing import List, Tuple, Optional
from enum import Enum
from ..entities.troop import Troop, TroopState
from ..entities.defense_buildings import DefenseBuilding
from ..entities.other_buildings import Wall
from ..systems.base_layout import BaseLayout
from ..core.config import TICK_RATE, MAX_BATTLE_DURATION
from ..utils.logger import BattleLogger

class BattleState(Enum):
    """États possibles de la bataille"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    VICTORY = "victory"
    DEFEAT = "defeat"
    TIMEOUT = "timeout"

class BattleSimulator:
    """Moteur principal de simulation de bataille"""
    
    def __init__(self, base_layout: BaseLayout, troops: List[Troop], battle_duration: Optional[float] = None, battle_id: Optional[str] = None, log_to_console: bool = False, log_to_file: bool = True):
        self.base_layout = base_layout
        self.troops = troops
        self.projectiles = [] # Pour les projectiles de mortier, etc.
        self.battle_duration = battle_duration if battle_duration is not None else MAX_BATTLE_DURATION
        self.history = []
        self.initial_troop_count = len(troops)
        self.current_tick = 0
        self.current_time = 0.0
        self.state = BattleState.NOT_STARTED
        self.start_time_real: Optional[float] = None
        self.battle_id = battle_id
        self.log_to_console_enabled = log_to_console
        self.log_to_file_enabled = log_to_file
        self.logger: Optional[BattleLogger] = None # Sera initialisé dans start()
        
        # Statistiques
        self.troops_deployed = 0
        self.troops_remaining = len(troops)
        self.initial_base_hp = base_layout.get_total_hp()
        
    def start(self) -> None:
        """Démarre la simulation"""
        if self.state != BattleState.NOT_STARTED:
            self.logger.warning("Battle already started or finished. Reset before starting again.", tick=self.current_tick, sim_time=self.current_time)
            return
        
        self.current_tick = 0
        self.current_time = 0.0
        self.state = BattleState.IN_PROGRESS
        self.start_time_real = time.time()
        
        # Initialiser le logger pour cette bataille
        self.logger = BattleLogger(battle_id=self.battle_id, 
                                   log_to_console=self.log_to_console_enabled, 
                                   log_to_file=self.log_to_file_enabled)
                                   
        self.logger.info(f"Battle started. Base: {self.base_layout.name}, Troops: {self.initial_troop_count}, Max Duration: {self.battle_duration}s", 
                         tick=self.current_tick, sim_time=self.current_time)
        
        # Log initial des troupes et bâtiments
        for troop in self.troops:
            self.logger.debug(f"Initial Troop: {troop!r}", tick=self.current_tick, sim_time=self.current_time)
        for building in self.base_layout.get_all_buildings():
            self.logger.debug(f"Initial Building: {building!r}", tick=self.current_tick, sim_time=self.current_time)
        
        # Initialiser les troupes
        for troop in self.troops:
            troop.spawn_time = self.current_time
            self.troops_deployed += 1
    
    def simulate_tick(self) -> None:
        """Simule un tick de la bataille"""
        if self.state != BattleState.IN_PROGRESS or not self.logger:
            return

        dt = 1.0 / TICK_RATE
        self.logger.debug(f"--- Tick Start --- DT: {dt}", tick=self.current_tick, sim_time=self.current_time)

        # Mettre à jour les troupes
        active_troops = [t for t in self.troops if t.is_alive()]
        if not active_troops and self.state == BattleState.IN_PROGRESS: # Early exit if all troops dead
            self.logger.info("All troops are dead.", tick=self.current_tick, sim_time=self.current_time)
            self._check_end_conditions()
            if self.state != BattleState.IN_PROGRESS: # If end condition met
                self.logger.debug("--- Tick End (Battle Ended Early) ---", tick=self.current_tick, sim_time=self.current_time)
                return

        for troop in active_troops:
            old_state = troop.state
            old_pos = (troop.x, troop.y)
            old_target = troop.target.type if troop.target else None
            troop.update(dt, self.base_layout.get_all_buildings(), self.base_layout.walls, self.current_time)
            # Log troop changes
            if old_pos != (troop.x, troop.y):
                self.logger.debug(f"Troop {troop.type}_{troop.level} moved from {old_pos} to ({troop.x:.2f}, {troop.y:.2f}) -> Target: {troop.target.type if troop.target else 'None'}", 
                                  tick=self.current_tick, sim_time=self.current_time)
            if troop.state != old_state:
                self.logger.info(f"Troop {troop.type}_{troop.level} state changed from {old_state.value} to {troop.state.value}", 
                                 tick=self.current_tick, sim_time=self.current_time)
            if troop.target and (troop.target.type if troop.target else None) != old_target:
                 self.logger.info(f"Troop {troop.type}_{troop.level} new target: {troop.target.type if troop.target else 'None'}", 
                                  tick=self.current_tick, sim_time=self.current_time)
            if troop.state == TroopState.ATTACKING and troop.last_attack_time == self.current_time:
                 # This requires troop.last_attack_time to be updated precisely in attack method
                 # And we need to know damage dealt, and target HP.
                 # This specific log might be better inside the troop.attack method or from building.take_damage
                 # For now, a general attack log:
                 self.logger.info(f"Troop {troop.type}_{troop.level} attacked {troop.target.type if troop.target else 'Unknown'}", 
                                  tick=self.current_tick, sim_time=self.current_time)
            if not troop.is_alive() and old_state != TroopState.DEAD:
                self.logger.info(f"Troop {troop.type}_{troop.level} died.", tick=self.current_tick, sim_time=self.current_time)

        # Mettre à jour les bâtiments (ex: défenses qui tirent)
        for building in self.base_layout.get_defenses():
            if not building.is_destroyed:
                # Logique d'attaque des défenses
                # Si une défense attaque, logguer: building.attack(target, self.current_time)
                # Exemple de log (à intégrer dans la logique d'attaque de la défense):
                # if building.attack(target, self.current_time): # attack retourne True si une attaque a eu lieu
                #    self.logger.info(f"Defense {building.type} attacked {target.type} for X damage.", 
                #                      tick=self.current_tick, sim_time=self.current_time)
                #    if not target.is_alive():
                #        self.logger.info(f"Troop {target.type} died from {building.type} attack.", 
                #                          tick=self.current_tick, sim_time=self.current_time)
                building.update(dt, self.troops, self.current_time, self.projectiles, self.logger) # Passer le logger aux défenses

        # Mettre à jour les projectiles
        new_projectiles = []
        for p in self.projectiles:
            p.update(dt)
            if p.has_impacted:
                self.logger.info(f"Projectile from {p.origin_type} impacted at ({p.target_x:.1f}, {p.target_y:.1f}), dealing {p.damage} AoE damage.",
                                 tick=self.current_tick, sim_time=self.current_time)
                # Gérer les dégâts de zone ici si nécessaire, et loguer les cibles touchées
            else:
                new_projectiles.append(p)
        self.projectiles = new_projectiles

        self._check_end_conditions()
        self._record_state()
        
        self.current_time += dt
        self.current_tick += 1
        self.logger.debug("--- Tick End ---", tick=self.current_tick -1, sim_time=self.current_time - dt) # Log with tick/time at start of tick
    
    def simulate_battle(self) -> BattleState:
        """Simule la bataille complète"""
        self.start()
        
        while self.state == BattleState.IN_PROGRESS:
            self.simulate_tick()
        
        return self.state
    
    def _check_end_conditions(self) -> None:
        """Vérifie si la bataille est terminée"""
        if self.state != BattleState.IN_PROGRESS: # Déjà terminé
            return

        original_state = self.state
        
        # Condition de victoire: tous les bâtiments (sauf les murs) détruits
        # Ou TH détruit + 50% destruction pour 2 étoiles, TH détruit pour 1 étoile.
        # Pour TH3, une condition simple: TH détruit = victoire (ou 100% destruction)
        # Si on veut être précis: destruction totale des bâtiments (hors murs)
        non_wall_buildings = [b for b in self.base_layout.get_all_buildings() if b.type != 'wall']
        if not non_wall_buildings or all(b.is_destroyed for b in non_wall_buildings):
            self.state = BattleState.VICTORY
            if self.logger: self.logger.info("VICTORY! All non-wall buildings destroyed.", tick=self.current_tick, sim_time=self.current_time)

        # Condition de défaite: toutes les troupes mortes ET pas de victoire
        elif not any(t.is_alive() for t in self.troops):
            if self.state == BattleState.IN_PROGRESS: # Assurer qu'on n'a pas déjà gagné au même tick
                self.state = BattleState.DEFEAT
                if self.logger: self.logger.info("DEFEAT! All troops eliminated.", tick=self.current_tick, sim_time=self.current_time)

        # Condition de timeout
        if self.current_time >= self.battle_duration and self.state == BattleState.IN_PROGRESS:
            self.state = BattleState.TIMEOUT
            if self.logger: self.logger.info(f"TIMEOUT! Battle duration {self.battle_duration:.1f}s reached.", tick=self.current_tick, sim_time=self.current_time)
        
        if self.state != original_state and self.logger:
             self.logger.info(f"Battle ended. Final State: {self.state.value}", tick=self.current_tick, sim_time=self.current_time)
    
    def _record_state(self) -> None:
        """Enregistre l'état actuel pour l'historique"""
        if self.current_tick % 5 == 0:  # Enregistrer tous les 5 ticks
            state = {
                'time': self.current_time,
                'troops': [
                    {
                        'type': t.type,
                        'x': t.x,
                        'y': t.y,
                        'hp': t.hp,
                        'state': t.state.value
                    }
                    for t in self.troops if t.is_alive()
                ],
                'buildings': [
                    {
                        'type': b.type,
                        'x': b.x,
                        'y': b.y,
                        'hp': b.hp,
                        'destroyed': b.is_destroyed
                    }
                    for b in self.base_layout.get_all_buildings()
                ],
                'destruction': self.base_layout.get_destruction_percentage()
            }
            self.history.append(state)
    
    def get_statistics(self) -> dict:
        """Retourne les statistiques de la bataille"""
        return {
            'duration': self.current_time,
            'state': self.state.value,
            'destruction_percentage': self.base_layout.get_destruction_percentage(),
            'stars': self.base_layout.get_stars(),
            'troops_deployed': self.troops_deployed,
            'troops_lost': sum(1 for t in self.troops if not t.is_alive()),
            'buildings_destroyed': sum(1 for b in self.base_layout.get_all_buildings() if b.is_destroyed),
            'defenses_destroyed': sum(1 for b in self.base_layout.get_defenses() if b.is_destroyed),
            'tick_count': self.current_tick
        }
    
    def is_finished(self) -> bool:
        """Vérifie si la bataille est terminée"""
        return self.state != BattleState.IN_PROGRESS
    
    def get_remaining_time(self) -> float:
        """Retourne le temps restant"""
        return max(0, self.battle_duration - self.current_time)
    
    def reset(self) -> None:
        """Réinitialise la simulation"""
        # Réinitialiser la base
        self.base_layout.reset()
        
        # Réinitialiser les troupes
        for troop in self.troops:
            troop.hp = troop.max_hp
            troop.state = TroopState.IDLE
            troop.target = None
            troop.path = []
            troop.last_attack_time = 0
        
        # Réinitialiser l'état
        self.state = BattleState.NOT_STARTED
        self.current_time = 0.0
        self.current_tick = 0
        self.history.clear()
    
    def __repr__(self) -> str:
        return (f"BattleSimulator(state={self.state.value}, "
                f"time={self.current_time:.1f}s, "
                f"destruction={self.base_layout.get_destruction_percentage():.1f}%)")


class BattleRunner:
    """Classe utilitaire pour exécuter des simulations"""
    
    @staticmethod
    def run_battle(base_layout: BaseLayout, troops: List[Troop], 
                   speed_multiplier: float = 1.0) -> dict:
        """Exécute une bataille avec visualisation optionnelle"""
        simulator = BattleSimulator(base_layout, troops)
        simulator.start()
        
        # Pour la visualisation en temps réel
        sleep_time = (1.0 / TICK_RATE) / speed_multiplier
        
        while not simulator.is_finished():
            simulator.simulate_tick()
            
            # Pause pour visualisation (peut être désactivé)
            if speed_multiplier > 0:
                time.sleep(sleep_time)
        
        return simulator.get_statistics()
    
    @staticmethod
    def run_instant_battle(base_layout: BaseLayout, troops: List[Troop]) -> dict:
        """Exécute une bataille instantanément sans visualisation"""
        simulator = BattleSimulator(base_layout, troops)
        simulator.simulate_battle()
        return simulator.get_statistics() 