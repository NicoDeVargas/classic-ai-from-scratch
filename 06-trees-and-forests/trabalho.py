import json
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from arvore import FEATURES, ArvoreRegressao, Floresta, carrega, divide, mae

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "saida")
SEMENTES = list(range(10))
PROFUNDIDADES = list(range(1, 11))
QUANTIDADES = [5, 10, 20, 40, 80]
ARVORES = 100
K = 3
AZUL = "#4f7396"
VERMELHO = "#152c43"
CINZA = "#a9b6c2"
VERDE = "#3f9e92"
AMBAR = "#9fd3cb"


def num(x, casas=1):
    return ("%.*f" % (casas, x)).replace(".", ",")


def estilo(ax):
    ax.grid(alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


def tarefa(args):
    tipo, arvores, profundidade, semente = args
    X, y = carrega()
    treino, teste = divide(len(y), semente)
    if tipo == "arvore":
        modelo = ArvoreRegressao(profundidade).treina(X[treino], y[treino])
    else:
        modelo = Floresta(arvores, profundidade, K, semente).treina(X[treino], y[treino])
    return args, (mae(y[treino], modelo.preve(X[treino])), mae(y[teste], modelo.preve(X[teste])))


def resumo(res, tipo, arvores, profundidade):
    valores = np.array([res[(tipo, arvores, profundidade, s)] for s in SEMENTES])
    return {"treino": valores[:, 0].tolist(), "teste": valores[:, 1].tolist(),
            "media_treino": float(valores[:, 0].mean()), "desvio_treino": float(valores[:, 0].std()),
            "media_teste": float(valores[:, 1].mean()), "desvio_teste": float(valores[:, 1].std())}


def grafico_divisoes(r, arquivo, cor):
    fig, ax = plt.subplots(figsize=(11, 4.8))
    x = np.arange(1, 11)
    ax.bar(x - 0.2, r["treino"], 0.4, color=CINZA, label="treino")
    ax.bar(x + 0.2, r["teste"], 0.4, color=cor, label="teste")
    for i in range(10):
        ax.text(x[i] - 0.2, r["treino"][i] + 1, num(r["treino"][i], 0), ha="center", fontsize=9.5)
        ax.text(x[i] + 0.2, r["teste"][i] + 1, num(r["teste"][i], 0), ha="center", fontsize=9.5)
    ax.axhline(r["media_teste"], color=cor, linestyle="--", linewidth=1.5)
    ax.text(10.75, r["media_teste"] + 1.5, "média do teste: %s" % num(r["media_teste"]), ha="right", fontsize=11, color=cor)
    ax.set_xticks(x)
    ax.set_ylim(0, 80)
    ax.set_xlabel("divisão treino/teste")
    ax.set_ylabel("MAE")
    ax.legend(loc="upper left", fontsize=11, ncol=2)
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, arquivo), dpi=160)
    plt.close(fig)


def grafico_profundidade(arvore, floresta):
    fig, eixos = plt.subplots(1, 2, figsize=(14, 5.2), sharey=True)
    for ax, serie, titulo in ((eixos[0], arvore, "uma árvore"), (eixos[1], floresta, "floresta de %d árvores" % ARVORES)):
        for chave, cor, rotulo in (("treino", CINZA, "treino"), ("teste", VERMELHO, "teste")):
            media = np.array([s["media_" + chave] for s in serie])
            desvio = np.array([s["desvio_" + chave] for s in serie])
            ax.plot(PROFUNDIDADES, media, "o-", color=cor, linewidth=2.2, label=rotulo)
            ax.fill_between(PROFUNDIDADES, media - desvio, media + desvio, color=cor, alpha=0.18)
        melhor = int(np.argmin([s["media_teste"] for s in serie]))
        ax.plot(PROFUNDIDADES[melhor], serie[melhor]["media_teste"], "o", color=VERDE, markersize=15, zorder=5)
        ax.annotate("melhor: profundidade %d\nMAE %s" % (PROFUNDIDADES[melhor], num(serie[melhor]["media_teste"])),
                    xy=(PROFUNDIDADES[melhor], serie[melhor]["media_teste"]), xytext=(0.36, 0.05), textcoords="axes fraction",
                    fontsize=11, color=VERDE, arrowprops={"arrowstyle": "->", "color": VERDE})
        ax.set_title(titulo, fontsize=13, fontweight="bold")
        ax.set_xticks(PROFUNDIDADES)
        ax.set_xlabel("profundidade máxima")
        ax.legend(loc="lower left", fontsize=11)
        estilo(ax)
    eixos[0].set_ylabel("MAE (média e desvio padrão em 10 divisões)")
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte3.png"), dpi=160)
    plt.close(fig)


def grafico_quantidade(serie, profundidade):
    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(len(QUANTIDADES))
    for chave, cor, rotulo in (("treino", CINZA, "treino"), ("teste", VERMELHO, "teste")):
        media = np.array([s["media_" + chave] for s in serie])
        desvio = np.array([s["desvio_" + chave] for s in serie])
        ax.errorbar(x, media, yerr=desvio, fmt="o-", color=cor, linewidth=2.2, capsize=5, label=rotulo)
        for i, v in enumerate(media):
            ax.text(x[i] + 0.08, v + 0.6, num(v), fontsize=10.5, color=cor)
    ax.set_xticks(x, [str(q) for q in QUANTIDADES])
    ax.set_xlabel("número de árvores na floresta (profundidade %d)" % profundidade)
    ax.set_ylabel("MAE (média e desvio padrão em 10 divisões)")
    ax.legend(fontsize=11, loc="center right")
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte4.png"), dpi=160)
    plt.close(fig)


