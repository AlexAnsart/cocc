"""
Démonstration avec visualisations améliorées
"""
# from clash_simulator.entities.troop_types import create_troop # Supprimé
# from clash_simulator.systems.base_layout import BaseLayout # Supprimé
from clash_simulator.systems.battle_simulator import BattleSimulator
from clash_simulator.visualization.terminal_display import BattleVisualizer
from clash_simulator.visualization.improved_display import CompactBattleVisualizer

# Imports pour les configurations
from clash_simulator.data.base_configs import get_base_layout_from_config
from clash_simulator.data.army_configs import get_army_from_config

def demo_compact_view(base_name: str = "Simple TH3 Par Défaut", army_name: str = "Armée Démo Visuelle"):
    """Démo avec la vue compacte, utilisant des configurations."""
    print(f"=== DÉMONSTRATION VUE COMPACTE (Base: {base_name}, Armée: {army_name}) ===\\n")
    
    try:
        base = get_base_layout_from_config(base_name)
        troops = get_army_from_config(army_name)
    except ValueError as e:
        print(f"Erreur de configuration pour la démo vue compacte: {e}")
        return

    print(f"Base '{base.name}' ({len(base.get_all_buildings())} éléments) et Armée '{army_name}' ({len(troops)} troupes) chargées.")

    # Créer le simulateur
    simulator = BattleSimulator(base, troops, battle_duration=60)
    
    # Utiliser la vue compacte
    visualizer = CompactBattleVisualizer(simulator)
    
    print("\\nLancement de la vue compacte...")
    print("L'affichage se met à jour toutes les secondes")
    # input("\\nAppuyez sur Entrée pour commencer...") # Optionnel
    
    visualizer.run(speed_multiplier=1.0)

def demo_comparison(base_name: str = "Simple TH3 Par Défaut", army_name: str = "Petite Armée Test Vitesse"):
    """Compare les deux types de visualisation, utilisant des configurations."""
    print("\\n=== COMPARAISON DES VISUALISATIONS ===")
    print("1. Vue classique (grille complète)")
    print("2. Vue compacte (résumé)")
    
    choice = input("\\nVotre choix (1-2): ")
    
    try:
        base = get_base_layout_from_config(base_name)
        troops = get_army_from_config(army_name)
    except ValueError as e:
        print(f"Erreur de configuration pour la démo comparaison: {e}")
        return

    print(f"Utilisation de la base '{base.name}' et de l'armée '{army_name}' ({len(troops)} troupes).")
    
    # Durée de bataille plus courte pour ces tests
    simulator = BattleSimulator(base, troops, battle_duration=30)
    
    if choice == "1":
        print("\\nVue classique - Mise à jour toutes les secondes")
        visualizer_classic = BattleVisualizer(simulator) # Renommé pour éviter conflit de nom
        visualizer_classic.run(speed_multiplier=1.0, show_legend=False, update_frequency=1.0)
    elif choice == "2":
        print("\\nVue compacte")
        visualizer_compact = CompactBattleVisualizer(simulator) # Renommé
        visualizer_compact.run(speed_multiplier=1.0)
    else:
        print("Choix de visualisation invalide.")

# if __name__ == "__main__": # Bloc commenté comme demandé
#     print("VISUALISATIONS AMÉLIORÉES\\n")
#     print("1. Démonstration vue compacte")
#     print("2. Comparaison des visualisations")
#     
#     choice_main = input("\\nVotre choix (1-2): ") # Renommé pour éviter conflit
#     
#     if choice_main == "1":
#         demo_compact_view()
#     elif choice_main == "2":
#         demo_comparison()
#     else:
#         print("Choix invalide") 