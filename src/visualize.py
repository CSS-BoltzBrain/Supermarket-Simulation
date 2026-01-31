from simulation import Simulation
import sys


if __name__ == "__main__":
    simulation = Simulation("configs/surround.yaml")
    simulation.load_checkpoints(sys.argv[1])
    anim = sys.argv[1].replace(".npy", ".mp4")
    simulation.save_fig(anim)