def exemplos(modelo, X, y, teste):
    previsto = modelo.preve(X[teste[:5]])
    return [{"indice": int(i), "real": float(r), "previsto": float(p)} for i, r, p in zip(teste[:5], y[teste[:5]], previsto)]


def imprime(titulo, r, ex):
    print(titulo)
    for i in range(10):
        print("  divisão %2d: MAE treino %6.2f   MAE teste %6.2f" % (i + 1, r["treino"][i], r["teste"][i]))
    print("  MAE de teste: média %.2f   desvio padrão %.2f" % (r["media_teste"], r["desvio_teste"]))
    print("  MAE de treino: média %.2f   desvio padrão %.2f" % (r["media_treino"], r["desvio_treino"]))
    print("  5 exemplos do último modelo (real -> previsto)")
    for e in ex:
        print("    paciente %3d: real %5.1f   previsto %5.1f" % (e["indice"], e["real"], e["previsto"]))


def main():
    os.makedirs(SAIDA, exist_ok=True)
    X, y = carrega()
    tarefas = [("arvore", 1, None, s) for s in SEMENTES] + [("floresta", ARVORES, None, s) for s in SEMENTES]
    tarefas += [("arvore", 1, p, s) for p in PROFUNDIDADES for s in SEMENTES]
    tarefas += [("floresta", ARVORES, p, s) for p in PROFUNDIDADES for s in SEMENTES]
    with ProcessPoolExecutor(max_workers=6) as ex:
        res = dict(ex.map(tarefa, tarefas, chunksize=2))
        p1 = resumo(res, "arvore", 1, None)
        p2 = resumo(res, "floresta", ARVORES, None)
        p3_arvore = [resumo(res, "arvore", 1, p) for p in PROFUNDIDADES]
        p3_floresta = [resumo(res, "floresta", ARVORES, p) for p in PROFUNDIDADES]
        melhor_arvore = PROFUNDIDADES[int(np.argmin([s["media_teste"] for s in p3_arvore]))]
        melhor_floresta = PROFUNDIDADES[int(np.argmin([s["media_teste"] for s in p3_floresta]))]
        res.update(ex.map(tarefa, [("floresta", q, melhor_floresta, s) for q in QUANTIDADES for s in SEMENTES], chunksize=2))
    p4 = [resumo(res, "floresta", q, melhor_floresta) for q in QUANTIDADES]

    treino, teste = divide(len(y), SEMENTES[-1])
    ex1 = exemplos(ArvoreRegressao().treina(X[treino], y[treino]), X, y, teste)
    ex2 = exemplos(Floresta(ARVORES, None, K, SEMENTES[-1]).treina(X[treino], y[treino]), X, y, teste)

    imprime("Parte 1: árvore de regressão (sem limite de profundidade)", p1, ex1)
    imprime("\nParte 2: floresta aleatória (%d árvores, %d features sorteadas por nó)" % (ARVORES, K), p2, ex2)
    print("\nParte 3: efeito da profundidade (média ± desvio do MAE em 10 divisões)")
    print("  prof.   árvore treino    árvore teste     floresta treino  floresta teste")
    for p, a, f in zip(PROFUNDIDADES, p3_arvore, p3_floresta):
        print("  %3d     %5.2f ± %4.2f     %5.2f ± %4.2f     %5.2f ± %4.2f     %5.2f ± %4.2f" % (
            p, a["media_treino"], a["desvio_treino"], a["media_teste"], a["desvio_teste"],
            f["media_treino"], f["desvio_treino"], f["media_teste"], f["desvio_teste"]))
    print("  melhor profundidade: árvore %d, floresta %d" % (melhor_arvore, melhor_floresta))
    print("\nParte 4: número de árvores (floresta com profundidade %d)" % melhor_floresta)
    for q, s in zip(QUANTIDADES, p4):
        print("  %3d árvores: teste %5.2f ± %4.2f   treino %5.2f ± %4.2f" % (
            q, s["media_teste"], s["desvio_teste"], s["media_treino"], s["desvio_treino"]))

    grafico_divisoes(p1, "parte1.png", VERMELHO)
    grafico_divisoes(p2, "parte2.png", VERDE)
    grafico_profundidade(p3_arvore, p3_floresta)
    grafico_quantidade(p4, melhor_floresta)

    dados = {"n": len(y), "n_treino": len(treino), "n_teste": len(teste), "arvores": ARVORES, "k": K,
             "media_target": float(y.mean()), "min_target": float(y.min()), "max_target": float(y.max()),
             "parte1": p1, "exemplos1": ex1, "parte2": p2, "exemplos2": ex2,
             "profundidades": PROFUNDIDADES, "parte3_arvore": p3_arvore, "parte3_floresta": p3_floresta,
             "melhor_arvore": melhor_arvore, "melhor_floresta": melhor_floresta,
             "quantidades": QUANTIDADES, "parte4": p4}
    with open(os.path.join(SAIDA, "resumo_trabalho.json"), "w", encoding="utf-8") as arq:
        json.dump(dados, arq, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
