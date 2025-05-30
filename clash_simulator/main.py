"""
Point d'entrée principal pour le simulateur Clash of Clans TH3
"""
import os
from clash_simulator.entities.troop_types import create_troop, Troop
from clash_simulator.systems.base_layout import BaseLayout
from clash_simulator.systems.battle_simulator import BattleSimulator
from clash_simulator.visualization.terminal_display import BattleVisualizer, TerminalDisplay
# Imports pour les démos et tests
from clash_simulator.demo_battle import demo_simple_attack as demo_battle_simple_attack
from clash_simulator.demo_battle import demo_speed_comparison as demo_battle_speed_comparison
from clash_simulator.demo_improved import demo_compact_view as demo_improved_compact_view
from clash_simulator.demo_improved import demo_comparison as demo_improved_comparison
from clash_simulator import test_components # Import the whole module to call its functions

# Imports pour les configurations
from clash_simulator.data.base_configs import get_base_layout_from_config, BASE_CONFIGURATIONS
from clash_simulator.data.army_configs import get_army_from_config, ARMY_CONFIGURATIONS
from typing import List

def run_all_component_tests():
    """Exécute tous les tests de test_components.py"""
    print("\n=== EXÉCUTION DES TESTS DE COMPOSANTS ===\n")
    test_components.test_building_creation()
    test_components.test_troop_creation()
    test_components.test_base_layout()
    test_components.test_simple_battle() # This is the test_simple_battle from test_components
    test_components.test_troop_targeting()
    test_components.test_pathfinding_around_walls()
    print("\n=== FIN DES TESTS DE COMPOSANTS ===\n")

def select_config(config_type: str, configs: dict, prompt_message: str) -> str:
    """Affiche une liste de configurations et demande à l'utilisateur d'en choisir une."""
    print(f"\n--- Choix de la {config_type} ---")
    if not configs:
        print(f"Aucune configuration de {config_type} disponible.")
        return ""
        
    config_names = list(configs.keys())
    for i, name in enumerate(config_names):
        print(f"{i+1}. {name}")
    
    while True:
        try:
            choice_num = input(f"{prompt_message} (numéro, ou 'q' pour annuler): ")
            if choice_num.lower() == 'q':
                return ""
            choice_idx = int(choice_num) - 1
            if 0 <= choice_idx < len(config_names):
                return config_names[choice_idx]
            else:
                print("Choix invalide.")
        except ValueError:
            print("Entrée invalide. Veuillez entrer un numéro.")

def main_test_simple_battle(base_name: str = "Simple TH3 Par Défaut", army_name: str = "Armée Mixte TH3 (Main)"):
    """Test avec une bataille simple en utilisant des configurations."""
    print(f"=== TEST DE BATAILLE CONFIGURÉE (Base: {base_name}, Armée: {army_name}) ===\n")
    
    try:
        print("Chargement de la base depuis la configuration...")
        base = get_base_layout_from_config(base_name)
        
        print("\nBase chargée:")
        display = TerminalDisplay()
        display.render_base(base)
        
        print("\nChargement de l'armée depuis la configuration...")
        troops = get_army_from_config(army_name)
        
        print(f"Armée chargée: {len(troops)} troupes")
        troop_counts = {}
        for t in troops:
            troop_counts[t.type] = troop_counts.get(t.type, 0) + 1
        for t_type, count in troop_counts.items():
            print(f"- {count} {t_type.capitalize()}s")

    except ValueError as e:
        print(f"Erreur de configuration: {e}")
        return

    # Créer le simulateur
    simulator = BattleSimulator(base, troops)
    
    # Lancer la visualisation
    visualizer = BattleVisualizer(simulator)
    
    print("\nLancement de la simulation...")
    
    visualizer.run(speed_multiplier=2.0, show_legend=True)
    
    # Afficher les résultats finaux
    stats = simulator.get_statistics()
    print("\n=== RÉSULTATS FINAUX ===")
    print(f"Durée: {stats['duration']:.1f} secondes")
    print(f"Destruction: {stats['destruction_percentage']:.1f}%")
    print(f"Étoiles: {stats['stars']}/3")
    print(f"Troupes perdues: {stats['troops_lost']}/{stats['troops_deployed']}")
    print(f"Bâtiments détruits: {stats['buildings_destroyed']}")
    print(f"Défenses détruites: {stats['defenses_destroyed']}")

def test_custom_battle():
    """Lance une bataille avec une base et une armée choisies par l'utilisateur."""
    print("\n=== BATAILLE PERSONNALISÉE VIA CONFIGURATIONS ===")
    
    base_name = select_config("base", BASE_CONFIGURATIONS, "Choisir une base")
    if not base_name:
        return
        
    army_name = select_config("armée", ARMY_CONFIGURATIONS, "Choisir une armée")
    if not army_name:
        return
        
    main_test_simple_battle(base_name, army_name)

