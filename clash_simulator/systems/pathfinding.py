"""
Pathfinding module using A* algorithm
"""
import heapq
from typing import List, Tuple, Set, Optional

from ..core.config import GRID_SIZE, PATHFINDING_CONFIG, TILE_SIZE
# We'll need BaseLayout to get buildings and walls, but this creates a circular import
# We'll likely need to pass buildings and walls directly to grid creation function
# from .base_layout import BaseLayout


class Node:
    """Represents a node in the A* pathfinding algorithm."""
    def __init__(self, position: Tuple[int, int], parent: Optional['Node'] = None):
        self.position = position
        self.parent = parent
        self.g = 0  # Cost from start to current node
        self.h = 0  # Heuristic cost from current node to end
        self.f = 0  # Total cost (g + h)

    def __lt__(self, other: 'Node') -> bool:
        return self.f < other.f

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return False
        return self.position == other.position

    def __hash__(self) -> int:
        return hash(self.position)


def create_pathfinding_grid(buildings: List, walls: List, troop_is_flying: bool) -> List[List[int]]:
    """
    Creates a grid representing the map, where:
    0 = walkable
    1 = occupied by building (not wall)
    2 = occupied by wall
    """
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    # Mark areas occupied by buildings (excluding walls)
    for building in buildings:
        if building.type != "wall" and not building.is_destroyed:
            # Buildings are placed at (x, y) tile coordinates
            # Their hitbox includes a gap
            x1, y1, x2, y2 = building.get_hitbox()
            
            # Iterate over the tiles covered by the hitbox
            # Ensure coordinates are within grid boundaries
            start_col = max(0, int(x1 / TILE_SIZE))
            end_col = min(GRID_SIZE -1, int(x2 / TILE_SIZE))
            start_row = max(0, int(y1 / TILE_SIZE))
            end_row = min(GRID_SIZE -1, int(y2 / TILE_SIZE))
            
            for r in range(start_row, end_row + 1):
                for c in range(start_col, end_col + 1):
                    if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                        grid[r][c] = 1 # Occupied by building

    # Mark areas occupied by walls (only if troop is not flying)
    if not troop_is_flying:
        for wall in walls:
            if not wall.is_destroyed:
                # Walls are 1x1
                wall_x, wall_y = int(wall.x / TILE_SIZE), int(wall.y / TILE_SIZE)
                if 0 <= wall_x < GRID_SIZE and 0 <= wall_y < GRID_SIZE:
                    grid[wall_y][wall_x] = 2 # Occupied by wall
    return grid


