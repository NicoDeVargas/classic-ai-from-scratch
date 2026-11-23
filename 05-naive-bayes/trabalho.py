import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from nb import FEATURES, DESCRICAO, NaiveBayesGaussiano, acuracias, carrega, divide

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "saida")
SEMENTES = list(range(10))
AZUL = "#2f6db5"
VERMELHO = "#d9534f"
CINZA = "#7f8c8d"
VERDE = "#2e9e5b"
CORES = [AZUL, VERMELHO]
NOMES = ["classe 0 (abaixo da média)", "classe 1 (acima da média)"]


def estilo(ax):
    ax.grid(alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


def rotulo(f):
    return "%s (%s)" % (f, DESCRICAO[f])


def gaussiana(x, media, variancia):
    return np.exp(-(x - media) ** 2 / (2 * variancia)) / np.sqrt(2 * np.pi * variancia)


def escolhe_amostra(modelo, X, y):
    p = modelo.probabilidades(X)
    dif = modelo.log_densidade(X)
    dif = dif[:, 1, :] - dif[:, 0, :]
    for i in range(len(y)):
        certo = modelo.classifica(X[i])[0] == y[i]
        if certo and 0.75 <= p[i].max() <= 0.92 and min((dif[i] > 0).sum(), (dif[i] < 0).sum()) >= 3:
            return i
    return 0


def grafico_classes(alvo, y):
    fig, ax = plt.subplots(figsize=(10, 4.6))
    faixas = np.linspace(alvo.min(), alvo.max(), 33)
    ax.hist(alvo[y == 0], bins=faixas, color=AZUL, label="classe 0: %d amostras" % (y == 0).sum())
    ax.hist(alvo[y == 1], bins=faixas, color=VERMELHO, label="classe 1: %d amostras" % (y == 1).sum())
    ax.axvline(alvo.mean(), color="black", linestyle="--", linewidth=1.6)
    ax.text(alvo.mean() + 4, ax.get_ylim()[1] * 0.93, "média = %s" % ("%.1f" % alvo.mean()).replace(".", ","), fontsize=11)
    ax.set_xlabel("progressão da doença depois de um ano (target)")
    ax.set_ylabel("pacientes")
    ax.legend(fontsize=11)
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "classes.png"), dpi=160)
    plt.close(fig)


def paineis(modelo, X, y, amostra=None, arquivo="gaussianas.png"):
    fig, eixos = plt.subplots(2, 5, figsize=(16, 6.6))
    dens = modelo.log_densidade(amostra)[0] if amostra is not None else None
    for i, (ax, f) in enumerate(zip(eixos.ravel(), FEATURES)):
        desvio = np.sqrt(modelo.variancia[:, i].max())
        xs = np.linspace(X[:, i].min() - desvio, X[:, i].max() + desvio, 300)
        for c in (0, 1):
            ax.hist(X[y == c, i], bins=14, density=True, color=CORES[c], alpha=0.18)
            ax.plot(xs, gaussiana(xs, modelo.media[c, i], modelo.variancia[c, i]), color=CORES[c], linewidth=2.2)
        ax.set_yticks([])
        ax.tick_params(labelsize=9)
        for lado in ("top", "right", "left"):
            ax.spines[lado].set_visible(False)
        if amostra is None:
            ax.set_title(rotulo(f), fontsize=11.5, fontweight="bold")
            continue
        vence = int(dens[1, i] > dens[0, i])
        ax.axvline(amostra[i], color="black", linewidth=1.6)
        for c in (0, 1):
            ax.plot(amostra[i], np.exp(dens[c, i]), "o", color=CORES[c], markersize=8, markeredgecolor="black", zorder=5)
        ax.set_title("%s = %s" % (rotulo(f), ("%.4g" % amostra[i]).replace(".", ",")), fontsize=11, fontweight="bold")
        ax.set_xlabel("log: classe 0 = %s · classe 1 = %s\nponto para a classe %d"
                      % (("%.2f" % dens[0, i]).replace(".", ","), ("%.2f" % dens[1, i]).replace(".", ","), vence),
                      fontsize=10, color=CORES[vence], fontweight="bold")
        for lado in ("top", "right", "left", "bottom"):
            ax.spines[lado].set_visible(True)
            ax.spines[lado].set_color(CORES[vence])
            ax.spines[lado].set_linewidth(3)
    fig.legend(handles=[plt.Line2D([], [], color=CORES[c], linewidth=3, label=NOMES[c]) for c in (0, 1)],
               loc="lower center", ncol=2, fontsize=12, frameon=False)
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(os.path.join(SAIDA, arquivo), dpi=150)
    plt.close(fig)


