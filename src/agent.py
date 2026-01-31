from product import Product
from typing import Tuple
import numpy as np


class Agent:
    def __init__(
        self,
        name: str,
        position: tuple[int, int],
        end_position: tuple[int, int],
        shopping_list: list[Product],
        state_map,
        adjust_probability: float = 0.1,
        init_dir: tuple[int, int] = None,
    ) -> None:
        """Initialize an agent with name, starting position, destination,
        and shopping list.

        Args:
            name: Unique identifier for the agent
            position: Starting (x, y) coordinates on the map
            end_position: Target (x, y) coordinates (typically an exit)
            shopping_list: List of Product objects to collect
            state_map: Reference to the StateMap managing the simulation
            adjust_probability: Probability of randomly changing direction
            (default 0.1)
            init_dir: Initial movement direction as (dx, dy) tuple
        """
        self.name = name
        self.position = position  # position is a tuple (x, y)
        self._shopping_list = shopping_list
        self._state_map = state_map
        self._end_position = end_position

        self._route = None

        self._pause_length = 0
        self._adjust_probability = adjust_probability

        self._dir = init_dir
        self._dirs = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        self._dir_alternatives = {
            d: [x for x in self._dirs if x != d] for d in self._dirs
        }

        assert (
            0 <= adjust_probability <= 1
        ), f"Probability must be in [0,1], got {adjust_probability}"
        assert len(position) == 2, "Position must be (x, y) tuple"
        assert len(end_position) == 2, "End position must be (x, y) tuple"
        assert isinstance(shopping_list, list), "Shopping list must be a list"

    def move(self, new_position: tuple[int, int]) -> None:
        """Move the agent to a new position."""
        assert len(new_position) == 2, "New position must be (x, y) tuple"
        assert all(
            isinstance(coord, (int, np.integer)) for coord in new_position
        ), "Coordinates must be integers"
        self.position = new_position

    def get_position(self) -> tuple[int, int]:
        """Return the current position of the agent."""
        return self.position

    def __str__(self) -> str:
        return (
            f"Agent {self.name} at position {self.get_position()}"
            f"going to {self._end_position}"
        )

    def __repr__(self) -> str:
        return (
            f"Agent {self.name} at position {self.get_position()}"
            f"going to {self._end_position}"
        )

    def _route_generator(self) -> None:
        """Generate a route based on the shopping list."""
        return None

    def request_route(
        self,
    ) -> Tuple[tuple[int, int], list[Product], tuple[int, int]]:
        """Return a tuple containing the agent's current position, shopping
        list, and destination.

        Returns:
            Tuple of (position, shopping_list, end_position) for route planning
        """
        return (
            self.get_position(),
            self._shopping_list,
            self._end_position,
        )

    def update(self) -> bool:
        """Update the agent's state for one simulation timestep.

        Performs movement logic including:
        - Direction initialization and random adjustment
        - Next position calculation and collision checking
        - Position update if move is valid
        - Writing position to passive agent map

        Returns:
            bool: True if the agent has reached its destination,
            False otherwise
        """
        x, y = self.get_position()

        # Verify invariant: no other agent has moved to our position this cycle
        assert self._state_map._passive_agent_map[y, x] == 0, (
            f"Collision at ({x}, {y}): passive_agent_map[{y}, {x}] ="
            f"{self._state_map._passive_agent_map[y, x]}"
        )

        self._route = (0, 0)
        if not self._dir:
            dir = np.random.randint(0, 4)
            self._dir = self._dirs[dir]

        if np.random.rand() < self._adjust_probability:
            prev_dir = self._dir
            # Pick a different direction
            available_dirs = self._dir_alternatives[prev_dir]
            self._dir = available_dirs[np.random.randint(0, 3)]

        # Calculate next position inline
        dx, dy = self._dir
        nx, ny = x + dx, y + dy

        # Inline available_spot check to avoid function call overhead
        state_map = self._state_map
        shop_x, shop_y = (
            nx // state_map._scale_factor,
            ny // state_map._scale_factor,
        )

        if (
            state_map.get_shop().walkable(shop_x, shop_y)
            and not state_map._active_agent_map[ny, nx]
            and not state_map._passive_agent_map[ny, nx]
        ):
            self.move((nx, ny))

        # Write final position to passive map (whether moved or stayed)
        x, y = self.get_position()
        state_map._passive_agent_map[y, x] += 1

        return self.get_position() == self._end_position

    def exists(self) -> bool:
        """Check if the agent exists at its current position on the
        passive agent map.

        Returns:
            bool: True if agent is marked at its position, False otherwise
        """
        x, y = self.get_position()
        return self._state_map._passive_agent_map[y, x] == 1
