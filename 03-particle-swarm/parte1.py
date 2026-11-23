import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.ticker import NullFormatter
from matplotlib.animation import FuncAnimation, FFMpegWriter

from pso import (EnxameParticulas, rastrigin, LIMITE, N_PARTICULAS, ITERACOES, W_MAX, W_MIN,
                 FRACAO_VMAX, TOLERANCIA)

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "saida")
SEMENTE = 2
C1 = 2.0
C2 = 2.0

SUBQUADROS = 3
PAUSA_INICIO = 24
PAUSA_FIM = 60
RASTRO = 7
PISO = 1e-10

VERMELHO = "#ff3b30"
AZUL = "#1b6ca8"


def malha(n=500, a=-LIMITE, b=LIMITE, c=None, d=None):
    c = a if c is None else c
    d = b if d is None else d
    xs = np.linspace(a, b, n)
    ys = np.linspace(c, d, n)
    X, Y = np.meshgrid(xs, ys)
    return X, Y, rastrigin(np.stack([X, Y], axis=-1))


def contorno(ax, X, Y, Z):
    ax.contourf(X, Y, Z, levels=40, cmap="viridis")
    ax.contour(X, Y, Z, levels=12, colors="white", linewidths=0.35, alpha=0.35)
    ax.set_xlim(-LIMITE, LIMITE)
    ax.set_ylim(-LIMITE, LIMITE)
    ax.set_aspect("equal")


def formata_f(f):
    if f < 1e-12:
        return "< 1e-12"
    if f < 1e-2:
        return "= %.1e" % f
    return "= %.3f" % f


def coordenada(v):
    return "%.1e" % v if abs(v) < 1e-3 else "%.4f" % v


def linha_do_tempo(resultado):
    historico = resultado["historico"]
    posicoes, iteracoes, gbests = [], [], []
    for _ in range(PAUSA_INICIO):
        posicoes.append(historico[0]["x"])
        iteracoes.append(0)
        gbests.append(0)
    for k in range(len(historico) - 1):
        for s in range(SUBQUADROS):
            t = s / SUBQUADROS
            posicoes.append((1 - t) * historico[k]["x"] + t * historico[k + 1]["x"])
            iteracoes.append(k if s == 0 else k + 1)
            gbests.append(k)
    for _ in range(PAUSA_FIM):
        posicoes.append(historico[-1]["x"])
        iteracoes.append(len(historico) - 1)
        gbests.append(len(historico) - 1)
    return np.array(posicoes), np.array(iteracoes), np.array(gbests)


def janelas_zoom(posicoes, gbests, historico):
    centros, metades = [], []
    centro = np.zeros(2)
    log_metade = np.log(LIMITE)
    for q in range(len(posicoes)):
        g = historico[gbests[q]]["g"]
        distancias = np.linalg.norm(posicoes[q] - g, axis=1)
        alvo = np.clip(1.3 * np.quantile(distancias, 0.6), 0.02, LIMITE)
        log_metade += 0.12 * (np.log(alvo) - log_metade)
        centro = centro + 0.25 * (g - centro)
        h = float(np.exp(log_metade))
        c = np.clip(centro, -LIMITE + h, LIMITE - h) if h < LIMITE else np.zeros(2)
        centros.append(c.copy())
        metades.append(min(h, LIMITE))
    return np.array(centros), np.array(metades)


