"""
Tests de débogage pour identifier les problèmes
"""
from clash_simulator.entities.troop_types import create_troop
from clash_simulator.entities.other_buildings import create_building
from clash_simulator.systems.base_layout import BaseLayout
from clash_simulator.systems.battle_simulator import BattleSimulator

def test_troop_movement():
    """Test le mouvement basique d'une troupe"""
    print("=== TEST MOUVEMENT DE TROUPE ===")
    
    # Base minimale
    base = BaseLayout("Test Movement")
    base.add_building("town_hall", 3, (20, 20))
    
    # Une seule troupe
    troop = create_troop("barbarian", 2, (10, 20))
    
    print(f"Position initiale: ({troop.x}, {troop.y})")
    print(f"État initial: {troop.state}")
    
    # Simuler quelques ticks
    simulator = BattleSimulator(base, [troop])
    simulator.start()
    
    for i in range(10):
        simulator.simulate_tick()
        print(f"Tick {i+1}: pos=({troop.x:.1f}, {troop.y:.1f}), état={troop.state.value}, cible={troop.target.type if troop.target else 'None'}")
    
    print()

def test_troop_targeting():
    """Test le ciblage des troupes"""
    print("=== TEST CIBLAGE ===")
    
    # Base avec plusieurs bâtiments
    base = BaseLayout("Test Targeting")
    base.add_building("cannon", 2, (15, 20))
    base.add_building("gold_mine", 3, (25, 20))
    
    # Différents types de troupes
    troops = [
        create_troop("barbarian", 2, (10, 20)),
        create_troop("giant", 1, (10, 21)),
        create_troop("goblin", 2, (10, 22))
    ]
    
    # Vérifier le ciblage initial
    for troop in troops:
        troop.find_target(base.buildings, base.walls, 0)
        print(f"{troop.type}: cible {troop.target.type if troop.target else 'AUCUNE'}")
    
    print()

def test_attack_range():
    """Test la portée d'attaque"""
    print("=== TEST PORTÉE D'ATTAQUE ===")
    
    base = BaseLayout("Test Range")
    building = create_building("cannon", 2, (20, 20))
    base.buildings.append(building)
    
    # Troupes à différentes distances
    positions = [(19, 20), (18, 20), (17, 20), (16, 20)]
    
    for i, pos in enumerate(positions):
        troop = create_troop("barbarian", 2, pos)
        in_range = troop.is_in_range(building)
        print(f"Troupe à {pos}: distance={troop.distance_to_building(building):.1f}, en portée={in_range}")
    
    print()

def test_simple_attack():
    """Test une attaque simple"""
    print("=== TEST ATTAQUE SIMPLE ===")
    
    base = BaseLayout("Test Attack")
    base.add_building("cannon", 2, (20, 20))
    
    # Placer une troupe très proche
    troop = create_troop("barbarian", 2, (19.5, 20))
    
    print(f"HP du bâtiment: {base.buildings[0].hp}")
    print(f"Position troupe: ({troop.x}, {troop.y})")
    print(f"Distance: {troop.distance_to_building(base.buildings[0]):.1f}")
    print(f"En portée: {troop.is_in_range(base.buildings[0])}")
    
    # Simuler
    simulator = BattleSimulator(base, [troop])
    simulator.start()
    
    for i in range(20):
        simulator.simulate_tick()
        if i % 5 == 0:
            print(f"\nTick {i}: HP bâtiment={base.buildings[0].hp}, État troupe={troop.state.value}")
    
    print(f"\nFinal: Destruction={base.get_destruction_percentage():.1f}%")

def test_pathfinding_issue():
    """Test spécifique pour le pathfinding"""
    print("=== TEST PATHFINDING ===")
    
    base = BaseLayout("Test Path")
    base.add_building("town_hall", 3, (20, 20))
    
    troop = create_troop("barbarian", 2, (10, 20))
    
    # Trouver une cible
    troop.find_target(base.buildings, base.walls, 0)
    print(f"Cible trouvée: {troop.target.type if troop.target else 'AUCUNE'}")
    
    if troop.target:
        # Calculer les positions d'attaque
        attack_positions = troop.target.get_attack_positions(troop.range)
        print(f"Positions d'attaque disponibles: {len(attack_positions)}")
        if attack_positions:
            print(f"Première position: {attack_positions[0]}")
            
            # Calculer le chemin
            path = troop.calculate_path(attack_positions[0], base.walls, 0)
            print(f"Chemin calculé: {path}")

if __name__ == "__main__":
    test_troop_movement()
    test_troop_targeting()
    test_attack_range()
    test_simple_attack()
    test_pathfinding_issue() 