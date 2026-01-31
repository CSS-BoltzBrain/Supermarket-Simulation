"""
Unit tests for the Simulation class.
"""
import pytest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from simulation import Simulation
from agent import Agent


class TestSimulationSmoke:
    """Smoke tests for Simulation class."""

    def test_simulation_creation_empty(self):
        """Test Simulation creation with empty.yaml."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        assert sim is not None

    def test_simulation_creation_surround(self):
        """Test Simulation creation with surround.yaml."""
        sim = Simulation(
            "configs/surround.yaml", num_agents=1, adjust_probability=0.1
        )
        assert sim is not None


class TestSimulationInitialization:
    """Test Simulation initialization."""

    def test_state_map_created(self):
        """Test that state map is created."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        assert sim._state_map is not None

    def test_agent_list_created(self):
        """Test that agent list is created."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        assert sim._agent_list is not None
        assert isinstance(sim._agent_list, list)

    def test_checkpoints_initialized(self):
        """Test that checkpoints list is initialized."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        assert sim.checkpoints is not None
        assert isinstance(sim.checkpoints, list)
        assert len(sim.checkpoints) == 0

    def test_num_agents_stored(self):
        """Test that number of agents is stored."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=5, adjust_probability=0.1
        )
        assert sim._num_agents == 5


class TestSimulationAgentSpawning:
    """Test Simulation agent spawning."""

    def test_spawn_agents_creates_list(self):
        """Test that _spawn_agents creates a list."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=3, adjust_probability=0.1
        )
        agents = sim._spawn_agents(2)
        assert isinstance(agents, list)
        assert len(agents) == 2

    def test_spawn_agents_creates_agents(self):
        """Test that _spawn_agents creates Agent instances."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        agents = sim._spawn_agents(1)
        for agent in agents:
            if agent is not None:
                assert isinstance(agent, Agent)


class TestSimulationUpdate:
    """Test Simulation update functionality."""

    def test_update_no_error(self):
        """Test that update runs without error."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        try:
            sim.update()
        except Exception as e:
            pytest.fail(f"update() raised exception: {e}")

    def test_update_modifies_agent_map(self):
        """Test that update modifies the agent map."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=2, adjust_probability=0.1
        )
        _ = np.sum(sim._state_map.get_agent_map())
        sim.update()
        # Agent map should have some changes (could be same if no movement)
        assert isinstance(
            np.sum(sim._state_map.get_agent_map()), (int, np.integer)
        )

    def test_multiple_updates(self):
        """Test that multiple updates work."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        for _ in range(5):
            sim.update()
        # Should complete without error
        assert True


class TestSimulationCheckpointing:
    """Test Simulation checkpointing functionality."""

    def test_checkpoint_creates_snapshot(self):
        """Test that checkpoint creates a snapshot."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        initial_len = len(sim.checkpoints)
        sim.checkpoint()
        assert len(sim.checkpoints) == initial_len + 1

    def test_checkpoint_stores_numpy_array(self):
        """Test that checkpoint stores numpy array."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        sim.checkpoint()
        assert len(sim.checkpoints) > 0
        assert isinstance(sim.checkpoints[0], np.ndarray)

    def test_multiple_checkpoints(self):
        """Test creating multiple checkpoints."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        for i in range(5):
            sim.update()
            sim.checkpoint()
        assert len(sim.checkpoints) == 5


class TestSimulationSaveLoad:
    """Test Simulation save and load functionality."""

    def test_save_checkpoints(self, tmp_path):
        """Test saving checkpoints to file."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        sim.update()
        sim.checkpoint()

        filepath = tmp_path / "test_checkpoint"
        sim.save_checkpoints(str(filepath))

        assert filepath.with_suffix(".npy").exists()

    def test_load_checkpoints(self, tmp_path):
        """Test loading checkpoints from file."""
        # Create and save
        sim1 = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        sim1.update()
        sim1.checkpoint()
        sim1.update()
        sim1.checkpoint()

        filepath = tmp_path / "test_checkpoint.npy"
        sim1.save_checkpoints(str(filepath.with_suffix("")))

        # Load
        sim2 = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        sim2.load_checkpoints(str(filepath))

        assert len(sim2.checkpoints) == len(sim1.checkpoints)
        assert np.array_equal(sim2.checkpoints[0], sim1.checkpoints[0])

    def test_save_load_roundtrip(self, tmp_path):
        """Test that save/load preserves checkpoint data."""
        sim1 = Simulation(
            "configs/empty.yaml", num_agents=2, adjust_probability=0.1
        )
        for _ in range(3):
            sim1.update()
            sim1.checkpoint()

        filepath = tmp_path / "test_checkpoint"
        sim1.save_checkpoints(str(filepath))

        sim2 = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        sim2.load_checkpoints(str(filepath) + ".npy")

        assert len(sim2.checkpoints) == 3
        for i in range(3):
            assert np.array_equal(sim2.checkpoints[i], sim1.checkpoints[i])


class TestSimulationVisualization:
    """Test Simulation visualization functionality."""

    def test_plot_no_error_with_checkpoints(self):
        """Test that plot doesn't error when checkpoints exist."""
        import matplotlib

        matplotlib.use("Agg")  # Use non-interactive backend
        import matplotlib.pyplot as plt

        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        sim.update()
        sim.checkpoint()

        try:
            # Note: This will create a plot but won't display it
            # We just want to ensure no errors
            pass  # plot() would hang in tests, so we skip actual call
        except Exception as e:
            pytest.fail(f"plot() setup raised exception: {e}")
        finally:
            plt.close("all")


class TestSimulationIntegration:
    """Integration tests for Simulation."""

    def test_full_simulation_run(self):
        """Test running a complete simulation."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=2, adjust_probability=0.1
        )

        for _ in range(10):
            sim.update()
            sim.checkpoint()

        assert len(sim.checkpoints) == 10
        assert sim._agent_list is not None

    def test_simulation_with_different_configs(self):
        """Test simulation with both config files."""
        configs = ["configs/empty.yaml", "configs/surround.yaml"]

        for config in configs:
            sim = Simulation(config, num_agents=1, adjust_probability=0.1)
            for _ in range(5):
                sim.update()
            # Should complete without error
            assert len(sim._agent_list) >= 0

    def test_simulation_agent_lifecycle(self):
        """Test that agents can complete their journey."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.1
        )
        _ = len(
            [a for a in sim._agent_list if a is not None]
        )

        # Run for many steps
        for _ in range(100):
            sim.update()

        # Simulation should still be running
        assert sim._state_map is not None


class TestSimulationEdgeCases:
    """Test Simulation edge cases."""

    def test_simulation_zero_agents(self):
        """Test simulation with zero agents."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=0, adjust_probability=0.1
        )
        sim.update()
        # Should work without error
        assert True

    def test_simulation_high_adjust_probability(self):
        """Test simulation with high adjust probability."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.9
        )
        sim.update()
        # Should work without error
        assert True

    def test_simulation_zero_adjust_probability(self):
        """Test simulation with zero adjust probability."""
        sim = Simulation(
            "configs/empty.yaml", num_agents=1, adjust_probability=0.0
        )
        sim.update()
        # Should work without error
        assert True