def gera_video(resultado, destino, rotulo):
    historico = resultado["historico"]
    posicoes, iteracoes, gbests = linha_do_tempo(resultado)
    centros, metades = janelas_zoom(posicoes, gbests, historico)
    curva = np.maximum(resultado["curva"], PISO)
    raios = resultado["raio"]
    passos = np.arange(len(curva))

    plt.rcParams.update({"font.size": 15})
    fig = plt.figure(figsize=(16, 9), dpi=100)
    fig.patch.set_facecolor("white")

    X, Y, Z = malha()
    principal = fig.add_axes([0.035, 0.07, 0.50, 0.80])
    contorno(principal, X, Y, Z)
    principal.set_xlabel("x")
    principal.set_ylabel("y")
    principal.plot([0], [0], marker="+", markersize=22, markeredgewidth=2.6, color="white",
                   zorder=6)
    rastros = LineCollection([], linewidths=1.6, zorder=7)
    principal.add_collection(rastros)
    pontos = principal.scatter([], [], s=70, color="white", edgecolors="black", linewidths=1.1,
                               zorder=8)
    estrela = principal.scatter([], [], s=420, marker="*", color=VERMELHO, edgecolors="white",
                                linewidths=1.3, zorder=9)
    moldura, = principal.plot([], [], color="white", linestyle="--", linewidth=1.6, zorder=5)

    zoom = fig.add_axes([0.575, 0.395, 0.27, 0.48])
    zoom.set_xticks([])
    zoom.set_yticks([])
    for lado in zoom.spines.values():
        lado.set_edgecolor("#333333")
        lado.set_linewidth(1.6)
    imagem = zoom.imshow(np.zeros((2, 2)), origin="lower", cmap="viridis", aspect="auto",
                         interpolation="bilinear")
    zoom_mino, = zoom.plot([0], [0], marker="+", markersize=26, markeredgewidth=2.8,
                           color="white", zorder=6)
    zoom_pontos = zoom.scatter([], [], s=90, color="white", edgecolors="black", linewidths=1.1,
                               zorder=8)
    zoom_estrela = zoom.scatter([], [], s=520, marker="*", color=VERMELHO, edgecolors="white",
                                linewidths=1.3, zorder=9)
    escala = zoom.text(0.02, 0.03, "", transform=zoom.transAxes, fontsize=13, color="white",
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.55,
                                 edgecolor="none"), zorder=10)
    zoom.set_title("zoom no gbest (acompanha o enxame)", fontsize=14, pad=6)
    linhas_zoom = []

    painel_f = fig.add_axes([0.62, 0.075, 0.16, 0.25])
    painel_r = fig.add_axes([0.825, 0.075, 0.15, 0.25])
    for painel, serie, nome in ((painel_f, curva, "f(gbest)"), (painel_r, np.maximum(raios, PISO),
                                                                "raio do enxame")):
        painel.plot(passos, serie, color="#cccccc", linewidth=1.2)
        painel.set_yscale("log")
        painel.set_xlim(0, len(curva) - 1)
        painel.set_title(nome, fontsize=14, pad=5)
        painel.set_xlabel("iteração", fontsize=12)
        painel.tick_params(labelsize=11)
        painel.yaxis.set_minor_formatter(NullFormatter())
        painel.grid(alpha=0.3)
    avanco_f, = painel_f.plot([], [], color=VERMELHO, linewidth=2.2)
    avanco_r, = painel_r.plot([], [], color=AZUL, linewidth=2.2)
    painel_f.axhline(TOLERANCIA, color="#555555", linestyle=":", linewidth=1.2)
    painel_f.text(len(curva) - 2, TOLERANCIA * 1.6, "f = 0.01", fontsize=10, color="#555555",
                  ha="right", va="bottom")

    legenda = fig.add_axes([0.855, 0.395, 0.135, 0.48])
    legenda.set_xlim(0, 1)
    legenda.set_ylim(0, 1)
    legenda.axis("off")
    itens = [("o", "white", 11, "partícula"), ("*", VERMELHO, 22, "melhor global\n(gbest)"),
             ("+", "black", 18, "mínimo global\n(0, 0)")]
    for i, (marca, cor, tam, texto) in enumerate(itens):
        y = 0.9 - i * 0.19
        legenda.plot([0.1], [y], marker=marca, markersize=tam, color=cor, markeredgecolor="black",
                     markeredgewidth=1.2 if marca != "+" else 2.6, linestyle="none")
        legenda.text(0.24, y, texto, fontsize=13, va="center")
    legenda.plot([0.02, 0.18], [0.33, 0.33], color="#999999", linewidth=1.8)
    legenda.text(0.24, 0.33, "rastro das\núltimas posições", fontsize=13, va="center")
    legenda.plot([0.02, 0.18], [0.14, 0.14], color="#555555", linestyle="--", linewidth=1.8)
    legenda.text(0.24, 0.14, "área do zoom", fontsize=13, va="center")

    titulo = fig.text(0.035, 0.955, "", fontsize=19, fontweight="bold", va="center")
    subtitulo = fig.text(0.035, 0.912, "", fontsize=15, color="#444444", va="center")
    fig.text(0.575, 0.955, rotulo, fontsize=17, fontweight="bold", color="#222222", va="center")

    def frame(q):
        k = iteracoes[q]
        gk = gbests[q]
        h = historico[gk]
        g = h["g"]
        inicio = max(0, q - RASTRO)
        trecho = posicoes[inicio:q + 1]
        segmentos, cores = [], []
        for t in range(len(trecho) - 1):
            alfa = 0.85 * (t + 1) / max(1, len(trecho) - 1)
            for i in range(trecho.shape[1]):
                segmentos.append([trecho[t, i], trecho[t + 1, i]])
                cores.append((1, 1, 1, alfa))
        rastros.set_segments(segmentos)
        rastros.set_color(cores)
        pontos.set_offsets(posicoes[q])
        estrela.set_offsets([g])

        c, m = centros[q], metades[q]
        if m < LIMITE * 0.92:
            moldura.set_data([c[0] - m, c[0] + m, c[0] + m, c[0] - m, c[0] - m],
                             [c[1] - m, c[1] - m, c[1] + m, c[1] + m, c[1] - m])
        else:
            moldura.set_data([], [])

        Xz, Yz, Zz = malha(140, c[0] - m, c[0] + m, c[1] - m, c[1] + m)
        imagem.set_data(Zz)
        imagem.set_extent((c[0] - m, c[0] + m, c[1] - m, c[1] + m))
        imagem.set_clim(Zz.min(), Zz.max())
        while linhas_zoom:
            linhas_zoom.pop().remove()
        linhas_zoom.append(zoom.contour(Xz, Yz, Zz, levels=10, colors="white", linewidths=0.5,
                                        alpha=0.45))
        zoom.set_xlim(c[0] - m, c[0] + m)
        zoom.set_ylim(c[1] - m, c[1] + m)
        zoom_pontos.set_offsets(posicoes[q])
        zoom_estrela.set_offsets([g])
        largura = 2 * m
        molde = "%.2f" if largura >= 0.1 else "%.3f"
        escala.set_text("janela: %s × %s" % (molde % largura, molde % largura))

        avanco_f.set_data(passos[:gk + 1], curva[:gk + 1])
        avanco_r.set_data(passos[:k + 1], np.maximum(raios[:k + 1], PISO))

        titulo.set_text("Iteração %d de %d   ·   f(gbest) %s"
                        % (k, ITERACOES, formata_f(h["fg"])))
        subtitulo.set_text("gbest = (%s, %s)   ·   inércia w = %.3f   ·   %d partículas"
                           % (coordenada(g[0]), coordenada(g[1]), historico[k]["w"], N_PARTICULAS))
        return []

    animacao = FuncAnimation(fig, frame, frames=len(posicoes), blit=False)
    import imageio_ffmpeg
    matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
    animacao.save(destino, writer=FFMpegWriter(fps=24, bitrate=3500))
    plt.close(fig)
    return destino


