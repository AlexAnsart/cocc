"""
Tests des composants individuels du simulateur
"""
from clash_simulator.entities.troop_types import create_troop
from clash_simulator.entities.other_buildings import create_building
from clash_simulator.systems.base_layout import BaseLayout, BaseBuilder
from clash_simulator.systems.battle_simulator import BattleSimulator, BattleRunner

# Imports pour les configurations
from clash_simulator.data.base_configs import get_base_layout_from_config
from clash_simulator.data.army_configs import get_army_from_config

def test_building_creation():
    """Test la création de différents types de bâtiments"""
    print("=== TEST CRÉATION DE BÂTIMENTS ===")
    
    buildings_to_test = [
        ("town_hall", 3, (10, 10)),
        ("cannon", 2, (5, 5)),
        ("archer_tower", 1, (15, 15)),
        ("mortar", 1, (20, 20)),
        ("wall", 2, (8, 8)),
        ("gold_mine", 3, (25, 25)),
        ("builder_hut", 1, (30, 30))
    ]
    
    for building_type, level, pos in buildings_to_test:
        try:
            building = create_building(building_type, level, pos)
            print(f"✓ {building_type} créé: {building}")
        except Exception as e:
            print(f"✗ Erreur pour {building_type}: {e}")
    
    print()

def test_troop_creation():
    """Test la création de différentes troupes"""
    print("=== TEST CRÉATION DE TROUPES ===")
    
    troops_to_test = [
        ("barbarian", 2, (5.0, 5.0)),
        ("archer", 2, (10.0, 10.0)),
        ("giant", 1, (15.0, 15.0)),
        ("wall_breaker", 1, (20.0, 20.0)),
        ("goblin", 2, (25.0, 25.0))
    ]
    
    for troop_type, level, pos in troops_to_test:
        try:
            troop = create_troop(troop_type, level, pos)
            print(f"✓ {troop_type} créé: {troop}")
        except Exception as e:
            print(f"✗ Erreur pour {troop_type}: {e}")
    
    print()

def test_base_layout():
    """Test la création et manipulation d'une base"""
    print("=== TEST BASE LAYOUT ===")
    
    base = BaseLayout("Test Base")
    
    # Ajouter quelques bâtiments
    success = base.add_building("town_hall", 3, (20, 20))
    print(f"Town Hall ajouté: {success}")
    
    success = base.add_building("cannon", 2, (15, 15))
    print(f"Cannon ajouté: {success}")
    
    success = base.add_building("wall", 2, (18, 18))
    print(f"Wall ajouté: {success}")
    
    print(f"Bâtiments dans la base: {len(base.buildings)}")
    print(f"Murs dans la base: {len(base.walls)}")
    print(f"HP totaux: {base.get_total_hp()}")
    
    print()

def test_simple_battle():
    """Test une bataille simple en utilisant des configurations."""
    print("=== TEST BATAILLE SIMPLE (VIA CONFIGS) ===")
    
    base_name = "Base Test Minima"
    army_name = "Armée Test Minima"

    try:
        print(f"Chargement de la base '{base_name}'...")
        base = get_base_layout_from_config(base_name)
        print(f"Chargement de l'armée '{army_name}'...")
        troops = get_army_from_config(army_name)
    except ValueError as e:
        print(f"✗ Erreur de configuration pour test_simple_battle: {e}")
        assert False, f"Configuration error: {e}"
        return

    print(f"Base '{base.name}' ({len(base.get_all_buildings())} éléments) et Armée '{army_name}' ({len(troops)} troupes) chargées pour le test.")
    
    # Simuler la bataille instantanément
    print("Lancement de la simulation instantanée...")
    stats = BattleRunner.run_instant_battle(base, troops)
    
    print(f"État final: {stats['state']}")
    print(f"Destruction: {stats['destruction_percentage']:.1f}%")
    print(f"Étoiles: {stats['stars']}")
    print(f"Durée: {stats['duration']:.1f}s")
    
    # On pourrait ajouter des assertions ici pour vérifier les résultats attendus
    assert stats['destruction_percentage'] > 0, "La destruction devrait être > 0 pour ce test simple"
    assert stats['state'] != "not_started", "L'état de la bataille ne devrait pas être 'not_started'"
    print("✓ Test de bataille simple terminé.")
    print()

