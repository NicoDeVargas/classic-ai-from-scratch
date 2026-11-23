import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

from pso import EnxameParticulas, TOLERANCIA, ITERACOES
from parte1 import (SAIDA, SEMENTE, VERMELHO, AZUL, PISO, gera_video, linha_do_tempo, malha,
                    contorno, formata_f, resumo_execucao)

PARES = [(0, 1), (1, 0), (1, 1), (1, 0.1), (2, 2), (4, 4)]
EXECUCOES = 100
TURMAS = 10
BASE_TURMAS = 10000
BACIA = 0.9
TOLERANCIAS = [BACIA, 1e-2, 1e-4, 1e-6]
FRACOES_VMAX = [0.1, 0.2, 0.3, 1.0, None]
CONSTRICOES = [1.0, 0.9, 0.8, 0.729, 0.6, 0.5, 0.4, 0.3]
CHI_IDEAL = 0.6
CHI_DEMAIS = 0.3
SEMENTE_CONSTRICAO = 0
CORES = ["#8e44ad", "#7f8c8d", "#2e86c1", "#e67e22", "#27ae60", "#c0392b"]


def nome(par):
    return "[%g, %g]" % par


def arquivo(par):
    return "parte2_c1-%g_c2-%g.mp4" % par


def bloco(args):
    par, sementes, extra = args
    resultados = [EnxameParticulas(par[0], par[1], semente=s, **extra).executa() for s in sementes]
    return {
        "f": np.array([r["f_gbest"] for r in resultados]),
        "iteracao": [r["iteracao_tolerancia"] for r in resultados],
        "curvas": np.array([r["curva"] for r in resultados]),
        "raios": np.array([r["raio"] for r in resultados]),
    }


def roda(ex, tarefas):
    return list(ex.map(bloco, tarefas))


def grafico_barras(principais, turmas):
    fig, ax = plt.subplots(figsize=(12, 5.6))
    posicoes = np.arange(len(PARES))
    convergiu = [int((principais[p]["f"] < TOLERANCIA).sum()) for p in PARES]
    bacia = [int((principais[p]["f"] < BACIA).sum()) for p in PARES]
    ax.bar(posicoes, bacia, width=0.62, color="#d5dbe0", label="gbest chegou à região do mínimo global (f < %g)" % BACIA)
    ax.bar(posicoes, convergiu, width=0.62, color=CORES, label="convergiu para o mínimo global (f < %g)" % TOLERANCIA)
    for i, p in enumerate(PARES):
        faixa = [int((t["f"] < TOLERANCIA).sum()) for t in turmas[p]]
        ax.plot([i, i], [min(faixa), max(faixa)], color="black", linewidth=1.6)
        ax.plot([i - 0.08, i + 0.08], [min(faixa)] * 2, color="black", linewidth=1.6)
        ax.plot([i - 0.08, i + 0.08], [max(faixa)] * 2, color="black", linewidth=1.6)
        ax.text(i + 0.12, max(convergiu[i], max(faixa)) + 1.5, str(convergiu[i]), ha="left",
                va="bottom", fontsize=15, fontweight="bold")
    ax.plot([], [], color="black", linewidth=1.6,
            label="faixa em %d outros lotes de %d execuções" % (TURMAS, EXECUCOES))
    ax.set_xticks(posicoes)
    ax.set_xticklabels(["c1, c2 = %s" % nome(p) for p in PARES], fontsize=12)
    ax.set_ylabel("execuções (de %d)" % EXECUCOES)
    ax.set_ylim(0, 112)
    ax.set_title("Convergência para o mínimo global em %d execuções por par" % EXECUCOES)
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte2_convergencias.png"), dpi=150)
    plt.close(fig)


def grafico_curvas(principais):
    fig, eixos = plt.subplots(1, 2, figsize=(13, 5.2))
    passos = np.arange(ITERACOES + 1)
    for p, cor in zip(PARES, CORES):
        curvas = np.maximum(principais[p]["curvas"], PISO)
        raios = np.maximum(principais[p]["raios"], PISO)
        eixos[0].plot(passos, np.median(curvas, axis=0), color=cor, linewidth=2.2, label=nome(p))
        eixos[1].plot(passos, np.median(raios, axis=0), color=cor, linewidth=2.2, label=nome(p))
    eixos[0].axhline(TOLERANCIA, color="#555555", linestyle=":", linewidth=1.3)
    eixos[0].set_title("f(gbest) — mediana das %d execuções" % EXECUCOES)
    eixos[0].text(0.98, 0.02, "valores abaixo de 1e-10 desenhados em 1e-10", transform=eixos[0].transAxes,
                  ha="right", va="bottom", fontsize=9, color="#777777")
    eixos[1].set_title("Raio do enxame — mediana das %d execuções" % EXECUCOES)
    for ax in eixos:
        ax.set_yscale("log")
        ax.set_xlabel("Iteração")
        ax.grid(alpha=0.3)
    eixos[0].legend(title="c1, c2", fontsize=10, loc="lower left")
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte2_curvas.png"), dpi=150)
    plt.close(fig)


