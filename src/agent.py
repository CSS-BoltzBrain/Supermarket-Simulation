from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from collections import deque
import random

from state import ShopMap, AgentMap, CellType


@dataclass
class Agent:
    """
    Agent representing a customer in the supermarket.
    Navigates to collect products from shopping list, then exits.
    """
    id: int = -1
    position: Tuple[int, int] = (0, 0)
    product_list: List[str] = field(default_factory=list)
    current_target: Optional[str] = None
    current_target_position: Optional[Tuple[int, int]] = None
    dwell_counter: int = 0
    dwell_time: int = 5
    interaction_distance: int = 1
    collected_products: List[str] = field(default_factory=list)
    heading_to_exit: bool = False
    stuck_counter: int = 0
    last_position: Optional[Tuple[int, int]] = None

    def think(self, shop_map: ShopMap, agent_map: AgentMap) -> Tuple[int, int]:
        """
        Determine the desired movement direction.
        Returns movement vector (delta_row, delta_col).
        """
        # Track if stuck
        if self.last_position == self.position:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        self.last_position = self.position

        # If dwelling at a product, stay in place
        if self.dwell_counter > 0:
            self.dwell_counter -= 1
            if self.dwell_counter == 0 and self.current_target:
                self.collected_products.append(self.current_target)
                self.current_target = None
                self.current_target_position = None
            return (0, 0)

        # If no current target, get next one
        if self.current_target is None:
            if not self.product_list:
                # All products collected, head to exit
                self.heading_to_exit = True
                if shop_map.exit_positions:
                    self.current_target_position = shop_map.exit_positions[0]
            else:
                # Get next product
                self.current_target = self.product_list.pop(0)
                positions = shop_map.get_product_positions_by_type(self.current_target)
                if positions:
                    # Find best product position considering accessibility
                    self.current_target_position = self._find_best_product_position(
                        shop_map, agent_map, positions)

        # If stuck for too long, try to find alternative target position or make random move
        if self.stuck_counter > 10:
            if self.current_target and not self.heading_to_exit:
                positions = shop_map.get_product_positions_by_type(self.current_target)
                if positions:
                    self.current_target_position = self._find_best_product_position(
                        shop_map, agent_map, positions)
            # Try a random move to break deadlock
            if self.stuck_counter > 15 and random.random() < 0.3:
                random_move = self._get_random_walkable_direction(shop_map, agent_map)
                if random_move != (0, 0):
                    self.stuck_counter = 0
                    return random_move

        # If no target position, stay in place
        if self.current_target_position is None:
            return (0, 0)

        # Check if we're adjacent to target (within interaction distance)
        if self._is_adjacent_to_target(shop_map):
            if self.heading_to_exit:
                # Signal to be removed (move onto exit)
                return self._get_direction_to(self.current_target_position)
            else:
                # Start dwelling at product
                self.dwell_counter = self.dwell_time
                return (0, 0)

        # Calculate direction toward target using pathfinding
        return self._find_path_direction(shop_map, agent_map)

    def _find_closest_position(self, positions: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Find the closest position from a list of positions."""
        if not positions:
            return self.position

        closest = positions[0]
        min_dist = self._manhattan_distance(self.position, closest)

        for pos in positions[1:]:
            dist = self._manhattan_distance(self.position, pos)
            if dist < min_dist:
                min_dist = dist
                closest = pos

        return closest

    def _find_best_product_position(self, shop_map: ShopMap, agent_map: AgentMap,
                                     positions: List[Tuple[int, int]]) -> Optional[Tuple[int, int]]:
        """Find the best product position considering accessibility."""
        candidates = []

        for pos in positions:
            # Check adjacent cells for this product
            adj_cell = self._find_best_adjacent_walkable(shop_map, agent_map, pos)
            if adj_cell is None:
                continue

            dist = self._manhattan_distance(self.position, adj_cell)
            is_occupied = agent_map.is_occupied(adj_cell[0], adj_cell[1])
            # Prioritize positions with unoccupied adjacent cells
            candidates.append((is_occupied, dist, pos))

        if not candidates:
            # Fallback to closest
            return self._find_closest_position(positions)

        candidates.sort(key=lambda x: (x[0], x[1]))
        return candidates[0][2]

    def _manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def _is_adjacent_to_target(self, shop_map: ShopMap) -> bool:
        """Check if agent is adjacent to (within interaction distance of) target."""
        if self.current_target_position is None:
            return False

        dist = self._manhattan_distance(self.position, self.current_target_position)

        # For exit, need to be on it; for products, adjacent is fine
        if self.heading_to_exit:
            return dist <= 1
        else:
            return dist <= self.interaction_distance

    def _get_direction_to(self, target: Tuple[int, int]) -> Tuple[int, int]:
        """Get simple direction vector toward target."""
        dr = 0
        dc = 0

        if target[0] > self.position[0]:
            dr = 1
        elif target[0] < self.position[0]:
            dr = -1

        if target[1] > self.position[1]:
            dc = 1
        elif target[1] < self.position[1]:
            dc = -1

        # Only move in one direction at a time (no diagonals)
        if dr != 0 and dc != 0:
            # Prefer the direction with larger distance
            if abs(target[0] - self.position[0]) >= abs(target[1] - self.position[1]):
                dc = 0
            else:
                dr = 0

        return (dr, dc)

    def _find_path_direction(self, shop_map: ShopMap, agent_map: AgentMap) -> Tuple[int, int]:
        """
        Find direction to move using BFS pathfinding.
        Falls back to simple heuristic if path not found.
        """
        if self.current_target_position is None:
            return (0, 0)

        # For products, find the best walkable cell adjacent to the product
        if not self.heading_to_exit:
            target = self._find_best_adjacent_walkable(shop_map, agent_map, self.current_target_position)
            if target is None:
                return (0, 0)
        else:
            target = self.current_target_position

        # If already at target, stay in place
        if self.position == target:
            return (0, 0)

        # BFS to find path
        path = self._bfs_path(shop_map, agent_map, self.position, target)

        if path and len(path) > 1:
            next_pos = path[1]
            return (next_pos[0] - self.position[0], next_pos[1] - self.position[1])

        # Fallback to simple direction
        return self._get_direction_to(target)

    def _find_best_adjacent_walkable(self, shop_map: ShopMap, agent_map: AgentMap,
                                      target: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Find the best walkable cell adjacent to the target (closest to agent)."""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        candidates = []

        for dr, dc in directions:
            adj_row = target[0] + dr
            adj_col = target[1] + dc
            if shop_map.is_walkable(adj_row, adj_col):
                dist = self._manhattan_distance(self.position, (adj_row, adj_col))
                occupied = agent_map.is_occupied(adj_row, adj_col)
                # Prioritize unoccupied cells, then by distance
                candidates.append((occupied, dist, (adj_row, adj_col)))

        if not candidates:
            return None

        # Sort by occupied (False first), then by distance
        candidates.sort(key=lambda x: (x[0], x[1]))
        return candidates[0][2]

    def _find_adjacent_walkable(self, shop_map: ShopMap, target: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Find a walkable cell adjacent to the target."""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        for dr, dc in directions:
            adj_row = target[0] + dr
            adj_col = target[1] + dc
            if shop_map.is_walkable(adj_row, adj_col):
                return (adj_row, adj_col)

        return None

    def _bfs_path(self, shop_map: ShopMap, agent_map: AgentMap,
                  start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """BFS pathfinding from start to goal."""
        if start == goal:
            return [start]

        queue = deque([(start, [start])])
        visited = {start}
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        while queue:
            current, path = queue.popleft()

            for dr, dc in directions:
                next_pos = (current[0] + dr, current[1] + dc)

                if next_pos in visited:
                    continue

                if next_pos == goal:
                    return path + [next_pos]

                # Check if walkable (ignore other agents for pathfinding to avoid deadlocks)
                if not shop_map.is_walkable(next_pos[0], next_pos[1]):
                    continue

                visited.add(next_pos)
                queue.append((next_pos, path + [next_pos]))

        return []  # No path found

    def _get_random_walkable_direction(self, shop_map: ShopMap, agent_map: AgentMap) -> Tuple[int, int]:
        """Get a random direction to a walkable, unoccupied cell."""
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)

        for dr, dc in directions:
            new_row = self.position[0] + dr
            new_col = self.position[1] + dc
            if (shop_map.is_walkable(new_row, new_col) and
                not agent_map.is_occupied(new_row, new_col)):
                return (dr, dc)

        return (0, 0)

    def update_position(self, new_position: Tuple[int, int]) -> None:
        """Update internal position state."""
        self.position = new_position

    def is_at_exit(self, shop_map: ShopMap) -> bool:
        """Check if agent is at the exit."""
        return shop_map.is_exit(self.position[0], self.position[1])

    def is_done(self) -> bool:
        """Check if agent has completed shopping (all products collected, heading to exit)."""
        return self.heading_to_exit and not self.product_list
