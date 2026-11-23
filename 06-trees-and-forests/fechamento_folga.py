import json
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from arvore import FEATURES, ArvoreRegressao, carrega, divide, mae
from fechamento import (AG_POPULACAO, AG_GERACOES, AG_CRUZAMENTO, AG_MUTACAO, AG_ELITE, PSO_PARTICULAS,
                        PSO_ITERACOES, PSO_C1, PSO_C2, PSO_W, PSO_FRACAO_VMAX, naive_bayes)
from trabalho import SAIDA, SEMENTES, AZUL, VERMELHO, CINZA, VERDE, AMBAR, num, estilo

SEMENTES_EXTRA = list(range(1000, 1100))
PARTES = 5
LIMITES_ARVORE = np.array([[1, 12], [2, 60]], dtype=float)


def partes(n, rng):
    ordem = rng.permutation(n)
    return [ordem[i::PARTES] for i in range(PARTES)]


def validacao_arvore(X, y, blocos, profundidade, minimo):
    erros = []
    for bloco in blocos:
        resto = np.setdiff1d(np.arange(len(y)), bloco)
        arvore = ArvoreRegressao(profundidade, minimo).treina(X[resto], y[resto])
        erros.append(mae(y[bloco], arvore.preve(X[bloco])))
    return float(np.mean(erros))


def validacao_bayes(X, classe, blocos, mascara):
    colunas = np.flatnonzero(mascara)
    if len(colunas) == 0:
        return 0.0
    acertos = []
    for bloco in blocos:
        resto = np.setdiff1d(np.arange(len(classe)), bloco)
        acertos.append((naive_bayes(X[resto][:, colunas], classe[resto], X[bloco][:, colunas]) == classe[bloco]).mean())
    return float(np.mean(acertos))


def enxame_arvore(X, y, blocos, rng):
    memoria = {}

    def avalia(pontos):
        saida = []
        for p in pontos:
            chave = (int(round(p[0])), int(round(p[1])))
            if chave not in memoria:
                memoria[chave] = validacao_arvore(X, y, blocos, *chave)
            saida.append(memoria[chave])
        return np.array(saida)

    vmax = PSO_FRACAO_VMAX * (LIMITES_ARVORE[:, 1] - LIMITES_ARVORE[:, 0])
    x = rng.uniform(LIMITES_ARVORE[:, 0], LIMITES_ARVORE[:, 1], (PSO_PARTICULAS, 2))
    x[0] = [LIMITES_ARVORE[0, 1], 2]
    v = rng.uniform(-vmax, vmax, (PSO_PARTICULAS, 2))
    f = avalia(x)
    p, fp = x.copy(), f.copy()
    g = int(np.argmin(fp))
    curva = [float(fp[g])]
    for it in range(PSO_ITERACOES):
        w = PSO_W[0] - it * (PSO_W[0] - PSO_W[1]) / PSO_ITERACOES
        r1, r2 = rng.random((PSO_PARTICULAS, 2)), rng.random((PSO_PARTICULAS, 2))
        v = np.clip(w * v + PSO_C1 * r1 * (p - x) + PSO_C2 * r2 * (p[g] - x), -vmax, vmax)
        x = np.clip(x + v, LIMITES_ARVORE[:, 0], LIMITES_ARVORE[:, 1])
        f = avalia(x)
        melhorou = f < fp
        p[melhorou], fp[melhorou] = x[melhorou], f[melhorou]
        g = int(np.argmin(fp))
        curva.append(float(fp[g]))
    return [int(round(c)) for c in p[g]], curva


def genetico_bayes(X, classe, blocos, rng):
    memoria = {}

    def aptidao(m):
        chave = tuple(m)
        if chave not in memoria:
            memoria[chave] = validacao_bayes(X, classe, blocos, m)
        return memoria[chave]

    populacao = rng.integers(0, 2, (AG_POPULACAO, len(FEATURES)))
    populacao[0] = 1
    curva = []
    for geracao in range(AG_GERACOES + 1):
        notas = np.array([aptidao(m) for m in populacao])
        curva.append(float(notas.max()))
        if geracao == AG_GERACOES:
            break
        ordem = np.argsort(notas)[::-1]
        peso = notas - notas.min() + 1e-6
        pais = populacao[rng.choice(AG_POPULACAO, AG_POPULACAO, p=peso / peso.sum())]
        filhos = pais.copy()
        for i in range(0, AG_POPULACAO - 1, 2):
            if rng.random() < AG_CRUZAMENTO:
                a, b = np.sort(rng.integers(1, len(FEATURES), 2))
                filhos[i, a:b], filhos[i + 1, a:b] = pais[i + 1, a:b], pais[i, a:b]
        muta = rng.random(filhos.shape) < AG_MUTACAO
        filhos[muta] = 1 - filhos[muta]
        filhos[:AG_ELITE] = populacao[ordem[:AG_ELITE]]
        populacao = filhos
    return populacao[int(np.argmax(notas))], curva


