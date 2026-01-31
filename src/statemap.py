import numpy as np
from shopmap import ShopMap
from agent import Agent
from product import Product


class StateMap:
    def __init__(
        self, filename: str, scale_factor: int, adjust_probability: float
    ) -> None:
        """Initialize the state map for tracking agent positions and
        shop layout.

        Args:
            filename: Path to shop layout YAML file
            scale_factor: Scaling factor for grid resolution
            adjust_probability: Probability for agent direction adjustments
        """
        self._shop_map = ShopMap(filename)
        self._scale_factor = scale_factor
        self._shop_size = self._shop_map.layout_array.shape
        self._active_agent_map = np.zeros(
            (
                self._shop_size[0] * scale_factor,
                self._shop_size[1] * scale_factor,
            ),
            dtype=np.int8,
        )
        self._passive_agent_map = np.zeros_like(self._active_agent_map)

        self._adjust_probability = adjust_probability

        self.entrances = np.argwhere(self._shop_map.layout_array == "I")
        self.exits = np.argwhere(self._shop_map.layout_array == "E")

    def get_shop(self) -> ShopMap:
        """Get the underlying ShopMap instance.

        Returns:
            ShopMap: The shop layout and product information
        """
        return self._shop_map

    def get_agent_map(self) -> np.ndarray:
        """Get the current active agent map showing agent positions.

        Returns:
            np.ndarray: 2D array with 1 where agents are present, 0 elsewhere
        """
        return self._active_agent_map

    def write_agent_map(self, position: tuple[int, int]) -> bool:
        """Mark an agent's position on the passive agent map.

        Args:
            position: Agent position as (x, y) tuple

        Returns:
            bool: Always True
        """
        x, y = position
        assert (
            0 <= x < self._active_agent_map.shape[1]
        ), f"X coordinate {x} out of bounds"
        assert (
            0 <= y < self._active_agent_map.shape[0]
        ), f"Y coordinate {y} out of bounds"

        self._passive_agent_map[y, x] += 1

        assert (
            self._passive_agent_map[y, x] <= 1
        ), "Multiple agents at the same position!"

        return True

    def update_agent_map(self) -> None:
        """Transfer agent positions from passive to active map and clear
        passive map.

        This implements double-buffering for agent positions during
        simulation updates.
        """
        self._active_agent_map[:] = self._passive_agent_map
        self._passive_agent_map.fill(0)

    def spawn_agent(self, position: tuple[int, int]) -> bool:
        """Attempt to spawn an agent at a specific position.

        Args:
            position: Desired spawn position as (x, y) tuple

        Returns:
            bool: True if spawn successful, False if position occupied
        """
        x, y = position
        if self._active_agent_map[y, x] == 1:
            return False  # Position already occupied
        self._active_agent_map[y, x] = 1
        return True

    def create_shopping_list(self) -> list[Product]:
        """Generate a random shopping list for an agent.

        Returns:
            list[Product]: Random selection of products from the shop
        """
        return self._shop_map.generate_shopping_list()

    def spawn_agent_start(self) -> Agent | None:
        """Spawn a new agent at a random entrance with a random exit
        destination.

        Selects an available entrance, pairs it with a non-aligned exit,
        generates a shopping list, and creates an Agent instance.

        Returns:
            Agent | None: New Agent instance, or None if no valid spawn
            location
        """
        # Fast batch check: are ANY entrances available?
        entrance_xs = self.entrances[:, 1]
        entrance_ys = self.entrances[:, 0]

        # Vectorized availability check for all entrances at once
        occupied = (
            self._active_agent_map[entrance_ys, entrance_xs]
            | self._passive_agent_map[entrance_ys, entrance_xs]
        )

        # If all entrances blocked, exit early
        if np.all(occupied):
            return None

        # Get indices of available entrances
        available_indices = np.where(~occupied)[0]

        # Shuffle only the available entrance indices
        np.random.shuffle(available_indices)

        # Try available entrances (limit to first 10 to avoid
        # excessive checking)
        max_attempts = min(10, len(available_indices))
        for idx in available_indices[:max_attempts]:
            entrance = self.entrances[idx]
            y, x = entrance

            # Pre-compute exit mask (non-aligned exits)
            y_mask = self.exits[:, 0] != y
            x_mask = self.exits[:, 1] != x
            mask = y_mask & x_mask

            es = self.exits[mask]
            n = len(es)
            if n == 0:
                continue

            ey, ex = es[np.random.randint(0, n)]

            # Determine initial direction based on entrance position
            if x == 0:
                init_dir = (1, 0)
            elif y == 0:
                init_dir = (0, 1)
            elif x == self._shop_size[1] - 1:
                init_dir = (-1, 0)
            elif y == self._shop_size[0] - 1:
                init_dir = (0, -1)
            else:
                init_dir = (1, 0)  # default

            # Double-check availability (may have changed during iteration)
            if self.available_spot((x, y)):
                self.write_agent_map((x, y))
                return Agent(
                    name="Test agent",
                    position=(x, y),
                    end_position=(ex, ey),
                    shopping_list=self.create_shopping_list(),
                    state_map=self,
                    adjust_probability=self._adjust_probability,
                    init_dir=init_dir,
                )

        return None

    def available_spot(self, position: tuple[int, int]) -> np.bool_:
        """Check if a position is available for agent placement.

        Verifies that the position is walkable and not occupied by
        another agent.

        Args:
            position: Position to check as (x, y) tuple

        Returns:
            np.bool_: True if position is available, False otherwise
        """
        x, y = position
        # Avoid np.array creation - direct integer division
        shop_x = x // self._scale_factor
        shop_y = y // self._scale_factor

        # Short-circuit evaluation: check occupancy first (fastest check)
        if self._active_agent_map[y, x] or self._passive_agent_map[y, x]:
            return np.bool_(False)

        return self.get_shop().walkable(shop_x, shop_y)
