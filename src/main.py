from simulation import simulate
from multiprocessing import Pool
import argparse
import random

import numpy as np


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run crowd simulation")
    parser.add_argument(
        "config", type=str, help="Path to YAML configuration file"
    )
    parser.add_argument(
        "scratch", type=str, help="Directory to save simulation results"
    )
    parser.add_argument(
        "timesteps", type=int, help="Number of simulation timesteps to run"
    )
    parser.add_argument(
        "--mode",
        choices=["baseline", "sweep"],
        default="sweep",
        help="Simulation mode: 'baseline' for single run, 'sweep' for"
        "multiple probabilities (default: sweep)",
    )
    parser.add_argument(
        "--probability",
        type=float,
        default=0.1,
        help="Agent adjustment probability for baseline mode (default: 0.1)",
    )
    parser.add_argument(
        "--num-agents",
        type=int,
        default=96,
        help="Number of agents to spawn per iteration (default: 96)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic runs (default: 42)",
    )
    parser.add_argument(
        "--random-seed",
        action="store_true",
        help="Disable deterministic seeding for randomized runs",
    )

    args = parser.parse_args()

    if not args.random_seed:
        random.seed(args.seed)
        np.random.seed(args.seed)

    if args.mode == "baseline":
        # Run single simulation with specified probability
        simulate(
            (
                args.config,
                args.scratch,
                args.timesteps,
                args.probability,
                args.num_agents,
            )
        )
    else:
        # Run multiple simulations with different probabilities
        probs = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1]
        sim_args = [
            (args.config, args.scratch, args.timesteps, prob, args.num_agents)
            for prob in probs
        ]

        with Pool() as pool:
            results = pool.map_async(simulate, sim_args)
            results.get()