def tarefa(semente):
    X, y = carrega()
    classe = (y > y.mean()).astype(int)
    treino, teste = divide(len(y), semente)
    Xa, ya, ca, Xt, yt, ct = X[treino], y[treino], classe[treino], X[teste], y[teste], classe[teste]
    rng = np.random.default_rng(2000 + semente)
    blocos = partes(len(treino), rng)

    params, curva_pso = enxame_arvore(Xa, ya, blocos, rng)
    mascara, curva_ag = genetico_bayes(Xa, ca, blocos, rng)
    colunas = np.flatnonzero(mascara)
    return {
        "semente": semente, "params": params, "mascara": mascara.tolist(), "curva_pso": curva_pso, "curva_ag": curva_ag,
        "arvore_livre": mae(yt, ArvoreRegressao().treina(Xa, ya).preve(Xt)),
        "arvore_pso": mae(yt, ArvoreRegressao(*params).treina(Xa, ya).preve(Xt)),
        "arvore_3": mae(yt, ArvoreRegressao(3).treina(Xa, ya).preve(Xt)),
        "bayes_todas": float((naive_bayes(Xa, ca, Xt) == ct).mean()),
        "bayes_ag": float((naive_bayes(Xa[:, colunas], ca, Xt[:, colunas]) == ct).mean()),
    }


def resume(rodadas):
    def estat(chave):
        v = np.array([r[chave] for r in rodadas])
        return {"media": float(v.mean()), "desvio": float(v.std())}

    return {
        "arvore_livre": estat("arvore_livre"), "arvore_pso": estat("arvore_pso"), "arvore_3": estat("arvore_3"),
        "bayes_todas": estat("bayes_todas"), "bayes_ag": estat("bayes_ag"),
        "pso_ganhou": int(sum(r["arvore_pso"] < r["arvore_livre"] for r in rodadas)),
        "ag_ganhou": int(sum(r["bayes_ag"] > r["bayes_todas"] for r in rodadas)),
        "ag_empatou": int(sum(r["bayes_ag"] == r["bayes_todas"] for r in rodadas)),
        "profundidades": [r["params"][0] for r in rodadas], "minimos": [r["params"][1] for r in rodadas],
        "n_medidas": float(np.mean([sum(r["mascara"]) for r in rodadas])),
        "vezes_escolhida": dict(zip(FEATURES, np.sum([r["mascara"] for r in rodadas], axis=0).tolist())),
        "curva_pso": np.mean([r["curva_pso"] for r in rodadas], axis=0).tolist(),
        "curva_ag": np.mean([r["curva_ag"] for r in rodadas], axis=0).tolist(),
    }


def imprime(titulo, r, n):
    print(titulo)
    print("  PSO na árvore: sem limite %.2f -> ajustada %.2f (profundidade 3 fixa: %.2f); melhor em %d de %d divisões"
          % (r["arvore_livre"]["media"], r["arvore_pso"]["media"], r["arvore_3"]["media"], r["pso_ganhou"], n))
    print("    profundidade escolhida: mediana %d (de %d a %d); mínimo para dividir: mediana %d"
          % (np.median(r["profundidades"]), min(r["profundidades"]), max(r["profundidades"]), np.median(r["minimos"])))
    print("  AG no Naive Bayes: 10 medidas %.1f%% -> escolhidas %.1f%%; melhor em %d, igual em %d, de %d divisões; média de %.1f medidas"
          % (r["bayes_todas"]["media"] * 100, r["bayes_ag"]["media"] * 100, r["ag_ganhou"], r["ag_empatou"], n, r["n_medidas"]))
    print("    vezes que cada medida foi escolhida:", r["vezes_escolhida"])


