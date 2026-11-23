import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter

from aco import (ColoniaFormigas, carrega_matriz, coordenadas, coordenadas_por_rota,
                 ITERACOES, JANELA_CONVERGENCIA)

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "saida")
MATRIZ = os.path.join(RAIZ, "distancia_matrix.csv")
SEMENTE = 1
N_FORMIGAS = 20
EVAPORACAO = 0.5


def grafico_convergencia(resultado):
    curva = resultado["curva"]
    iteracoes = np.arange(1, len(curva) + 1)

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(iteracoes, curva, color="#1b6ca8", linewidth=2.0, label="melhor distância encontrada")

    convergencia = resultado["iteracao_convergencia"]
    if convergencia:
        ax.axvline(convergencia, color="#c0392b", linestyle="--", linewidth=1.4)
        ax.annotate("convergência: iteração %d\ndistância %.2f"
                    % (convergencia, curva[convergencia - 1]),
                    xy=(convergencia, curva[convergencia - 1]),
                    xytext=(22, 30), textcoords="offset points",
                    color="#c0392b", fontsize=11,
                    bbox=dict(boxstyle="round,pad=0.35", facecolor="white",
                              edgecolor="#c0392b", linewidth=1.0),
                    arrowprops=dict(arrowstyle="->", color="#c0392b", linewidth=1.2))

    ax.set_xlabel("Iteração")
    ax.set_ylabel("Melhor distância")
    ax.set_title("Evolução da melhor distância por iteração")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte1_convergencia.png"), dpi=150)
    plt.close(fig)


def grafico_rota(resultado, pontos):
    rota = resultado["melhor_rota"]
    ciclo = np.append(rota, rota[0])

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.plot(pontos[ciclo, 0], pontos[ciclo, 1], color="#1b6ca8", linewidth=1.8, zorder=1)
    ax.scatter(pontos[:, 0], pontos[:, 1], s=180, color="white", edgecolors="#1B1035",
               linewidths=1.6, zorder=2)
    for i, (x, y) in enumerate(pontos):
        ax.text(x, y, str(i), ha="center", va="center", fontsize=8.5, zorder=3)

    ax.set_title("Melhor rota encontrada — distância %.2f" % resultado["melhor_distancia"])
    ax.set_xticks([])
    ax.set_yticks([])
    for lado in ax.spines.values():
        lado.set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte1_melhor_rota.png"), dpi=150)
    plt.close(fig)


def painel_grafo(fig, caixa, pontos, subtitulo):
    n = len(pontos)
    pares = [(i, j) for i in range(n) for j in range(i + 1, n)]
    segmentos = np.array([[pontos[i], pontos[j]] for i, j in pares])

    ax = fig.add_axes(caixa)
    ax.set_facecolor("white")
    feromonio = LineCollection(segmentos, linewidths=0.2, colors="white", zorder=1)
    ax.add_collection(feromonio)
    rota = LineCollection([], linewidths=2.2, colors="#1b6ca8", zorder=2, alpha=0.92)
    ax.add_collection(rota)
    ax.scatter(pontos[:, 0], pontos[:, 1], s=150, color="white", edgecolors="#222222",
               linewidths=1.3, zorder=3)
    for i, (x, y) in enumerate(pontos):
        ax.text(x, y, str(i), ha="center", va="center", fontsize=7.5, zorder=4)

    margem = 0.09 * max(np.ptp(pontos[:, 0]), np.ptp(pontos[:, 1]))
    ax.set_xlim(pontos[:, 0].min() - margem, pontos[:, 0].max() + margem)
    ax.set_ylim(pontos[:, 1].min() - margem, pontos[:, 1].max() + margem)
    ax.set_xticks([])
    ax.set_yticks([])
    for lado in ax.spines.values():
        lado.set_visible(False)
    ax.set_title(subtitulo, fontsize=10.5, color="#444444", pad=6)

    return {
        "pontos": pontos,
        "feromonio": feromonio,
        "rota": rota,
        "i": np.array([i for i, _ in pares]),
        "j": np.array([j for _, j in pares]),
    }


