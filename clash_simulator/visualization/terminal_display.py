"""
Système de visualisation dans le terminal avec couleurs
"""
import os
import sys
from typing import List, Optional
from ..core.config import GRID_SIZE, COLORS, DISPLAY_CONFIG, TICK_RATE
from ..entities.troop import Troop, TroopState
from ..entities.defense_buildings import DefenseBuilding, Mortar
from ..systems.base_layout import BaseLayout
from ..systems.battle_simulator import BattleSimulator

class TerminalDisplay:
    """Affichage de la bataille dans le terminal"""
    
    def __init__(self, width: int = GRID_SIZE, height: int = GRID_SIZE):
        self.width = width
        self.height = height
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        self.enable_colors = self._check_color_support()
        
    def _check_color_support(self) -> bool:
        """Vérifie si le terminal supporte les couleurs"""
        # Windows
        if sys.platform == "win32":
            try:
                # Activer les codes ANSI sur Windows 10+
                import ctypes
                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
                return True
            except:
                return False
        # Unix/Linux/Mac
        else:
            return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    
    def clear_screen(self) -> None:
        """Efface l'écran"""
        if sys.platform == "win32":
            os.system('cls')
        else:
            os.system('clear')
    
    def get_color(self, color_name: str) -> str:
        """Retourne le code couleur si activé"""
        if self.enable_colors and color_name in COLORS:
            return COLORS[color_name]
        return ""
    
    def reset_color(self) -> str:
        """Retourne le code de réinitialisation des couleurs"""
        if self.enable_colors:
            return COLORS["reset"]
        return ""
    
    def render_base(self, base_layout: BaseLayout) -> None:
        """Affiche uniquement la base"""
        self._reset_grid()
        
        # Placer les bâtiments
        for building in base_layout.get_all_buildings():
            self._place_building(building)
        
        self._print_grid()
    
    def render_battle(self, simulator: BattleSimulator) -> None:
        """Affiche l'état actuel de la bataille avec la grille et les statistiques côte à côte."""
        self._reset_grid() # Prépare self.grid avec les symboles colorés
        
        # Placer les bâtiments, troupes, projectiles...
        for building in simulator.base_layout.get_all_buildings():
            self._place_building(building)
        for troop in simulator.troops:
            if troop.is_alive():
                self._place_troop(troop)
        for building in simulator.base_layout.buildings:
            if isinstance(building, Mortar) and hasattr(building, 'projectiles'):
                for projectile in building.projectiles:
                    self._place_projectile(projectile)
        
        grid_lines = self._print_grid(return_lines=True) or []
        stats_lines_raw = self._print_stats(simulator, return_lines=True) or []

        grid_line_width_no_ansi = 0
        if grid_lines:
            import re
            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
            # Utiliser la largeur de la première ligne de la grille comme référence pour le padding
            # Cette largeur inclut les bordures et les espaces internes de la grille.
            grid_line_width_no_ansi = len(ansi_escape.sub('', grid_lines[0]))

        # Décalage pour le bloc de statistiques
        stats_vertical_offset = len(grid_lines) // 3 if grid_lines else 0
        
        # Créer les lignes de statistiques décalées
        stats_lines_padded = ["" for _ in range(stats_vertical_offset)] + stats_lines_raw

        max_height = max(len(grid_lines), len(stats_lines_padded))
        spacing = "   " 

        final_display_lines = []
        for i in range(max_height):
            grid_part = grid_lines[i] if i < len(grid_lines) else " " * grid_line_width_no_ansi
            stats_part = stats_lines_padded[i] if i < len(stats_lines_padded) else ""
            
            final_display_lines.append(f"{grid_part}{spacing}{stats_part}")
        
        for line in final_display_lines:
            print(line)
    
    def _reset_grid(self) -> None:
        """Réinitialise la grille"""
        empty_symbol = DISPLAY_CONFIG["terrain"]["empty"]["symbol"]
        empty_color = DISPLAY_CONFIG["terrain"]["empty"]["color"]
        colored_empty = self.get_color(empty_color) + empty_symbol + self.reset_color()
        
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = colored_empty
    
    def _place_building(self, building) -> None:
        """Place un bâtiment sur la grille"""
        if building.type not in DISPLAY_CONFIG["buildings"]:
            return
        
        config = DISPLAY_CONFIG["buildings"][building.type]
        symbol = config["symbol"]
        color = config["color"]
        
        # Si le bâtiment est détruit, utiliser une couleur différente
        if building.is_destroyed:
            colored_symbol = self.get_color("gray") + "x" + self.reset_color()
        else:
            # Indicateur de santé
            hp_ratio = building.hp / building.max_hp
            if hp_ratio < 0.3:
                color = "red"
            elif hp_ratio < 0.6:
                color = "yellow"
            
            colored_symbol = self.get_color(color) + symbol + self.reset_color()
        
        # Placer le symbole sur toutes les tuiles du bâtiment
        for dy in range(building.size):
            for dx in range(building.size):
                x = building.x + dx
                y = building.y + dy
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y][x] = colored_symbol
    
    def _place_troop(self, troop: Troop) -> None:
        """Place une troupe sur la grille"""
        if troop.type not in DISPLAY_CONFIG["troops"]:
            return
        
        config = DISPLAY_CONFIG["troops"][troop.type]
        symbol = config["symbol"]
        color = config["color"]
        
        # Modifier la couleur selon l'état
        if troop.state == TroopState.ATTACKING:
            symbol = symbol.upper()  # Majuscule quand attaque
        elif troop.state == TroopState.MOVING:
            color = "cyan"  # Cyan quand en mouvement
        
        # Indicateur de santé
        hp_ratio = troop.hp / troop.max_hp
        if hp_ratio < 0.3:
            color = "red"
        elif hp_ratio < 0.6:
            color = "yellow"
        
        colored_symbol = self.get_color(color) + symbol + self.reset_color()
        
        # Placer la troupe
        x = int(troop.x)
        y = int(troop.y)
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = colored_symbol
    
    def _place_projectile(self, projectile: dict) -> None:
        """Place un projectile de mortier"""
        x = int(projectile['target_x'])
        y = int(projectile['target_y'])
        
        if 0 <= x < self.width and 0 <= y < self.height:
            symbol = self.get_color("orange") + "◎" + self.reset_color()
            self.grid[y][x] = symbol
    
    def _print_grid(self, return_lines: bool = False) -> Optional[List[str]]:
        """Affiche la grille ou retourne ses lignes."""
        lines = []
        # Bordure supérieure
        lines.append("┌" + "─" * (self.width + 2) + "┐")
        
        # Contenu
        for row_idx, row_content in enumerate(self.grid):
            line_str = "│ " + "".join(row_content) + " │"
            lines.append(line_str)
        
        # Bordure inférieure
        lines.append("└" + "─" * (self.width + 2) + "┘")
        
        if return_lines:
            return lines
        else:
            for line in lines:
                print(line)
            return None # Explicite pour la clarté
    
    def _print_stats(self, simulator: BattleSimulator, return_lines: bool = False) -> Optional[List[str]]:
        """Affiche les statistiques de la bataille ou retourne ses lignes."""
        stats = simulator.get_statistics()
        
        lines = []
        lines.append(f"{self.get_color('cyan')}╔══════════════════════════════════════╗{self.reset_color()}")
        lines.append(f"{self.get_color('cyan')}║        STATISTIQUES DE BATAILLE      ║{self.reset_color()}")
        lines.append(f"{self.get_color('cyan')}╠══════════════════════════════════════╣{self.reset_color()}")
        
        # Temps
        time_color = "green" if simulator.get_remaining_time() > 60 else "yellow" if simulator.get_remaining_time() > 30 else "red"
        lines.append(f"{self.get_color('cyan')}║{self.reset_color()} Temps: {self.get_color(time_color)}{simulator.current_time:.1f}s / {simulator.battle_duration}s{self.reset_color()}")
        
        # Destruction
        destruction = stats['destruction_percentage']
        dest_color = "red" if destruction < 30 else "yellow" if destruction < 70 else "green"
        lines.append(f"{self.get_color('cyan')}║{self.reset_color()} Destruction: {self.get_color(dest_color)}{destruction:.1f}%{self.reset_color()}")
        
        # Étoiles
        stars = stats['stars']
        stars_display = self.get_color("yellow") + "★" * stars + "☆" * (3 - stars) + self.reset_color()
        lines.append(f"{self.get_color('cyan')}║{self.reset_color()} Étoiles: {stars_display}")
        
        # Troupes
        troops_color = "green" if stats['troops_lost'] == 0 else "yellow" if stats['troops_lost'] < stats['troops_deployed'] / 2 else "red"
        lines.append(f"{self.get_color('cyan')}║{self.reset_color()} Troupes: {self.get_color(troops_color)}{stats['troops_deployed'] - stats['troops_lost']}/{stats['troops_deployed']}{self.reset_color()}")
        
        # État
        state_colors = {
            "in_progress": "yellow",
            "victory": "green",
            "defeat": "red",
            "timeout": "orange"
        }
        state_color = state_colors.get(stats['state'], "white")
        lines.append(f"{self.get_color('cyan')}║{self.reset_color()} État: {self.get_color(state_color)}{stats['state'].upper()}{self.reset_color()}")
        
        lines.append(f"{self.get_color('cyan')}╚══════════════════════════════════════╝{self.reset_color()}")
        
        if return_lines:
            return lines
        else:
            for line in lines:
                print(line)
            return None # Explicite pour la clarté
    
    def print_legend(self) -> None:
        """Affiche la légende des symboles"""
        print(f"\n{self.get_color('cyan')}LÉGENDE:{self.reset_color()}")
        
        print(f"\n{self.get_color('yellow')}Bâtiments:{self.reset_color()}")
        for building_type, config in DISPLAY_CONFIG["buildings"].items():
            symbol = config["symbol"]
            color = config["color"]
            colored_symbol = self.get_color(color) + symbol + self.reset_color()
            print(f"  {colored_symbol} - {building_type.replace('_', ' ').title()}")
        
        print(f"\n{self.get_color('yellow')}Troupes:{self.reset_color()}")
        for troop_type, config in DISPLAY_CONFIG["troops"].items():
            symbol = config["symbol"]
            color = config["color"]
            colored_symbol = self.get_color(color) + symbol + self.reset_color()
            print(f"  {colored_symbol} - {troop_type.replace('_', ' ').title()}")
        
        print(f"\n{self.get_color('yellow')}Symboles spéciaux:{self.reset_color()}")
        print(f"  {self.get_color('gray')}x{self.reset_color()} - Bâtiment détruit")
        print(f"  {self.get_color('orange')}◎{self.reset_color()} - Projectile de mortier")
        print(f"  {self.get_color('cyan')}MAJUSCULE{self.reset_color()} - Troupe en train d'attaquer")


