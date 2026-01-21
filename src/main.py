#!/usr/bin/env python3
"""
Supermarket Crowd Simulation - Entry Point

An agent-based simulation of customer movement in a supermarket environment.
"""

import argparse
import random
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

import yaml

from state import ShopMap, StateMap, CellType
from agent import Agent


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Supermarket Crowd Simulation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--config', '-c',
        type=str,
        default='config.yaml',
        help='Path to configuration YAML file'
    )
    parser.add_argument(
        '--agent-count',
        type=int,
        default=None,
        help='Override simulation.agent_spawn_count from config'
    )
    parser.add_argument(
        '--scale-factor',
        type=int,
        default=None,
        help='Override map.scale_factor from config'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.1,
        help='Delay between iterations (seconds) for visualization'
    )
    parser.add_argument(
        '--no-visual',
        action='store_true',
        help='Disable console visualization'
    )
    return parser.parse_args()


def create_random_shopping_list(product_types: List[str], min_items: int = 1, max_items: int = 4) -> List[str]:
    """Create a randomized shopping list for an agent."""
    num_items = random.randint(min_items, max_items)
    return random.sample(product_types, min(num_items, len(product_types)))


def render_state(state_map: StateMap, iteration: int, agents_spawned: int, agents_exited: int) -> str:
    """Render the current state as a string for console display."""
    lines = []
    lines.append(f"=== Iteration {iteration} | Spawned: {agents_spawned} | Active: {len(state_map.agent_map.agents)} | Exited: {agents_exited} ===")
    lines.append("")

    shop_map = state_map.shop_map
    agent_map = state_map.agent_map

    for row in range(shop_map.rows):
        line = ""
        for col in range(shop_map.cols):
            # Check for agent at this position
            agent_pos = state_map.shop_to_agent_coords(row, col)
            if agent_map.is_occupied(agent_pos[0], agent_pos[1]):
                line += "@"  # Agent symbol
            else:
                cell = shop_map.get_cell(row, col)
                if cell:
                    line += cell.value
                else:
                    line += " "
        lines.append(line)

    lines.append("")
    return "\n".join(lines)


def run_simulation(config: Dict[str, Any], args: argparse.Namespace) -> None:
    """Run the main simulation loop."""
    # Extract config values with CLI overrides
    sim_config = config.get('simulation', {})
    agent_config = config.get('agent', {})
    map_config = config.get('map', {})

    max_iterations = sim_config.get('max_iterations', 1000)
    agent_spawn_rate = sim_config.get('agent_spawn_rate', 5)
    agent_spawn_count = args.agent_count or sim_config.get('agent_spawn_count', 20)
    scale_factor = args.scale_factor or map_config.get('scale_factor', 1)

    interaction_distance = agent_config.get('interaction_distance', 1)
    product_dwell_time = agent_config.get('product_dwell_time', 5)

    # Initialize shop map
    shop_layout = config.get('shop_layout', '')
    products_config = config.get('products', [])
    shop_map = ShopMap.from_layout(shop_layout, products_config)

    # Initialize state map
    state_map = StateMap.create(shop_map, scale_factor)

    # Get available product types
    product_types = shop_map.get_all_product_types()

    # Simulation state
    agents_spawned = 0
    agents_exited = 0
    iteration = 0

    print("Starting Supermarket Crowd Simulation")
    print(f"Map size: {shop_map.rows}x{shop_map.cols}")
    print(f"Scale factor: {scale_factor}")
    print(f"Products: {product_types}")
    print(f"Target agents: {agent_spawn_count}")
    print("-" * 40)

    while iteration < max_iterations:
        # Spawn new agent at entrance if conditions met
        if agents_spawned < agent_spawn_count and iteration % agent_spawn_rate == 0:
            if shop_map.entrance_positions:
                entrance = shop_map.entrance_positions[0]
                spawn_pos = state_map.shop_to_agent_coords(entrance[0], entrance[1])

                if not state_map.agent_map.is_occupied(spawn_pos[0], spawn_pos[1]):
                    shopping_list = create_random_shopping_list(product_types)
                    new_agent = Agent(
                        product_list=shopping_list,
                        dwell_time=product_dwell_time,
                        interaction_distance=interaction_distance
                    )
                    if state_map.agent_map.spawn_agent(spawn_pos, new_agent):
                        agents_spawned += 1

        # Process each agent
        agents_to_remove = []

        for agent in state_map.agent_map.get_all_agents():
            # Get movement intent from agent
            movement = agent.think(shop_map, state_map.agent_map)
            dr, dc = movement

            if dr == 0 and dc == 0:
                continue  # Agent staying in place

            # Calculate new position
            new_row = agent.position[0] + dr
            new_col = agent.position[1] + dc

            # Validate movement
            shop_row, shop_col = state_map.agent_to_shop_coords(new_row, new_col)

            # Check if agent reached exit
            if shop_map.is_exit(shop_row, shop_col) and agent.heading_to_exit:
                agents_to_remove.append(agent.id)
                continue

            # Check if movement is valid
            if state_map.can_move_to(new_row, new_col):
                state_map.agent_map.move_agent(agent.id, (new_row, new_col))
            else:
                # Try alternative directions (perpendicular)
                alternatives = []
                if dr != 0:
                    alternatives = [(0, 1), (0, -1)]
                elif dc != 0:
                    alternatives = [(1, 0), (-1, 0)]

                moved = False
                for alt_dr, alt_dc in alternatives:
                    alt_row = agent.position[0] + alt_dr
                    alt_col = agent.position[1] + alt_dc
                    if state_map.can_move_to(alt_row, alt_col):
                        state_map.agent_map.move_agent(agent.id, (alt_row, alt_col))
                        moved = True
                        break
                # If still blocked, agent stays in place

        # Remove agents that reached exit
        for agent_id in agents_to_remove:
            state_map.agent_map.remove_agent(agent_id)
            agents_exited += 1

        # Render state
        if not args.no_visual:
            print("\033[H\033[J", end="")  # Clear screen
            print(render_state(state_map, iteration, agents_spawned, agents_exited))
            time.sleep(args.delay)

        # Check if simulation is complete
        if agents_exited >= agent_spawn_count and len(state_map.agent_map.agents) == 0:
            print(f"\nSimulation complete! All {agents_exited} agents have exited.")
            break

        iteration += 1

    # Final summary
    print("\n" + "=" * 40)
    print("Simulation Summary")
    print("=" * 40)
    print(f"Total iterations: {iteration}")
    print(f"Agents spawned: {agents_spawned}")
    print(f"Agents exited: {agents_exited}")
    print(f"Agents remaining: {len(state_map.agent_map.agents)}")


def main():
    """Main entry point."""
    args = parse_args()

    # Determine config path
    config_path = Path(args.config)
    if not config_path.is_absolute():
        # Try relative to script location
        script_dir = Path(__file__).parent
        config_path = script_dir / args.config

    if not config_path.exists():
        print(f"Error: Configuration file not found: {config_path}")
        sys.exit(1)

    config = load_config(str(config_path))
    run_simulation(config, args)


if __name__ == '__main__':
    main()