def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    """Manhattan distance heuristic for A*."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(node_pos: Tuple[int, int], grid: List[List[int]], troop_type: str, troop_is_flying: bool) -> List[Tuple[Tuple[int, int], float]]:
    """
    Gets walkable neighbors of a node.
    Returns a list of ((x, y), cost_multiplier).
    """
    neighbors = []
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]: # 8 directions
        x, y = node_pos[0] + dx, node_pos[1] + dy

        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            cost_multiplier = 1.0
            
            if grid[y][x] == 1 and not troop_is_flying: # Building occupied, not walkable for ground
                continue
            elif grid[y][x] == 2 and not troop_is_flying: # Wall
                if troop_type == "wall_breaker":
                    cost_multiplier = PATHFINDING_CONFIG["wall_penalties"].get(troop_type, 0.1)
                else:
                    # Troops pathing around walls should have a high cost, but not infinite
                    # This allows them to eventually break a wall if it's the only option,
                    # but prefer open paths.
                    # For A* to choose to go *through* a wall tile, that tile needs to be part of the path.
                    # The actual "breaking" of the wall is handled by troop attack logic.
                    # Here, we just assign a high traversal cost.
                    cost_multiplier = PATHFINDING_CONFIG["wall_penalties"].get(troop_type, 15.0) 
            
            # Diagonal movement cost is higher (sqrt(2) ~ 1.414)
            move_cost = 1.414 if abs(dx) == 1 and abs(dy) == 1 else 1.0
            
            neighbors.append(((x, y), move_cost * cost_multiplier))
    return neighbors


def reconstruct_path(current_node: Node) -> List[Tuple[int, int]]:
    """Reconstructs the path from the end node to the start node."""
    path = []
    while current_node:
        path.append(current_node.position)
        current_node = current_node.parent
    return path[::-1] # Return reversed path


def find_path(
    start_pos_world: Tuple[float, float], 
    end_pos_world: Tuple[float, float], 
    buildings: List, 
    walls: List, 
    troop_type: str, 
    troop_is_flying: bool
) -> Optional[List[Tuple[float, float]]]:
    """
    A* pathfinding algorithm.
    Takes world coordinates, converts them to grid coordinates.
    Returns a list of world coordinates for the path, or None if no path is found.
    """
    start_node_pos = (int(start_pos_world[0] / TILE_SIZE), int(start_pos_world[1] / TILE_SIZE))
    end_node_pos = (int(end_pos_world[0] / TILE_SIZE), int(end_pos_world[1] / TILE_SIZE))

    # Ensure start and end are within grid
    start_node_pos = (max(0, min(start_node_pos[0], GRID_SIZE - 1)), max(0, min(start_node_pos[1], GRID_SIZE - 1)))
    end_node_pos = (max(0, min(end_node_pos[0], GRID_SIZE - 1)), max(0, min(end_node_pos[1], GRID_SIZE - 1)))

    grid = create_pathfinding_grid(buildings, walls, troop_is_flying)

    # If end node is unwalkable for ground troops (and troop is ground), try to find a nearby walkable tile
    if not troop_is_flying and grid[end_node_pos[1]][end_node_pos[0]] != 0:
        original_unwalkable_grid_target = end_node_pos # This is a TUPLE (int,int) of grid coords
        # end_pos_world is the original TUPLE (float,float) of the desired attack position

        possible_alternatives = [] # List of ( (alt_grid_x, alt_grid_y), distance_sq_to_original_world_target )
        
        for dx_offset in range(-3, 4): # Search a 7x7 grid area
            for dy_offset in range(-3, 4):
                if dx_offset == 0 and dy_offset == 0:
                    continue
                
                alt_gx, alt_gy = original_unwalkable_grid_target[0] + dx_offset, original_unwalkable_grid_target[1] + dy_offset
                
                if 0 <= alt_gx < GRID_SIZE and 0 <= alt_gy < GRID_SIZE and grid[alt_gy][alt_gx] == 0: # If tile is walkable
                    # Calculate this alternative grid cell's world coordinates (center of tile)
                    alt_wx = (alt_gx * TILE_SIZE) + (TILE_SIZE / 2.0)
                    alt_wy = (alt_gy * TILE_SIZE) + (TILE_SIZE / 2.0)
                    
                    # Calculate squared distance from this alternative's world pos to the *original desired world attack position*
                    dist_sq = (alt_wx - end_pos_world[0])**2 + (alt_wy - end_pos_world[1])**2
                    possible_alternatives.append( ((alt_gx, alt_gy), dist_sq) )
        
        if possible_alternatives:
            possible_alternatives.sort(key=lambda item: item[1]) # Sort by distance squared
            chosen_alternative_grid_target = possible_alternatives[0][0]
            # print(f"Pathfinding DEBUG: Original grid target {original_unwalkable_grid_target} (for world target {end_pos_world[0]:.1f},{end_pos_world[1]:.1f}) was unwalkable. New grid target is {chosen_alternative_grid_target} (closest to world target).")
            end_node_pos = chosen_alternative_grid_target # Update end_node_pos for A*
        else:
            # No walkable alternative found within the 7x7 area
            if not (troop_type == "wall_breaker" and grid[original_unwalkable_grid_target[1]][original_unwalkable_grid_target[0]] == 2) :
                # print(f"Pathfinding DEBUG: Grid target {original_unwalkable_grid_target} (for world target {end_pos_world[0]:.1f},{end_pos_world[1]:.1f}) unwalkable, no alternative found within 7x7 search radius.")
                return None

    open_set = []
    closed_set: Set[Node] = set()

    start_node = Node(start_node_pos)
    end_node = Node(end_node_pos) # Only used for heuristic calculation and check

    heapq.heappush(open_set, start_node)

    while open_set:
        current_node = heapq.heappop(open_set)

        if current_node.position == end_node.position: # end_node.position is the (possibly alternative) grid cell tile
            grid_path = reconstruct_path(current_node)
            # Convert grid path to world coordinates (center of tiles initially)
            world_path_tile_centers = [((x * TILE_SIZE) + (TILE_SIZE / 2.0), (y * TILE_SIZE) + (TILE_SIZE / 2.0)) for x, y in grid_path]

            if not world_path_tile_centers: 
                # print("Pathfinding DEBUG: A* found current_node == end_node but path reconstruction failed (empty grid_path)")
                return None

            # The A* algorithm targets 'end_node.position' (a grid cell).
            # The troop's ultimate desired world coordinate was 'end_pos_world' (the precise attack spot).
            last_astar_tile_center_x, last_astar_tile_center_y = world_path_tile_centers[-1]
            
            # Calculate squared distance from the center of the last A* grid cell to the precise desired world target.
            dist_sq_final_hop = (last_astar_tile_center_x - end_pos_world[0])**2 + \
                                (last_astar_tile_center_y - end_pos_world[1])**2

            # If the center of the last A* tile is very close to the desired world target (e.g., within sqrt(2) * TILE_SIZE),
            # it implies the troop is in the correct or adjacent tile. Make the final step go to the precise 'end_pos_world'.
            # Threshold: (1.5 * TILE_SIZE)^2 = 2.25 * TILE_SIZE^2. Since TILE_SIZE=1, this is 2.25.
            # This covers being in the same tile (dist < 0.5), or an adjacent cardinal (dist < 1.0) or diagonal (dist < 1.414)
            if dist_sq_final_hop < (1.5 * TILE_SIZE)**2 : # Roughly, if desired world point is in same or adjacent tile as A* end tile
                final_path_waypoints = []
                if len(world_path_tile_centers) > 1:
                    final_path_waypoints.extend(world_path_tile_centers[:-1]) # All but the last tile center
                
                # Add the precise world target as the last waypoint.
                # Ensures that if the start A* tile IS the A* target tile, we still provide a path to the precise world coord.
                final_path_waypoints.append(end_pos_world) 
                
                # print(f"Pathfinding DEBUG: Path ({len(final_path_waypoints)} wp) adjusted to end at precise world target {end_pos_world[0]:.1f},{end_pos_world[1]:.1f}.")
                return final_path_waypoints
            else:
                # If the precise world target is too far from the center of the last A* tile,
                # something might be off, or the A* couldn't get closer. Path to tile centers for now.
                # print(f"Pathfinding DEBUG: Path ({len(world_path_tile_centers)} wp) ends at A* tile center {world_path_tile_centers[-1]}. Precise target {end_pos_world[0]:.1f},{end_pos_world[1]:.1f} was too far (dist_sq={dist_sq_final_hop:.1f}).")
                return world_path_tile_centers

        closed_set.add(current_node)

        for neighbor_pos, move_cost_multiplier in get_neighbors(current_node.position, grid, troop_type, troop_is_flying):
            neighbor_node = Node(neighbor_pos, current_node)

            if neighbor_node in closed_set:
                continue
            
            # Calculate tentative g score
            # Cost to move from current to neighbor is base_move_cost * specific_tile_multiplier
            # Base move cost is 1 for cardinal, 1.414 for diagonal
            # specific_tile_multiplier is from get_neighbors (e.g. wall penalty)
            
            dx = neighbor_pos[0] - current_node.position[0]
            dy = neighbor_pos[1] - current_node.position[1]
            base_move_cost = 1.414 if abs(dx) == 1 and abs(dy) == 1 else 1.0
            
            tentative_g = current_node.g + (base_move_cost * move_cost_multiplier)

            # Check if neighbor is already in open_set and if this path is better
            existing_node_in_open_set = next((n for n in open_set if n.position == neighbor_pos), None)

            if existing_node_in_open_set is not None and tentative_g >= existing_node_in_open_set.g:
                continue # This path is not better

            # This is the best path so far to this neighbor
            neighbor_node.g = tentative_g
            neighbor_node.h = heuristic(neighbor_node.position, end_node.position)
            neighbor_node.f = neighbor_node.g + neighbor_node.h
            
            # If it was already in open_set with a higher g, update it. Otherwise, add.
            if existing_node_in_open_set is not None:
                open_set.remove(existing_node_in_open_set) # Remove and re-add to re-sort heap
                heapq.heapify(open_set) # Not strictly necessary to heapify after remove, but push will maintain heap property
            
            heapq.heappush(open_set, neighbor_node)
            
    # print(f"Pathfinding: No path found from {start_node_pos} to {end_node_pos} for {troop_type}")
    return None 