def test_troop_targeting():
    """Test le ciblage des troupes"""
    print("=== TEST CIBLAGE DES TROUPES ===")
    
    # Créer une base avec différents types de bâtiments
    base = BaseLayout("Base Test Ciblage")
    base.add_building("cannon", 2, (10, 10))
    base.add_building("gold_mine", 3, (20, 20))
    base.add_building("elixir_collector", 3, (30, 30))
    
    # Tester différentes troupes
    giant = create_troop("giant", 1, (0, 0))
    goblin = create_troop("goblin", 2, (0, 0))
    
    # Le géant devrait préférer la défense
    giant.find_target(base.buildings, base.walls, 0)
    print(f"Géant cible: {giant.target.type if giant.target else 'Aucune'}")
    
    # Le gobelin devrait préférer les ressources
    goblin.find_target(base.buildings, base.walls, 0)
    print(f"Gobelin cible: {goblin.target.type if goblin.target else 'Aucune'}")
    
    print()

def test_pathfinding_around_walls():
    """Test A* pathfinding around a simple wall obstacle."""
    print("=== TEST PATHFINDING AUTOUR DES MURS ===")
    base = BaseLayout("Pathfinding Test Base")

    # Cible : un canon au centre
    cannon_type = "cannon"
    cannon_level = 1
    cannon_pos = (20, 20)
    base.add_building(cannon_type, cannon_level, cannon_pos) 
    # Récupérer l'objet canon ajouté pour l'assigner comme cible
    # Cela suppose que add_building ajoute à la fin de self.buildings et que c'est le seul bâtiment non-mur
    target_cannon = None
    for b in base.buildings:
        if b.type == cannon_type and b.x == cannon_pos[0] and b.y == cannon_pos[1]:
            target_cannon = b
            break
    assert target_cannon is not None, "Le canon cible n'a pas été trouvé dans la base après ajout."

    # Mur barrant le chemin direct
    # Placer les murs entre la troupe (spawn à ~5,20) et le canon (20,20)
    # Le canon (20,20) de taille 3x3 occupe [20,21,22] x [20,21,22]
    # Hitbox avec gap de 0.5 : [19.5, 22.5] x [19.5, 22.5]
    # Position d'attaque sera autour de ça. ex: (19.0, 20.5) si range=0.5 et troop à gauche
    # Mur vertical à x=15, de y=18 à y=22
    wall_positions = [(15, y) for y in range(18, 23)] 
    for wx, wy in wall_positions:
        base.add_building("wall", 1, (wx, wy))
    
    print(f"Base créée avec {len(base.buildings)} bâtiments et {len(base.walls)} murs.")
    for building in base.buildings:
        print(f"  - {building.type} at ({building.x}, {building.y}), size {building.size}")
    for wall in base.walls:
        print(f"  - Wall at ({wall.x}, {wall.y})")

    # Troupe : un barbare à gauche du mur
    barbarian_start_pos = (5.0, 20.5) # World coordinates
    barbarian = create_troop("barbarian", 1, barbarian_start_pos)
    barbarian.target = target_cannon # Assigner la cible manuellement pour ce test

    print(f"Barbare créé à {barbarian_start_pos}, cible: Cannon à ({target_cannon.x},{target_cannon.y})")

    # Calculer le chemin
    # La méthode calculate_path s'attend maintenant à target_building, all_buildings, walls, current_time
    current_sim_time = 0.0
    path = barbarian.calculate_path(target_cannon, base.buildings, base.walls, current_sim_time)

    if path:
        print(f"✓ Chemin trouvé avec {len(path)} points:")
        # for point in path:
        #     print(f"  -> ({point[0]:.1f}, {point[1]:.1f})")
        
        # Vérifications basiques:
        # 1. Le chemin ne doit pas traverser les tuiles de mur (x=15)
        #    Les points du chemin sont les centres des tuiles (x.5, y.5)
        #    Donc une tuile murale à (15,Y) couvre x de 15.0 à 16.0
        #    Un point de chemin à (15.5, Y.5) serait sur une tuile (15,Y)
        path_on_wall = False
        for p_world_x, p_world_y in path:
            path_tile_x = int(p_world_x) # TILE_SIZE is 1.0
            if path_tile_x == 15 and (18 <= int(p_world_y) <= 22):
                path_on_wall = True
                print(f"✗ ERREUR: Le point du chemin ({p_world_x:.1f}, {p_world_y:.1f}) est sur un mur!")
                break
        if not path_on_wall:
            print("✓ Le chemin ne semble pas traverser les tuiles de mur directes (x=15).")

        # 2. Le premier point doit être proche du barbare
        # print(f"Distance au premier point: {barbarian.distance_to(path[0][0], path[0][1]):.2f}")
        # Le premier point du chemin A* EST la tuile de départ
        assert barbarian.distance_to(path[0][0], path[0][1]) < 1.0, "Le premier point du chemin devrait être la tuile de départ." 

        # 3. Le dernier point doit être une position d'attaque valide pour le canon
        #    Le canon est à (20,20), taille 3. Hitbox [19.5, 22.5] x [19.5, 22.5]
        #    Barbarian range 0.4. Attack pos should be ~0.4 from hitbox edge.
        last_path_point = path[-1]
        target_cx, target_cy = target_cannon.get_center()
        dist_to_target_center = barbarian.distance_to(target_cx, target_cy) # troop to center
        dist_last_wp_to_target_center = target_cannon.distance_to(last_path_point[0], last_path_point[1])
        
        # is_in_range from troop perspective, standing at last_path_point, attacking target_cannon
        # Temporarily move troop to last path point to use its is_in_range
        original_troop_pos = (barbarian.x, barbarian.y)
        barbarian.x, barbarian.y = last_path_point
        can_attack_from_last_point = barbarian.is_in_range(target_cannon)
        barbarian.x, barbarian.y = original_troop_pos # reset position
        
        if can_attack_from_last_point:
            print(f"✓ Le dernier point du chemin {last_path_point} est à portée du canon.")
        else:
            print(f"✗ ERREUR: Le dernier point du chemin {last_path_point} N'EST PAS à portée du canon.")
            print(f"   Distance du point au centre du canon: {dist_last_wp_to_target_center:.2f}")
            print(f"   Hitbox canon: {target_cannon.get_hitbox()}, Range Barbare: {barbarian.range}")

        assert can_attack_from_last_point, "Le dernier point du chemin doit être une position d'attaque valide."

    else:
        print("✗ ERREUR: Aucun chemin trouvé!")
        # Afficher la grille pour le débogage si aucun chemin n'est trouvé
        from clash_simulator.systems.pathfinding import create_pathfinding_grid, TILE_SIZE
        grid = create_pathfinding_grid(
            [b for b in base.buildings if b.type != 'wall'], 
            base.walls, 
            barbarian.is_flying
        )
        print("Grille de pathfinding générée:")
        for r_idx, row in enumerate(grid):
            row_str = "".join(map(str, row))
            # Marquer start et end pour visibilité
            start_tx, start_ty = int(barbarian_start_pos[0]/TILE_SIZE), int(barbarian_start_pos[1]/TILE_SIZE)
            
            # Trouver la target_pos_world utilisée par calculate_path
            attack_positions = target_cannon.get_attack_positions(barbarian.range)
            target_pos_world_used = min(attack_positions, key=lambda pos: barbarian.distance_to(pos[0], pos[1])) if attack_positions else target_cannon.get_center()
            end_tx, end_ty = int(target_pos_world_used[0]/TILE_SIZE), int(target_pos_world_used[1]/TILE_SIZE)
            
            display_row = ""
            for c_idx, cell_val in enumerate(row):
                char_to_add = str(cell_val)
                if r_idx == start_ty and c_idx == start_tx:
                    char_to_add = "S"
                elif r_idx == end_ty and c_idx == end_tx:
                    char_to_add = "E"
                display_row += char_to_add
            print(f"{r_idx:2d}: {display_row}")

    assert path is not None, "Un chemin aurait dû être trouvé."
    print()

# if __name__ == "__main__":
#     test_building_creation()
#     test_troop_creation()
#     test_base_layout()
#     test_simple_battle()
#     test_troop_targeting()
#     test_pathfinding_around_walls() # Temporarily commented out
# 
#     # test_pathfinding_around_walls() 