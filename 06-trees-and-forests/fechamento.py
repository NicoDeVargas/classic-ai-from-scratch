import json
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from arvore import FEATURES, ArvoreRegressao, Floresta, carrega, divide, mae
from trabalho import SAIDA, SEMENTES, ARVORES, K, AZUL, VERMELHO, CINZA, VERDE, AMBAR, num, estilo

ARVORES_BUSCA = 40
AG_POPULACAO = 12
AG_GERACOES = 8
AG_CRUZAMENTO = 0.9
AG_MUTACAO = 0.05
AG_ELITE = 2
PSO_PARTICULAS = 8
PSO_ITERACOES = 10
PSO_C1 = 2.0
PSO_C2 = 2.0
PSO_W = (0.9, 0.4)
PSO_FRACAO_VMAX = 0.2
LIMITES = np.array([[1, 12], [1, 10], [2, 40]], dtype=float)
NOMES_PSO = ["profundidade", "medidas sorteadas", "mínimo para dividir"]


class Avaliador:
    def __init__(self, X, y, semente):
        self.X, self.y, self.semente, self.memoria = X, y, semente, {}

    def erro(self, mascara, profundidade, k, minimo):
        chave = (tuple(mascara), profundidade, k, minimo)
        if chave not in self.memoria:
            colunas = np.flatnonzero(mascara)
            if len(colunas) == 0:
                self.memoria[chave] = 1e9
            else:
                floresta = Floresta(ARVORES_BUSCA, profundidade, min(k, len(colunas)), self.semente, minimo=minimo)
                Xc = self.X[:, colunas]
                self.memoria[chave] = floresta.treina(Xc, self.y).erro_fora_da_sacola(Xc, self.y)
        return self.memoria[chave]


def algoritmo_genetico(avaliador, rng):
    populacao = rng.integers(0, 2, (AG_POPULACAO, len(FEATURES)))
    populacao[0] = 1
    curva = []
    for geracao in range(AG_GERACOES + 1):
        erros = np.array([avaliador.erro(m, None, K, 2) for m in populacao])
        curva.append(float(erros.min()))
        if geracao == AG_GERACOES:
            break
        ordem = np.argsort(erros)
        aptidao = erros.max() - erros + 1e-6
        pais = populacao[rng.choice(AG_POPULACAO, AG_POPULACAO, p=aptidao / aptidao.sum())]
        filhos = pais.copy()
        for i in range(0, AG_POPULACAO - 1, 2):
            if rng.random() < AG_CRUZAMENTO:
                a, b = np.sort(rng.integers(1, len(FEATURES), 2))
                filhos[i, a:b], filhos[i + 1, a:b] = pais[i + 1, a:b], pais[i, a:b]
        muta = rng.random(filhos.shape) < AG_MUTACAO
        filhos[muta] = 1 - filhos[muta]
        filhos[:AG_ELITE] = populacao[ordem[:AG_ELITE]]
        populacao = filhos
    return populacao[int(np.argmin(erros))], curva


def enxame(avaliador, mascara, rng):
    largura = LIMITES[:, 1] - LIMITES[:, 0]
    vmax = PSO_FRACAO_VMAX * largura
    x = rng.uniform(LIMITES[:, 0], LIMITES[:, 1], (PSO_PARTICULAS, 3))
    x[0] = [LIMITES[0, 1], K, 2]
    v = rng.uniform(-vmax, vmax, (PSO_PARTICULAS, 3))

    def avalia(pontos):
        return np.array([avaliador.erro(mascara, *[int(round(c)) for c in p]) for p in pontos])

    f = avalia(x)
    p, fp = x.copy(), f.copy()
    g = int(np.argmin(fp))
    curva = [float(fp[g])]
    for it in range(PSO_ITERACOES):
        w = PSO_W[0] - it * (PSO_W[0] - PSO_W[1]) / PSO_ITERACOES
        r1, r2 = rng.random((PSO_PARTICULAS, 3)), rng.random((PSO_PARTICULAS, 3))
        v = np.clip(w * v + PSO_C1 * r1 * (p - x) + PSO_C2 * r2 * (p[g] - x), -vmax, vmax)
        x = np.clip(x + v, LIMITES[:, 0], LIMITES[:, 1])
        f = avalia(x)
        melhorou = f < fp
        p[melhorou], fp[melhorou] = x[melhorou], f[melhorou]
        g = int(np.argmin(fp))
        curva.append(float(fp[g]))
    return [int(round(c)) for c in p[g]], curva