def grafico_parte1(acc, matriz):
    fig, (a, b) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [1.5, 1]})
    a.bar(range(1, 11), acc * 100, color=AZUL)
    for i, v in enumerate(acc):
        a.text(i + 1, v * 100 + 0.8, ("%.1f" % (v * 100)).replace(".", ","), ha="center", fontsize=10)
    a.axhline(acc.mean() * 100, color="black", linestyle="--", linewidth=1.5)
    a.axhspan((acc.mean() - acc.std()) * 100, (acc.mean() + acc.std()) * 100, color="black", alpha=0.08)
    a.text(10.45, acc.mean() * 100 + 0.6, ("média %.1f%%" % (acc.mean() * 100)).replace(".", ","), ha="right", fontsize=11)
    a.set_xticks(range(1, 11))
    a.set_ylim(50, 85)
    a.set_xlabel("divisão treino/teste")
    a.set_ylabel("acurácia no teste (%)")
    estilo(a)
    b.imshow(matriz, cmap="Blues", vmin=0, vmax=matriz.max() * 1.25)
    for i in range(2):
        for j in range(2):
            b.text(j, i, str(matriz[i, j]), ha="center", va="center", fontsize=26, fontweight="bold",
                   color="white" if matriz[i, j] > matriz.max() * 0.6 else "#1f2933")
    b.set_xticks([0, 1], ["previu 0", "previu 1"], fontsize=12)
    b.set_yticks([0, 1], ["real 0", "real 1"], fontsize=12)
    b.set_title("matriz de confusão (última divisão)", fontsize=12)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte1.png"), dpi=160)
    plt.close(fig)


def grafico_contribuicoes(priori, dens, prob):
    fig, eixos = plt.subplots(1, 3, figsize=(16, 6), gridspec_kw={"width_ratios": [1, 1, 0.55]})
    for c in (0, 1):
        ax = eixos[c]
        ordem = np.argsort(dens[c])[::-1]
        nomes = [FEATURES[i] for i in ordem] + ["priori"]
        valores = list(dens[c][ordem]) + [priori[c]]
        cores = [CORES[c]] * 10 + [CINZA]
        ax.barh(range(11), valores, color=cores)
        for k, v in enumerate(valores):
            ax.text(v - 0.12, k, ("%.2f" % v).replace(".", ","), va="center", ha="right", fontsize=10.5)
        ax.set_yticks(range(11), nomes, fontsize=11.5)
        ax.invert_yaxis()
        ax.set_xlim(min(dens.min(), priori.min()) - 1.4, 0)
        total = priori[c] + dens[c].sum()
        ax.set_title("%s\nsoma dos logs = %s" % (NOMES[c], ("%.2f" % total).replace(".", ",")), fontsize=12.5, fontweight="bold",
                     color=CORES[c])
        ax.set_xlabel("log da probabilidade (quanto mais perto de 0, mais a favor)")
        estilo(ax)
    ax = eixos[2]
    ax.bar([0, 1], prob * 100, color=CORES, width=0.6)
    for c in (0, 1):
        ax.text(c, prob[c] * 100 + 2, ("%.1f%%" % (prob[c] * 100)).replace(".", ","), ha="center", fontsize=15, fontweight="bold")
    ax.set_xticks([0, 1], ["classe 0", "classe 1"], fontsize=12)
    ax.set_ylim(0, 110)
    ax.set_yticks([])
    ax.set_title("probabilidade final", fontsize=12.5, fontweight="bold")
    for lado in ("top", "right", "left"):
        ax.spines[lado].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "contribuicoes.png"), dpi=150)
    plt.close(fig)


def grafico_parte2(individuais):
    ordem = sorted(FEATURES, key=lambda f: individuais[f].mean(), reverse=True)
    fig, ax = plt.subplots(figsize=(11, 5.4))
    medias = [individuais[f].mean() * 100 for f in ordem]
    cores = [VERDE] * 3 + [CINZA] * 7
    ax.barh(range(10), medias, xerr=[individuais[f].std() * 100 for f in ordem], color=cores, ecolor="#555555", capsize=3)
    for k, v in enumerate(medias):
        ax.text(51, k, ("%.1f%%" % v).replace(".", ","), va="center", color="white", fontsize=11, fontweight="bold")
    ax.set_yticks(range(10), [rotulo(f) for f in ordem], fontsize=11.5)
    ax.invert_yaxis()
    ax.set_xlim(50, 82)
    ax.set_xlabel("acurácia média em 10 divisões, usando só essa feature (%)")
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte2.png"), dpi=160)
    plt.close(fig)
    return ordem


def grafico_parte3(todas, tres, nomes):
    fig, ax = plt.subplots(figsize=(11, 5))
    x = np.arange(1, 11)
    ax.plot(x, todas * 100, "o-", color=CINZA, linewidth=1.8, markersize=8, label="todas as 10 features")
    ax.plot(x, tres * 100, "o-", color=VERDE, linewidth=1.8, markersize=8, label="só " + ", ".join(nomes))
    for serie, cor in ((todas, CINZA), (tres, VERDE)):
        ax.axhline(serie.mean() * 100, color=cor, linestyle="--", linewidth=1.3)
    ax.set_xticks(x)
    ax.set_xlabel("divisão treino/teste")
    ax.set_ylabel("acurácia no teste (%)")
    ax.legend(fontsize=11.5)
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte3.png"), dpi=160)
    plt.close(fig)


