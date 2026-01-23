"""
MAZE SOLVER MODULE (v6 - Auto-Entry/Exit Handling)

This module handles the logic for translating a shopping list into an optimized
walking path through a grid-based store layout.

DATA TYPES REFERENCE:

1. INPUTS:
   - layout_grid (numpy.ndarray): A 2D array of strings representing the map.
     ('0' = walkable aisle, 'I' = Entrance, 'E' = Exit, 'P1'...'Pn' = Shelves).
   - shopping_list_names (List[str]): A list of product names (e.g., ['milk', 'bread']).
   - current_pos (Optional[Tuple[int, int]]): The agent's current coordinates. 
     If None, defaults to the Store Entrance ('I').

2. OUTPUT:
   - path (List[Tuple[int, int]]): An ordered list of coordinate tuples.
     Example: [(0, 0), (0, 1), (1, 1), ...]
     This represents the step-by-step coordinates the agent must visit to
     collect all items and finally leave through the store Exit.
"""

import heapq
import numpy as np
import itertools
from typing import List, Tuple, Dict, Any, Optional

# --- EXPLICIT TYPE DEFINITIONS ---
Grid = np.ndarray
Coord = Tuple[int, int]
Path = List[Coord]
ProductDict = Dict[str, Any]
ShoppingList = List[str]