def video(resultado, pontos_ordenados, pontos_originais):
    historico = resultado["historico"]
    maximo = max(float(h["feromonio"].max()) for h in historico)
    maximo = maximo if maximo > 0 else 1.0

    fig = plt.figure(figsize=(12.2, 7.6))
    fig.patch.set_facecolor("white")

    esquerda = painel_grafo(fig, [0.015, 0.155, 0.47, 0.70], pontos_ordenados,
                            "círculo ordenado pela rota final")
    direita = painel_grafo(fig, [0.515, 0.155, 0.47, 0.70], pontos_originais,
                           "círculo na ordem original (0 a 19)")
    paineis = [esquerda, direita]

    titulo = fig.suptitle("", fontsize=13.5, y = 0.975, linespacing=1.5)

    curva = resultado["curva"]
    painel = fig.add_axes([0.055, 0.045, 0.27, 0.075])
    painel.plot(np.arange(1, len(curva) + 1), curva, color="#CCCCCC", linewidth=1.0)
    avanco, = painel.plot([], [], color="#1b6ca8", linewidth=1.8)
    painel.set_xlim(1, len(curva))
    painel.set_ylim(curva.min() - (curva[0] - curva.min()) * 0.08, curva[0] * 1.02)
    painel.set_xticks([])
    painel.set_yticks([])
    marca_painel = painel.axvline(1, color="#1b6ca8", linewidth=1.0, alpha=0.0)
    painel.set_title("melhor distância por iteração", fontsize=8.5, pad=4)
    for lado in painel.spines.values():
        lado.set_edgecolor("#999999")

    barra = fig.add_axes([0.685, 0.055, 0.26, 0.022])
    gradiente = np.linspace(0, 1, 256).reshape(1, -1)
    barra.imshow(gradiente, aspect="auto", cmap="gray_r", extent=(0, 1, 0, 1))
    barra.set_xticks([0, 1])
    barra.set_xticklabels(["0", "%.1f" % maximo], fontsize=8.5)
    barra.set_yticks([])
    barra.set_title("feromônio na aresta", fontsize=8.5, pad=4)

    fig.text(0.505, 0.077, "os dois painéis mostram exatamente os mesmos dados —\n"
                         "muda só a posição das cidades no desenho",
             ha="center", va="center", fontsize=9, color="#777777", style="italic",
             linespacing=1.4)

    mudou_em = np.array([h["iteracao"] for h in historico], dtype=int)
    for k in range(1, len(historico)):
        piorou = historico[k]["melhor_distancia"] < historico[k - 1]["melhor_distancia"] - 1e-9
        mudou_em[k] = historico[k]["iteracao"] if piorou else mudou_em[k - 1]

    def frame(k):
        h = historico[k]
        ciclo = np.append(h["melhor_rota"], h["melhor_rota"][0])

        artistas = []
        for pnl in paineis:
            tau = h["feromonio"][pnl["i"], pnl["j"]]
            intensidade = np.clip(tau / maximo, 0.0, 1.0)
            pnl["feromonio"].set_color([(1.0 - v, 1.0 - v, 1.0 - v) for v in intensidade])
            pnl["feromonio"].set_linewidths(0.2 + 4.0 * intensidade)
            pts = pnl["pontos"]
            pnl["rota"].set_segments([[pts[ciclo[t]], pts[ciclo[t + 1]]]
                                      for t in range(len(h["melhor_rota"]))])
            artistas += [pnl["feromonio"], pnl["rota"]]

        avanco.set_data(np.arange(1, k + 2), curva[:k + 1])
        estavel = h["iteracao"] - mudou_em[k]
        marca_painel.set_xdata([mudou_em[k], mudou_em[k]])
        marca_painel.set_alpha(0.9 if estavel >= 1 else 0.0)

        titulo.set_text("Iteração %d de %d   |   melhor distância = %.2f\n"
                        "rota em azul: inalterada há %d iteraç%s"
                        % (h["iteracao"], len(historico), h["melhor_distancia"],
                           estavel, "ão" if estavel == 1 else "ões"))
        return artistas + [avanco, titulo]

    animacao = FuncAnimation(fig, frame, frames=len(historico), interval=80, blit=False)

    destino = os.path.join(SAIDA, "parte1_feromonio.mp4")
    try:
        import imageio_ffmpeg
        matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
        animacao.save(destino, writer=FFMpegWriter(fps=12, bitrate=2600))
    except Exception as erro:
        print("ffmpeg indisponivel (%s); gerando GIF" % erro)
        destino = os.path.join(SAIDA, "parte1_feromonio.gif")
        animacao.save(destino, writer=PillowWriter(fps=12))
    plt.close(fig)
    return destino