def grafico_funcao():
    X, Y, Z = malha(400)
    fig = plt.figure(figsize=(13, 5.6))
    ax3 = fig.add_subplot(1, 2, 1, projection="3d")
    ax3.plot_surface(X, Y, Z, cmap="viridis", linewidth=0, antialiased=True, rstride=4, cstride=4)
    ax3.set_title("Rastrigin em 3D")
    ax3.set_xlabel("x")
    ax3.set_ylabel("y")
    ax3.view_init(elev=32, azim=-60)
    ax = fig.add_subplot(1, 2, 2)
    contorno(ax, X, Y, Z)
    ax.plot([0], [0], marker="+", markersize=18, markeredgewidth=2.4, color=VERMELHO)
    ax.set_title("Contorno — mínimo global em (0, 0), f = 0")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "rastrigin.png"), dpi=150)
    plt.close(fig)


def grafico_convergencia(resultado):
    curva = np.maximum(resultado["curva"], PISO)
    fig, eixos = plt.subplots(1, 2, figsize=(13, 4.8))
    eixos[0].plot(curva, color=VERMELHO, linewidth=2.2)
    eixos[0].axhline(TOLERANCIA, color="#555555", linestyle=":", linewidth=1.3,
                     label="tolerância de convergência (f < %g)" % TOLERANCIA)
    eixos[0].set_yscale("log")
    eixos[0].set_title("Melhor valor encontrado, f(gbest)")
    eixos[0].legend(loc="upper right", fontsize=10)
    eixos[1].plot(np.maximum(resultado["raio"], PISO), color=AZUL, linewidth=2.2)
    eixos[1].set_yscale("log")
    eixos[1].set_title("Raio do enxame (maior distância entre duas partículas)")
    for ax in eixos:
        ax.set_xlabel("Iteração")
        ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte1_convergencia.png"), dpi=150)
    plt.close(fig)


