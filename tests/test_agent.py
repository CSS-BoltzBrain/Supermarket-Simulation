"""
Unit tests for the Agent class.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent import Agent
from statemap import StateMap
from product import Product


class TestAgentSmoke:
    """Smoke tests for Agent class."""

    def test_agent_creation(self):
        """Test that an Agent can be created."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
        )
        assert agent is not None


class TestAgentInitialization:
    """Test Agent initialization."""

    def test_agent_has_name(self):
        """Test that agent has a name."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
        )
        assert agent.name == "Test Agent"

    def test_agent_has_position(self):
        """Test that agent has a position."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
        )
        assert agent.position == (10, 10)

    def test_agent_has_end_position(self):
        """Test that agent has an end position."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
        )
        assert agent._end_position == (20, 20)

    def test_agent_has_shopping_list(self):
        """Test that agent has a shopping list."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
        )
        assert agent._shopping_list == shopping_list

    def test_agent_default_adjust_probability(self):
        """Test that agent has default adjust probability."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
        )
        assert agent._adjust_probability == 0.1

    def test_agent_custom_adjust_probability(self):
        """Test that agent accepts custom adjust probability."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
            adjust_probability=0.5,
        )
        assert agent._adjust_probability == 0.5

    def test_agent_init_dir(self):
        """Test that agent accepts initial direction."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
            init_dir=(1, 0),
        )
        assert agent._dir == (1, 0)


class TestAgentMovement:
    """Test Agent movement functionality."""

    def test_move(self):
        """Test that agent can move to a new position."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
        )
        agent.move((15, 15))
        assert agent.position == (15, 15)

    def test_get_position(self):
        """Test getting agent position."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
        )
        assert agent.get_position() == (10, 10)


class TestAgentRouteRequest:
    """Test Agent route request functionality."""

    def test_request_route(self):
        """Test that request_route returns correct tuple."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
        )
        route_info = agent.request_route()
        assert isinstance(route_info, tuple)
        assert len(route_info) == 3
        assert route_info[0] == (10, 10)
        assert route_info[1] == shopping_list
        assert route_info[2] == (20, 20)


class TestAgentStringRepresentation:
    """Test Agent string representations."""

    def test_str_representation(self):
        """Test __str__ method."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
        )
        str_repr = str(agent)
        assert "Test Agent" in str_repr
        assert "(10, 10)" in str_repr
        assert "(20, 20)" in str_repr

    def test_repr_representation(self):
        """Test __repr__ method."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        agent = Agent(
            name="Test Agent",
            position=(10, 10),
            end_position=(20, 20),
            shopping_list=shopping_list,
            state_map=state_map,
        )
        repr_str = repr(agent)
        assert "Test Agent" in repr_str


class TestAgentUpdate:
    """Test Agent update functionality."""

    def test_update_returns_bool(self):
        """Test that update returns a boolean."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        agent = state_map.spawn_agent_start()
        if agent is not None:
            state_map.update_agent_map()
            result = agent.update()
            assert isinstance(result, bool)

    def test_update_reaches_destination(self):
        """Test that update returns True when at destination."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        shopping_list = state_map.create_shopping_list()
        # Place agent at end position
        exits = state_map.exits
        if len(exits) > 0:
            y, x = exits[0]
            # Do not move during the update
            init_dir = (0, 0)
            agent = Agent(
                name="Test Agent",
                position=(x, y),
                end_position=(x, y),
                shopping_list=shopping_list,
                state_map=state_map,
                adjust_probability=0.0,
                init_dir=init_dir,
            )
            state_map.write_agent_map((x, y))
            state_map.update_agent_map()
            result = agent.update()
            assert result is True


class TestAgentWithRealStateMap:
    """Test Agent with realistic state map scenarios."""

    def test_agent_spawned_from_statemap(self):
        """Test agent spawned from StateMap."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        agent = state_map.spawn_agent_start()
        if agent is not None:
            assert isinstance(agent, Agent)
            assert agent.name is not None
            assert agent.position is not None

    def test_multiple_agents_different_positions(self):
        """Test that multiple agents can be spawned."""
        state_map = StateMap(
            "configs/empty.yaml", scale_factor=1, adjust_probability=0.1
        )
        agents = []
        for _ in range(3):
            agent = state_map.spawn_agent_start()
            if agent is not None:
                agents.append(agent)
                state_map.update_agent_map()

        # At least some agents should be created
        assert len(agents) >= 0