class BattleVisualizer:
    """Visualiseur de bataille avec mise à jour en temps réel"""
    
    def __init__(self, simulator: BattleSimulator):
        self.simulator = simulator
        self.display = TerminalDisplay()
        
    def run(self, speed_multiplier: float = 1.0, show_legend: bool = True, update_frequency: float = 1.0) -> None:
        """Lance la visualisation de la bataille
        
        Args:
            speed_multiplier: Multiplicateur de vitesse de simulation
            show_legend: Afficher la légende au début
            update_frequency: Fréquence de mise à jour de l'affichage en secondes
        """
        import time
        
        if show_legend:
            self.display.print_legend()
            input("\nAppuyez sur Entrée pour commencer la simulation...")
        
        self.simulator.start()
        
        # Temps entre chaque tick de simulation
        tick_sleep_time = (1.0 / TICK_RATE) / speed_multiplier
        
        # Compteur pour la mise à jour de l'affichage
        last_display_time = time.time()
        
        while not self.simulator.is_finished():
            # Toujours simuler à la bonne vitesse
            self.simulator.simulate_tick()
            time.sleep(tick_sleep_time)
            
            # Mais ne rafraîchir l'affichage que selon update_frequency
            current_time = time.time()
            if current_time - last_display_time >= update_frequency:
                self.display.clear_screen()
                self.display.render_battle(self.simulator)
                last_display_time = current_time
        
        # Affichage final
        self.display.clear_screen()
        self.display.render_battle(self.simulator)
        
        print(f"\n{self.display.get_color('green')}Simulation terminée !{self.display.reset_color()}")
        
        # Résumé final amélioré
        stats = self.simulator.get_statistics()
        self._print_final_summary(stats)
    
    def _print_final_summary(self, stats: dict) -> None:
        """Affiche un résumé final détaillé"""
        print(f"\n{self.display.get_color('cyan')}╔════════════════════════════════════════╗{self.display.reset_color()}")
        print(f"{self.display.get_color('cyan')}║          RÉSUMÉ DE LA BATAILLE         ║{self.display.reset_color()}")
        print(f"{self.display.get_color('cyan')}╠════════════════════════════════════════╣{self.display.reset_color()}")
        
        # Résultat
        result_color = "green" if stats['state'] == "victory" else "red" if stats['state'] == "defeat" else "yellow"
        print(f"{self.display.get_color('cyan')}║{self.display.reset_color()} Résultat: {self.display.get_color(result_color)}{stats['state'].upper():^26}{self.display.reset_color()} {self.display.get_color('cyan')}║{self.display.reset_color()}")
        
        # Étoiles
        stars = "★" * stats['stars'] + "☆" * (3 - stats['stars'])
        print(f"{self.display.get_color('cyan')}║{self.display.reset_color()} Étoiles: {self.display.get_color('yellow')}{stars:^27}{self.display.reset_color()} {self.display.get_color('cyan')}║{self.display.reset_color()}")
        
        # Destruction
        print(f"{self.display.get_color('cyan')}║{self.display.reset_color()} Destruction: {self.display.get_color('white')}{stats['destruction_percentage']:>5.0f}%{self.display.reset_color()}                  {self.display.get_color('cyan')}║{self.display.reset_color()}")
        
        # Durée
        print(f"{self.display.get_color('cyan')}║{self.display.reset_color()} Durée: {self.display.get_color('white')}{stats['duration']:>6.1f}s{self.display.reset_color()}                    {self.display.get_color('cyan')}║{self.display.reset_color()}")
        
        # Troupes
        print(f"{self.display.get_color('cyan')}║{self.display.reset_color()} Troupes survivantes: {self.display.get_color('white')}{stats['troops_deployed'] - stats['troops_lost']:>2}/{stats['troops_deployed']:<2}{self.display.reset_color()}           {self.display.get_color('cyan')}║{self.display.reset_color()}")
        
        # Bâtiments
        print(f"{self.display.get_color('cyan')}║{self.display.reset_color()} Bâtiments détruits: {self.display.get_color('white')}{stats['buildings_destroyed']:>3}{self.display.reset_color()}              {self.display.get_color('cyan')}║{self.display.reset_color()}")
        
        print(f"{self.display.get_color('cyan')}╚════════════════════════════════════════╝{self.display.reset_color()}")
 