def main():
    os.makedirs(SAIDA, exist_ok=True)
    distancias = carrega_matriz(MATRIZ)
    colonia = ColoniaFormigas(distancias, n_formigas=N_FORMIGAS, evaporacao=EVAPORACAO,
                              semente=SEMENTE)
    resultado = colonia.executa(historico=True)

    print("Parte 1 - ACO aplicado ao TSP de %d cidades" % len(distancias))
    print("formigas=%d  evaporacao=%.2f  alfa=%g  beta=%g  Q=%g  iteracoes=%d"
          % (N_FORMIGAS, EVAPORACAO, colonia.alfa, colonia.beta, colonia.q, ITERACOES))
    print("")
    print("menor distancia encontrada: %.4f" % resultado["melhor_distancia"])
    print("rota: %s" % " -> ".join(str(c) for c in resultado["melhor_rota"]))
    print("")
    if resultado["convergiu"]:
        print("CONVERGENCIA na iteracao %d" % resultado["iteracao_convergencia"])
        print("  a melhor distancia foi atingida ali e nao melhorou nas %d iteracoes"
              % (resultado["iteracoes_executadas"] - resultado["ultima_melhora"]))
        print("  seguintes, cumprindo a janela de %d exigida no enunciado."
              % JANELA_CONVERGENCIA)
    else:
        print("NAO convergiu dentro das %d iteracoes" % ITERACOES)
        print("  a ultima melhora foi na iteracao %d, faltando %d iteracoes"
              % (resultado["ultima_melhora"],
                 JANELA_CONVERGENCIA - (resultado["iteracoes_executadas"]
                                        - resultado["ultima_melhora"])))
        print("  para fechar a janela de %d." % JANELA_CONVERGENCIA)

    pontos = coordenadas_por_rota(resultado["melhor_rota"])
    pontos_originais = coordenadas(distancias)
    grafico_convergencia(resultado)
    grafico_rota(resultado, pontos)
    destino = video(resultado, pontos, pontos_originais)

    resumo = {
        "cidades": int(len(distancias)),
        "formigas": N_FORMIGAS,
        "evaporacao": EVAPORACAO,
        "iteracoes": ITERACOES,
        "janela_convergencia": JANELA_CONVERGENCIA,
        "melhor_distancia": round(resultado["melhor_distancia"], 4),
        "distancia_inicial": round(float(resultado["curva"][0]), 4),
        "rota": [int(c) for c in resultado["melhor_rota"]],
        "iteracao_convergencia": resultado["iteracao_convergencia"],
        "primeira_estabilizacao": resultado["primeira_estabilizacao"],
        "ultima_melhora": resultado["ultima_melhora"],
        "convergiu": bool(resultado["convergiu"]),
        "feromonio_maximo": round(max(float(h["feromonio"].max())
                                      for h in resultado["historico"]), 2),
    }
    caminho = os.path.join(SAIDA, "resumo_parte1.json")
    with open(caminho, "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)

    print("")
    print("arquivos gerados:")
    print(" ", os.path.join(SAIDA, "parte1_convergencia.png"))
    print(" ", os.path.join(SAIDA, "parte1_melhor_rota.png"))
    print(" ", destino)


if __name__ == "__main__":
    main()