def main():
    os.makedirs(SAIDA, exist_ok=True)
    X, y, alvo = carrega()
    print("Parte 1")
    print("média do target: %.2f" % alvo.mean())
    print("classe 0 (abaixo ou igual à média): %d amostras" % (y == 0).sum())
    print("classe 1 (acima da média): %d amostras" % (y == 1).sum())
    grafico_classes(alvo, y)

    todas = acuracias(X, y, list(range(10)), SEMENTES)
    for s, a in zip(SEMENTES, todas):
        print("divisão %2d: acurácia %.4f" % (s + 1, a))
    print("acurácia média: %.4f   desvio padrão: %.4f" % (todas.mean(), todas.std()))

    treino, teste = divide(len(y), SEMENTES[-1])
    modelo = NaiveBayesGaussiano().treina(X[treino], y[treino])
    previsto = modelo.classifica(X[teste])
    matriz = np.array([[((y[teste] == r) & (previsto == p)).sum() for p in (0, 1)] for r in (0, 1)])
    print("\nmatriz de confusão da última divisão (linhas: real, colunas: previsto)")
    print(matriz)
    grafico_parte1(todas, matriz)
    paineis(modelo, X[treino], y[treino])

    k = escolhe_amostra(modelo, X[teste], y[teste])
    amostra = X[teste][k]
    dens = modelo.log_densidade(amostra)[0]
    prob = modelo.probabilidades(amostra)[0]
    print("\namostra %d do teste (índice %d no dataset), classe real %d" % (k, teste[k], y[teste][k]))
    print("  " + ", ".join("%s=%.4g" % (f, v) for f, v in zip(FEATURES, amostra)))
    print("a) log da priori: classe 0 = %.4f   classe 1 = %.4f" % tuple(modelo.log_priori))
    for c in (0, 1):
        print("b) classe %d: log da densidade de cada feature, em ordem decrescente" % c)
        for i in np.argsort(dens[c])[::-1]:
            print("     %-4s %9.4f" % (FEATURES[i], dens[c, i]))
        print("     log da posteriori (priori + soma) = %.4f" % (modelo.log_priori[c] + dens[c].sum()))
    print("c) probabilidades: classe 0 = %.2f%%   classe 1 = %.2f%%" % (prob[0] * 100, prob[1] * 100))
    print("d) classe escolhida: %d" % prob.argmax())
    paineis(modelo, X[treino], y[treino], amostra, "passo_a_passo.png")
    grafico_contribuicoes(modelo.log_priori, dens, prob)

    print("\nParte 2: uma feature por vez")
    individuais = {f: acuracias(X, y, [i], SEMENTES) for i, f in enumerate(FEATURES)}
    ordem = grafico_parte2(individuais)
    for f in ordem:
        print("  %-4s acurácia média %.4f   desvio %.4f" % (f, individuais[f].mean(), individuais[f].std()))

    print("\nParte 3: as 3 melhores features (%s)" % ", ".join(ordem[:3]))
    tres = acuracias(X, y, [FEATURES.index(f) for f in ordem[:3]], SEMENTES)
    print("  3 features:  média %.4f   desvio %.4f" % (tres.mean(), tres.std()))
    print("  10 features: média %.4f   desvio %.4f" % (todas.mean(), todas.std()))
    print("  3 features melhor em %d divisões, igual em %d, pior em %d"
          % ((tres > todas).sum(), (tres == todas).sum(), (tres < todas).sum()))
    grafico_parte3(todas, tres, ordem[:3])

    resumo = {
        "media_target": float(alvo.mean()), "classes": [int((y == 0).sum()), int((y == 1).sum())],
        "n_treino": len(treino), "n_teste": len(teste),
        "parte1": {"acuracias": todas.tolist(), "media": float(todas.mean()), "desvio": float(todas.std()),
                   "matriz": matriz.tolist()},
        "modelo": {"priori": np.exp(modelo.log_priori).tolist(), "media": modelo.media.tolist(),
                   "desvio": np.sqrt(modelo.variancia).tolist()},
        "amostra": {"indice_teste": int(k), "indice_dataset": int(teste[k]), "real": int(y[teste][k]),
                    "valores": dict(zip(FEATURES, amostra.tolist())), "log_priori": modelo.log_priori.tolist(),
                    "log_densidade": dens.tolist(),
                    "log_posteriori": (modelo.log_priori + dens.sum(axis=1)).tolist(),
                    "probabilidades": prob.tolist(), "classe": int(prob.argmax()),
                    "a_favor_1": [f for i, f in enumerate(FEATURES) if dens[1, i] > dens[0, i]],
                    "a_favor_0": [f for i, f in enumerate(FEATURES) if dens[1, i] <= dens[0, i]]},
        "parte2": [{"feature": f, "media": float(individuais[f].mean()), "desvio": float(individuais[f].std())}
                   for f in ordem],
        "parte3": {"features": ordem[:3], "acuracias": tres.tolist(), "media": float(tres.mean()),
                   "desvio": float(tres.std()), "melhor": int((tres > todas).sum()),
                   "igual": int((tres == todas).sum()), "pior": int((tres < todas).sum())},
    }
    with open(os.path.join(SAIDA, "resumo_trabalho.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