def grafico_constricao(constricao):
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(CONSTRICOES))
    conv = [constricao[c]["convergiu"] for c in CONSTRICOES]
    bac = [constricao[c]["bacia"] for c in CONSTRICOES]
    ax.bar(x, bac, width=0.6, color="#d5dbe0", label="chegou à região do mínimo global")
    ax.bar(x, conv, width=0.6, color="#c0392b", label="convergiu (f < %g)" % TOLERANCIA)
    for i, v in enumerate(conv):
        ax.text(i, v + 2.5, str(v), ha="center", va="bottom", fontsize=14, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["sem\nconstrição" if c == 1.0 else "χ = %g" % c for c in CONSTRICOES])
    ax.set_ylim(0, 112)
    ax.set_ylabel("execuções (de %d)" % EXECUCOES)
    ax.set_title("c1 = c2 = 4 com fator de constrição χ multiplicando a nova velocidade")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "parte2_constricao.png"), dpi=150)
    plt.close(fig)


def gera_grade(resultados, destino):
    linhas = {p: linha_do_tempo(resultados[p]) for p in PARES}
    total = len(next(iter(linhas.values()))[0])
    X, Y, Z = malha(300)
    plt.rcParams.update({"font.size": 15})
    fig, eixos = plt.subplots(2, 3, figsize=(16, 9), dpi=100)
    fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.02, wspace=0.05, hspace=0.16)
    artistas = {}
    for ax, p in zip(eixos.flat, PARES):
        contorno(ax, X, Y, Z)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.plot([0], [0], marker="+", markersize=16, markeredgewidth=2.2, color="white", zorder=5)
        pontos = ax.scatter([], [], s=34, color="white", edgecolors="black", linewidths=0.8, zorder=6)
        estrela = ax.scatter([], [], s=240, marker="*", color=VERMELHO, edgecolors="white",
                             linewidths=1.0, zorder=7)
        rotulo = ax.set_title("", fontsize=15)
        artistas[p] = (pontos, estrela, rotulo)
    titulo = fig.text(0.5, 0.95, "", ha="center", fontsize=20, fontweight="bold")
    fig.text(0.5, 0.905, "mesmo enxame inicial (semente %d) nos seis pares — só c1 e c2 mudam" % SEMENTE,
             ha="center", fontsize=15, color="#444444")

    def frame(q):
        for p in PARES:
            posicoes, iteracoes, gbests = linhas[p]
            h = resultados[p]["historico"][gbests[q]]
            pontos, estrela, rotulo = artistas[p]
            pontos.set_offsets(posicoes[q])
            estrela.set_offsets([h["g"]])
            rotulo.set_text("c1, c2 = %s   ·   f(gbest) %s" % (nome(p), formata_f(h["fg"])))
        titulo.set_text("Iteração %d de %d" % (linhas[PARES[0]][1][q], ITERACOES))
        return []

    animacao = FuncAnimation(fig, frame, frames=total, blit=False)
    import imageio_ffmpeg
    matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
    animacao.save(destino, writer=FFMpegWriter(fps=24, bitrate=4500))
    plt.close(fig)
    return destino


def video_par(par):
    resultado = EnxameParticulas(par[0], par[1], semente=SEMENTE).executa(historico=True)
    gera_video(resultado, os.path.join(SAIDA, arquivo(par)),
               "c1 = %g, c2 = %g  ·  semente %d" % (par[0], par[1], SEMENTE))
    return par, resumo_execucao(resultado)