class AgentPathfinder:
    def __init__(self, layout_grid: Grid, products_by_code: ProductDict):
        """
        Initialize the pathfinder with static map data.
        Automatically locates the store Entrance ('I') and Exit ('E').
        """
        self.grid = layout_grid
        self.rows, self.cols = layout_grid.shape
        self.products_by_code = products_by_code
        self.name_to_code = {p.name: code for code, p in products_by_code.items()}
        
        # Cache for distances to avoid re-running BFS for known pairs
        self.memo_dist = {}
        
        # 1. Locate Default Entrance ('I')
        entrance_matches = np.argwhere(self.grid == 'I')
        if len(entrance_matches) > 0:
            self.entrance_pos = tuple(entrance_matches[0])
        else:
            print("Warning: No Entrance ('I') found in layout.")
            self.entrance_pos = None

        # 2. Locate Fixed Exit ('E')
        exit_matches = np.argwhere(self.grid == 'E')
        if len(exit_matches) > 0:
            self.exit_pos = tuple(exit_matches[0])
        else:
            print("Warning: No Exit ('E') found in layout. Pathing will not include exit.")
            self.exit_pos = None

    def solve_path(self, 
                   shopping_list_names: ShoppingList, 
                   current_pos: Optional[Coord] = None) -> Path:
        """
        Calculates the optimal route.

        :param shopping_list_names: List of product names to visit.
        :param current_pos: (row, col) tuple of where the agent is NOW.
                            If None, defaults to self.entrance_pos ('I').
        :return: A list of (row, col) tuples representing the optimal path.
        """
        # 1. Determine Start Position
        if current_pos is not None:
            start_coord = current_pos
        elif self.entrance_pos is not None:
            start_coord = self.entrance_pos
        else:
            # Fallback if no current_pos given and no Entrance found
            print("Error: No start position provided and no Entrance ('I') on map.")
            return []

        # 2. Resolve Targets
        items_data = []
        for name in shopping_list_names:
            if name not in self.name_to_code:
                print(f"Warning: Item '{name}' unknown.")
                continue
            
            code = self.name_to_code[name]
            shelf_locs = self._find_product_locations(code)
            
            if not shelf_locs:
                print(f"Warning: Item '{name}' ({code}) not placed on map.")
                continue
            
            # Pick the "center" shelf location to find the nearest aisle
            center_loc = shelf_locs[len(shelf_locs)//2]
            target_aisle = self._get_nearest_aisle(center_loc)
            
            if target_aisle:
                items_data.append({'name': name, 'pos': target_aisle})

        # Define Nodes
        start_node = self._get_nearest_aisle(start_coord)
        exit_node = None
        
        if self.exit_pos:
            exit_node = self._get_nearest_aisle(self.exit_pos)
        
        # 3. Optimize Route
        # If list is small, use Exact TSP. If large, use Heuristic.
        if len(items_data) <= 9:
            # print(f"Optimization: Using EXACT solver for {len(items_data)} items.")
            sorted_items = self._optimize_route_exact(start_node, items_data, exit_node)
        else:
            # print(f"Optimization: Using HEURISTIC solver for {len(items_data)} items.")
            sorted_items = self._optimize_route_heuristic(start_node, items_data, exit_node)
        
        # 4. Generate Path (A*)
        full_path = [start_node]
        curr = start_node
        
        # Walk to items
        for item in sorted_items:
            segment = self._a_star(curr, item['pos'])
            if segment:
                full_path.extend(segment[1:])
                curr = item['pos']
            
        # Walk to Exit
        if exit_node:
            segment = self._a_star(curr, exit_node)
            if segment:
                full_path.extend(segment[1:])

        return full_path

    # =========================================================================
    #  OPTIMIZATION STRATEGIES
    # =========================================================================

    def _optimize_route_exact(self, start: Coord, items: List[Dict], exit_pos: Optional[Coord]) -> List[Dict]:
        """Brute Force TSP. Checks every possible permutation."""
        n = len(items)
        if n == 0: return []
        
        item_indices = list(range(n))
        best_order = None
        min_total_dist = float('inf')

        for perm in itertools.permutations(item_indices):
            # Start -> First Item
            current_dist = self._get_memoized_dist(start, items[perm[0]]['pos'])
            
            # Item -> Item
            valid = True
            for i in range(n - 1):
                d = self._get_memoized_dist(items[perm[i]]['pos'], items[perm[i+1]]['pos'])
                if d == float('inf'): 
                    valid = False; break
                current_dist += d
            
            if not valid: continue

            # Last Item -> Exit
            if exit_pos:
                d_exit = self._get_memoized_dist(items[perm[-1]]['pos'], exit_pos)
                current_dist += d_exit

            if current_dist < min_total_dist:
                min_total_dist = current_dist
                best_order = perm

        return [items[i] for i in best_order]

    def _optimize_route_heuristic(self, start: Coord, items: List[Dict], exit_pos: Optional[Coord]) -> List[Dict]:
        """Nearest Neighbor + 2-Opt."""
        if not items: return []
        
        # Phase 1: Greedy Nearest Neighbor
        path = []
        remaining = items[:]
        curr = start
        
        while remaining:
            best_idx = -1
            min_dist = float('inf')
            for i, item in enumerate(remaining):
                d = self._get_memoized_dist(curr, item['pos'])
                if d < min_dist:
                    min_dist = d
                    best_idx = i
            
            next_item = remaining.pop(best_idx)
            path.append(next_item)
            curr = next_item['pos']

        # Phase 2: 2-Opt Local Search
        improved = True
        iterations = 0
        while improved and iterations < 50:
            improved = False
            iterations += 1
            current_total = self._calculate_path_cost(start, path, exit_pos)

            for i in range(len(path) - 1):
                for j in range(i + 1, len(path)):
                    new_path = path[:i] + path[i:j+1][::-1] + path[j+1:]
                    new_total = self._calculate_path_cost(start, new_path, exit_pos)
                    if new_total < current_total:
                        path = new_path
                        current_total = new_total
                        improved = True
                        break 
                if improved: break
        
        return path

    def _calculate_path_cost(self, start: Coord, item_path: List[Dict], exit_pos: Optional[Coord]) -> int:
        dist = self._get_memoized_dist(start, item_path[0]['pos'])
        for k in range(len(item_path) - 1):
            dist += self._get_memoized_dist(item_path[k]['pos'], item_path[k+1]['pos'])
        if exit_pos:
            dist += self._get_memoized_dist(item_path[-1]['pos'], exit_pos)
        return dist

    # =========================================================================
    #  CORE UTILS
    # =========================================================================

    def _get_memoized_dist(self, p1: Coord, p2: Coord) -> int:
        if p1 == p2: return 0
        key = tuple(sorted((p1, p2)))
        if key in self.memo_dist: return self.memo_dist[key]
        d = self._bfs_distance(p1, p2)
        self.memo_dist[key] = d
        return d

    def _bfs_distance(self, start: Coord, goal: Coord) -> int:
        queue = [(start, 0)]
        visited = {start}
        while queue:
            (curr_r, curr_c), dist = queue.pop(0)
            if (curr_r, curr_c) == goal: return dist
            
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = curr_r + dr, curr_c + dc
                if self._is_walkable(nr, nc) and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append(((nr, nc), dist + 1))
        return float('inf')

    def _get_nearest_aisle(self, target_pos: Coord) -> Optional[Coord]:
        r, c = target_pos
        if self._is_walkable(r, c): return (r, c)
        
        queue = [(r, c)]
        visited = set([(r, c)])
        
        while queue:
            curr_r, curr_c = queue.pop(0)
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if (nr, nc) not in visited:
                        if self._is_walkable(nr, nc): return (nr, nc)
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        return None

    def _a_star(self, start: Coord, goal: Coord) -> Path:
        if start == goal: return [start]
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        f_score = {start: abs(start[0]-goal[0]) + abs(start[1]-goal[1])}
        open_set_hash = {start}

        while open_set:
            current = heapq.heappop(open_set)[1]
            open_set_hash.remove(current)

            if current == goal:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]

            for dr, dc in [(0,1), (0,-1), (1,0), (-1,0)]:
                nr, nc = current[0]+dr, current[1]+dc
                if self._is_walkable(nr, nc):
                    tent_g = g_score[current] + 1
                    if (nr, nc) not in g_score or tent_g < g_score[(nr, nc)]:
                        came_from[(nr, nc)] = current
                        g_score[(nr, nc)] = tent_g
                        f_score[(nr, nc)] = tent_g + abs(nr-goal[0]) + abs(nc-goal[1])
                        if (nr, nc) not in open_set_hash:
                            heapq.heappush(open_set, (f_score[(nr, nc)], (nr, nc)))
                            open_set_hash.add((nr, nc))
        return []

    def _find_product_locations(self, code: str) -> List[Coord]:
        matches = np.argwhere(self.grid == code)
        return [(r, c) for r, c in matches]

    def _is_walkable(self, r: int, c: int) -> bool:
        if not (0 <= r < self.rows and 0 <= c < self.cols): return False
        val = self.grid[r, c]
        return val == '0' or val == 'I' or val == 'E'
