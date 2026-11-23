import json
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from arvore import FEATURES, DESCRICAO, ArvoreRegressao, Floresta, carrega, divide, mae
from trabalho import SAIDA, SEMENTES, ARVORES, K, AZUL, VERMELHO, CINZA, VERDE, AMBAR, num, estilo

SEMENTES_EXTRA = list(range(1000, 1030))
KS = [1, 3, 5, 10]
BOOST_ARVORES = 100
BOOST_PROFUNDIDADE = 2
BOOST_TAXA = 0.1


def rotulo(f):
    return "%s (%s)" % (f, DESCRICAO[f])


def boosting(X, y, Xt):
    base = y.mean()
    previsto, previsto_t = np.full(len(y), base), np.full(len(Xt), base)
    for _ in range(BOOST_ARVORES):
        arvore = ArvoreRegressao(BOOST_PROFUNDIDADE).treina(X, y - previsto)
        previsto += BOOST_TAXA * arvore.preve(X)
        previsto_t += BOOST_TAXA * arvore.preve(Xt)
    return previsto_t


def regressao_linear(X, y, Xt):
    A = np.column_stack([np.ones(len(X)), X])
    coef = np.linalg.lstsq(A, y, rcond=None)[0]
    return np.column_stack([np.ones(len(Xt)), Xt]) @ coef


def tarefa(args):
    nome, semente = args
    X, y = carrega()
    treino, teste = divide(len(y), semente)
    Xa, ya, Xt = X[treino], y[treino], X[teste]
    if nome == "media":
        previsto = np.full(len(teste), ya.mean())
    elif nome == "arvore":
        previsto = ArvoreRegressao().treina(Xa, ya).preve(Xt)
    elif nome == "arvore3":
        previsto = ArvoreRegressao(3).treina(Xa, ya).preve(Xt)
    elif nome == "boosting":
        previsto = boosting(Xa, ya, Xt)
    elif nome == "linear":
        previsto = regressao_linear(Xa, ya, Xt)
    else:
        previsto = Floresta(ARVORES, None, int(nome[1:]), semente).treina(Xa, ya).preve(Xt)
    return args, mae(y[teste], previsto)


def fora_da_sacola(X, y):
    linhas = []
    for s in SEMENTES:
        treino, teste = divide(len(y), s)
        floresta = Floresta(ARVORES, None, K, s).treina(X[treino], y[treino])
        cada = floresta.preve_cada(X[treino])
        fora = np.array([~np.isin(np.arange(len(treino)), a) for a in floresta.amostras])
        previsto = (cada * fora).sum(axis=0) / fora.sum(axis=0)
        linhas.append({"fora": mae(y[treino], previsto), "teste": mae(y[teste], floresta.preve(X[teste])),
                       "fracao_fora": float(fora.mean())})
    return linhas


def grafico_corte_raiz(X, y):
    fig, eixos = plt.subplots(2, 5, figsize=(16, 6.8))
    total = y.var()
    melhores = []
    for i, (ax, f) in enumerate(zip(eixos.ravel(), FEATURES)):
        valores = np.unique(X[:, i])
        cortes = (valores[1:] + valores[:-1]) / 2
        depois = []
        for c in cortes:
            e = X[:, i] <= c
            depois.append((e.sum() * y[e].var() + (~e).sum() * y[~e].var()) / len(y))
        depois = np.array(depois)
        k = int(depois.argmin())
        melhores.append({"feature": f, "limiar": float(cortes[k]), "variancia": float(depois[k]),
                         "reducao": float(total - depois[k])})
        ax.plot(cortes, total - depois, color=AZUL, linewidth=2)
        ax.fill_between(cortes, total - depois, color=AZUL, alpha=0.15)
        ax.axvline(cortes[k], color="black", linewidth=1.4, linestyle="--")
        ax.plot(cortes[k], total - depois[k], "o", color=VERMELHO, markersize=9, markeredgecolor="black", zorder=5)
        ax.set_title(rotulo(f), fontsize=11.5, fontweight="bold")
        ax.set_xlabel("melhor corte: %s ≤ %s\nredução da variância: %s" % (f, num(cortes[k], 2 if f in ("s4", "s5") else 1),
                                                                           num(total - depois[k], 0)), fontsize=10)
        ax.tick_params(labelsize=9)
        estilo(ax)
    teto = max(m["reducao"] for m in melhores) * 1.12
    vencedor = int(np.argmax([m["reducao"] for m in melhores]))
    for i, ax in enumerate(eixos.ravel()):
        ax.set_ylim(0, teto)
        if i == vencedor:
            for lado in ("top", "right", "left", "bottom"):
                ax.spines[lado].set_visible(True)
                ax.spines[lado].set_color(VERDE)
                ax.spines[lado].set_linewidth(3.5)
            ax.xaxis.label.set_color(VERDE)
            ax.xaxis.label.set_fontweight("bold")
    eixos[0, 0].set_ylabel("redução da variância")
    eixos[1, 0].set_ylabel("redução da variância")
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "corte_raiz.png"), dpi=150)
    plt.close(fig)
    return {"variancia_inicial": float(total), "cortes": melhores, "vencedor": FEATURES[vencedor]}