def video_constricao(contagens):
    casos = [(1.0, "sem constrição (χ = 1)"), (CHI_IDEAL, "χ = %s · ideal" % virgula(CHI_IDEAL)),
             (CHI_DEMAIS, "χ = %s · amortecido demais" % virgula(CHI_DEMAIS))]
    resultados = {c: EnxameParticulas(4, 4, constricao=c, semente=SEMENTE_CONSTRICAO).executa(historico=True)
                  for c, _ in casos}
    linhas = {c: linha_do_tempo(resultados[c]) for c, _ in casos}
    total = len(linhas[1.0][0])
    X, Y, Z = malha(300)
    plt.rcParams.update({"font.size": 15})
    fig = plt.figure(figsize=(16, 9), dpi=100)
    artistas = {}
    for k, (c, rotulo) in enumerate(casos):
        ax = fig.add_axes([0.025 + k * 0.325, 0.175, 0.31, 0.551])
        contorno(ax, X, Y, Z)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.plot([0], [0], marker="+", markersize=18, markeredgewidth=2.4, color="white", zorder=5)
        pontos = ax.scatter([], [], s=40, color="white", edgecolors="black", linewidths=0.9, zorder=6)
        estrela = ax.scatter([], [], s=280, marker="*", color=VERMELHO, edgecolors="white",
                             linewidths=1.0, zorder=7)
        fig.text(0.025 + k * 0.325 + 0.155, 0.75, rotulo, ha="center", fontsize=17, fontweight="bold")
        valor = fig.text(0.025 + k * 0.325 + 0.155, 0.125, "", ha="center", fontsize=14, color="#333333")
        fig.text(0.025 + k * 0.325 + 0.155, 0.075, "em %d execuções: convergiu %d" % (EXECUCOES, contagens[c]),
                 ha="center", fontsize=14, color="#666666")
        artistas[c] = (pontos, estrela, valor)
    titulo = fig.text(0.5, 0.925, "", ha="center", fontsize=21, fontweight="bold")
    fig.text(0.5, 0.87, "c1 = c2 = 4 · mesmo enxame inicial (semente %d) · só o fator de constrição χ muda"
             % SEMENTE_CONSTRICAO, ha="center", fontsize=15, color="#444444")

    def frame(q):
        for c, _ in casos:
            posicoes, iteracoes, gbests = linhas[c]
            h = resultados[c]["historico"][gbests[q]]
            raio_atual = resultados[c]["raio"][iteracoes[q]]
            pontos, estrela, valor = artistas[c]
            pontos.set_offsets(posicoes[q])
            estrela.set_offsets([h["g"]])
            valor.set_text("f(gbest) %s   ·   raio do enxame %s" % (formata_f(h["fg"]),
                           ("%.1e" % raio_atual) if raio_atual < 0.01 else ("%.2f" % raio_atual)))
        titulo.set_text("Iteração %d de %d" % (linhas[1.0][1][q], ITERACOES))
        return []

    animacao = FuncAnimation(fig, frame, frames=total, blit=False)
    import imageio_ffmpeg
    matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
    destino = os.path.join(SAIDA, "parte2_constricao.mp4")
    animacao.save(destino, writer=FFMpegWriter(fps=24, bitrate=4500))
    plt.close(fig)
    return {"semente": SEMENTE_CONSTRICAO, "casos": [
        {"chi": c, "f_gbest": resultados[c]["f_gbest"], "convergiu": resultados[c]["convergiu"],
         "raio_final": float(resultados[c]["raio"][-1])} for c, _ in casos]}


def virgula(x):
    return ("%g" % x).replace(".", ",")


def video_grade(_):
    resultados = {p: EnxameParticulas(p[0], p[1], semente=SEMENTE).executa(historico=True) for p in PARES}
    gera_grade(resultados, os.path.join(SAIDA, "parte2_comparativo.mp4"))
    return None


