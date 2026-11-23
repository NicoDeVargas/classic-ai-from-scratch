import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from nb import FEATURES, NaiveBayesGaussiano, acuracias, carrega, divide
from trabalho import AZUL, VERMELHO, CINZA, VERDE, SAIDA, estilo

SEMENTES = list(range(1000, 1300))
FAIXAS = [(0.5, 0.6), (0.6, 0.7), (0.7, 0.8), (0.8, 0.9), (0.9, 0.95), (0.95, 1.001)]
AMBAR = "#e8a33d"


def log_normal(X, media, cov):
    d = X - media
    return -0.5 * np.einsum("ij,jk,ik->i", d, np.linalg.inv(cov), d) - 0.5 * np.linalg.slogdet(cov)[1]


def bayes_completo(X, y, treino, teste, mesma_covariancia):
    priori = [np.log((y[treino] == c).mean()) for c in (0, 1)]
    medias = [X[treino][y[treino] == c].mean(axis=0) for c in (0, 1)]
    covs = [np.cov(X[treino][y[treino] == c].T) for c in (0, 1)]
    if mesma_covariancia:
        n = [(y[treino] == c).sum() for c in (0, 1)]
        covs = [((n[0] - 1) * covs[0] + (n[1] - 1) * covs[1]) / (sum(n) - 2)] * 2
    pontos = np.array([priori[c] + log_normal(X[teste], medias[c], covs[c]) for c in (0, 1)])
    return (pontos.argmax(axis=0) == y[teste]).mean()


def naive_sem_correlacao(X, y, treino, teste):
    media, desvio = X[treino].mean(axis=0), X[treino].std(axis=0)
    Z, Zt = (X[treino] - media) / desvio, (X[teste] - media) / desvio
    _, eixos = np.linalg.eigh(np.cov(Z.T))
    modelo = NaiveBayesGaussiano().treina(Z @ eixos, y[treino])
    return (modelo.classifica(Zt @ eixos) == y[teste]).mean()


def calibracao(X, y, colunas):
    certeza, acerto = [], []
    for s in SEMENTES:
        treino, teste = divide(len(y), s)
        modelo = NaiveBayesGaussiano().treina(X[treino][:, colunas], y[treino])
        certeza += list(modelo.probabilidades(X[teste][:, colunas]).max(axis=1))
        acerto += list(modelo.classifica(X[teste][:, colunas]) == y[teste])
    certeza, acerto = np.array(certeza), np.array(acerto)
    linhas = []
    for a, b in FAIXAS:
        k = (certeza >= a) & (certeza < b)
        linhas.append({"de": a, "ate": min(b, 1.0), "n": int(k.sum()), "certeza": float(certeza[k].mean()),
                       "acerto": float(acerto[k].mean())})
    return linhas


def grafico_curva(curva, ordem, dez, tres):
    fig, ax = plt.subplots(figsize=(11, 5.2))
    x = np.arange(1, 11)
    medias = np.array([c["media"] for c in curva]) * 100
    melhor = int(medias.argmax())
    ax.plot(x, medias, "o-", color=AZUL, linewidth=2.2, markersize=9)
    ax.plot(x[melhor], medias[melhor], "o", color=VERDE, markersize=15, zorder=5)
    for k, v in enumerate(medias):
        ax.text(x[k], v + 0.35, ("%.1f" % v).replace(".", ","), ha="center", fontsize=10.5,
                fontweight="bold" if k == melhor else "normal")
    ax.set_xticks(x, ["+ %s" % f if k else f for k, f in enumerate(ordem)], fontsize=11)
    ax.set_xlabel("features usadas, entrando na ordem do ranking da Parte 2")
    ax.set_ylabel("acurácia média em %d divisões (%%)" % len(SEMENTES))
    ax.set_ylim(medias.min() - 1, medias.max() + 1.6)
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "extra_curva.png"), dpi=160)
    plt.close(fig)


def grafico_correlacao(X):
    corr = np.corrcoef(X.T)
    fig, ax = plt.subplots(figsize=(6.6, 6))
    ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    for i in range(10):
        for j in range(10):
            ax.text(j, i, ("%.2f" % corr[i, j]).replace(".", ",").replace("0,", ",") if i != j else "",
                    ha="center", va="center", fontsize=8.5,
                    color="white" if abs(corr[i, j]) > 0.6 else "#1f2933", fontweight="bold" if abs(corr[i, j]) > 0.6 else "normal")
    ax.set_xticks(range(10), FEATURES, fontsize=11)
    ax.set_yticks(range(10), FEATURES, fontsize=11)
    ax.set_title("correlação entre as features", fontsize=12.5)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "extra_correlacao.png"), dpi=160)
    plt.close(fig)
    return corr


