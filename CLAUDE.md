# Supermarket Crowd Simulation

An agent-based simulation of customer movement in a supermarket environment. The goal is to observe crowd dynamics, particularly clogging behavior when many agents are spawned in a short period.

## Project Objective

Build a minimal viable product (MVP) that simulates agents navigating a supermarket to collect products from their shopping list, then exiting. The simulation should demonstrate clogging behavior when agent density is high.

---

## Architecture Overview

### Core Data Structures

The simulation uses two overlapping 2D grids:

1. **Shop Map**: Static grid describing the supermarket geometry (walls, shelves, products, entrance, exit)
2. **Agent Map**: Dynamic grid tracking agent positions

When `map_scale_factor = 1`, both grids share the same dimensions. The `StateMap` class combines both maps.

### Cell Types (Shop Map)

| Type | Symbol | Description |
|------|--------|-------------|
| Floor | `.` | Walkable space |
| Wall | `#` | Boundary, impassable |
| Shelf | `S` | Obstacle, impassable |
| Product | `P` | Product location (on shelf edge), impassable |
| Entrance | `E` | Agent spawn point |
| Exit | `X` | Agent removal point |

---

## File Structure

```
src/
├── main.py      # Entry point, simulation controller, YAML config loader
├── state.py     # StateMap, ShopMap, AgentMap classes
├── agent.py     # Agent class with movement logic
└── config.yaml  # Simulation parameters and shop layout
```

---

## Configuration (YAML)

The simulation is configured via a YAML file with the following structure:

```yaml
# Simulation parameters
simulation:
  max_iterations: 1000
  agent_spawn_rate: 5        # Spawn one agent every N iterations
  agent_spawn_count: 20      # Total agents to spawn

# Agent parameters
agent:
  interaction_distance: 1    # Distance to "reach" a product (cells)
  product_dwell_time: 5      # Iterations to stay at each product

# Map parameters
map:
  scale_factor: 1            # Agent map scale relative to shop map

# Shop layout (2D grid)
#Shelf elements are able to be converted to be product elements.
#So We do not need to define "product" in "shop_layout".
shop_layout:
  size:
    - x: 100
      y: 100
  shelf:
    - type: rectangle
      x: 0
      y: 10
      width: 6
      height: 3
    - type: rectangle
      x: 10
      y: 10
      width: 6
      height: 3
    - type: circle
      x: 30
      y: 10
      radius: 4
  entrance:
    - x: 0
      y: 0
      width: 1
      height: 1
  exit:
    - x: 100
      y: 100
      width: 1
      height: 1


# Product types (map position to product type)
products:
  - type: "bread"
    positions: [[3, 4], [3, 5]]
  - type: "milk"
    positions: [[3, 11], [3, 12]]
  - type: "eggs"
    positions: [[5, 4], [5, 5]]
  - type: "cheese"
    positions: [[7, 11], [7, 12]]
```

### CLI Override Parameters

The following YAML parameters can be overridden via command-line arguments:

- `--agent-count`: Override `simulation.agent_spawn_count`
- `--scale-factor`: Override `map.scale_factor`

Design the CLI to be extensible for additional overrides in the future.

---

## Core Classes

### `ShopMap`
- Loads shop layout from YAML
- Provides cell type queries (is_walkable, is_product, etc.)
- Stores product locations and types
- Identifies entrance and exit positions

### `AgentMap`
- Tracks all agent positions on the grid
- Provides collision detection between agents
- Methods:
  - `update()`: Iterate through all agents, invoke thinking, update positions
  - `spawn_agent(position, product_list)`: Add new agent at entrance
  - `remove_agent(agent_id)`: Remove agent that reached exit

### `StateMap`
- Combines `ShopMap` and `AgentMap`
- Provides unified view of the simulation state
- Handles map scale factor transformations

### `Agent`
- Properties:
  - `id`: Unique identifier
  - `position`: Current (row, col) on agent map
  - `product_list`: List of product types to collect (ordered)
  - `current_target`: Current product being sought
  - `dwell_counter`: Countdown when at a product location
- Methods:
  - `think(shop_map, agent_map)`: Returns desired movement direction and distance
  - `update_position(new_position)`: Update internal state

---

## Algorithm

### Simulation Loop

```
1. Initialize ShopMap from YAML
2. Initialize empty AgentMap
3. For each iteration:
   a. Spawn new agent at entrance (if spawn conditions met)
   b. For each agent:
      - Call agent.think() to get movement intent
      - Validate movement (no collisions with walls, shelves, other agents)
      - If blocked, try alternative directions or stay in place
      - Update agent position
      - If at product location: decrement dwell counter, mark product collected when done
      - If all products collected: set target to exit
      - If at exit: remove agent
   c. Record/display simulation state
```

### Agent Movement Logic (`think` method)

1. If `dwell_counter > 0`: Stay in place, decrement counter
2. If `current_target` is None:
   - If `product_list` is empty: Target the exit
   - Else: Pop next product from list, set as target
3. Calculate direction toward target using pathfinding or simple heuristic
4. Return movement vector (direction + distance, typically 1 cell)

### Collision Handling

- Agents cannot move onto: walls, shelves, products, other agents
- If primary direction is blocked, try perpendicular directions
- If all directions blocked, stay in place for this iteration

---

## MVP Requirements

1. Single entrance and single exit
2. Agents spawn at entrance with randomized product lists
3. Agents navigate to each product in order, dwell, then proceed
4. Agents exit after completing their shopping list
5. Basic visualization (console output or simple graphics)
6. Configurable via YAML with CLI overrides

---

## Deferred Features (Post-MVP)

- `_potential_deadlock_detection()`: Detect and resolve gridlock patterns
- Multiple entrances/exits
- Agent priority/urgency levels
- More sophisticated pathfinding (A*)
- Analytics and metrics collection

---

## Running the Simulation

```bash
# Basic run with config file
python src/main.py --config config.yaml

# Override agent count
python src/main.py --config config.yaml --agent-count 50

# Override scale factor
python src/main.py --config config.yaml --scale-factor 2
```
