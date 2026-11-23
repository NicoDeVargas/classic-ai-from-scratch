import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
FUNDO = "#16242f"


def capa():
    x = np.linspace(-4, 6, 400)
    fig, ax = plt.subplots(figsize=(8, 6), facecolor=FUNDO)
    ax.set_facecolor(FUNDO)
    for media, desvio, cor in ((0, 1.1, "#4f8fdc"), (2.3, 1.3, "#e0655f")):
        y = np.exp(-(x - media) ** 2 / (2 * desvio ** 2)) / desvio
        ax.plot(x, y, color=cor, linewidth=4)
        ax.fill_between(x, y, color=cor, alpha=0.22)
        ax.plot(1.7, np.exp(-(1.7 - media) ** 2 / (2 * desvio ** 2)) / desvio, "o", color=cor, markersize=16,
                markeredgecolor="white", markeredgewidth=2, zorder=5)
    ax.axvline(1.7, color="white", linewidth=2.2, linestyle="--")
    ax.axis("off")
    fig.savefig(os.path.join(IMG, "capa.png"), dpi=150, facecolor=FUNDO)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    capa()
    print("capa gerada")
