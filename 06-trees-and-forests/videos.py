import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter
from matplotlib.colors import LinearSegmentedColormap

from arvore import FEATURES, ArvoreRegressao, Floresta, carrega, divide, mae
from trabalho import SAIDA, SEMENTES, CINZA, VERMELHO, VERDE, num, estilo

FPS = 20
EIXOS = ["bmi", "s5"]
MAPA = LinearSegmentedColormap.from_list("ufci", ["#f4faf8", "#bfe3dd", "#75bfb4", "#3f8f8a", "#152c43"])
GRADE = 220


def prepara():
    X, y = carrega()
    colunas = [FEATURES.index(f) for f in EIXOS]
    treino, teste = divide(len(y), SEMENTES[-1])
    Xa, ya, Xt, yt = X[treino][:, colunas], y[treino], X[teste][:, colunas], y[teste]
    gx = np.linspace(Xa[:, 0].min() - 0.5, Xa[:, 0].max() + 0.5, GRADE)
    gy = np.linspace(Xa[:, 1].min() - 0.1, Xa[:, 1].max() + 0.1, GRADE)
    malha = np.column_stack([m.ravel() for m in np.meshgrid(gx, gy)])
    return Xa, ya, Xt, yt, gx, gy, malha


def desenha_mapa(ax, valores, gx, gy, Xa, ya, titulo):
    ax.clear()
    ax.imshow(valores.reshape(GRADE, GRADE), origin="lower", extent=(gx[0], gx[-1], gy[0], gy[-1]), aspect="auto",
              cmap=MAPA, vmin=40, vmax=300, interpolation="nearest")
    ax.scatter(Xa[:, 0], Xa[:, 1], c=ya, cmap=MAPA, vmin=40, vmax=300, s=22, edgecolors="#152c43", linewidths=0.6)
    ax.set_xlabel("bmi (IMC)")
    ax.set_ylabel("s5 (log dos triglicerídeos)")
    ax.set_title(titulo, fontsize=14, fontweight="bold")


def video_arvore(escritor):
    Xa, ya, Xt, yt, gx, gy, malha = prepara()
    profundidades = list(range(0, 11))
    modelos = [ArvoreRegressao(p).treina(Xa, ya) for p in profundidades]
    erro_treino = [mae(ya, m.preve(Xa)) for m in modelos]
    erro_teste = [mae(yt, m.preve(Xt)) for m in modelos]
    melhor = int(np.argmin(erro_teste))

    fig = plt.figure(figsize=(16, 9), dpi=100)
    titulo = fig.text(0.5, 0.95, "", ha="center", fontsize=21, fontweight="bold")
    fig.text(0.5, 0.905, "cada ponto é um paciente do treino; a cor é a progressão da doença (claro = baixa, escuro = alta); o fundo é o que a árvore prevê",
             ha="center", fontsize=12.5, color="#555555")
    ax_m = fig.add_axes([0.06, 0.09, 0.50, 0.76])
    ax_e = fig.add_axes([0.64, 0.40, 0.32, 0.45])
    info = fig.text(0.64, 0.30, "", fontsize=15, va="top", linespacing=1.6)
    destino = os.path.join(SAIDA, "arvore_crescendo.mp4")
    with escritor.saving(fig, destino, 100):
        for i, p in enumerate(profundidades):
            titulo.set_text("A árvore crescendo: profundidade %d" % p)
            desenha_mapa(ax_m, modelos[i].preve(malha), gx, gy, Xa, ya, "%d regiões" % modelos[i].folhas())
            ax_e.clear()
            ax_e.plot(profundidades[:i + 1], erro_treino[:i + 1], "o-", color=CINZA, linewidth=2.4, label="erro no treino")
            ax_e.plot(profundidades[:i + 1], erro_teste[:i + 1], "o-", color=VERMELHO, linewidth=2.4, label="erro no teste")
            ax_e.set_xlim(-0.3, 10.3)
            ax_e.set_ylim(0, 75)
            ax_e.set_xticks(profundidades)
            ax_e.set_xlabel("profundidade")
            ax_e.set_ylabel("MAE")
            ax_e.legend(loc="lower left", fontsize=12)
            estilo(ax_e)
            texto = "regiões (folhas): %d\nerro no treino: %s\nerro no teste: %s" % (
                modelos[i].folhas(), num(erro_treino[i]), num(erro_teste[i]))
            if i > melhor:
                texto += "\n\no treino continua melhorando,\nmas o teste piora desde a profundidade %d:\na árvore está decorando os pacientes" % profundidades[melhor]
            info.set_text(texto)
            for _ in range(int(FPS * (1.6 if i < len(profundidades) - 1 else 4))):
                escritor.grab_frame()
    plt.close(fig)
    return {"arquivo": "arvore_crescendo.mp4", "melhor": profundidades[melhor], "teste_melhor": erro_teste[melhor],
            "teste_final": erro_teste[-1], "treino_final": erro_treino[-1], "folhas_final": modelos[-1].folhas(),
            "duracao_s": round((len(profundidades) - 1) * 1.6 + 4)}


