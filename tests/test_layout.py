import numpy as np
import os
from src.layout import load_layout_yaml, load_products
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def plot_layout(layout_array: np.ndarray) -> None:
    h, w = layout_array.shape
    numeric_grid = np.zeros((h, w), dtype=int)

    for i in range(h):
        for j in range(w):
            cell = layout_array[i, j]
            if cell == '0':
                numeric_grid[i, j] = 0
            elif cell == '#':
                numeric_grid[i, j] = 1
            elif cell == 'I':
                numeric_grid[i, j] = 2
            elif cell == 'E':
                numeric_grid[i, j] = 3
            elif cell.startswith('P'):
                numeric_grid[i, j] = 4

    cmap = ListedColormap([
        'white',        # 0 empty
        'saddlebrown',  # 1 wall
        'green',        # 2 entrance
        'red',          # 3 exit
        'gold'          # 4 shelf
    ])

    fig, ax = plt.subplots(figsize=(w / 4, h / 4))
    ax.imshow(numeric_grid, origin='lower', cmap=cmap)

    ax.set_xticks(np.arange(-0.5, w, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, h, 1), minor=True)
    ax.grid(which='minor', color='gray', linewidth=0.3)
    ax.tick_params(which='both', bottom=False, left=False,
                   labelbottom=False, labelleft=False)
    for i in range(h):
        for j in range(w):
            cell = layout_array[i, j]
            if cell.startswith("P"):
                ax.text(
                    j, i, cell,
                    ha='center', va='center',
                    fontsize=6,
                    color='black'
                )
    plt.tight_layout()
    plt.show()

filename = os.path.join("configs", "supermarket1.yaml")
layout_array = load_layout_yaml(filename)
products_list, products_by_code, products_by_category= load_products(filename)
# print(products_by_category)
# print(products_by_code)
# print(products_list)
# np.set_printoptions(threshold=np.inf)
print(layout_array)
plot_layout(layout_array)