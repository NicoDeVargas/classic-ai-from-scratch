import json
import os
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from arvore import FEATURES, Floresta, carrega, divide, mae
from extras import regressao_linear
from trabalho import SAIDA, SEMENTES, ARVORES, K, VERMELHO, VERDE, num, estilo

MISTURAS = [0.0, 0.25, 0.5, 0.75, 1.0]


def alvos():
    X, y = carrega()
    A = np.column_stack([np.ones(len(y)), X])
    coef = np.linalg.lstsq(A, y, rcond=None)[0]
    reta = A @ coef
    ruido = float(np.std(y - reta))
    c = {f: X[:, i] for i, f in enumerate(FEATURES)}
    alto = lambda f: c[f] > np.median(c[f])
    torto = 1.0 * (alto("bmi") & alto("s5")) + 0.7 * (alto("bp") & ~alto("s3")) + 0.5 * np.sin((c["s6"] - c["s6"].mean()) / c["s6"].std() * 2.5)
    torto = (torto - torto.mean()) / torto.std() * reta.std() + reta.mean()
    return X, reta, torto, ruido


def tarefa(args):
    mistura, semente = args
    X, reta, torto, ruido = alvos()
    y = (1 - mistura) * reta + mistura * torto + np.random.default_rng(500 + semente).normal(0, ruido, len(reta))
    treino, teste = divide(len(y), semente)
    linear = mae(y[teste], regressao_linear(X[treino], y[treino], X[teste]))
    floresta = mae(y[teste], Floresta(ARVORES, None, K, semente).treina(X[treino], y[treino]).preve(X[teste]))
    return mistura, linear, floresta


def grafico(linhas):
    fig, ax = plt.subplots(figsize=(11, 5.6))
    x = [l["mistura"] * 100 for l in linhas]
    for chave, cor, nome, larg in [("linear", VERMELHO, "regressão linear", 2.0), ("floresta", VERDE, "floresta aleatória", 3.4)]:
        m = np.array([l[chave] for l in linhas])
        d = np.array([l[chave + "_dp"] for l in linhas])
        ax.fill_between(x, m - d, m + d, color=cor, alpha=0.12, linewidth=0)
        ax.plot(x, m, "o-", color=cor, linewidth=larg, label=nome)
        outro = np.array([l["floresta" if chave == "linear" else "linear"] for l in linhas])
        for xi, mi, oi in zip(x, m, outro):
            ax.annotate(num(mi), (xi, mi), textcoords="offset points", xytext=(0, 10 if mi >= oi else -18),
                        ha="center", fontsize=11, color=cor, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["0%\n(só reta)", "25%", "50%", "75%", "100%\n(só degraus e curvas)"])
    ax.set_xlabel("quanto do alvo artificial é torto")
    ax.set_ylabel("MAE no teste")
    ax.set_title("Mesmos pacientes, alvo inventado: quanto mais torto, mais a floresta ganha", fontsize=14, fontweight="bold")
    ax.legend(loc="upper left", fontsize=12, frameon=False)
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "alvo_torto.png"), dpi=150)
    plt.close(fig)


def main():
    casos = [(m, s) for m in MISTURAS for s in SEMENTES]
    with ProcessPoolExecutor(max_workers=6) as pool:
        res = list(pool.map(tarefa, casos))
    linhas = []
    for m in MISTURAS:
        lin = np.array([r[1] for r in res if r[0] == m])
        flo = np.array([r[2] for r in res if r[0] == m])
        linhas.append({"mistura": m, "linear": float(lin.mean()), "linear_dp": float(lin.std()),
                       "floresta": float(flo.mean()), "floresta_dp": float(flo.std()),
                       "floresta_ganha": int((flo < lin).sum()), "divisoes": len(lin)})
        print("torto %3d%%  linear %s  floresta %s  floresta ganha em %d/%d" % (
            m * 100, num(lin.mean()), num(flo.mean()), (flo < lin).sum(), len(lin)))
    with open(os.path.join(SAIDA, "resumo_alvo_torto.json"), "w", encoding="utf-8") as arq:
        json.dump({"ruido": alvos()[3], "linhas": linhas}, arq, ensure_ascii=False, indent=2)
    grafico(linhas)


if __name__ == "__main__":
    main()
