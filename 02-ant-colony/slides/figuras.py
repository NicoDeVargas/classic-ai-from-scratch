import os
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)
from aco import ColoniaFormigas, carrega_matriz, coordenadas_por_rota

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
MATRIZ = os.path.join(RAIZ, "distancia_matrix.csv")
SEMENTE = 1


def desenha(pontos, tau, maximo, destino, rotulos=True, tamanho=6.4, fundo="white",
            invertido=False):
    n = len(pontos)
    pares = [(i, j) for i in range(n) for j in range(i + 1, n)]
    segmentos = np.array([[pontos[i], pontos[j]] for i, j in pares])
    valores = np.array([tau[i, j] for i, j in pares])
    intensidade = np.clip(valores / maximo, 0.0, 1.0) if maximo > 0 else np.zeros(len(pares))

    fig = plt.figure(figsize=(tamanho, tamanho))
    fig.patch.set_facecolor(fundo)
    ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
    ax.set_facecolor(fundo)

    cores = ([(v, v, v) for v in intensidade] if invertido
             else [(1.0 - v, 1.0 - v, 1.0 - v) for v in intensidade])
    ax.add_collection(LineCollection(segmentos, colors=cores,
                                     linewidths=0.25 + 4.5 * intensidade, zorder=1))
    ax.scatter(pontos[:, 0], pontos[:, 1], s=230,
               color=fundo if invertido else "white",
               edgecolors="white" if invertido else "#241F1C",
               linewidths=1.6, zorder=3)
    if rotulos:
        for i, (x, y) in enumerate(pontos):
            ax.text(x, y, str(i), ha="center", va="center", fontsize=9.5,
                    color="white" if invertido else "black", zorder=4)

    margem = 0.07 * max(np.ptp(pontos[:, 0]), np.ptp(pontos[:, 1]))
    ax.set_xlim(pontos[:, 0].min() - margem, pontos[:, 0].max() + margem)
    ax.set_ylim(pontos[:, 1].min() - margem, pontos[:, 1].max() + margem)
    ax.set_xticks([])
    ax.set_yticks([])
    for lado in ax.spines.values():
        lado.set_visible(False)
    fig.savefig(destino, dpi=170, facecolor=fundo)
    plt.close(fig)


def capa_video(mp4, destino, instante="11.5"):
    if not os.path.exists(mp4):
        print("video ainda nao existe; capa do video nao gerada")
        return
    import subprocess
    import imageio_ffmpeg
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-ss", instante, "-i", mp4,
                    "-frames:v", "1", destino], capture_output=True)


def main():
    os.makedirs(IMG, exist_ok=True)
    distancias = carrega_matriz(MATRIZ)
    resultado = ColoniaFormigas(distancias, n_formigas=20, evaporacao=0.5,
                                semente=SEMENTE).executa(historico=True)
    historico = resultado["historico"]
    pontos = coordenadas_por_rota(resultado["melhor_rota"])
    maximo = max(float(h["feromonio"].max()) for h in historico)

    inicial = np.full_like(distancias, 1.0)
    np.fill_diagonal(inicial, 0.0)
    desenha(pontos, inicial, maximo * 0.35, os.path.join(IMG, "grafo_inicial.png"))
    desenha(pontos, historico[-1]["feromonio"], maximo,
            os.path.join(IMG, "grafo_final.png"))
    desenha(pontos, historico[2]["feromonio"], maximo,
            os.path.join(IMG, "grafo_cedo.png"))
    desenha(pontos, historico[-1]["feromonio"], maximo,
            os.path.join(IMG, "grafo_capa.png"), rotulos=False,
            fundo="#241F1C", invertido=True)

    capa_video(os.path.join(RAIZ, "saida", "parte1_feromonio.mp4"),
               os.path.join(IMG, "video_capa.png"))

    print("figuras geradas em", IMG)
    print("feromonio maximo da execucao: %.2f" % maximo)


if __name__ == "__main__":
    main()