def tarefa(semente):
    X, y = carrega()
    treino, teste = divide(len(y), semente)
    Xa, ya, Xt, yt = X[treino], y[treino], X[teste], y[teste]
    avaliador = Avaliador(Xa, ya, semente)
    rng = np.random.default_rng(1000 + semente)
    todas = np.ones(len(FEATURES), dtype=int)

    def testa(mascara, profundidade, k, minimo):
        colunas = np.flatnonzero(mascara)
        floresta = Floresta(ARVORES, profundidade, min(k, len(colunas)), semente, minimo=minimo).treina(Xa[:, colunas], ya)
        return mae(yt, floresta.preve(Xt[:, colunas]))

    mascara, curva_ag = algoritmo_genetico(avaliador, rng)
    params, curva_pso = enxame(avaliador, todas, rng)
    params_juntos, curva_juntos = enxame(avaliador, mascara, rng)
    return {
        "semente": semente, "mascara": mascara.tolist(), "params": params, "params_juntos": params_juntos,
        "curva_ag": curva_ag, "curva_pso": curva_pso, "curva_juntos": curva_juntos,
        "avaliacoes": len(avaliador.memoria),
        "teste": {"padrao": testa(todas, None, K, 2), "ag": testa(mascara, None, K, 2),
                  "pso": testa(todas, *params), "juntos": testa(mascara, *params_juntos)},
    }


def naive_bayes(Xa, ca, Xt):
    pontos = []
    for c in (0, 1):
        media, var = Xa[ca == c].mean(axis=0), Xa[ca == c].var(axis=0)
        pontos.append(np.log((ca == c).mean()) + (-0.5 * np.log(2 * np.pi * var) - (Xt - media) ** 2 / (2 * var)).sum(axis=1))
    return (pontos[1] > pontos[0]).astype(int)


def classificacao(X, y):
    corte = y.mean()
    classe = (y > corte).astype(int)
    acertos = {"bayes": [], "arvore3": [], "floresta": []}
    for s in SEMENTES:
        treino, teste = divide(len(y), s)
        acertos["bayes"].append((naive_bayes(X[treino], classe[treino], X[teste]) == classe[teste]).mean())
        arvore = ArvoreRegressao(3).treina(X[treino], y[treino])
        acertos["arvore3"].append(((arvore.preve(X[teste]) > corte).astype(int) == classe[teste]).mean())
        floresta = Floresta(ARVORES, None, K, s).treina(X[treino], y[treino])
        acertos["floresta"].append(((floresta.preve(X[teste]) > corte).astype(int) == classe[teste]).mean())
    return {k: {"media": float(np.mean(v)), "desvio": float(np.std(v))} for k, v in acertos.items()}


def grafico(resumo):
    fig, eixos = plt.subplots(1, 3, figsize=(17, 5.4), gridspec_kw={"width_ratios": [1, 1.15, 1]})
    ax = eixos[0]
    for chave, cor, rotulo in (("curva_ag", AMBAR, "algoritmo genético: quais medidas usar"),
                               ("curva_pso", AZUL, "enxame de partículas: como configurar")):
        curva = np.mean([r[chave] for r in resumo["rodadas"]], axis=0)
        ax.plot(range(len(curva)), curva, "o-", color=cor, linewidth=2.2, label=rotulo)
    ax.set_xlabel("geração do AG / iteração do PSO")
    ax.set_ylabel("melhor erro fora da sacola (média das 10 divisões)")
    ax.set_title("a busca melhorando a floresta", fontsize=13, fontweight="bold")
    ax.legend(fontsize=10.5)
    estilo(ax)

    ax = eixos[1]
    nomes = ["floresta\npadrão", "+ AG\n(medidas)", "+ PSO\n(configuração)", "AG + PSO"]
    chaves = ["padrao", "ag", "pso", "juntos"]
    medias = [resumo["teste"][c]["media"] for c in chaves]
    desvios = [resumo["teste"][c]["desvio"] for c in chaves]
    ax.bar(range(4), medias, yerr=desvios, color=[CINZA, AMBAR, AZUL, VERDE], ecolor="#555555", capsize=5, width=0.62)
    for i, v in enumerate(medias):
        ax.text(i, 40.6, num(v), ha="center", fontsize=14, fontweight="bold", color="white")
    ax.axhline(resumo["linear"], color="black", linestyle="--", linewidth=1.4)
    ax.text(3.45, resumo["linear"] + 0.25, "regressão linear: %s" % num(resumo["linear"]), ha="right", fontsize=10.5)
    ax.set_xticks(range(4), nomes, fontsize=11.5)
    ax.set_ylim(40, 52)
    ax.set_ylabel("MAE de teste (10 divisões)")
    ax.set_title("o que a busca rendeu no teste", fontsize=13, fontweight="bold")
    estilo(ax)

    ax = eixos[2]
    c = resumo["classificacao"]
    nomes = ["Naive Bayes\n(trabalho 5)", "árvore de\nprofundidade 3", "floresta\naleatória"]
    medias = [c[k]["media"] * 100 for k in ("bayes", "arvore3", "floresta")]
    desvios = [c[k]["desvio"] * 100 for k in ("bayes", "arvore3", "floresta")]
    ax.bar(range(3), medias, yerr=desvios, color=[VERMELHO, CINZA, VERDE], ecolor="#555555", capsize=5, width=0.6)
    for i, v in enumerate(medias):
        ax.text(i, 61, num(v) + "%", ha="center", fontsize=14, fontweight="bold", color="white")
    ax.set_xticks(range(3), nomes, fontsize=11.5)
    ax.set_ylim(60, 82)
    ax.set_ylabel("acurácia (acima ou abaixo da média)")
    ax.set_title("a pergunta do trabalho passado", fontsize=13, fontweight="bold")
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "fechamento.png"), dpi=150)
    plt.close(fig)


