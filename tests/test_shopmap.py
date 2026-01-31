"""
Unit tests for the ShopMap class.
"""

import pytest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from shopmap import ShopMap
from product import Product


class TestShopMapSmoke:
    """Smoke tests for ShopMap class."""

    def test_load_empty_config(self):
        """Test loading the empty.yaml configuration."""
        shop = ShopMap("configs/empty.yaml")
        assert shop is not None

    def test_load_surround_config(self):
        """Test loading the surround.yaml configuration."""
        shop = ShopMap("configs/surround.yaml")
        assert shop is not None


class TestShopMapInitialization:
    """Test ShopMap initialization."""

    def test_layout_array_created(self):
        """Test that layout_array is created."""
        shop = ShopMap("configs/empty.yaml")
        assert shop.layout_array is not None
        assert isinstance(shop.layout_array, np.ndarray)

    def test_empty_dimensions(self):
        """Test that empty.yaml has correct dimensions."""
        shop = ShopMap("configs/empty.yaml")
        assert shop.height == 300
        assert shop.width == 600

    def test_surround_dimensions(self):
        """Test that surround.yaml has correct dimensions."""
        shop = ShopMap("configs/surround.yaml")
        assert shop.height == 400
        assert shop.width == 400

    def test_products_list_created(self):
        """Test that products_list is created."""
        shop = ShopMap("configs/empty.yaml")
        assert shop.products_list is not None
        assert isinstance(shop.products_list, list)

    def test_product_dict_created(self):
        """Test that product_dict is created."""
        shop = ShopMap("configs/empty.yaml")
        assert shop.product_dict is not None
        assert isinstance(shop.product_dict, dict)

    def test_products_by_category_created(self):
        """Test that products_by_category is created."""
        shop = ShopMap("configs/empty.yaml")
        assert shop.products_by_category is not None
        assert isinstance(shop.products_by_category, dict)


class TestShopMapLayout:
    """Test ShopMap layout functionality."""

    def test_empty_has_entrances(self):
        """Test that empty.yaml has entrance cells."""
        shop = ShopMap("configs/empty.yaml")
        entrances = np.argwhere(shop.layout_array == "I")
        assert len(entrances) > 0

    def test_empty_has_exits(self):
        """Test that empty.yaml has exit cells."""
        shop = ShopMap("configs/empty.yaml")
        exits = np.argwhere(shop.layout_array == "E")
        assert len(exits) > 0

    def test_empty_has_walls(self):
        """Test that empty.yaml has wall cells."""
        shop = ShopMap("configs/empty.yaml")
        walls = np.argwhere(shop.layout_array == "#")
        assert len(walls) > 0

    def test_surround_has_entrances(self):
        """Test that surround.yaml has entrance cells."""
        shop = ShopMap("configs/surround.yaml")
        entrances = np.argwhere(shop.layout_array == "I")
        assert len(entrances) > 0

    def test_layout_contains_valid_cells(self):
        """Test that layout contains only valid cell types."""
        shop = ShopMap("configs/empty.yaml")
        unique_vals = np.unique(shop.layout_array)
        valid_prefixes = ["0", "#", "I", "E", "P"]
        for val in unique_vals:
            assert any(val.startswith(prefix) for prefix in valid_prefixes)


class TestShopMapWalkable:
    """Test ShopMap walkable method."""

    def test_walkable_floor(self):
        """Test that floor cells are walkable."""
        shop = ShopMap("configs/empty.yaml")
        # Find a floor cell
        floors = np.argwhere(shop.layout_array == "0")
        if len(floors) > 0:
            y, x = floors[0]
            assert bool(shop.walkable(x, y)) is True

    def test_walkable_entrance(self):
        """Test that entrance cells are walkable."""
        shop = ShopMap("configs/empty.yaml")
        entrances = np.argwhere(shop.layout_array == "I")
        if len(entrances) > 0:
            y, x = entrances[0]
            assert bool(shop.walkable(x, y)) is True

    def test_walkable_exit(self):
        """Test that exit cells are walkable."""
        shop = ShopMap("configs/empty.yaml")
        exits = np.argwhere(shop.layout_array == "E")
        if len(exits) > 0:
            y, x = exits[0]
            assert bool(shop.walkable(x, y)) is True

    def test_not_walkable_wall(self):
        """Test that wall cells are not walkable."""
        shop = ShopMap("configs/empty.yaml")
        walls = np.argwhere(shop.layout_array == "#")
        if len(walls) > 0:
            y, x = walls[0]
            assert bool(shop.walkable(x, y)) is False

    def test_not_walkable_out_of_bounds(self):
        """Test that out-of-bounds coordinates are not walkable."""
        shop = ShopMap("configs/empty.yaml")
        assert bool(shop.walkable(-1, 0)) is False
        assert bool(shop.walkable(0, -1)) is False
        assert bool(shop.walkable(shop.width + 1, 0)) is False
        assert bool(shop.walkable(0, shop.height + 1)) is False


class TestShopMapProducts:
    """Test ShopMap product functionality."""

    def test_product_dict_has_exit(self):
        """Test that product_dict contains Exit product."""
        shop = ShopMap("configs/empty.yaml")
        assert "E" in shop.product_dict
        assert shop.product_dict["E"].name == "Exit"

    def test_products_are_product_instances(self):
        """Test that all products are Product instances."""
        shop = ShopMap("configs/empty.yaml")
        for product in shop.products_list:
            assert isinstance(product, Product)

    def test_generate_shopping_list(self):
        """Test that generate_shopping_list returns a list."""
        shop = ShopMap("configs/empty.yaml")
        shopping_list = shop.generate_shopping_list()
        assert isinstance(shopping_list, list)

    def test_shopping_list_contains_products(self):
        """Test that shopping list contains Product instances."""
        shop = ShopMap("configs/empty.yaml")
        shopping_list = shop.generate_shopping_list()
        for item in shopping_list:
            assert isinstance(item, Product)

    def test_shopping_list_has_exit(self):
        """Test that shopping list always ends with Exit."""
        shop = ShopMap("configs/empty.yaml")
        if len(shop.products_list) > 0:
            shopping_list = shop.generate_shopping_list()
            if len(shopping_list) > 0:
                assert shopping_list[-1].name == "Exit"


class TestShopMapPlotting:
    """Test ShopMap plotting functionality."""

    def test_plot_layout_no_error(self):
        """Test that _plot_layout doesn't raise errors."""
        import matplotlib.pyplot as plt

        shop = ShopMap("configs/empty.yaml")
        fig, ax = plt.subplots()
        try:
            shop._plot_layout(ax)
            plt.close(fig)
        except Exception as e:
            plt.close(fig)
            pytest.fail(f"_plot_layout raised exception: {e}")
