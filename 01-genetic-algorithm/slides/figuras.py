import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ag import schaffer_f6, LIMITE

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")

CAIXA = dict(boxstyle="round,pad=0.35", facecolor="#1B1035", edgecolor="none", alpha=0.88)
SETA = dict(arrowstyle="->", color="white", linewidth=1.6)


def contorno():
    eixo = np.linspace(-LIMITE, LIMITE, 600)
    X, Y = np.meshgrid(eixo, eixo)
    Z = schaffer_f6(X, Y)

    fig, ax = plt.subplots(figsize=(6.4, 6.4))
    ax.contourf(X, Y, Z, levels=40, cmap="viridis")

    ax.add_patch(plt.Circle((0, 0), np.pi, fill=False, color="white", linewidth=2.2, linestyle="--"))
    ax.plot(0, 0, marker="*", color="#FF4B4B", markersize=24, linestyle="none")

    ax.annotate("máximo global\nf = 1.000", xy=(0, 0), xytext=(-8.8, 6.6),
                color="white", fontsize=11.5, fontweight="bold", bbox=CAIXA, arrowprops=SETA)
    ax.annotate("anel de máximos locais\nr = π,  f = 0.99027", xy=(2.22, -2.22), xytext=(0.4, -8.8),
                color="white", fontsize=11.5, fontweight="bold", bbox=CAIXA, arrowprops=SETA)

    ax.set_xlim(-LIMITE, LIMITE)
    ax.set_ylim(-LIMITE, LIMITE)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Curvas de nível da Schaffer's f6")
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "f6_contorno.png"), dpi=170)
    plt.close(fig)


def corte_radial():
    r = np.linspace(0, 8, 4000)
    f = schaffer_f6(r, np.zeros_like(r))

    fig, ax = plt.subplots(figsize=(9.0, 4.6))
    ax.plot(r, f, color="#21918C", linewidth=2.2)
    ax.axhline(0.99027, color="#C9A227", linewidth=1.4, linestyle="--")
    ax.axvline(0.0985, color="#FF4B4B", linewidth=1.4, linestyle=":")

    ax.annotate("f(0) = 1.000", (0, 1.0), textcoords="offset points", xytext=(26, 6),
                fontsize=11, fontweight="bold", color="#440154")
    ax.annotate("anel r = π: 0.99027", (np.pi, 0.99027), textcoords="offset points", xytext=(14, -30),
                fontsize=11, color="#8A6D00")
    ax.annotate("só quem tem r < 0.0985\nsupera o anel", (0.0985, 0.45), textcoords="offset points",
                xytext=(48, 0), fontsize=11, color="#B03030")

    ax.set_xlabel("distância da origem  r = √(x² + y²)")
    ax.set_ylabel("fitness")
    ax.set_title("Corte radial: a bacia central é estreita e o vale ao redor é profundo")
    ax.set_ylim(0, 1.06)
    ax.set_xlim(0, 8)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "f6_corte_radial.png"), dpi=170)
    plt.close(fig)


def contorno_limpo():
    eixo = np.linspace(-LIMITE, LIMITE, 600)
    X, Y = np.meshgrid(eixo, eixo)
    Z = schaffer_f6(X, Y)

    fig = plt.figure(figsize=(5.0, 5.0))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.contourf(X, Y, Z, levels=40, cmap="viridis")
    ax.set_xlim(-LIMITE, LIMITE)
    ax.set_ylim(-LIMITE, LIMITE)
    ax.axis("off")
    fig.savefig(os.path.join(IMG, "f6_contorno_limpo.png"), dpi=170)
    plt.close(fig)


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    contorno()
    contorno_limpo()
    corte_radial()
    print("figuras geradas em", IMG)