def video_floresta(escritor):
    Xa, ya, Xt, yt, gx, gy, malha = prepara()
    floresta = Floresta(100, None, 1, SEMENTES[-1]).treina(Xa, ya)
    mapas = floresta.preve_cada(malha)
    testes = floresta.preve_cada(Xt)
    acumulado = np.cumsum(mapas, axis=0) / np.arange(1, 101)[:, None]
    erro_media = [mae(yt, testes[:n].mean(axis=0)) for n in range(1, 101)]
    erro_uma = [mae(yt, t) for t in testes]

    fig = plt.figure(figsize=(16, 9), dpi=100)
    titulo = fig.text(0.5, 0.95, "", ha="center", fontsize=21, fontweight="bold")
    fig.text(0.5, 0.905, "cada árvore sozinha é um mapa cheio de recortes; a média de muitas árvores vira um mapa suave, que erra menos",
             ha="center", fontsize=12.5, color="#555555")
    ax_u = fig.add_axes([0.05, 0.40, 0.42, 0.45])
    ax_f = fig.add_axes([0.54, 0.40, 0.42, 0.45])
    ax_e = fig.add_axes([0.08, 0.08, 0.86, 0.22])
    destino = os.path.join(SAIDA, "floresta_media.mp4")
    quadros = 0
    with escritor.saving(fig, destino, 100):
        for n in range(1, 101):
            titulo.set_text("A floresta: a média de %d árvore%s" % (n, "s" if n > 1 else ""))
            desenha_mapa(ax_u, mapas[n - 1], gx, gy, Xa, ya, "árvore nº %d sozinha: erro %s" % (n, num(erro_uma[n - 1])))
            desenha_mapa(ax_f, acumulado[n - 1], gx, gy, Xa, ya, "média das %d: erro %s" % (n, num(erro_media[n - 1])))
            ax_e.clear()
            ax_e.plot(range(1, n + 1), erro_uma[:n], ".", color=CINZA, markersize=7, label="cada árvore sozinha")
            ax_e.plot(range(1, n + 1), erro_media[:n], "-", color=VERDE, linewidth=2.8, label="média das árvores até aqui")
            ax_e.set_xlim(0, 101)
            ax_e.set_ylim(40, 75)
            ax_e.set_xlabel("número de árvores")
            ax_e.set_ylabel("MAE no teste")
            ax_e.legend(loc="upper right", fontsize=12, ncol=2)
            estilo(ax_e)
            repete = 14 if n <= 10 else (3 if n < 100 else FPS * 4)
            quadros += repete
            for _ in range(repete):
                escritor.grab_frame()
    plt.close(fig)
    return {"arquivo": "floresta_media.mp4", "erro_uma": float(np.mean(erro_uma)), "erro_100": erro_media[-1],
            "erro_10": erro_media[9], "duracao_s": round(quadros / FPS)}


def main():
    import imageio_ffmpeg
    matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
    plt.rcParams.update({"font.size": 12})
    resumo = {"features": EIXOS, "arvore": video_arvore(FFMpegWriter(fps=FPS, bitrate=4000)),
              "floresta": video_floresta(FFMpegWriter(fps=FPS, bitrate=4000))}
    with open(os.path.join(SAIDA, "resumo_videos.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)
    print(resumo)


if __name__ == "__main__":
    main()
