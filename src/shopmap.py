import numpy as np
import yaml
from matplotlib.colors import ListedColormap, BoundaryNorm
from typing import Dict, List
from product import Product
import random


class ShopMap:
    """
    A class representing the supermarket layout.
    """

    def __init__(self, filename: str) -> None:
        """Initialize a ShopMap by loading layout and products from a
        YAML file.

        Args:
            filename: Path to the YAML configuration file
        """
        self.layout_array = self.load_layout_yaml(filename)
        assert self.layout_array is not None, "Layout array must be loaded"
        assert self.layout_array.size > 0, "Layout cannot be empty"

        (
            self.products_list,
            self._products_by_code,
            self.products_by_category,
        ) = self._load_products(filename)
        self.height, self.width = self.layout_array.shape

        self._walkable_mask = np.isin(self.layout_array, ["0", "I", "E"])

        assert (
            self.height > 0 and self.width > 0
        ), f"Invalid dimensions: {self.height}x{self.width}"
        assert (
            len(self._products_by_code) > 0
        ), "Must have at least exit product"

    @property
    def product_dict(self) -> dict[str, Product]:
        """Get the dictionary mapping product codes to Product objects.

        Returns:
            dict[str, Product]: Mapping of product codes (e.g., 'P1')
            to Product instances
        """
        return self._products_by_code

    def _fill_rectangle(
        self, grid: np.ndarray, x: int, y: int, w: int, h: int, value: str
    ) -> None:
        """Fill a rectangular area in the grid with a specific value.

        Args:
            grid: The grid array to modify
            x: Starting x coordinate
            y: Starting y coordinate
            w: Width of rectangle
            h: Height of rectangle
            value: Value to fill with
        """
        height, width = grid.shape
        for i in range(y, y + h):
            for j in range(x, x + w):
                if 0 <= i < height and 0 <= j < width:
                    grid[i, j] = value

    def load_layout_yaml(self, filename: str) -> np.ndarray:
        """
        Load a supermarket layout from a yaml file, return an np.ndarray.
        """
        with open(filename, "r") as f:
            data = yaml.safe_load(f)

        width: int = data["width"]
        height: int = data["height"]

        assert width > 0, f"Width must be positive, got {width}"
        assert height > 0, f"Height must be positive, got {height}"
        assert (
            width < 10000 and height < 10000
        ), "Dimensions unreasonably large"

        grid = np.full((height, width), "0", dtype="<U4")

        # --- Walls ---
        for wall in data.get("walls", []):
            self._fill_rectangle(
                grid, wall["x"], wall["y"], wall["width"], wall["height"], "#"
            )

        # --- Entrances ---
        for entrance in data.get("entrance", []):
            x0, y0 = entrance["start"]
            x1, y1 = entrance["end"]
            if x0 == x1:
                for i in range(min(y0, y1), max(y0, y1) + 1):
                    grid[i, x0] = "I"
            elif y0 == y1:
                for j in range(min(x0, x1), max(x0, x1) + 1):
                    grid[y0, j] = "I"

        # --- Exits ---
        for exit_ in data.get("exit", []):
            x0, y0 = exit_["start"]
            x1, y1 = exit_["end"]
            if x0 == x1:
                for i in range(min(y0, y1), max(y0, y1) + 1):
                    grid[i, x0] = "E"
            elif y0 == y1:
                for j in range(min(x0, x1), max(x0, x1) + 1):
                    grid[y0, j] = "E"

        # --- Products ---
        categories: Dict[str, List[dict]] = data.get("categories", {})

        # --- Shelves with categories ---
        for shelf in data.get("shelves", []):
            category = shelf["category"]
            product_list = categories.get(category, [])

            codes = [p["code"] for p in product_list]
            n_products = len(codes)
            cells = shelf["width"] * shelf["height"]

            block_size = max(1, cells // n_products)

            cell_idx = 0
            product_idx = 0

            for i in range(shelf["y"], shelf["y"] + shelf["height"]):
                for j in range(shelf["x"], shelf["x"] + shelf["width"]):
                    grid[i, j] = codes[product_idx]
                    cell_idx += 1

                    if cell_idx >= block_size:
                        cell_idx = 0
                        product_idx = min(product_idx + 1, n_products - 1)

        return grid

    def _plot_layout(self, ax) -> None:
        """Render the shop layout on a matplotlib axes.

        Visualizes walls, entrances, exits, aisles, and product locations.

        Args:
            ax: Matplotlib axes object to draw on
        """
        h, w = self.layout_array.shape
        numeric_grid = np.zeros((h, w), dtype=int)

        for y in range(h):
            for x in range(w):
                cell = self.layout_array[y, x]
                if cell == "0":
                    numeric_grid[y, x] = 0
                elif cell == "#":
                    numeric_grid[y, x] = 1
                elif cell == "I":
                    numeric_grid[y, x] = 2
                elif cell == "E":
                    numeric_grid[y, x] = 3
                elif cell.startswith("P"):
                    numeric_grid[y, x] = 4

        cmap = ListedColormap(
            [
                "white",  # 0 empty
                "saddlebrown",  # 1 wall
                "green",  # 2 entrance
                "red",  # 3 exit
                "gold",  # 4 shelf
            ]
        )

        bounds = [-0.5, 0.5, 1.5, 2.5, 3.5, 4.5]
        norm = BoundaryNorm(bounds, cmap.N)

        ax.imshow(numeric_grid, origin="lower", cmap=cmap, norm=norm)

        ax.invert_yaxis()

        ax.set_xticks(np.arange(-0.5, w, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, h, 1), minor=True)
        ax.grid(which="minor", color="gray", linewidth=0.3)
        ax.tick_params(
            which="both",
            bottom=False,
            left=False,
            labelbottom=False,
            labelleft=False,
        )
        for y in range(h):
            for x in range(w):
                cell = self.layout_array[y, x]
                if cell.startswith("P"):
                    ax.text(
                        x,
                        y,
                        cell,
                        ha="center",
                        va="center",
                        fontsize=6,
                        color="black",
                    )

    def _load_products(
        self, filename: str
    ) -> tuple[list[Product], dict[str, Product], dict[str, list[Product]]]:
        """
        Load products & categories from the same YAML file as the layout.
        Returns:
            - products_list: [Product]
            - products_by_code: dict[str, Product]
            - products_by_category: dict[str, list[Product]]
        """
        with open(filename, "r") as f:
            data = yaml.safe_load(f)

        products_by_code: dict[str, Product] = {}
        products_by_category: dict[str, list[Product]] = {}
        products_list = []

        for category, products in data.get("categories", {}).items():
            products_by_category[category] = []

            for p in products:
                product = Product(
                    name=p["name"],
                    category=category,
                )

                products_list.append(product)
                products_by_category[category].append(product)
                products_by_code[p["code"]] = product

        products_by_code["E"] = Product(
            name="Exit", category="Exit", waiting_time=0
        )

        return products_list, products_by_code, products_by_category

    def generate_shopping_list(self) -> list[Product]:
        """
        Generate a random shopping list for an agent.
        """
        num_items = random.randint(0, len(self.products_list))
        shopping_list = random.sample(self.products_list, num_items)

        # Add the exit at the end
        shopping_list.append(self._products_by_code["E"])

        assert (
            len(shopping_list) > 0
        ), "Shopping list must contain at least exit"
        assert all(
            isinstance(p, Product) for p in shopping_list
        ), "All items must be Product instances"
        assert shopping_list[-1].category == "Exit", "Last item must be Exit"

        return shopping_list

    def walkable(self, x, y) -> np.bool_:
        """Check if a position on the shop map is walkable.

        Args:
            x: X coordinate (column)
            y: Y coordinate (row)

        Returns:
            bool: True if position is walkable ('0', 'I', or 'E'),
            False otherwise
        """
        if not (0 <= y < self.height and 0 <= x < self.width):
            return np.bool_(False)
        return self._walkable_mask[y, x]
