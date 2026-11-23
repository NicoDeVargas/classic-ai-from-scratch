import json
import os
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from pso import EnxameParticulas, rastrigin, LIMITE
from parte1 import SEMENTE, C1, C2, VERMELHO, malha, contorno

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")


def capa(resultado, k=12):
    X, Y, Z = malha(500)
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_axes([0, 0, 1, 1])
    contorno(ax, X, Y, Z)
    ax.axis("off")
    hist = resultado["historico"]
    for i in range(len(hist[0]["x"])):
        trilha = np.array([hist[j]["x"][i] for j in range(max(0, k - 5), k + 1)])
        ax.plot(trilha[:, 0], trilha[:, 1], color="white", alpha=0.6, linewidth=1.3)
    ax.scatter(hist[k]["x"][:, 0], hist[k]["x"][:, 1], s=70, color="white", edgecolors="black",
               linewidths=1.0, zorder=3)
    ax.scatter([hist[k]["g"][0]], [hist[k]["g"][1]], s=420, marker="*", color=VERMELHO,
               edgecolors="white", linewidths=1.2, zorder=4)
    fig.savefig(os.path.join(IMG, "capa.png"), dpi=160)
    plt.close(fig)


def rastrigin_planos():
    X, Y, Z = malha(500)
    fig, ax = plt.subplots(figsize=(6, 6))
    contorno(ax, X, Y, Z)
    ax.plot([0], [0], marker="+", markersize=22, markeredgewidth=3, color=VERMELHO)
    ax.set_xlabel("x", fontsize=13)
    ax.set_ylabel("y", fontsize=13)
    ax.tick_params(labelsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, "rastrigin_contorno.png"), dpi=160)
    plt.close(fig)

    X, Y, Z = malha(300)
    fig = plt.figure(figsize=(6, 5))
    ax = fig.add_axes([-0.06, -0.04, 1.12, 1.12], projection="3d")
    ax.plot_surface(X, Y, Z, cmap="viridis", linewidth=0, antialiased=True, rstride=2, cstride=2)
    ax.view_init(elev=30, azim=-60)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    fig.savefig(os.path.join(IMG, "rastrigin_3d.png"), dpi=160, transparent=True)
    plt.close(fig)


def minimos_locais():
    xs = np.linspace(-LIMITE, LIMITE, 2049)
    X, Y = np.meshgrid(xs, xs)
    Z = rastrigin(np.stack([X, Y], axis=-1))
    centro = Z[1:-1, 1:-1]
    minimo = np.ones_like(centro, dtype=bool)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx or dy:
                minimo &= centro < Z[1 + dy:Z.shape[0] - 1 + dy, 1 + dx:Z.shape[1] - 1 + dx]
    vizinho = minimize_scalar(lambda t: rastrigin([t, 0.0]), bounds=(0.5, 1.5), method="bounded")
    return int(minimo.sum()), float(vizinho.fun)


def main():
    os.makedirs(IMG, exist_ok=True)
    resultado = EnxameParticulas(C1, C2, semente=SEMENTE).executa(historico=True)
    capa(resultado)
    rastrigin_planos()
    n, vizinho = minimos_locais()
    extras = {
        "minimos_locais": n,
        "f_minimo_vizinho": vizinho,
        "raio": {str(k): float(resultado["raio"][k]) for k in (0, 10, 30, 60, 100)},
        "f": {str(k): float(resultado["curva"][k]) for k in (0, 10, 30, 60, 100)},
        "f_max": float(rastrigin([4.52299, 4.52299])),
    }
    colapso = []
    for s in range(100):
        r = EnxameParticulas(0, 1, semente=s).executa()
        abaixo = np.flatnonzero(r["raio"] < 1e-2)
        colapso.append(int(abaixo[0]) if len(abaixo) else 100)
    extras["colapso_0_1_mediana"] = float(np.median(colapso))
    with open(os.path.join(IMG, "extras.json"), "w", encoding="utf-8") as arq:
        json.dump(extras, arq, ensure_ascii=False, indent=2)
    print(json.dumps(extras, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
