import json
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from aco import ColoniaFormigas, carrega_matriz

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "saida")
MATRIZ = os.path.join(RAIZ, "distancia_matrix.csv")

RHOS = [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
N_FORMIGAS = 20
EXECUCOES = 60
PRIMEIRA_SEMENTE = 3000

EQUILIBRIO = (1.5, 1.0)
FAMILIA = [
    (1.0, 5.0, "α=1, β=5 (enunciado): plana", "#999999"),
    (1.25, 1.0, "α=1,25, β=1: só pesa evaporar pouco", "#7fb3d5"),
    (1.5, 1.0, "α=1,5, β=1: os dois lados pesam", "#1b6ca8"),
    (2.0, 1.0, "α=2, β=1: só pesa evaporar demais", "#c0392b"),
]

_DISTANCIAS = None


def _distancias():
    global _DISTANCIAS
    if _DISTANCIAS is None:
        _DISTANCIAS = carrega_matriz(MATRIZ)
    return _DISTANCIAS


def mede(args):
    alfa, beta, rho = args
    d = np.array([ColoniaFormigas(_distancias(), n_formigas=N_FORMIGAS, evaporacao=rho,
                                  alfa=alfa, beta=beta, semente=PRIMEIRA_SEMENTE + s)
                  .executa(parar_na_convergencia=True)["melhor_distancia"]
                  for s in range(EXECUCOES)])
    return args, float(d.mean()), float(d.std(ddof=1)), float(d.std(ddof=1) / np.sqrt(len(d)))


def varre(pares):
    tarefas = [(a, b, r) for a, b in pares for r in RHOS]
    with ProcessPoolExecutor() as ex:
        return {args: (m, dp, ep) for args, m, dp, ep in ex.map(mede, tarefas)}


def grafico_equilibrio(res, destino):
    alfa, beta = EQUILIBRIO
    x = np.array(RHOS)
    media = np.array([res[(alfa, beta, r)][0] for r in RHOS])
    erro = np.array([res[(alfa, beta, r)][2] for r in RHOS])

    i = int(np.argmin(media))
    zona = [r for r, m, e in zip(RHOS, media, erro)
            if m - media[i] <= 1.96 * np.hypot(e, erro[i])]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.fill_between(x, media - 1.96 * erro, media + 1.96 * erro, color="#1b6ca8",
                    alpha=0.18, zorder=1, label="intervalo de confiança de 95%")
    ax.plot(x, media, "o-", color="#1b6ca8", linewidth=2.2, markersize=7, zorder=2,
            label="distância média (%d execuções por ponto)" % EXECUCOES)
    ax.plot(x[i], media[i], "o", color="#2e8b57", markersize=13, zorder=3)

    topo = media.max()
    ax.annotate("equilíbrio: ρ = %.2f\ndistância %.1f" % (RHOS[i], media[i]), xy=(x[i], media[i]),
                xytext=(x[i] + 0.08, media[i] + (topo - media[i]) * 0.22),
                fontsize=11, color="#2e8b57", fontweight="bold",
                arrowprops=dict(arrowstyle="->", color="#2e8b57", linewidth=1.3))
    ax.text(0.01, topo, "pouca evaporação:\no feromônio inicial\nnunca é esquecido",
            fontsize=10, color="#666666", va="top", ha="left")
    ax.text(0.5, topo, "evaporação demais:\na colônia não acumula\nmemória",
            fontsize=10, color="#666666", va="top", ha="left")

    ax.set_xlabel("Taxa de evaporação (ρ)")
    ax.set_ylabel("Distância final média")
    ax.set_title("Taxa de evaporação com α = %g e β = %g: existe um ponto ótimo" % (alfa, beta))
    ax.set_xlim(-0.03, 1.03)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)
    return RHOS[i], float(media[i]), zona


def grafico_familia(res, destino):
    fig, ax = plt.subplots(figsize=(10, 6))
    for alfa, beta, rotulo, cor in FAMILIA:
        media = [res[(alfa, beta, r)][0] for r in RHOS]
        estilo = "--" if beta == 5.0 else "-"
        ax.plot(RHOS, media, estilo, marker="o", markersize=5, linewidth=2.0, color=cor,
                label=rotulo)
    ax.set_xlabel("Taxa de evaporação (ρ)")
    ax.set_ylabel("Distância final média")
    ax.set_title("A forma da curva depende de α e β")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def main():
    os.makedirs(SAIDA, exist_ok=True)
    pares = [(a, b) for a, b, _, _ in FAMILIA]
    res = varre(pares)

    alfa, beta = EQUILIBRIO
    print("Analise complementar - existe uma taxa de evaporacao ideal?")
    print("%d formigas, Q=100, sem elitismo, %d execucoes por ponto (sementes %d a %d)"
          % (N_FORMIGAS, EXECUCOES, PRIMEIRA_SEMENTE, PRIMEIRA_SEMENTE + EXECUCOES - 1))
    print("")
    print("  %-6s" % "rho" + "".join("%16s" % rot.split(":")[0].split(" (")[0] for _, _, rot, _ in FAMILIA))
    for r in RHOS:
        print("  %-6.2f" % r + "".join("%16.1f" % res[(a, b, r)][0] for a, b, _, _ in FAMILIA))
    print("")

    rho_otimo, dist_otima, zona = grafico_equilibrio(
        res, os.path.join(SAIDA, "parte3_c_equilibrio.png"))
    grafico_familia(res, os.path.join(SAIDA, "parte3_d_familia.png"))

    ponta_esq = res[(alfa, beta, RHOS[0])][0]
    ponta_dir = res[(alfa, beta, RHOS[-1])][0]
    print("com alfa=%g e beta=%g:" % (alfa, beta))
    print("  minimo em rho=%.2f, distancia media %.1f" % (rho_otimo, dist_otima))
    print("  zona de equilibrio (sem diferenca significativa do minimo): rho de %.2f a %.2f"
          % (min(zona), max(zona)))
    print("  rho=0 fica %.1f acima do minimo; rho=1 fica %.1f acima"
          % (ponta_esq - dist_otima, ponta_dir - dist_otima))

    resumo = {
        "execucoes": EXECUCOES,
        "primeira_semente": PRIMEIRA_SEMENTE,
        "rhos": RHOS,
        "equilibrio": {"alfa": alfa, "beta": beta, "rho_otimo": rho_otimo,
                       "distancia_otima": round(dist_otima, 2),
                       "zona": [min(zona), max(zona)],
                       "ponta_esquerda": round(ponta_esq, 2),
                       "ponta_direita": round(ponta_dir, 2),
                       "excesso_esquerda": round(ponta_esq - dist_otima, 1),
                       "excesso_direita": round(ponta_dir - dist_otima, 1)},
        "familia": [{"alfa": a, "beta": b, "rotulo": rot,
                     "medias": [round(res[(a, b, r)][0], 2) for r in RHOS]}
                    for a, b, rot, _ in FAMILIA],
    }
    with open(os.path.join(SAIDA, "resumo_equilibrio.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)

    print("")
    print("arquivos gerados:")
    for nome in ["parte3_c_equilibrio.png", "parte3_d_familia.png", "resumo_equilibrio.json"]:
        print(" ", os.path.join(SAIDA, nome))


if __name__ == "__main__":
    main()
