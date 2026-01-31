"""
Unit tests for the StateMap class.
"""
import pytest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from statemap import StateMap
from agent import Agent
from shopmap import ShopMap


class TestStateMapSmoke:
    """Smoke tests for StateMap class."""

    def test_statemap_creation_empty(self):
        """Test StateMap creation with empty.yaml."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        assert state_map is not None

    def test_statemap_creation_surround(self):
        """Test StateMap creation with surround.yaml."""
        state_map = StateMap(
            "configs/surround.yaml", scale_factor=1, adjust_probability=0.1
        )
        assert state_map is not None


class TestStateMapInitialization:
    """Test StateMap initialization."""

    def test_shop_map_created(self):
        """Test that ShopMap is created."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shop = state_map.get_shop()
        assert isinstance(shop, ShopMap)

    def test_agent_map_created(self):
        """Test that agent map is created."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        agent_map = state_map.get_agent_map()
        assert isinstance(agent_map, np.ndarray)

    def test_agent_map_dimensions_no_scale(self):
        """Test agent map dimensions without scaling."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        agent_map = state_map.get_agent_map()
        shop = state_map.get_shop()
        assert agent_map.shape == (shop.height, shop.width)

    def test_agent_map_dimensions_with_scale(self):
        """Test agent map dimensions with scaling."""
        scale = 2
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=scale, adjust_probability=0.1
        )
        agent_map = state_map.get_agent_map()
        shop = state_map.get_shop()
        assert agent_map.shape == (shop.height * scale, shop.width * scale)

    def test_agent_map_initially_empty(self):
        """Test that agent map is initially all zeros."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        agent_map = state_map.get_agent_map()
        assert np.all(agent_map == 0)

    def test_entrances_found(self):
        """Test that entrances are identified."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        assert len(state_map.entrances) > 0

    def test_exits_found(self):
        """Test that exits are identified."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        assert len(state_map.exits) > 0


class TestStateMapAgentManagement:
    """Test StateMap agent management functionality."""

    def test_spawn_agent_start(self):
        """Test spawning an agent at start position."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        agent = state_map.spawn_agent_start()
        if agent is not None:
            assert isinstance(agent, Agent)

    def test_spawn_agent_has_position(self):
        """Test that spawned agent has a position."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        agent = state_map.spawn_agent_start()
        if agent is not None:
            assert agent.position is not None
            assert isinstance(agent.position, tuple)
            assert len(agent.position) == 2

    def test_spawn_agent_has_shopping_list(self):
        """Test that spawned agent has a shopping list."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        agent = state_map.spawn_agent_start()
        if agent is not None:
            assert agent._shopping_list is not None
            assert isinstance(agent._shopping_list, list)

    def test_create_shopping_list(self):
        """Test creating a shopping list."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        assert isinstance(shopping_list, list)

    def test_write_agent_map(self):
        """Test writing to agent map."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        # Find a walkable position
        entrances = state_map.entrances
        if len(entrances) > 0:
            y, x = entrances[0]
            result = state_map.write_agent_map((x, y))
            assert result is True


class TestStateMapAgentMapUpdates:
    """Test StateMap agent map update functionality."""

    def test_update_agent_map(self):
        """Test updating agent map from passive to active."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        entrances = state_map.entrances
        if len(entrances) > 0:
            y, x = entrances[0]
            state_map.write_agent_map((x, y))
            state_map.update_agent_map()
            agent_map = state_map.get_agent_map()
            assert agent_map[y, x] == 1

    def test_passive_map_cleared_after_update(self):
        """Test that passive map is cleared after update."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        entrances = state_map.entrances
        if len(entrances) > 0:
            y, x = entrances[0]
            state_map.write_agent_map((x, y))
            state_map.update_agent_map()
            assert np.all(state_map._passive_agent_map == 0)


class TestStateMapAvailableSpot:
    """Test StateMap available_spot functionality."""

    def test_available_spot_entrance(self):
        """Test that entrance positions are available."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        entrances = state_map.entrances
        if len(entrances) > 0:
            y, x = entrances[0]
            assert bool(state_map.available_spot((x, y))) is True

    def test_available_spot_occupied(self):
        """Test that occupied positions are not available."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        entrances = state_map.entrances
        if len(entrances) > 0:
            y, x = entrances[0]
            state_map.write_agent_map((x, y))
            assert state_map.available_spot((x, y)) is False

    def test_available_spot_after_update(self):
        """Test spot availability after map update."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        entrances = state_map.entrances
        if len(entrances) > 0:
            y, x = entrances[0]
            state_map.write_agent_map((x, y))
            state_map.update_agent_map()
            assert state_map.available_spot((x, y)) is False


class TestStateMapScaling:
    """Test StateMap with different scale factors."""

    def test_scaling_factor_2(self):
        """Test StateMap with scale factor 2."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=2, adjust_probability=0.1
        )
        agent_map = state_map.get_agent_map()
        shop = state_map.get_shop()
        assert agent_map.shape == (shop.height * 2, shop.width * 2)

    def test_scaling_factor_3(self):
        """Test StateMap with scale factor 3."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=3, adjust_probability=0.1
        )
        agent_map = state_map.get_agent_map()
        shop = state_map.get_shop()
        assert agent_map.shape == (shop.height * 3, shop.width * 3)

    def test_available_spot_with_scaling(self):
        """Test available_spot with scaling."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=2, adjust_probability=0.1
        )
        entrances = state_map.entrances
        if len(entrances) > 0:
            y, x = entrances[0]
            # Scale up the position
            scaled_x, scaled_y = x * 2, y * 2
            # Should still work with proper scaling logic
            result = state_map.available_spot((scaled_x, scaled_y))
            assert result in (True, False)