def grafico(resumo, floresta):
    r, e = resumo["principal"], resumo["extra"]
    fig, eixos = plt.subplots(1, 3, figsize=(17, 5.4), gridspec_kw={"width_ratios": [1, 1.1, 1.15]})

    ax = eixos[0]
    medias = [r["arvore_livre"]["media"], r["arvore_pso"]["media"]]
    desvios = [r["arvore_livre"]["desvio"], r["arvore_pso"]["desvio"]]
    ax.bar(range(2), medias, yerr=desvios, color=[VERMELHO, VERDE], ecolor="#555555", capsize=5, width=0.6)
    for i, v in enumerate(medias):
        ax.text(i, 41.2, num(v), ha="center", fontsize=17, fontweight="bold", color="white")
    ax.set_xticks(range(2), ["árvore\nsem limite", "árvore ajustada\npelo PSO"], fontsize=12)
    ax.set_ylim(40, 72)
    ax.set_ylabel("MAE de teste (10 divisões)")
    ax.set_title("onde havia folga: o PSO na árvore", fontsize=13, fontweight="bold", color=VERDE)
    estilo(ax)

    ax = eixos[1]
    chaves = ["padrao", "pso", "ag", "juntos"]
    medias = [floresta["teste"][c]["media"] for c in chaves]
    desvios = [floresta["teste"][c]["desvio"] for c in chaves]
    ax.bar(range(4), medias, yerr=desvios, color=[VERDE, AZUL, AZUL, AZUL], ecolor="#555555", capsize=5, width=0.62)
    for i, v in enumerate(medias):
        ax.text(i, 41.2, num(v), ha="center", fontsize=15, fontweight="bold", color="white")
    ax.set_xticks(range(4), ["floresta\npadrão", "+ PSO", "+ AG", "AG + PSO"], fontsize=12)
    ax.set_ylim(40, 72)
    ax.set_title("onde não havia: o AG e o PSO na floresta", fontsize=13, fontweight="bold", color=AZUL)
    estilo(ax)

    ax = eixos[2]
    ordem = sorted(e["vezes_escolhida"], key=e["vezes_escolhida"].get, reverse=True)
    vezes = [e["vezes_escolhida"][f] for f in ordem]
    ax.barh(range(10), vezes, color=[VERDE if v >= 90 else CINZA for v in vezes])
    for i, v in enumerate(vezes):
        ax.text(v + 1.5, i, "%d%%" % v, va="center", fontsize=11)
    ax.set_yticks(range(10), ordem, fontsize=12)
    ax.invert_yaxis()
    ax.set_xlim(0, 115)
    ax.set_xlabel("em quantas das %d divisões o AG manteve a medida (%%)" % resumo["divisoes_extra"])
    ax.set_title("o AG no Naive Bayes: as medidas que sobrevivem", fontsize=13, fontweight="bold")
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "fechamento.png"), dpi=150)
    plt.close(fig)


def main():
    with ProcessPoolExecutor(max_workers=6) as ex:
        principais = list(ex.map(tarefa, SEMENTES))
        extras = list(ex.map(tarefa, SEMENTES_EXTRA, chunksize=2))
    resumo = {"partes": PARTES, "principal": resume(principais), "extra": resume(extras), "divisoes_extra": len(SEMENTES_EXTRA),
              "rodadas": principais}
    print("Fechamento, parte 2: a busca onde há folga (a busca só enxerga o treino, com validação em %d partes)" % PARTES)
    for r in principais:
        print("  divisão %2d: PSO escolheu profundidade %2d, mínimo %2d | árvore %.2f -> %.2f | AG escolheu %-34s Bayes %.1f%% -> %.1f%%"
              % (r["semente"] + 1, *r["params"], r["arvore_livre"], r["arvore_pso"],
                 ",".join(f for f, m in zip(FEATURES, r["mascara"]) if m), r["bayes_todas"] * 100, r["bayes_ag"] * 100))
    imprime("\nNas 10 divisões do trabalho", resumo["principal"], len(SEMENTES))
    imprime("\nEm outras %d divisões" % len(SEMENTES_EXTRA), resumo["extra"], len(SEMENTES_EXTRA))
    with open(os.path.join(SAIDA, "resumo_folga.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)
    with open(os.path.join(SAIDA, "resumo_fechamento.json"), encoding="utf-8") as arq:
        grafico(resumo, json.load(arq))


if __name__ == "__main__":
    main()
