import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from arvore import Floresta
from trabalho import SEMENTES
from videos import prepara, GRADE, MAPA

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
FUNDO = "#ffffff"


def capa():
    Xa, ya, _, _, gx, gy, malha = prepara()
    media = Floresta(100, None, 1, SEMENTES[-1]).treina(Xa, ya).preve(malha)
    fig = plt.figure(figsize=(6, 6), facecolor=FUNDO)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.imshow(media.reshape(GRADE, GRADE), origin="lower", extent=(gx[0], gx[-1], gy[0], gy[-1]), aspect="auto",
              cmap=MAPA, vmin=40, vmax=300)
    ax.scatter(Xa[:, 0], Xa[:, 1], c=ya, cmap=MAPA, vmin=40, vmax=300, s=26, edgecolors="#152c43", linewidths=0.6)
    ax.axis("off")
    fig.savefig(os.path.join(IMG, "capa.png"), dpi=150, facecolor=FUNDO)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    capa()
    print("capa gerada")
