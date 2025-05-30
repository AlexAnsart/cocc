"""
Système de visualisation amélioré avec une mise en page plus claire
"""
import os
import sys
from typing import List, Dict
from ..core.config import GRID_SIZE, COLORS, DISPLAY_CONFIG, TICK_RATE
from ..entities.troop import Troop, TroopState
from ..systems.base_layout import BaseLayout
from ..systems.battle_simulator import BattleSimulator

class ImprovedDisplay:
    """Affichage amélioré de la bataille avec une meilleure mise en page"""
    
    def __init__(self):
        self.enable_colors = self._check_color_support()
        
    def _check_color_support(self) -> bool:
        """Vérifie si le terminal supporte les couleurs"""
        if sys.platform == "win32":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                return False
        else:
            return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def clear_screen(self) -> None:
        """Efface l'écran"""
        os.system('cls' if sys.platform == "win32" else 'clear')
    
    def get_color(self, color_name: str) -> str:
        """Retourne le code couleur si activé"""
        if self.enable_colors and color_name in COLORS:
            return COLORS[color_name]
        return ""
    
    def reset_color(self) -> str:
        """Retourne le code de réinitialisation des couleurs"""
        return COLORS["reset"] if self.enable_colors else ""
    
    def render_compact_battle(self, simulator: BattleSimulator) -> None:
        """Affiche une vue compacte de la bataille"""
        self.clear_screen()
        stats = simulator.get_statistics()
        
        # En-tête
        print(f"{self.get_color('cyan')}═════════════════════════════════════════════════════════════{self.reset_color()}")
        print(f"{self.get_color('yellow')}        SIMULATEUR CLASH OF CLANS - BATAILLE EN COURS        {self.reset_color()}")
        print(f"{self.get_color('cyan')}═════════════════════════════════════════════════════════════{self.reset_color()}\n")
        
        # Statistiques principales sur une ligne
        self._print_main_stats(simulator, stats)
        
        # Vue simplifiée de la carte
        print(f"\n{self.get_color('cyan')}▌ CARTE DE BATAILLE ▐{self.reset_color()}")
        self._print_simplified_map(simulator)
        
        # État des troupes et bâtiments
        print(f"\n{self.get_color('cyan')}▌ ÉTAT DES FORCES ▐{self.reset_color()}")
        self._print_forces_status(simulator)
        
        # Actions en cours
        print(f"\n{self.get_color('cyan')}▌ ACTIONS EN COURS ▐{self.reset_color()}")
        self._print_current_actions(simulator)
    
    def _print_main_stats(self, simulator: BattleSimulator, stats: dict) -> None:
        """Affiche les statistiques principales sur une ligne"""
        # Temps
        time_ratio = simulator.current_time / simulator.battle_duration
        time_bar = self._create_progress_bar(time_ratio, 20)
        time_color = "green" if time_ratio < 0.5 else "yellow" if time_ratio < 0.8 else "red"
        
        # Destruction
        dest_ratio = stats['destruction_percentage'] / 100
        dest_bar = self._create_progress_bar(dest_ratio, 20)
        dest_color = "red" if dest_ratio < 0.3 else "yellow" if dest_ratio < 0.7 else "green"
        
        # Étoiles
        stars = "★" * stats['stars'] + "☆" * (3 - stats['stars'])
        
        print(f"⏱  Temps: {self.get_color(time_color)}{time_bar} {simulator.current_time:.0f}/{simulator.battle_duration}s{self.reset_color()}")
        print(f"💥 Destruction: {self.get_color(dest_color)}{dest_bar} {stats['destruction_percentage']:.0f}%{self.reset_color()}")
        print(f"⭐ Étoiles: {self.get_color('yellow')}{stars}{self.reset_color()}")
        print(f"⚔  Troupes: {self.get_color('green')}{stats['troops_deployed'] - stats['troops_lost']}/{stats['troops_deployed']}{self.reset_color()}")
    
    def _create_progress_bar(self, ratio: float, length: int) -> str:
        """Crée une barre de progression"""
        filled = int(ratio * length)
        bar = "█" * filled + "░" * (length - filled)
        return f"[{bar}]"
    
    def _print_simplified_map(self, simulator: BattleSimulator) -> None:
        """Affiche une carte simplifiée 20x20"""
        # Créer une grille simplifiée
        simplified_size = 20
        scale = GRID_SIZE / simplified_size
        grid = [[' ' for _ in range(simplified_size)] for _ in range(simplified_size)]
        
        # Placer les bâtiments
        for building in simulator.base_layout.get_all_buildings():
            x = int(building.x / scale)
            y = int(building.y / scale)
            if 0 <= x < simplified_size and 0 <= y < simplified_size:
                if building.is_destroyed:
                    grid[y][x] = 'x'
                elif building.type == "town_hall":
                    grid[y][x] = 'T'
                elif building.type in ["cannon", "archer_tower", "mortar"]:
                    grid[y][x] = 'D'
                elif building.type == "wall":
                    grid[y][x] = '#'
                else:
                    grid[y][x] = 'B'
        
        # Placer les troupes
        for troop in simulator.troops:
            if troop.is_alive():
                x = int(troop.x / scale)
                y = int(troop.y / scale)
                if 0 <= x < simplified_size and 0 <= y < simplified_size:
                    if grid[y][x] == ' ':
                        grid[y][x] = '*'
        
        # Afficher la grille
        print("┌" + "─" * (simplified_size * 2) + "┐")
        for row in grid:
            print("│" + " ".join(row) + "│")
        print("└" + "─" * (simplified_size * 2) + "┘")
        
        print(f"{self.get_color('gray')}Légende: T=Town Hall, D=Défense, B=Bâtiment, #=Mur, *=Troupe, x=Détruit{self.reset_color()}")
    
    def _print_forces_status(self, simulator: BattleSimulator) -> None:
        """Affiche l'état des forces"""
        # Compter les troupes par type
        troop_counts = {}
        for troop in simulator.troops:
            if troop.is_alive():
                troop_counts[troop.type] = troop_counts.get(troop.type, 0) + 1
        
        # Compter les bâtiments actifs
        defense_count = sum(1 for b in simulator.base_layout.buildings 
                          if b.type in ["cannon", "archer_tower", "mortar"] and not b.is_destroyed)
        other_count = sum(1 for b in simulator.base_layout.buildings 
                         if b.type not in ["cannon", "archer_tower", "mortar"] and not b.is_destroyed)
        wall_count = sum(1 for w in simulator.base_layout.walls if not w.is_destroyed)
        
        # Afficher
        if troop_counts:
            troops_str = ", ".join(f"{count} {troop_type}" for troop_type, count in troop_counts.items())
            print(f"Troupes actives: {self.get_color('green')}{troops_str}{self.reset_color()}")
        else:
            print(f"Troupes actives: {self.get_color('red')}Aucune{self.reset_color()}")
        
        print(f"Défenses actives: {self.get_color('yellow')}{defense_count}{self.reset_color()}")
        print(f"Autres bâtiments: {self.get_color('blue')}{other_count}{self.reset_color()}")
        print(f"Murs intacts: {self.get_color('gray')}{wall_count}{self.reset_color()}")
    
    def _print_current_actions(self, simulator: BattleSimulator) -> None:
        """Affiche les actions en cours"""
        actions = []
        
        # Actions des troupes
        for troop in simulator.troops[:5]:  # Limiter à 5 pour ne pas surcharger
            if troop.is_alive():
                if troop.state == TroopState.ATTACKING and troop.target:
                    actions.append(f"{troop.type} attaque {troop.target.type}")
                elif troop.state == TroopState.MOVING and troop.target:
                    actions.append(f"{troop.type} → {troop.target.type}")
        
        if actions:
            for action in actions:
                print(f"• {action}")
        else:
            print(f"{self.get_color('gray')}Aucune action en cours{self.reset_color()}")


class CompactBattleVisualizer:
    """Visualiseur de bataille avec affichage compact"""
    
    def __init__(self, simulator: BattleSimulator):
        self.simulator = simulator
        self.display = ImprovedDisplay()
    
    def run(self, speed_multiplier: float = 1.0) -> None:
        """Lance la visualisation compacte"""
        import time
        
        self.simulator.start()
        
        # Mise à jour toutes les secondes
        last_update = time.time()
        
        while not self.simulator.is_finished():
            # Simuler
            for _ in range(TICK_RATE):  # Simuler 1 seconde de jeu
                if not self.simulator.is_finished():
                    self.simulator.simulate_tick()
                    time.sleep((1.0 / TICK_RATE) / speed_multiplier)
            
            # Afficher
            self.display.render_compact_battle(self.simulator)
        
        # Affichage final
        self.display.render_compact_battle(self.simulator)
        print(f"\n{self.display.get_color('green')}✓ Simulation terminée !{self.display.reset_color()}") 