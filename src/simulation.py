from statemap import StateMap
from agent import Agent
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.animation import ArtistAnimation
from multiprocessing import Pool

import sys

from tqdm import tqdm


class Simulation:
    def __init__(
        self, filename: str, num_agents=5, adjust_probability=0.1
    ) -> None:
        """Initialize a supermarket simulation.

        Args:
            filename: Path to shop layout YAML file
            num_agents: Number of agents to simulate (default 5)
            adjust_probability: Probability of agent direction changes
            (default 0.1)
        """
        self._state_map = StateMap(
            filename, scale_factor=1, adjust_probability=adjust_probability
        )
        self._agent_list = self._spawn_agents(num_agents)
        self._num_agents = num_agents
        self._adjust_probability = adjust_probability
        self.checkpoints = []

        self._state_map.update_agent_map()

    def _spawn_agents(self, num_agents: int) -> list[Agent | None]:
        """Spawn a given number of agents in the simulation."""
        agent_list = [
            self._state_map.spawn_agent_start() for _ in range(num_agents)
        ]

        return agent_list

    def plot(self) -> None:
        """Display an animated plot of the simulation using saved checkpoints.

        Creates a matplotlib animation showing agent movement over time.
        """
        fig = plt.figure(figsize=(10, 8))
        ax = fig.subplots()
        self._state_map.get_shop()._plot_layout(ax)

        # Add title with probability
        title = (
            f"Crowd Simulation\n"
            f"Adjustment Probability: {self._adjust_probability:.3f}"
        )
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

        cmap = ListedColormap([(0, 0, 0, 0), "black"])
        ims = []
        for i in range(len(self.checkpoints)):
            im = ax.imshow(self.checkpoints[i], animated=True, cmap=cmap)
            if i == 0:
                im = ax.imshow(self.checkpoints[i], cmap=cmap)
            ims.append([im])

        _ = ArtistAnimation(
            fig, ims, interval=50, blit=True, repeat_delay=1000
        )

        plt.tight_layout()
        plt.show()

    def update(self) -> None:
        """Update the simulation by one timestep.

        Updates all agent positions, removes agents that reached their
        destination, spawns new agents, and updates the agent map.
        """
        # Passive map should be empty at start of update cycle
        # assert np.all(
        #     self._state_map._passive_agent_map == 0
        # ), "Passive map must be empty at cycle start"

        # Update all agents and keep only those that haven't reached
        # their destination
        self._agent_list = [
            agent for agent in self._agent_list if agent and not agent.update()
        ]

        assert np.all(
            agent.exists() for agent in self._agent_list
        ), "All agents must exist"

        # Always attempt to spawn _num_agents (most will fail if entrances
        # are blocked)
        self._agent_list.extend(
            [a for a in self._spawn_agents(self._num_agents) if a is not None]
        )

        self._state_map.update_agent_map()

    def checkpoint(self) -> None:
        """Save the current agent map state as a checkpoint for
        visualization."""
        self.checkpoints += [
            np.array(self._state_map.get_agent_map(), dtype=np.int8)
        ]

    def save_checkpoints(self, filename: str) -> None:
        """Save all checkpoints to a NumPy file.

        Args:
            filename: Path to save checkpoints to (without .npy extension)
        """
        arr = np.array(self.checkpoints, dtype=np.int8)
        np.save(filename, arr)

    def load_checkpoints(self, filename: str) -> None:
        """Load checkpoints from a NumPy file.

        Args:
            filename: Path to load checkpoints from
        """
        arr = np.load(filename)
        self.checkpoints = arr

    def save_fig(self, filename: str) -> None:
        """Save the simulation animation to a video file.

        Args:
            filename: Output video filename (e.g., 'animation.mp4')
        """
        fig = plt.figure(figsize=(10, 8))
        ax = fig.subplots()
        self._state_map.get_shop()._plot_layout(ax)

        # Add title with probability
        title = (
            f"Supermarket Crowd Simulation\n"
            f"Adjustment Probability: {self._adjust_probability:.3f}"
        )
        ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

        cmap = ListedColormap([(0, 0, 0, 0), "black"])
        ims = []
        for i in range(len(self.checkpoints)):
            im = ax.imshow(self.checkpoints[i], animated=True, cmap=cmap)
            if i == 0:
                im = ax.imshow(self.checkpoints[i], cmap=cmap)
            ims.append([im])

        ani = ArtistAnimation(
            fig, ims, interval=50, blit=True, repeat_delay=1000
        )
        ani.save(filename=filename, writer="ffmpeg")


def simulate(args) -> None:
    """Run a complete simulation with specified parameters.

    Args:
        args: Tuple of (config_file, scratch_disk, timesteps, prob, num_agents)
            config_file: Path to YAML configuration file
            scratch_disk: Directory to save results
            timesteps: Number of simulation steps to run
            prob: Adjustment probability for agents
            num_agents: Number of agents to spawn per iteration
    """
    config_file, scratch_disk, timesteps, prob, num_agents = args
    simulation = Simulation(config_file, num_agents, adjust_probability=prob)

    tk0 = tqdm(range(timesteps), total=timesteps, disable=None)
    for i in tk0:
        simulation.update()
        if not i % 1:
            simulation.checkpoint()

    simulation.save_checkpoints(
        f"{scratch_disk}/simulation_{timesteps}_{prob}"
    )

    simulation.plot()


if __name__ == "__main__":
    scratch_disk = sys.argv[1]
    timesteps = int(sys.argv[2])
    # for prob in [0.1]:
    probs = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1]

    args = [(scratch_disk, timesteps, prob) for prob in probs]

    with Pool() as pool:
        results = pool.map_async(simulate, args)
        results.get()
