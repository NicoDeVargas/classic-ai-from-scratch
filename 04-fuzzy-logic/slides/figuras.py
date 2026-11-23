import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from fuzzy import Controlador

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
FUNDO = "#1e2328"


def capa():
    fs, ws, z = Controlador().superficie(61, 61)
    F, W = np.meshgrid(fs, ws)
    fig = plt.figure(figsize=(6, 6), facecolor=FUNDO)
    ax = fig.add_axes([-0.12, -0.12, 1.24, 1.24], projection="3d", facecolor=FUNDO)
    ax.plot_surface(F, W, np.round(z, 6), cmap="RdYlBu_r", vmin=-10, vmax=20, linewidth=0.25,
                    edgecolor="#ffffff30", antialiased=True)
    ax.view_init(elev=27, azim=-130)
    ax.set_zlim(-10, 30)
    ax.set_axis_off()
    fig.savefig(os.path.join(IMG, "capa.png"), dpi=170, facecolor=FUNDO)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    capa()
    print("capa gerada")
