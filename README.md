# Supermarket Crowd Simulation

A high-performance Python-based framework designed for large-scale crowd simulations in supermarket environments. Built to handle hundreds of agents simultaneously, the framework efficiently models pedestrian movement, collision avoidance, and complex crowd dynamics through optimized algorithms and double-buffered state management.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Architecture](#architecture)
- [Testing](#testing)
- [Examples](#examples)
- [Advanced Configuration](#advanced-configuration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

## Overview

This simulation framework is specifically designed for large-scale crowd dynamics in retail environments, capable of simulating hundreds of autonomous agents in near real-time. The framework employs efficient collision detection, double-buffered state updates, and optimized movement algorithms to handle complex crowd behaviors at scale. Agents navigate through configurable shop layouts, avoid collisions with walls and other agents, and exhibit emergent crowd patterns through simple individual rules.

### Key Features

- **Large-Scale Simulation**: Designed to handle 100+ agents simultaneously with optimized performance
- **Efficient Architecture**: Double-buffered state management enables collision-free parallel agent updates
- **Configurable Layouts**: Define shop layouts via YAML files including walls, entrances, exits, and product shelves
- **Scalable Agent System**: Individual agents with random walk behavior and efficient collision avoidance
- **Real-Time Visualization**: Animated matplotlib visualizations and video export for crowd analysis
- **Production-Ready**: Comprehensive pytest test suite with 98+ tests ensuring reliability at scale

## Installation

### Requirements

- Python 3.10 or higher
- NumPy
- Matplotlib
- PyYAML
- pytest (for testing)
- tqdm (for progress bars)
- ffmpeg (optional, for video export)

### Setup

```bash
# Clone or navigate to the repository
cd "Supermarket Simulation"

# Install dependencies
pip install numpy matplotlib pyyaml pytest tqdm

# Optional: Install ffmpeg for video export
# Ubuntu/Debian: sudo apt-get install ffmpeg
# macOS: brew install ffmpeg
```

## Quick Start
Large-Scale Simulation

```bash
# Run with default parameters (96 agents, sweep mode)
python3 src/main.py configs/empty.yaml scratch/ 1000

# Run a large crowd simulation with 200+ agents
python3 src/main.py configs/surround.yaml scratch/ 1000 \
    --mode baseline \
    --probability 0.1 \
    --num-agents 200

# Quick test with smaller crowd (50 agents)
python3 src/main.py configs/empty.yaml scratch/ 5
python3 src/main.py configs/empty.yaml scratch/ 1000 \
    --mode baseline \
    --probability 0.1 \
    --num-agents 50
```

### Running Tests

```bash
# Run all tests
python3 -m pytest tests/

# Run with verbose output
python3 -m pytest tests/ -v

# Run specific test file
python3 -m pytest tests/test_simulation.py
```

## Configuration

### Shop Layout YAML Format

Shop layouts are defined in YAML files with the following structure:

```yaml
width: 600          # Shop width in grid units
height: 300         # Shop height in grid units

walls:
  - type: rectangle
    x: 0            # Top-left x coordinate
    y: 0            # Top-left y coordinate
    width: 600      # Rectangle width
    height: 1       # Rectangle height

entrance:
  - type: line
    start: [0, 40]  # [x, y] start point
    end: [0, 80]    # [x, y] end point

exit:
  - type: line
    start: [0, 200]
    end: [0, 280]

categories:
  Dairy:
    - name: "Milk"
      code: "P1"
    - name: "Cheese"
      code: "P2"
  
shelves:
  - category: Dairy
    x: 50
    y: 50
    width: 20
    height: 10
```

### Available Configurations

- **configs/empty.yaml**: Basic rectangular environment with minimal obstacles
- **configs/surround.yaml**: Complex layout with multiple entrances/exits on all sides
- **configs/supermarket1.yaml**: Realistic supermarket layout with product shelves

## Usage

### Programmatic API

```python
from src.simulation import Simulation

# Create simulation instance
sim = Simulation(
    filename="configs/empty.yaml",
    num_agents=50,
    adjust_probability=0.1
)

# Run simulation for N timesteps
for i in range(1000):
    sim.update()
    if i % 10 == 0:
        sim.checkpoint()  # Save state for visualization

# Save checkpoints to file
sim.save_checkpoints("scratch/simulation_1000_0.1")

# Display animated visualization
sim.plot()

# Save animation to video
sim.save_fig("output.mp4")
```

### Loading and Visualizing Saved Results

```python
from src.simulation import Simulation

# Create simulation and load saved checkpoints
sim = Simulation("configs/empty.yaml")
sim.load_checkpoints("scratch/simulation_1000_0.1.npy")

# Visualize
sim.plot()

# Or save to video
sim.save_fig("replay.mp4")
```

### Command Line Arguments

**src/main.py**

```
positional arguments:
  config                Path to YAML configuration file
  scratch               Directory to save simulation results
  timesteps             Number of simulation timesteps to run

optional arguments:
  --mode {baseline,sweep}
                        Simulation mode (default: sweep)
  --probability FLOAT   Agent adjustment probability (default: 0.1)
  --num-agents INT      Number of agents to spawn (default: 96)
  --seed INT            Random seed for deterministic runs (default: 42)
  --random-seed         Disable deterministic seeding for randomized runs
```

**Mode Options:**
- `baseline`: Single simulation run with specified probability
- `sweep`: Multiple runs across different probability values [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]

### Default run
```bash
python3 src/main.py configs/surround.yaml scratch/ 300
```

## Architecture

### Project Structure

```
Supermarket Simulation/
├── src/
│   ├── agent.py           # Agent class with movement logic
│   ├── product.py         # Product data structure
│   ├── shopmap.py         # Shop layout management
│   ├── statemap.py        # Agent position tracking
│   ├── simulation.py      # Main simulation controller
│   ├── main.py           # Command-line interface
│   └── visualize.py      # Visualization utilities
├── tests/
│   ├── test_agent.py     # Agent class tests
│   ├── test_product.py   # Product class tests
│   ├── test_shopmap.py   # ShopMap class tests
│   ├── test_statemap.py  # StateMap class tests
│   └── test_simulation.py # Simulation tests
├── configs/
│   ├── empty.yaml        # Basic configuration
│   ├── surround.yaml     # Complex configuration
│   └── supermarket1.yaml # Realistic layout
└── scratch/              # Output directory for results
```

### Core Components

**Agent** (`src/agent.py`)
- Represents individual pedestrians
- Implements random walk with direction adjustment
- Handles collision detection and avoidance
- Tracks position, destination, and shopping list

**ShopMap** (`src/shopmap.py`)
- Loads and parses YAML configuration files
- Manages shop layout (walls, entrances, exits, shelves)
- Provides walkability checks for navigation
- Handles product placement and shopping lists

**StateMap** (`src/statemap.py`)
- Orchestrates efficient parallel agent updates each timestep
- Manages agent lifecycle at scale (spawn, move, remove at destination)
- Handles checkpointing and visualization for crowd analysis
- Pairs entrances with exits for agent destinations

**Simulation** (`src/simulation.py`)
- Main simulation controller
The framework's double-buffered architecture enables efficient large-scale crowd simulation:

1. **Agent Update Phase**: Each agent independently calculates and attempts movement
   - Direction may randomly adjust based on `adjust_probability`
   - Next position calculated and validated (walkable, not occupied)
   - Agent writes final position to passive map
   - All agents update in parallel without conflicts

2. **Map Update Phase**: Passive map transferred to active map
   - Atomic swap enables collision-free updates at scale
   - Passive map cleared for next cycle
   - Maintains consistency even with 100+ concurrent agents

3. **Lifecycle Management**:
   - Agents reaching destination are removed
   - New agents spawn at available entrances
   - Agent count dynamically maintained near target value
   - System scales efficiently with population sizut conflicts
   - Passive map cleared for next cycle

3. **Lifecycle Management**:
   - Agents reaching destination are removed
   - New agents spawn at available entrances

## Testing

The framework includes comprehensive tests covering all components.
Tests are run via pytest; the CLI in src/main.py is for simulation runs and
does not execute the test suite.

### Running Tests

```bash
# All tests
python3 -m pytest tests/

# Specific test categories
python3 -m pytest tests/test_agent.py -v
python3 -m pytest tests/test_simulation.py -v

# With coverage report
python3 -m pytest tests/ --cov=src --cov-report=html
```
### Large Crowd Simulation

```python
from src.simulation import Simulation

# Create a large-scale crowd simulation with 150 agents
sim = Simulation("configs/surround.yaml", num_agents=150, adjust_probability=0.1)

# Run for 1000 timesteps
for i in range(1000):
    sim.update()
    if i % 10 == 0:  # Checkpoint every 10 steps
        sim.checkpoint()
```
### Example 1: Basic Simulation and Visualization

```python
from src.simulation import Simulation

# Create and run simulation
sim = Simulation("configs/empty.yaml", num_agents=30, adjust_probability=0.1)

for i in range(500):
    sim.update()
    sim.checkpoint()

sim.plot()
```

### Example 2: Parameter Sweep

```python
from src.simulation import simulate
from multiprocessing import Pool

# Test different probabilities
probabilities = [0.01, 0.05, 0.1, 0.5, 1.0]
args = [
    ("configs/empty.yaml", "scratch", 1000, prob, 50)
    for prob in probabilities
]

with Pool() as pool:
    results = pool.map(simulate, args)
```

### Example 3: Custom Agent Behavior

```python
from src.statemap import StateMap
from src.agent import Agent

# Create custom state map
state_map = StateMap("configs/empty.yaml", scale_factor=1, adjust_probability=0.2)

# Manually create agent
shopping_list = state_map.create_shopping_list()
agent = Agent(
    name="CustomAgent",
    position=(100, 100),
    end_position=(500, 200),
    shopping_list=shopping_list,
    state_map=state_map,
    adjust_probability=0.05,  # Less random than default
    init_dir=(1, 0)  # Start moving right
)
```

### Example 4: Analyzing Saved Results

```python
import numpy as np
from src.simulation import Simulation

# Load saved simulation
sim = Simulation("configs/empty.yaml")
sim.load_checkpoints("scratch/simulation_1000_0.1.npy")

# Analyze agent density over time
checkpoints = np.array(sim.checkpoints)
agent_counts = [cp.sum() for cp in checkpoints]

print(f"Average agents: {np.mean(agent_counts):.1f}")
print(f"Peak agents: {np.max(agent_counts)}")
print(f"Min agents: {np.min(agent_counts)}")
```

## Advanced Configuration

### Adjust Probability Parameter

Controls how often agents randomly change direction:
- **0.0**: Agents maintain initial direction (straight line movement)
- **0.1**: Slight randomness, mostly directed movement (default)
- **0.5**: Moderate randomness, balanced behavior
- **1.0**: Maximum randomness, changes direction every step

### Scale Factor
. The framework is optimized for large populations:
- **Recommended range**: 50-200 agents for realistic crowd dynamics
- **Tested scale**: Successfully handles 200+ agents in complex layouts
- Actual count varies based on entrance availability and spawn success
- Performance remains efficient even at high agent counts due to optimized algorithms
- Consider layout size and complexityl cost quadratically
- Useful for fine-grained movement analysis

### Agent Count

NuThe framework is optimized for 100+ agents; slowdown should be minimal
- If experiencing issues, ensure you're using Python 3.10+
- Consider reducing to 100-150 agents if running on limited hardware
- Use smaller layouts for testing purposes
- Check that numpy is properly installed and up to date
- Consider layout size when choosing agent count

## Troubleshooting

### Common Issues

**Simulation runs slowly**
- Reduce number of agents
- Use smaller layouts
- Consider optimizing the layout configuration

**No agents spawning**
- Check entrance definitions in YAML
- Verify entrances are not blocked by walls
- Ensure exits exist in configuration

**Tests failing**
- Verify all dependencies installed
- Check Python version (3.10+ required)
- Run `python3 -m pytest tests/ -v` for details

**Visualization not displaying**
- Check matplotlib backend configuration
- Ensure display environment available
- Try saving to file instead with `save_fig()`

## Contributing

When modifying the codebase:
1. Run full test suite: `python3 -m pytest tests/`
2. Format code: `black --line-length=79 src/ tests/`
3. Verify type hints are accurate
4. Update docstrings for modified functions
5. Add tests for new functionality
