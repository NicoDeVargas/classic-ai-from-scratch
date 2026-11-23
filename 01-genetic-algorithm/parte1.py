import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter, PillowWriter

from ag import AlgoritmoGenetico, schaffer_f6, avalia, no_maximo_global, LIMITE, TOLERANCIA

SAIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saida")
SEMENTE = 0


def grade():
    eixo = np.linspace(-LIMITE, LIMITE, 400)
    X, Y = np.meshgrid(eixo, eixo)
    return X, Y, schaffer_f6(X, Y)


def grafico_evolucao(historico):
    geracoes = [h["geracao"] for h in historico]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(geracoes, [h["melhor"] for h in historico], label="melhor da geração", color="#1b6ca8")
    ax.plot(geracoes, [h["media"] for h in historico], label="média da população", color="#e08c1a")
    ax.plot(geracoes, [h["pior"] for h in historico], label="pior da geração", color="#c0392b")
    ax.set_xlabel("Geração")
    ax.set_ylabel("Fitness")
    ax.set_title("Evolução do fitness (melhor, média e pior)")
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.3)
    ax.legend(loc="center", bbox_to_anchor=(0.5, 0.30), ncol=3)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte1_fitness_populacao.png"), dpi=150)
    plt.close(fig)


def grafico_melhor(historico):
    geracoes = [h["geracao"] for h in historico]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(geracoes, [h["melhor"] for h in historico], color="#1b6ca8")
    ax.set_xlabel("Geração")
    ax.set_ylabel("Fitness do melhor indivíduo")
    ax.set_title("Fitness do melhor indivíduo por geração")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte1_melhor_individuo.png"), dpi=150)
    plt.close(fig)


def video(historico):
    X, Y, Z = grade()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.contourf(X, Y, Z, levels=40, cmap="viridis")
    ax.contour(X, Y, Z, levels=20, colors="white", linewidths=0.4, alpha=0.5)
    ax.plot(0, 0, marker="*", markersize=20, linestyle="none", markerfacecolor="white",
            markeredgecolor="#1B1035", markeredgewidth=1.0, label="máximo global")
    dispersao = ax.scatter([], [], s=28, color="white", edgecolors="black", linewidths=0.6,
                           label="população")
    melhor = ax.scatter([], [], s=150, color="#FF3B3B", edgecolors="white", linewidths=1.4,
                        zorder=5, label="melhor da geração")
    ax.set_xlim(-LIMITE, LIMITE)
    ax.set_ylim(-LIMITE, LIMITE)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc="upper right")
    titulo = ax.set_title("")

    zoom = ax.inset_axes([0.015, 0.015, 0.30, 0.30])
    janela = 0.4
    ze = np.linspace(-janela, janela, 200)
    ZX, ZY = np.meshgrid(ze, ze)
    zoom.contourf(ZX, ZY, schaffer_f6(ZX, ZY), levels=40, cmap="viridis")
    zoom.add_patch(plt.Rectangle((-TOLERANCIA, -TOLERANCIA), 2 * TOLERANCIA, 2 * TOLERANCIA,
                                 fill=False, edgecolor="white", linewidth=1.6, linestyle="--"))
    zoom.plot(0, 0, marker="*", markersize=11, linestyle="none", markerfacecolor="white",
              markeredgecolor="#1B1035", markeredgewidth=0.8)
    zoom_pop = zoom.scatter([], [], s=22, color="white", edgecolors="black", linewidths=0.5)
    zoom_melhor = zoom.scatter([], [], s=110, color="#FF3B3B", edgecolors="white", linewidths=1.2,
                               zorder=5)
    zoom.set_xlim(-janela, janela)
    zoom.set_ylim(-janela, janela)
    zoom.set_xticks([])
    zoom.set_yticks([])
    for lado in zoom.spines.values():
        lado.set_edgecolor("white")
        lado.set_linewidth(1.2)
    zoom_titulo = zoom.text(0.5, 0.955, "", transform=zoom.transAxes, ha="center", va="top",
                            fontsize=8.5, color="white", zorder=6,
                            bbox=dict(boxstyle="round,pad=0.22", facecolor="#1B1035",
                                      edgecolor="none", alpha=0.85))

    def frame(i):
        h = historico[i]
        pontos = h["pontos"]
        aptidoes = avalia(pontos)
        indice = int(np.argmax(aptidoes))

        dispersao.set_offsets(pontos)
        melhor.set_offsets(pontos[indice:indice + 1])
        zoom_pop.set_offsets(pontos)
        zoom_melhor.set_offsets(pontos[indice:indice + 1])

        dentro = np.sum((np.abs(pontos[:, 0]) <= TOLERANCIA) & (np.abs(pontos[:, 1]) <= TOLERANCIA))
        zoom_titulo.set_text("zoom ±%.1f  ·  %d na caixa ±%.2f" % (janela, dentro, TOLERANCIA))
        titulo.set_text("Geração %d  |  melhor fitness = %.6f  |  x = %+.4f  y = %+.4f"
                        % (h["geracao"], h["melhor"], pontos[indice, 0], pontos[indice, 1]))
        return dispersao, melhor, titulo

    animacao = FuncAnimation(fig, frame, frames=len(historico), interval=66, blit=False)

    destino = os.path.join(SAIDA, "parte1_populacao.mp4")
    try:
        import imageio_ffmpeg
        matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
        animacao.save(destino, writer=FFMpegWriter(fps=15, bitrate=2400))
    except Exception as erro:
        print("ffmpeg indisponivel (%s); gerando GIF" % erro)
        destino = os.path.join(SAIDA, "parte1_populacao.gif")
        animacao.save(destino, writer=PillowWriter(fps=15))
    plt.close(fig)
    return destino


def main():
    os.makedirs(SAIDA, exist_ok=True)
    algoritmo = AlgoritmoGenetico(semente=SEMENTE)
    resultado = algoritmo.executa(historico=True)
    historico = resultado["historico"]

    print("Parte 1 - Schaffer's f6")
    print("populacao=%d  geracoes=%d  busca=[%g, %g]" % (
        algoritmo.tamanho_populacao, algoritmo.geracoes, -LIMITE, LIMITE))
    print("melhor individuo: x = %.6f   y = %.6f" % (resultado["x"], resultado["y"]))
    print("fitness: %.8f" % resultado["aptidao"])
    print("dentro do maximo global (|x|,|y| <= 0.09): %s" % (
        "sim" if no_maximo_global(resultado["x"], resultado["y"]) else "nao"))

    grafico_evolucao(historico)
    grafico_melhor(historico)
    destino = video(historico)

    print("")
    print("arquivos gerados:")
    print(" ", os.path.join(SAIDA, "parte1_fitness_populacao.png"))
    print(" ", os.path.join(SAIDA, "parte1_melhor_individuo.png"))
    print(" ", destino)


if __name__ == "__main__":
    main()
