from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum


class CellType(Enum):
    """Cell types for the shop map."""
    FLOOR = '.'
    WALL = '#'
    SHELF = 'S'
    PRODUCT = 'P'
    ENTRANCE = 'E'
    EXIT = 'X'


@dataclass
class ShopMap:
    """
    Static grid describing the supermarket geometry.
    Loads shop layout from YAML and provides cell type queries.
    """
    grid: List[List[CellType]] = field(default_factory=list)
    rows: int = 0
    cols: int = 0
    entrance_positions: List[Tuple[int, int]] = field(default_factory=list)
    exit_positions: List[Tuple[int, int]] = field(default_factory=list)
    product_positions: Dict[Tuple[int, int], str] = field(default_factory=dict)

    @classmethod
    def from_layout(cls, layout_str: str, products_config: List[Dict[str, Any]] = None) -> 'ShopMap':
        """Create a ShopMap from a layout string."""
        shop_map = cls()
        lines = layout_str.strip().split('\n')
        shop_map.rows = len(lines)
        shop_map.cols = max(len(line) for line in lines) if lines else 0

        # Parse the grid
        for row_idx, line in enumerate(lines):
            row = []
            for col_idx, char in enumerate(line):
                try:
                    cell_type = CellType(char)
                except ValueError:
                    cell_type = CellType.FLOOR  # Default to floor for unknown chars

                row.append(cell_type)

                if cell_type == CellType.ENTRANCE:
                    shop_map.entrance_positions.append((row_idx, col_idx))
                elif cell_type == CellType.EXIT:
                    shop_map.exit_positions.append((row_idx, col_idx))

            # Pad row to ensure consistent width
            while len(row) < shop_map.cols:
                row.append(CellType.FLOOR)

            shop_map.grid.append(row)

        # Map product positions to types
        if products_config:
            for product in products_config:
                product_type = product['type']
                for pos in product['positions']:
                    shop_map.product_positions[(pos[0], pos[1])] = product_type

        return shop_map

    def get_cell(self, row: int, col: int) -> Optional[CellType]:
        """Get cell type at given position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col]
        return None

    def is_walkable(self, row: int, col: int) -> bool:
        """Check if cell is walkable (floor, entrance, or exit)."""
        cell = self.get_cell(row, col)
        return cell in (CellType.FLOOR, CellType.ENTRANCE, CellType.EXIT)

    def is_product(self, row: int, col: int) -> bool:
        """Check if cell contains a product."""
        cell = self.get_cell(row, col)
        return cell == CellType.PRODUCT

    def is_entrance(self, row: int, col: int) -> bool:
        """Check if cell is an entrance."""
        cell = self.get_cell(row, col)
        return cell == CellType.ENTRANCE

    def is_exit(self, row: int, col: int) -> bool:
        """Check if cell is an exit."""
        cell = self.get_cell(row, col)
        return cell == CellType.EXIT

    def get_product_type(self, row: int, col: int) -> Optional[str]:
        """Get the product type at given position, if any."""
        return self.product_positions.get((row, col))

    def get_product_positions_by_type(self, product_type: str) -> List[Tuple[int, int]]:
        """Get all positions for a given product type."""
        return [pos for pos, ptype in self.product_positions.items() if ptype == product_type]

    def get_all_product_types(self) -> List[str]:
        """Get list of all unique product types."""
        return list(set(self.product_positions.values()))


@dataclass
class AgentMap:
    """
    Dynamic grid tracking agent positions.
    Provides collision detection between agents.
    """
    rows: int
    cols: int
    agents: Dict[int, 'Agent'] = field(default_factory=dict)
    position_to_agent: Dict[Tuple[int, int], int] = field(default_factory=dict)
    next_agent_id: int = 0

    def is_occupied(self, row: int, col: int) -> bool:
        """Check if a cell is occupied by an agent."""
        return (row, col) in self.position_to_agent

    def get_agent_at(self, row: int, col: int) -> Optional['Agent']:
        """Get the agent at given position, if any."""
        agent_id = self.position_to_agent.get((row, col))
        if agent_id is not None:
            return self.agents.get(agent_id)
        return None

    def spawn_agent(self, position: Tuple[int, int], agent: 'Agent') -> bool:
        """Add new agent at position. Returns False if position is occupied."""
        if self.is_occupied(position[0], position[1]):
            return False

        agent.id = self.next_agent_id
        agent.position = position
        self.agents[agent.id] = agent
        self.position_to_agent[position] = agent.id
        self.next_agent_id += 1
        return True

    def remove_agent(self, agent_id: int) -> bool:
        """Remove agent that reached exit. Returns False if agent not found."""
        if agent_id not in self.agents:
            return False

        agent = self.agents[agent_id]
        if agent.position in self.position_to_agent:
            del self.position_to_agent[agent.position]
        del self.agents[agent_id]
        return True

    def move_agent(self, agent_id: int, new_position: Tuple[int, int]) -> bool:
        """Move agent to new position. Returns False if position is occupied."""
        if agent_id not in self.agents:
            return False

        if self.is_occupied(new_position[0], new_position[1]):
            return False

        agent = self.agents[agent_id]
        old_position = agent.position

        # Update position mappings
        if old_position in self.position_to_agent:
            del self.position_to_agent[old_position]

        agent.position = new_position
        self.position_to_agent[new_position] = agent_id
        return True

    def get_all_agents(self) -> List['Agent']:
        """Get list of all agents."""
        return list(self.agents.values())

    def _potential_deadlock_detection(self) -> bool:
        """Detect potential deadlocks in the agent map."""
        # Deferred feature - placeholder for future implementation
        return False


@dataclass
class StateMap:
    """
    Combines ShopMap and AgentMap.
    Provides unified view of the simulation state.
    """
    shop_map: ShopMap
    agent_map: AgentMap
    scale_factor: int = 1

    @classmethod
    def create(cls, shop_map: ShopMap, scale_factor: int = 1) -> 'StateMap':
        """Create a StateMap from a ShopMap."""
        agent_rows = shop_map.rows * scale_factor
        agent_cols = shop_map.cols * scale_factor
        agent_map = AgentMap(rows=agent_rows, cols=agent_cols)
        return cls(shop_map=shop_map, agent_map=agent_map, scale_factor=scale_factor)

    def shop_to_agent_coords(self, row: int, col: int) -> Tuple[int, int]:
        """Convert shop map coordinates to agent map coordinates."""
        return (row * self.scale_factor, col * self.scale_factor)

    def agent_to_shop_coords(self, row: int, col: int) -> Tuple[int, int]:
        """Convert agent map coordinates to shop map coordinates."""
        return (row // self.scale_factor, col // self.scale_factor)

    def is_walkable(self, row: int, col: int) -> bool:
        """Check if position is walkable (considering both maps)."""
        shop_row, shop_col = self.agent_to_shop_coords(row, col)
        return (self.shop_map.is_walkable(shop_row, shop_col) and
                not self.agent_map.is_occupied(row, col))

    def can_move_to(self, row: int, col: int) -> bool:
        """Check if an agent can move to position."""
        shop_row, shop_col = self.agent_to_shop_coords(row, col)
        return (self.shop_map.is_walkable(shop_row, shop_col) and
                not self.agent_map.is_occupied(row, col))
