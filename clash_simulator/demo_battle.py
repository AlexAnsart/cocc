"""
Démonstration d'une bataille visuelle en temps réel
"""
# from clash_simulator.entities.troop_types import create_troop # Supprimé
# from clash_simulator.systems.base_layout import BaseLayout # Supprimé
from clash_simulator.systems.battle_simulator import BattleSimulator, BattleRunner # BattleRunner ajouté
from clash_simulator.visualization.terminal_display import BattleVisualizer

# Imports pour les configurations
from clash_simulator.data.base_configs import get_base_layout_from_config
from clash_simulator.data.army_configs import get_army_from_config

def demo_simple_attack(base_name: str = "Simple TH3 Par Défaut", army_name: str = "Armée Démo Visuelle"):
    """Démo d'une attaque simple avec visualisation, utilisant des configurations."""
    print(f"=== DÉMONSTRATION DE BATAILLE VISUELLE (Base: {base_name}, Armée: {army_name}) ===\\n")
    
    try:
        base = get_base_layout_from_config(base_name)
        troops = get_army_from_config(army_name)
    except ValueError as e:
        print(f"Erreur de configuration pour la démo: {e}")
        return

    print(f"Base '{base.name}' et Armée '{army_name}' chargées.")
    print(f"Nombre de troupes: {len(troops)}")
    # Afficher un résumé de l'armée si besoin
    troop_counts = {}
    for t in troops:
        troop_counts[t.type] = troop_counts.get(t.type, 0) + 1
    for t_type, count in troop_counts.items():
        print(f"- {count} {t_type.capitalize()}s")

    # Créer le simulateur avec durée réduite pour la démo
    simulator = BattleSimulator(base, troops, battle_duration=60)
    
    # Créer le visualiseur
    visualizer = BattleVisualizer(simulator)
    
    print("\\nLa bataille va commencer...")
    print("Vitesse: 10 ticks par seconde (vitesse normale)")
    print("Durée: 60 secondes maximum")
    # input("\\nAppuyez sur Entrée pour lancer la bataille...") # Optionnel
    
    # Lancer la visualisation à vitesse normale (1.0)
    visualizer.run(speed_multiplier=1.0, show_legend=True, update_frequency=1.0)

def demo_speed_comparison(base_name: str = "Simple TH3 Par Défaut", army_name: str = "Petite Armée Test Vitesse"):
    """Démo avec différentes vitesses, utilisant des configurations."""
    print("\\n=== COMPARAISON DES VITESSES ===")
    print("1. Vitesse normale (1x) - 10 ticks/seconde")
    print("2. Vitesse rapide (2x) - 20 ticks/seconde") 
    print("3. Vitesse très rapide (5x) - 50 ticks/seconde")
    print("4. Instantané (pas de visualisation)")
    
    choice = input("\\nChoisissez une vitesse (1-4): ")
    
    try:
        base = get_base_layout_from_config(base_name)
        troops = get_army_from_config(army_name)
    except ValueError as e:
        print(f"Erreur de configuration pour la démo de vitesse: {e}")
        return
    
    print(f"Utilisation de la base '{base.name}' et de l'armée '{army_name}' ({len(troops)} troupes).")

    # Durée de bataille plus courte pour ces tests
    simulator = BattleSimulator(base, troops, battle_duration=30)
    
    if choice == "1":
        visualizer = BattleVisualizer(simulator)
        visualizer.run(speed_multiplier=1.0, show_legend=False)
    elif choice == "2":
        visualizer = BattleVisualizer(simulator)
        visualizer.run(speed_multiplier=2.0, show_legend=False)
    elif choice == "3":
        visualizer = BattleVisualizer(simulator)
        visualizer.run(speed_multiplier=5.0, show_legend=False)
    elif choice == "4":
        # from clash_simulator.systems.battle_simulator import BattleRunner # Déjà importé en haut
        stats = BattleRunner.run_instant_battle(base, troops) # Pas besoin de recréer le simulateur
        print(f"\\nRésultat instantané:")
        print(f"État: {stats['state']}")
        print(f"Destruction: {stats['destruction_percentage']:.1f}%")
        print(f"Durée: {stats['duration']:.1f}s")
    else:
        print("Choix de vitesse invalide.")

# if __name__ == "__main__": # Bloc commenté comme demandé
#     print("SIMULATEUR CLASH OF CLANS - DÉMO\\n")
#     print("1. Démonstration d'une bataille complète")
#     print("2. Test des différentes vitesses")
#     
#     choice = input("\\nVotre choix (1-2): ")
#     
#     if choice == "1":
#         # Utiliser des configurations par défaut ou demander à l'utilisateur
#         demo_simple_attack() 
#     elif choice == "2":
#         demo_speed_comparison()
#     else:
#         print("Choix invalide") 