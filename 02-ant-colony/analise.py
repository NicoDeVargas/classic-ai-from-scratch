import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from aco import ColoniaFormigas, carrega_matriz, ITERACOES, JANELA_CONVERGENCIA

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "saida")
MATRIZ = os.path.join(RAIZ, "distancia_matrix.csv")
EXECUCOES = 10

AZUL = "#1b6ca8"
VERMELHO = "#c0392b"


def amostra(distancias, n_formigas, evaporacao):
    distancias_finais = []
    iteracoes_convergencia = []
    sem_convergir = 0

    for semente in range(EXECUCOES):
        colonia = ColoniaFormigas(distancias, n_formigas=n_formigas, evaporacao=evaporacao,
                                  semente=semente)
        r = colonia.executa(parar_na_convergencia=True)
        distancias_finais.append(r["melhor_distancia"])
        if r["convergiu"]:
            iteracoes_convergencia.append(r["iteracao_convergencia"])
        else:
            sem_convergir += 1
            iteracoes_convergencia.append(ITERACOES)

    return {
        "media": float(np.mean(distancias_finais)),
        "desvio": float(np.std(distancias_finais, ddof=1)),
        "iteracoes": float(np.mean(iteracoes_convergencia)),
        "sem_convergir": sem_convergir,
    }


def tabela(titulo, rotulo, valores, linhas):
    print(titulo)
    print("")
    print("  %-14s %14s %14s %16s %12s"
          % (rotulo, "média dist.", "desvio padrão", "média iterações", "não conv."))
    print("  " + "-" * 74)
    for v, l in zip(valores, linhas):
        print("  %-14s %14.4f %14.4f %16.1f %12d"
              % (v, l["media"], l["desvio"], l["iteracoes"], l["sem_convergir"]))
    print("")


def grafico_distancia(valores, linhas, rotulo, titulo, destino, categorico=False):
    medias = np.array([l["media"] for l in linhas])
    desvios = np.array([l["desvio"] for l in linhas])
    x = np.arange(len(valores)) if categorico else np.array(valores, dtype=float)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.errorbar(x, medias, yerr=desvios, marker="o", markersize=8, linewidth=2.0,
                color=AZUL, ecolor=VERMELHO, elinewidth=1.6, capsize=6,
                label="média ± desvio padrão")
    ax.set_xlabel(rotulo)
    ax.set_ylabel("Distância final")
    ax.set_title(titulo)
    if categorico:
        ax.set_xticks(x)
        ax.set_xticklabels([str(v) for v in valores])
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def grafico_iteracoes(valores, linhas, rotulo, titulo, destino, categorico=False):
    iteracoes = np.array([l["iteracoes"] for l in linhas])
    x = np.arange(len(valores)) if categorico else np.array(valores, dtype=float)

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(x, iteracoes, marker="o", markersize=8, linewidth=2.0, color=AZUL)
    ax.set_xlabel(rotulo)
    ax.set_ylabel("Iterações até a convergência")
    ax.set_title(titulo)
    if categorico:
        ax.set_xticks(x)
        ax.set_xticklabels([str(v) for v in valores])
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(destino, dpi=150)
    plt.close(fig)


def parte2(distancias):
    formigas = [3, 5, 10, 20, 40, 80]
    linhas = [amostra(distancias, n, 0.5) for n in formigas]

    tabela("Parte 2 - numero de formigas (evaporacao fixa em 0.5, %d execucoes cada)" % EXECUCOES,
           "formigas", formigas, linhas)

    grafico_distancia(formigas, linhas, "Número de formigas",
                      "Parte 2 — distância final por tamanho da colônia",
                      os.path.join(SAIDA, "parte2_a_distancia.png"), categorico=True)
    grafico_iteracoes(formigas, linhas, "Número de formigas",
                      "Parte 2 — iterações até a convergência por tamanho da colônia",
                      os.path.join(SAIDA, "parte2_b_iteracoes.png"), categorico=True)
    return formigas, linhas


def parte3(distancias):
    evaporacoes = [0.0, 0.25, 0.5, 0.75, 1.0]
    linhas = [amostra(distancias, 20, p) for p in evaporacoes]

    tabela("Parte 3 - taxa de evaporacao (20 formigas, %d execucoes cada)" % EXECUCOES,
           "evaporação", evaporacoes, linhas)

    grafico_distancia(evaporacoes, linhas, "Taxa de evaporação (ρ)",
                      "Parte 3 — distância final por taxa de evaporação",
                      os.path.join(SAIDA, "parte3_a_distancia.png"))
    grafico_iteracoes(evaporacoes, linhas, "Taxa de evaporação (ρ)",
                      "Parte 3 — iterações até a convergência por taxa de evaporação",
                      os.path.join(SAIDA, "parte3_b_iteracoes.png"))
    return evaporacoes, linhas


def main():
    os.makedirs(SAIDA, exist_ok=True)
    distancias = carrega_matriz(MATRIZ)

    print("ACO - analise de sensibilidade (alfa=1, beta=5, Q=100, sem elitismo)")
    print("convergencia: melhor distancia estavel por %d iteracoes consecutivas"
          % JANELA_CONVERGENCIA)
    print("limite de %d iteracoes; a execucao para assim que converge" % ITERACOES)
    print("")

    formigas, l2 = parte2(distancias)
    evaporacoes, l3 = parte3(distancias)

    with open(os.path.join(SAIDA, "analise_resultados.txt"), "w", encoding="utf-8") as arq:
        arq.write("Parte 2 - numero de formigas (evaporacao 0.5)\n")
        arq.write("formigas;media;desvio;iteracoes;nao_convergiram\n")
        for v, l in zip(formigas, l2):
            arq.write("%d;%.4f;%.4f;%.1f;%d\n"
                      % (v, l["media"], l["desvio"], l["iteracoes"], l["sem_convergir"]))
        arq.write("\nParte 3 - taxa de evaporacao (20 formigas)\n")
        arq.write("evaporacao;media;desvio;iteracoes;nao_convergiram\n")
        for v, l in zip(evaporacoes, l3):
            arq.write("%.2f;%.4f;%.4f;%.1f;%d\n"
                      % (v, l["media"], l["desvio"], l["iteracoes"], l["sem_convergir"]))

    resumo = {
        "execucoes": EXECUCOES,
        "parte2": {"formigas": formigas, "linhas": l2},
        "parte3": {"evaporacoes": evaporacoes, "linhas": l3},
    }
    with open(os.path.join(SAIDA, "resumo_analise.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)

    print("arquivos gerados:")
    for nome in ["parte2_a_distancia.png", "parte2_b_iteracoes.png",
                 "parte3_a_distancia.png", "parte3_b_iteracoes.png",
                 "analise_resultados.txt"]:
        print(" ", os.path.join(SAIDA, nome))


if __name__ == "__main__":
    main()
