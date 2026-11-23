import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ag import AlgoritmoGenetico, no_maximo_global, LIMITE

SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saida")
EXECUCOES = 100


def grafico_dispersao(resultados):
    xs = np.array([r["x"] for r in resultados])
    ys = np.array([r["y"] for r in resultados])
    ok = np.array([r["global"] for r in resultados])

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(xs[~ok], ys[~ok], color="#c0392b", s=30, label="máximo local")
    ax.scatter(xs[ok], ys[ok], color="#1b6ca8", s=30, label="máximo global")
    ax.add_patch(plt.Rectangle((-0.09, -0.09), 0.18, 0.18, fill=False,
                               edgecolor="black", linewidth=1.2))
    ax.set_xlim(-LIMITE, LIMITE)
    ax.set_ylim(-LIMITE, LIMITE)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title("Solução final de cada uma das %d execuções" % EXECUCOES)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte2_dispersao.png"), dpi=150)
    plt.close(fig)


def main():
    os.makedirs(SAIDA, exist_ok=True)
    resultados = []
    linhas = []

    print("Parte 2 - %d execucoes independentes" % EXECUCOES)
    print("%-5s %12s %12s %12s  %s" % ("exec", "x", "y", "fitness", "máximo global"))

    for i in range(EXECUCOES):
        r = AlgoritmoGenetico(semente=i).executa()
        r["global"] = no_maximo_global(r["x"], r["y"])
        resultados.append(r)
        linha = "%-5d %12.6f %12.6f %12.8f  %s" % (
            i + 1, r["x"], r["y"], r["aptidao"], "SIM" if r["global"] else "nao")
        print(linha)
        linhas.append(linha)

    acertos = sum(r["global"] for r in resultados)
    resumo = [
        "",
        "convergiu para o maximo global em %d de %d execucoes (%.1f%%)" % (
            acertos, EXECUCOES, 100.0 * acertos / EXECUCOES),
        "criterio: -0.09 <= x <= 0.09 e -0.09 <= y <= 0.09",
        "requisito de 50%%: %s" % ("atendido" if acertos >= EXECUCOES / 2 else "NAO atendido"),
        "fitness medio: %.8f" % np.mean([r["aptidao"] for r in resultados]),
    ]
    for l in resumo:
        print(l)

    cabecalho = "%-5s %12s %12s %12s  %s" % ("exec", "x", "y", "fitness", "máximo global")
    with open(os.path.join(SAIDA, "parte2_resultados.txt"), "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join([cabecalho] + linhas + resumo) + "\n")

    grafico_dispersao(resultados)
    print("")
    print("arquivos gerados:")
    print(" ", os.path.join(SAIDA, "parte2_resultados.txt"))
    print(" ", os.path.join(SAIDA, "parte2_dispersao.png"))


if __name__ == "__main__":
    main()