def main():
    X, y = carrega()
    with ProcessPoolExecutor(max_workers=6) as ex:
        rodadas = list(ex.map(tarefa, SEMENTES))
    teste = {c: {"media": float(np.mean([r["teste"][c] for r in rodadas])),
                 "desvio": float(np.std([r["teste"][c] for r in rodadas])),
                 "ganhou": int(sum(r["teste"][c] < r["teste"]["padrao"] for r in rodadas))}
             for c in ("padrao", "ag", "pso", "juntos")}
    escolhidas = np.sum([r["mascara"] for r in rodadas], axis=0)
    linear = []
    for s in SEMENTES:
        treino, t = divide(len(y), s)
        A = np.column_stack([np.ones(len(treino)), X[treino]])
        coef = np.linalg.lstsq(A, y[treino], rcond=None)[0]
        linear.append(mae(y[t], np.column_stack([np.ones(len(t)), X[t]]) @ coef))
    resumo = {"rodadas": rodadas, "teste": teste, "linear": float(np.mean(linear)),
              "vezes_escolhida": dict(zip(FEATURES, escolhidas.tolist())),
              "params": {n: [r["params"][i] for r in rodadas] for i, n in enumerate(NOMES_PSO)},
              "avaliacoes": int(np.mean([r["avaliacoes"] for r in rodadas])),
              "classificacao": classificacao(X, y),
              "config": {"arvores_busca": ARVORES_BUSCA, "ag": [AG_POPULACAO, AG_GERACOES], "pso": [PSO_PARTICULAS, PSO_ITERACOES]}}

    print("Fechamento: o AG e o PSO dos trabalhos anteriores ajustando a floresta")
    print("(a busca só enxerga o treino de cada divisão, pelo erro fora da sacola; o teste fica guardado)")
    for r in rodadas:
        print("  divisão %2d: AG escolheu %-38s PSO escolheu prof. %2d, %2d medidas, mínimo %2d | teste: padrão %.2f  AG %.2f  PSO %.2f  AG+PSO %.2f"
              % (r["semente"] + 1, ",".join(f for f, m in zip(FEATURES, r["mascara"]) if m), *r["params"],
                 r["teste"]["padrao"], r["teste"]["ag"], r["teste"]["pso"], r["teste"]["juntos"]))
    for c, nome in (("padrao", "floresta padrão"), ("ag", "+ AG (medidas)"), ("pso", "+ PSO (configuração)"), ("juntos", "AG + PSO")):
        print("  %-22s MAE de teste %.2f ± %.2f   melhor que a padrão em %d de 10" % (nome, teste[c]["media"], teste[c]["desvio"], teste[c]["ganhou"]))
    print("  regressão linear nas mesmas divisões: %.2f" % resumo["linear"])
    print("  vezes que o AG escolheu cada medida:", resumo["vezes_escolhida"])
    print("\nA pergunta do trabalho de Naive Bayes (acima ou abaixo da média), nas mesmas 10 divisões")
    for k, nome in (("bayes", "Naive Bayes"), ("arvore3", "árvore de profundidade 3"), ("floresta", "floresta aleatória")):
        print("  %-26s acurácia %.1f%% ± %.1f" % (nome, resumo["classificacao"][k]["media"] * 100, resumo["classificacao"][k]["desvio"] * 100))
    grafico(resumo)
    with open(os.path.join(SAIDA, "resumo_fechamento.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