def grafico_calibracao(dez, tres, nomes):
    fig, ax = plt.subplots(figsize=(8.6, 6))
    ax.plot([50, 100], [50, 100], color="black", linestyle="--", linewidth=1.3, label="ideal: certeza = acerto")
    for linhas, cor, rotulo in ((dez, VERMELHO, "todas as 10 features"), (tres, VERDE, "só " + ", ".join(nomes))):
        ax.plot([l["certeza"] * 100 for l in linhas], [l["acerto"] * 100 for l in linhas], "o-", color=cor,
                linewidth=2.2, markersize=9, label=rotulo)
    ultimo = dez[-1]
    ax.annotate("diz %s%% de certeza,\nacerta %s%%" % (("%.0f" % (ultimo["certeza"] * 100)), ("%.0f" % (ultimo["acerto"] * 100))),
                xy=(ultimo["certeza"] * 100, ultimo["acerto"] * 100), xytext=(72, 90), fontsize=11.5, color=VERMELHO,
                arrowprops={"arrowstyle": "->", "color": VERMELHO})
    ax.set_xlabel("certeza que o modelo declara (%)")
    ax.set_ylabel("quanto ele acerta de verdade (%)")
    ax.set_xlim(50, 101)
    ax.set_ylim(40, 101)
    ax.legend(fontsize=11, loc="lower right")
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "extra_calibracao.png"), dpi=160)
    plt.close(fig)


def grafico_modelos(modelos):
    fig, ax = plt.subplots(figsize=(10, 4.6))
    nomes = [m["nome"] for m in modelos]
    medias = [m["media"] * 100 for m in modelos]
    ax.barh(range(len(modelos)), medias, color=[CINZA, AMBAR, AMBAR, AMBAR, VERDE])
    for k, v in enumerate(medias):
        ax.text(v + 0.15, k, ("%.1f%%" % v).replace(".", ","), va="center", fontsize=12, fontweight="bold")
    ax.set_yticks(range(len(modelos)), nomes, fontsize=11.5)
    ax.invert_yaxis()
    ax.set_xlim(65, 78)
    ax.set_xlabel("acurácia média em %d divisões (%%)" % len(SEMENTES))
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "extra_modelos.png"), dpi=160)
    plt.close(fig)


def main():
    X, y, _ = carrega()
    with open(os.path.join(SAIDA, "resumo_trabalho.json"), encoding="utf-8") as arq:
        trabalho = json.load(arq)
    ordem = [p["feature"] for p in trabalho["parte2"]]
    indices = [FEATURES.index(f) for f in ordem]

    print("Extra 1: quantas features usar? (%d divisões)" % len(SEMENTES))
    curva = []
    for k in range(1, 11):
        a = acuracias(X, y, indices[:k], SEMENTES)
        curva.append({"features": ordem[:k], "media": float(a.mean()), "desvio": float(a.std())})
        print("  %2d features (%s): %.4f" % (k, ", ".join(ordem[:k]), a.mean()))
    grafico_curva(curva, ordem, curva[9], curva[2])
    melhor = max(curva, key=lambda c: c["media"])

    corr = grafico_correlacao(X)
    pares = sorted(((abs(corr[i, j]), FEATURES[i], FEATURES[j], corr[i, j]) for i in range(10) for j in range(i)), reverse=True)[:3]
    print("\nExtra 2: correlações mais fortes")
    for _, a, b, c in pares:
        print("  %s e %s: %.2f" % (b, a, c))

    print("\nExtra 3: a certeza do modelo confere? (certeza declarada x acerto real)")
    cal_dez = calibracao(X, y, list(range(10)))
    cal_tres = calibracao(X, y, indices[:3])
    for nome, linhas in (("10 features", cal_dez), ("3 features", cal_tres)):
        for l in linhas:
            print("  %-11s certeza %.0f-%.0f%%: declara %.1f%%, acerta %.1f%% (%d previsões)"
                  % (nome, l["de"] * 100, l["ate"] * 100, l["certeza"] * 100, l["acerto"] * 100, l["n"]))
    grafico_calibracao(cal_dez, cal_tres, ordem[:3])

    print("\nExtra 4: e sem a hipótese ingênua?")
    resultados = {"sem_corr": [], "completo": [], "completo_igual": []}
    for s in SEMENTES:
        treino, teste = divide(len(y), s)
        resultados["sem_corr"].append(naive_sem_correlacao(X, y, treino, teste))
        resultados["completo"].append(bayes_completo(X, y, treino, teste, False))
        resultados["completo_igual"].append(bayes_completo(X, y, treino, teste, True))
    modelos = [
        {"nome": "Naive Bayes, 10 features", "media": curva[9]["media"]},
        {"nome": "Naive Bayes depois de tirar a correlação (PCA)", "media": float(np.mean(resultados["sem_corr"]))},
        {"nome": "Bayes com covariância, uma por classe", "media": float(np.mean(resultados["completo"]))},
        {"nome": "Bayes com covariância, a mesma nas duas classes", "media": float(np.mean(resultados["completo_igual"]))},
        {"nome": "Naive Bayes, as %d melhores features" % len(melhor["features"]), "media": melhor["media"]},
    ]
    for m in modelos:
        print("  %-50s %.4f" % (m["nome"], m["media"]))
    grafico_modelos(modelos)

    resumo = {"divisoes": len(SEMENTES), "curva": curva, "melhor_k": len(melhor["features"]),
              "correlacoes": [{"a": b, "b": a, "valor": float(c)} for _, a, b, c in pares],
              "calibracao_10": cal_dez, "calibracao_3": cal_tres, "modelos": modelos}
    with open(os.path.join(SAIDA, "resumo_extras.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