def interactive_menu():
    """Menu interactif pour le simulateur"""
    while True:
        print("\n=== SIMULATEUR CLASH OF CLANS TH3 ===")
        print("--- Batailles et Sauvegardes ---")
        print("1. Lancer une bataille (choisir base et armée)")
        print("2. Créer et sauvegarder une nouvelle base (via console)")
        print("3. Charger une base depuis un fichier JSON et simuler (choisir armée)")
        
        print("--- Démonstrations Visuelles (utilisent des configurations par défaut ou choisies) ---")
        print("D1. Démo: Attaque simple (Affichage Classique)")
        print("D2. Démo: Comparaison des vitesses (Affichage Classique)")
        print("D3. Démo: Vue compacte (Affichage Amélioré)")
        print("D4. Démo: Comparaison des visualisations (Classique vs Amélioré)")
        print("--- Tests ---")
        print("T1. Exécuter tous les tests de composants")
        print("--- Actions ---")
        print("Q. Quitter")
        
        choice = input("\nVotre choix: ").upper()
        
        if choice == "1":
            base_name = select_config("base", BASE_CONFIGURATIONS, "Choisir une base pour la bataille")
            if not base_name: continue
            army_name = select_config("armée", ARMY_CONFIGURATIONS, "Choisir une armée pour la bataille")
            if not army_name: continue
            main_test_simple_battle(base_name, army_name)
            
        elif choice == "2":
            create_and_save_base()
        elif choice == "3":
            load_and_simulate_base_from_file()
            
        elif choice == "D1":
            print("\nLancement Démo: Attaque simple (Classique)...")
            demo_battle_simple_attack(base_name="Simple TH3 Par Défaut", army_name="Armée Démo Visuelle")
        elif choice == "D2":
            print("\nLancement Démo: Comparaison des vitesses (Classique)...")
            demo_battle_speed_comparison(base_name="Simple TH3 Par Défaut", army_name="Petite Armée Test Vitesse")
        elif choice == "D3":
            print("\nLancement Démo: Vue compacte (Amélioré)...")
            demo_improved_compact_view(base_name="Simple TH3 Par Défaut", army_name="Armée Démo Visuelle")
        elif choice == "D4":
            print("\nLancement Démo: Comparaison des visualisations...")
            demo_improved_comparison(base_name="Simple TH3 Par Défaut", army_name="Petite Armée Test Vitesse")
            
        elif choice == "T1":
            run_all_component_tests()
        elif choice == "Q":
            print("Au revoir!")
            break
        else:
            print("Choix invalide!")

def create_and_save_base():
    """Interface pour créer et sauvegarder une base"""
    print("\n=== CRÉATION DE BASE ===")
    name = input("Nom de la base: ")
    base = BaseLayout(name)
    
    while True:
        print(f"\nBase: {name}")
        print("1. Ajouter un bâtiment")
        print("2. Voir la base")
        print("3. Sauvegarder")
        print("4. Retour")
        
        choice = input("Choix: ")
        
        if choice == "1":
            building_type = input("Type de bâtiment: ")
            level = int(input("Niveau: "))
            x = int(input("Position X: "))
            y = int(input("Position Y: "))
            
            if base.add_building(building_type, level, (x, y)):
                print("Bâtiment ajouté!")
            else:
                print("Impossible d'ajouter le bâtiment!")
                
        elif choice == "2":
            display = TerminalDisplay()
            display.render_base(base)
            
        elif choice == "3":
            os.makedirs("data/bases", exist_ok=True)
            filename = f"data/bases/{name.replace(' ', '_').lower()}.json"
            base.save_to_file(filename)
            print(f"Base sauvegardée dans {filename}")
            
        elif choice == "4":
            break

def load_and_simulate_base_from_file():
    """Charge une base depuis un fichier JSON et lance une simulation avec une armée choisie."""
    print("\n=== CHARGER UNE BASE DEPUIS UN FICHIER JSON ET SIMULER ===")
    
    base_file_path = ""
    if os.path.exists("data/bases"):
        bases_json = [f for f in os.listdir("data/bases") if f.endswith(".json")]
        if bases_json:
            print("Bases JSON disponibles:")
            for i, base_file in enumerate(bases_json, 1):
                print(f"{i}. {base_file}")
            
            try:
                choice_num = input("Choisir une base (numéro, ou 'q' pour annuler): ")
                if choice_num.lower() == 'q': return
                choice_idx = int(choice_num) - 1
                if 0 <= choice_idx < len(bases_json):
                    base_file_path = os.path.join("data/bases", bases_json[choice_idx])
                else:
                    print("Choix invalide.")
                    return
            except ValueError:
                print("Entrée invalide.")
                return
        else:
            print("Aucune base sauvegardée en JSON trouvée dans data/bases/ !")
            return
    else:
        print("Dossier data/bases introuvable!")
        return

    if not base_file_path:
        return

    try:
        base = BaseLayout()
        base.load_from_file(base_file_path)
        print(f"Base '{base.name}' chargée depuis {base_file_path}")
        
        # Afficher la base
        display = TerminalDisplay()
        print("\nBase chargée:")
        display.render_base(base)

        army_name = select_config("armée", ARMY_CONFIGURATIONS, "Choisir une armée pour attaquer cette base")
        if not army_name:
            return
            
        troops = get_army_from_config(army_name)
        print(f"Armée '{army_name}' chargée: {len(troops)} troupes.")
        
        # Simuler
        simulator = BattleSimulator(base, troops)
        visualizer = BattleVisualizer(simulator)
        print("\nLancement de la simulation...")
        visualizer.run()

    except Exception as e:
        print(f"Erreur lors du chargement ou de la simulation de la base: {e}")

if __name__ == "__main__":
    interactive_menu()
    # test_simple_battle() # Commented out direct call 