def grafico_instantes(resultado, momentos=(0, 10, 30, 100)):
    X, Y, Z = malha(400)
    fig, eixos = plt.subplots(1, len(momentos), figsize=(4.2 * len(momentos), 4.6))
    for ax, k in zip(eixos, momentos):
        h = resultado["historico"][k]
        contorno(ax, X, Y, Z)
        ax.plot([0], [0], marker="+", markersize=16, markeredgewidth=2.2, color="white")
        ax.scatter(h["x"][:, 0], h["x"][:, 1], s=40, color="white", edgecolors="black",
                   linewidths=0.9, zorder=3)
        ax.scatter([h["g"][0]], [h["g"][1]], s=260, marker="*", color=VERMELHO,
                   edgecolors="white", linewidths=1.0, zorder=4)
        ax.set_title("iteração %d — f(gbest) %s" % (k, formata_f(h["fg"])), fontsize=12)
        ax.set_xticks([])
        ax.set_yticks([])
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte1_instantes.png"), dpi=150)
    plt.close(fig)


def resumo_execucao(resultado):
    return {
        "f_gbest": resultado["f_gbest"],
        "gbest": [float(v) for v in resultado["gbest"]],
        "convergiu": resultado["convergiu"],
        "iteracao_tolerancia": resultado["iteracao_tolerancia"],
        "raio_final": float(resultado["raio"][-1]),
        "raio_inicial": float(resultado["raio"][0]),
        "f_inicial": float(resultado["curva"][0]),
    }


def main():
    os.makedirs(SAIDA, exist_ok=True)
    enxame = EnxameParticulas(C1, C2, semente=SEMENTE)
    resultado = enxame.executa(historico=True)

    print("Parte 1 - PSO na funcao de Rastrigin (n = 2)")
    print("particulas=%d  iteracoes=%d  c1=%g  c2=%g  w: %.1f -> %.1f  vmax=%.3f  semente=%d"
          % (N_PARTICULAS, ITERACOES, C1, C2, W_MAX, W_MIN, enxame.vmax, SEMENTE))
    print("")
    print("melhor posicao encontrada: (%.6f, %.6f)" % tuple(resultado["gbest"]))
    print("valor da funcao nessa posicao: %.3e" % resultado["f_gbest"])
    if resultado["convergiu"]:
        print("CONVERGIU para o minimo global (f < %g) na iteracao %d"
              % (TOLERANCIA, resultado["iteracao_tolerancia"]))
    else:
        print("NAO convergiu para o minimo global (f >= %g)" % TOLERANCIA)
    print("raio do enxame: %.3f no inicio, %.3f no fim" % (resultado["raio"][0], resultado["raio"][-1]))

    grafico_funcao()
    grafico_convergencia(resultado)
    grafico_instantes(resultado)
    destino = gera_video(resultado, os.path.join(SAIDA, "parte1_enxame.mp4"),
                         "c1 = %g, c2 = %g  ·  semente %d" % (C1, C2, SEMENTE))

    resumo = {
        "semente": SEMENTE, "c1": C1, "c2": C2, "particulas": N_PARTICULAS,
        "iteracoes": ITERACOES, "w_max": W_MAX, "w_min": W_MIN, "fracao_vmax": FRACAO_VMAX,
        "vmax": enxame.vmax, "limite": LIMITE, "tolerancia": TOLERANCIA,
    }
    resumo.update(resumo_execucao(resultado))
    with open(os.path.join(SAIDA, "resumo_parte1.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)

    print("")
    print("arquivos gerados em", SAIDA)
    print("  rastrigin.png, parte1_convergencia.png, parte1_instantes.png,", os.path.basename(destino))


if __name__ == "__main__":
    main()