def main():
    os.makedirs(SAIDA, exist_ok=True)
    com_videos = "--sem-videos" not in sys.argv
    with ProcessPoolExecutor() as ex:
        videos = [ex.submit(video_par, p) for p in PARES] + [ex.submit(video_grade, None)] if com_videos else []

        principais = dict(zip(PARES, roda(ex, [(p, range(EXECUCOES), {}) for p in PARES])))
        brutos = roda(ex, [(p, range(BASE_TURMAS + t * EXECUCOES, BASE_TURMAS + (t + 1) * EXECUCOES), {})
                           for p in PARES for t in range(TURMAS)])
        turmas = {p: brutos[i * TURMAS:(i + 1) * TURMAS] for i, p in enumerate(PARES)}
        vmax = roda(ex, [(p, range(EXECUCOES), {"fracao_vmax": fr}) for fr in FRACOES_VMAX for p in PARES])
        constr = roda(ex, [((4, 4), range(EXECUCOES), {"constricao": c}) for c in CONSTRICOES])

        if com_videos:
            resumo_videos = dict(v.result() for v in videos[:-1])
            videos[-1].result()
        else:
            with open(os.path.join(SAIDA, "resumo_parte2.json"), encoding="utf-8") as arq:
                anterior = json.load(arq)["pares"]
            resumo_videos = {(a["c1"], a["c2"]): a["execucao_video"] for a in anterior}

    print("Parte 2 - efeito de c1 e c2 (%d execucoes por par, sementes 0 a %d)" % (EXECUCOES, EXECUCOES - 1))
    print("convergencia = melhor valor final f(gbest) < %g" % TOLERANCIA)
    print("")
    print("%-12s %12s %18s %22s" % ("c1, c2", "convergiu", "regiao do minimo", "outros %d lotes" % TURMAS))
    resumo = {"execucoes": EXECUCOES, "tolerancia": TOLERANCIA, "bacia": BACIA, "turmas": TURMAS,
              "semente_video": SEMENTE, "pares": []}
    for i, p in enumerate(PARES):
        d = principais[p]
        conv = int((d["f"] < TOLERANCIA).sum())
        bac = int((d["f"] < BACIA).sum())
        faixa = [int((t["f"] < TOLERANCIA).sum()) for t in turmas[p]]
        its = [k for k in d["iteracao"] if k is not None]
        print("%-12s %8d/%d %14d/%d %15d a %d" % (nome(p), conv, EXECUCOES, bac, EXECUCOES, min(faixa), max(faixa)))
        resumo["pares"].append({
            "c1": p[0], "c2": p[1], "nome": nome(p), "convergiu": conv, "bacia": bac,
            "faixa_turmas": [min(faixa), max(faixa)], "media_turmas": float(np.mean(faixa)),
            "tolerancias": {("%g" % t): int((d["f"] < t).sum()) for t in TOLERANCIAS},
            "vmax": {("%g" % fr if fr else "sem"): int((vmax[j * len(PARES) + i]["f"] < TOLERANCIA).sum())
                     for j, fr in enumerate(FRACOES_VMAX)},
            "iteracao_mediana": float(np.median(its)) if its else None,
            "f_mediana": float(np.median(d["f"])),
            "raio_final_mediana": float(np.median(d["raios"][:, -1])),
            "raio_it20_mediana": float(np.median(d["raios"][:, 20])),
            "video": arquivo(p),
            "execucao_video": resumo_videos[p],
        })

    print("")
    print("sensibilidade a tolerancia (quantas execucoes ficaram abaixo de cada valor):")
    print("%-12s " % "c1, c2" + " ".join("%10s" % ("f<%g" % t) for t in TOLERANCIAS))
    for item in resumo["pares"]:
        print("%-12s " % item["nome"] + " ".join("%10d" % v for v in item["tolerancias"].values()))
    print("")
    print("sensibilidade ao Vmax (fracao do intervalo [-5.12, 5.12]; usado: 0.2):")
    print("%-12s " % "c1, c2" + " ".join("%8s" % k for k in resumo["pares"][0]["vmax"]))
    for item in resumo["pares"]:
        print("%-12s " % item["nome"] + " ".join("%8d" % v for v in item["vmax"].values()))

    resumo["constricao"] = []
    print("")
    print("extra: c1 = c2 = 4 com fator de constricao")
    constricao = {}
    for c, d in zip(CONSTRICOES, constr):
        constricao[c] = {"chi": c, "convergiu": int((d["f"] < TOLERANCIA).sum()),
                         "bacia": int((d["f"] < BACIA).sum()),
                         "raio_final_mediana": float(np.median(d["raios"][:, -1]))}
        resumo["constricao"].append(constricao[c])
        print("  chi = %-5g convergiu %3d/%d   regiao %3d/%d   raio final mediano %.3g"
              % (c, constricao[c]["convergiu"], EXECUCOES, constricao[c]["bacia"], EXECUCOES,
                 constricao[c]["raio_final_mediana"]))

    grafico_barras(principais, turmas)
    grafico_curvas(principais)
    grafico_constricao(constricao)
    if com_videos:
        resumo["video_constricao"] = video_constricao({c: constricao[c]["convergiu"] for c in CONSTRICOES})
    else:
        with open(os.path.join(SAIDA, "resumo_parte2.json"), encoding="utf-8") as arq:
            resumo["video_constricao"] = json.load(arq).get("video_constricao")
    with open(os.path.join(SAIDA, "resumo_parte2.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)

    print("")
    print("arquivos gerados em", SAIDA)
    print("  parte2_convergencias.png, parte2_curvas.png, parte2_constricao.png")
    print("  parte2_comparativo.mp4 e um video por par:", ", ".join(arquivo(p) for p in PARES))


if __name__ == "__main__":
    if "--so-video-constricao" in sys.argv:
        with open(os.path.join(SAIDA, "resumo_parte2.json"), encoding="utf-8") as arq:
            resumo = json.load(arq)
        resumo["video_constricao"] = video_constricao({c["chi"]: c["convergiu"] for c in resumo["constricao"]})
        with open(os.path.join(SAIDA, "resumo_parte2.json"), "w", encoding="utf-8") as arq:
            json.dump(resumo, arq, ensure_ascii=False, indent=2)
        print(resumo["video_constricao"])
    else:
        main()