def desenha_arvore(arvore, profundidade):
    posicao, contador = {}, [0]

    def coloca(no):
        if arvore.feature[no] < 0:
            posicao[no] = (contador[0], -arvore.nivel[no])
            contador[0] += 1
        else:
            coloca(arvore.esq[no])
            coloca(arvore.dir[no])
            posicao[no] = ((posicao[arvore.esq[no]][0] + posicao[arvore.dir[no]][0]) / 2, -arvore.nivel[no])

    coloca(0)
    fig, ax = plt.subplots(figsize=(15, 6.6))
    for no, (x, yy) in posicao.items():
        folha = arvore.feature[no] < 0
        if not folha:
            for filho, texto in ((arvore.esq[no], "sim"), (arvore.dir[no], "não")):
                xf, yf = posicao[filho]
                ax.plot([x, xf], [yy - 0.2, yf + 0.2], color="#555555", linewidth=1.5, zorder=1)
                ax.text((x + xf) / 2, (yy + yf) / 2, texto, fontsize=10, color="#555555", ha="center", va="center",
                        bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5})
            f = FEATURES[arvore.feature[no]]
            texto = "%s ≤ %s?\n%d pacientes · média %s" % (f, num(arvore.limiar[no], 2 if f in ("s4", "s5") else 1),
                                                           arvore.n[no], num(arvore.valor[no], 0))
            cor, borda = "#ffffff", VERMELHO
        else:
            texto = "prevê %s\n%d pacientes" % (num(arvore.valor[no], 0), arvore.n[no])
            cor, borda = "#dff1ee", VERDE
        ax.text(x, yy, texto, ha="center", va="center", fontsize=10.5 if folha else 11, fontweight="bold" if folha else "normal",
                bbox={"facecolor": cor, "edgecolor": borda, "boxstyle": "round,pad=0.45", "linewidth": 1.8}, zorder=3)
    ax.set_xlim(-0.6, contador[0] - 0.4)
    ax.set_ylim(-profundidade - 0.45, 0.45)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "arvore_desenho.png"), dpi=150)
    plt.close(fig)


def grafico_fora(linhas):
    fig, ax = plt.subplots(figsize=(8.6, 5))
    x = np.arange(1, 11)
    ax.bar(x - 0.2, [l["fora"] for l in linhas], 0.4, color=AMBAR, label="estimativa com os pacientes fora da sacola")
    ax.bar(x + 0.2, [l["teste"] for l in linhas], 0.4, color=VERDE, label="MAE no conjunto de teste")
    ax.set_xticks(x)
    ax.set_ylim(30, 60)
    ax.set_xlabel("divisão treino/teste")
    ax.set_ylabel("MAE")
    ax.legend(fontsize=10.5, loc="upper center")
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "extra_fora_da_sacola.png"), dpi=160)
    plt.close(fig)


def grafico_k(ks):
    fig, ax = plt.subplots(figsize=(8.6, 5))
    medias = [k["media"] for k in ks]
    ax.bar(range(len(ks)), medias, color=[VERDE if k["k"] == K else CINZA for k in ks], width=0.6)
    for i, v in enumerate(medias):
        ax.text(i, v + 0.15, num(v), ha="center", fontsize=12, fontweight="bold")
    ax.set_xticks(range(len(ks)), ["%d de 10%s" % (k["k"], "\n(só bagging)" if k["k"] == 10 else ("\n(a nossa floresta)" if k["k"] == K else "")) for k in ks], fontsize=11.5)
    ax.set_ylim(min(medias) - 2, max(medias) + 1.2)
    ax.set_xlabel("features sorteadas em cada nó")
    ax.set_ylabel("MAE médio de teste em %d divisões" % len(SEMENTES_EXTRA))
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "extra_k.png"), dpi=160)
    plt.close(fig)


def grafico_modelos(modelos):
    fig, ax = plt.subplots(figsize=(10.5, 5))
    medias = [m["media"] for m in modelos]
    cores = [CINZA, VERMELHO, VERMELHO, AMBAR, VERDE, AMBAR, AZUL]
    ax.barh(range(len(modelos)), medias, color=cores)
    for i, v in enumerate(medias):
        ax.text(v + 0.4, i, num(v), va="center", fontsize=12, fontweight="bold")
    ax.set_yticks(range(len(modelos)), [m["nome"] for m in modelos], fontsize=11.5)
    ax.invert_yaxis()
    ax.set_xlim(35, 72)
    ax.set_xlabel("MAE médio de teste em %d divisões (quanto menor, melhor)" % len(SEMENTES_EXTRA))
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "extra_modelos.png"), dpi=160)
    plt.close(fig)


