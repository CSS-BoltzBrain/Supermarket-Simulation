import os
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import traceback

import sys
import os

# Get the path to the project root (one level up from this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Add it to the system path so Python can find 'src'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# NOW you can import from src
from src.maze_solver_v2 import AgentPathfinder

# Import your existing modules
from src.layout import load_layout_yaml, load_products
from src.maze_solver_v2 import AgentPathfinder

def plot_full_map_with_sequence(layout_array, path=None, pickup_targets=None, title="Supermarket Simulation"):
    h, w = layout_array.shape
    numeric_grid = np.zeros((h, w), dtype=int)

    # Convert grid strings to numbers for coloring
    for i in range(h):
        for j in range(w):
            cell = layout_array[i, j]
            if cell == '0': numeric_grid[i, j] = 0   # Floor
            elif cell == '#': numeric_grid[i, j] = 1 # Wall
            elif cell == 'I': numeric_grid[i, j] = 2 # Entrance
            elif cell == 'E': numeric_grid[i, j] = 3 # Exit
            elif cell.startswith('P'): numeric_grid[i, j] = 4 # Shelf

    # Colors: White(Floor), Brown(Wall), Green(In), Red(Out), Gold(Shelf)
    cmap = ListedColormap(['white', 'saddlebrown', 'green', 'red', 'gold'])

    fig, ax = plt.subplots(figsize=(16, 9))
    ax.imshow(numeric_grid, origin='lower', cmap=cmap)
    
    # Grid lines
    ax.set_xticks(np.arange(-0.5, w, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, h, 1), minor=True)
    ax.grid(which='minor', color='gray', linestyle=':', linewidth=0.3)

    # --- 1. DETERMINE STOP ORDER ---
    # We walk the path. If we hit a coordinate that is in our 'pickup_targets' list,
    # we assign it the next number.
    
    stop_map = {} # Key: (r,c), Value: Sequence Number
    visited_targets = set()
    counter = 1

    if path and pickup_targets:
        for step in path:
            if step in pickup_targets and step not in visited_targets:
                stop_map[step] = counter
                visited_targets.add(step)
                counter += 1

    # --- 2. DRAW PATH ARROWS ---
    if path and len(path) > 1:
        for k in range(len(path) - 1):
            curr_r, curr_c = path[k]
            next_r, next_c = path[k+1]
            
            # Check if this is a stop location
            if (curr_r, curr_c) in stop_map:
                # Get the sequence number
                num = stop_map[(curr_r, curr_c)]
                # Draw the Number (Green, Bold, Large)
                ax.text(curr_c, curr_r, str(num), ha='center', va='center', 
                        fontsize=11, fontweight='heavy', color='green', zorder=10)
            else:
                # Draw Directional Arrow (Small, Blue)
                dr = next_r - curr_r
                dc = next_c - curr_c
                
                arrow = ""
                if dr == 1: arrow = "^"
                elif dr == -1: arrow = "v"
                elif dc == 1: arrow = ">"
                elif dc == -1: arrow = "<"
                
                ax.text(curr_c, curr_r, arrow, ha='center', va='center', 
                        fontsize=5, fontweight='bold', color='blue')
        
        # Mark End
        ax.text(path[-1][1], path[-1][0], "X", ha='center', va='center', fontsize=12, fontweight='bold', color='red')

    # --- 3. DRAW ALL PRODUCT CODES ---
    for i in range(h):
        for j in range(w):
            cell = layout_array[i, j]
            if cell.startswith("P"):
                ax.text(j, i, cell, ha='center', va='center', fontsize=5, color='black', alpha=0.7)

    ax.set_title(title)
    plt.tight_layout()
    plt.show()

def run_simulation():
    filename = os.path.join("configs", "supermarket1.yaml")
    size_shopping_list = 10
    
    if not os.path.exists(filename):
        print(f"Error: '{filename}' not found.")
        return

    print(f"Loading Layout: {filename}...")
    layout_grid = load_layout_yaml(filename)
    products_list, products_by_code, products_by_category= load_products(filename)

    agent = AgentPathfinder(layout_grid, products_by_code)

    start_pos = (5, 1)
    exit_pos = (18, 1)

    # --- GENERATE RANDOM SHOPPING LIST ---
    all_product_names = list(agent.name_to_code.keys())
    
    if len(all_product_names) < size_shopping_list:
        shopping_list = all_product_names
    else:
        shopping_list = random.sample(all_product_names, size_shopping_list)

    print(f"Shopping List: {shopping_list}")

    # --- CALCULATE PICKUP TARGETS ---
    # We identify the specific coordinate (aisle spot) for each item.
    pickup_targets = set()
    
    for item in shopping_list:
        code = agent.name_to_code.get(item)
        if code:
            shelves = agent._find_product_locations(code)
            if shelves:
                # Use the same logic as the agent: find center, then nearest aisle
                center = shelves[len(shelves)//2]
                target = agent._get_nearest_aisle(center)
                if target:
                    pickup_targets.add(target)

    # --- SOLVE & PLOT ---
    try:
        path = agent.solve_path(start_pos, shopping_list, exit_pos)
        
        if path:
            print(f"Success! Path calculated: {len(path)} steps.")
            # Pass the targets to the plotter to determine order
            plot_full_map_with_sequence(layout_grid, path, pickup_targets, 
                                        title=f"Optimal Route for {size_shopping_list} Items")
        else:
            print("Solver failed to find a path.")
            
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    run_simulation()