def grafico_importancia(imp):
    ordem = sorted(imp, key=imp.get, reverse=True)
    fig, ax = plt.subplots(figsize=(8.6, 5))
    ax.barh(range(10), [imp[f] * 100 for f in ordem], color=[VERDE] * 3 + [CINZA] * 7)
    for i, f in enumerate(ordem):
        ax.text(imp[f] * 100 + 0.4, i, num(imp[f] * 100, 0) + "%", va="center", fontsize=11)
    ax.set_yticks(range(10), [rotulo(f) for f in ordem], fontsize=11)
    ax.invert_yaxis()
    ax.set_xlabel("parte da redução de variância da floresta que vem de cada feature (%)")
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "extra_importancia.png"), dpi=160)
    plt.close(fig)
    return ordem


def main():
    X, y = carrega()
    treino, teste = divide(len(y), SEMENTES[-1])
    raiz = grafico_corte_raiz(X[treino], y[treino])
    arvore3 = ArvoreRegressao(3).treina(X[treino], y[treino])
    desenha_arvore(arvore3, 3)
    print("Como a raiz é escolhida (última divisão): variância inicial %.0f" % raiz["variancia_inicial"])
    for c in sorted(raiz["cortes"], key=lambda c: -c["reducao"]):
        print("  %-4s melhor corte em %8.3f   redução da variância %7.1f" % (c["feature"], c["limiar"], c["reducao"]))

    print("\nExtra: os pacientes fora da sacola")
    fora = fora_da_sacola(X, y)
    for i, l in enumerate(fora):
        print("  divisão %2d: estimativa %.2f   teste %.2f" % (i + 1, l["fora"], l["teste"]))
    print("  média: estimativa %.2f   teste %.2f   fração de pacientes fora de cada árvore %.3f"
          % (np.mean([l["fora"] for l in fora]), np.mean([l["teste"] for l in fora]), np.mean([l["fracao_fora"] for l in fora])))
    grafico_fora(fora)

    nomes = ["media", "arvore", "arvore3", "boosting", "linear"] + ["k%d" % k for k in KS]
    with ProcessPoolExecutor(max_workers=6) as ex:
        res = dict(ex.map(tarefa, [(n, s) for n in nomes for s in SEMENTES_EXTRA], chunksize=2))
    media = {n: float(np.mean([res[(n, s)] for s in SEMENTES_EXTRA])) for n in nomes}
    ks = [{"k": k, "media": media["k%d" % k]} for k in KS]
    print("\nExtra: quantas features sortear em cada nó (%d divisões)" % len(SEMENTES_EXTRA))
    for k in ks:
        print("  %2d features: MAE %.2f" % (k["k"], k["media"]))
    grafico_k(ks)

    modelos = [
        {"nome": "prever sempre a média", "media": media["media"]},
        {"nome": "uma árvore sem limite", "media": media["arvore"]},
        {"nome": "uma árvore de profundidade 3", "media": media["arvore3"]},
        {"nome": "bagging (100 árvores, todas as features)", "media": media["k10"]},
        {"nome": "floresta aleatória (100 árvores, 3 features)", "media": media["k3"]},
        {"nome": "boosting (100 árvores de profundidade 2)", "media": media["boosting"]},
        {"nome": "regressão linear", "media": media["linear"]},
    ]
    print("\nExtra: comparação de modelos (%d divisões)" % len(SEMENTES_EXTRA))
    for m in modelos:
        print("  %-46s MAE %.2f" % (m["nome"], m["media"]))
    grafico_modelos(modelos)

    floresta = Floresta(ARVORES, None, K, SEMENTES[-1]).treina(X[treino], y[treino])
    ganho = np.zeros(10)
    for a in floresta.arvores:
        internos = a.feature >= 0
        np.add.at(ganho, a.feature[internos], a.ganho[internos])
    imp = dict(zip(FEATURES, (ganho / ganho.sum()).tolist()))
    ordem = grafico_importancia(imp)
    print("\nExtra: importância das features na floresta")
    for f in ordem:
        print("  %-4s %.1f%%" % (f, imp[f] * 100))

    resumo = {"divisoes": len(SEMENTES_EXTRA), "raiz": raiz, "fora": fora,
              "fora_media": float(np.mean([l["fora"] for l in fora])), "fora_teste": float(np.mean([l["teste"] for l in fora])),
              "fracao_fora": float(np.mean([l["fracao_fora"] for l in fora])), "ks": ks, "modelos": modelos,
              "importancia": imp, "importancia_ordem": ordem,
              "boosting": {"arvores": BOOST_ARVORES, "profundidade": BOOST_PROFUNDIDADE, "taxa": BOOST_TAXA},
              "arvore3": {"folhas": arvore3.folhas(), "raiz": FEATURES[arvore3.feature[0]], "limiar": float(arvore3.limiar[0])}}
    with open(os.path.join(SAIDA, "resumo_extras.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
