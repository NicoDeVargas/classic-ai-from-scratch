import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.animation import FuncAnimation, FFMpegWriter

from fuzzy import Controlador
from simulacao import (Cruzamento, taxa_secundaria, DURACAO, VERDE_BASE, VERDE_MIN, VERDE_MAX,
                       VERDE_PRINCIPAL, AMARELO, CHEGADA_PRINCIPAL, VAZAO, PICO)

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "saida")
PICOS = [0.06, 0.12, 0.20, 0.28]
SEMENTES = 100
SEMENTES_FIXO = 100
VERDES_FIXOS = list(range(15, 61, 3))
DEFUZZ = ["centroide", "bissetor", "mom"]
PICO_VIDEO = 0.20
SEMENTE_VIDEO = 0
JANELA_VIDEO = (2520, 4800)
PASSO_VIDEO = 2
CARROS_VISIVEIS = 30

CINZA = "#7f8c8d"
AZUL = "#2f6db5"
VERDE = "#2e9e5b"
AMBAR = "#e8a33d"
VERMELHO = "#d9534f"


def medidas(r):
    return (r["atraso_sec"], r["atraso_pri"], r["atraso_todos"], r["fila_max_sec"])


def tarefa(args):
    tipo, pico, valor, semente = args
    if tipo == "fixo":
        r = Cruzamento(None, semente, pico, registrar=True, verde_fixo=valor).roda()
    else:
        r = Cruzamento(Controlador(defuzz=valor), semente, pico, registrar=True).roda()
    return args, medidas(r)


def estilo(ax):
    ax.grid(alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


def grafico_dia(fixo, fz):
    t = np.arange(DURACAO) / 60
    fig, eixos = plt.subplots(3, 1, figsize=(12, 9.5), sharex=True,
                              gridspec_kw={"height_ratios": [1, 1.6, 1.2]})
    eixos[0].plot(t, [taxa_secundaria(x, PICO_VIDEO) * 3600 for x in range(DURACAO)], color=AMBAR, linewidth=2.2,
                  label="via secundária")
    eixos[0].axhline(CHEGADA_PRINCIPAL * 3600, color=CINZA, linestyle="--", linewidth=1.6, label="via principal")
    eixos[0].set_ylabel("chegadas\n(veículos/h)")
    eixos[0].legend(loc="upper left", fontsize=10)
    eixos[1].plot(t, [l[1] for l in fixo["linha"]], color=CINZA, linewidth=1.2, label="tempo fixo (verde 30 s)")
    eixos[1].plot(t, [l[1] for l in fz["linha"]], color=AZUL, linewidth=1.4, label="fuzzy")
    eixos[1].axhline(30, color="#555555", linestyle=":", linewidth=1.2)
    eixos[1].text(119, 31, "30 veículos: limite do universo de QueueSec", fontsize=9, color="#555555", ha="right")
    eixos[1].set_ylabel("fila na via\nsecundária")
    eixos[1].legend(loc="upper left", fontsize=10)
    td = [d[0] / 60 for d in fz["decisoes"]]
    eixos[2].step(td, [d[4] for d in fz["decisoes"]], where="post", color=AZUL, linewidth=1.8,
                  label="verde escolhido pelo fuzzy")
    eixos[2].axhline(VERDE_BASE, color=CINZA, linewidth=1.6, label="tempo fixo")
    eixos[2].set_ylabel("verde da via\nsecundária (s)")
    eixos[2].set_xlabel("minuto da simulação")
    eixos[2].legend(loc="upper left", fontsize=10)
    for ax in eixos:
        estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "simulacao_dia.png"), dpi=160)
    plt.close(fig)


def grafico_cenarios(cen):
    fig, ax = plt.subplots(figsize=(12, 5.6))
    x = np.arange(len(PICOS))
    largura = 0.26
    series = [("tempo fixo (30 s)", CINZA, [c["fixo30"]["todos"] for c in cen]),
              ("melhor tempo fixo do cenário", AMBAR, [c["melhor_fixo"]["todos"] for c in cen]),
              ("fuzzy", AZUL, [c["fuzzy"]["todos"] for c in cen])]
    for k, (rotulo, cor, valores) in enumerate(series):
        barras = ax.bar(x + (k - 1) * largura, valores, largura, color=cor, label=rotulo)
        for b, v in zip(barras, valores):
            ax.text(b.get_x() + b.get_width() / 2, v + 1.2, "%.0f" % v, ha="center", fontsize=10)
    for i, c in enumerate(cen):
        ax.text(x[i], -9, "melhor fixo: %d s" % c["melhor_fixo"]["verde"], ha="center", fontsize=9.5, color="#8a6d1f")
    ax.set_xticks(x)
    ax.set_xticklabels([("sem pico (%d veíc./h)" if p <= 0.06 else "pico de %d veíc./h") % round(p * 3600)
                        for p in PICOS], fontsize=11)
    ax.set_ylabel("espera média por veículo (s)\nas duas vias")
    ax.set_ylim(-14, max(c["fixo30"]["todos"] for c in cen) * 1.12)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.legend(loc="upper left", fontsize=10.5)
    estilo(ax)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "simulacao_cenarios.png"), dpi=160)
    plt.close(fig)


def desenha_cruzamento(ax, titulo):
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 8.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Rectangle((-10, -1.2), 20, 2.4, color="#4a4f55"))
    ax.add_patch(Rectangle((-1.2, -10), 2.4, 16, color="#4a4f55"))
    ax.add_patch(Rectangle((-1.2, -1.2), 2.4, 2.4, color="#3d4247"))
    for x in np.arange(-9.5, -1.4, 1.0):
        ax.plot([x, x + 0.5], [0, 0], color="#d8d8d8", linewidth=1)
    ax.plot([-1.3, -1.3], [-1.2, 0], color="white", linewidth=2.5)
    ax.plot([0, 1.2], [-1.3, -1.3], color="white", linewidth=2.5)
    sem_pri = Circle((-1.9, 1.7), 0.45, color=VERMELHO, zorder=5)
    sem_sec = Circle((1.9, -1.9), 0.45, color=VERMELHO, zorder=5)
    ax.add_patch(sem_pri)
    ax.add_patch(sem_sec)
    ax.text(-9.8, 1.6, "via principal", fontsize=10, color="#333333")
    ax.text(1.8, -9.6, "via secundária", fontsize=10, color="#333333", rotation=90, va="bottom")
    carros_pri = [ax.add_patch(Rectangle((-1.5 - 0.28 * (k + 1), -1.0), 0.22, 0.8, color="#e8e8e8", zorder=4))
                  for k in range(CARROS_VISIVEIS)]
    carros_sec = [ax.add_patch(Rectangle((0.2, -1.5 - 0.28 * (k + 1)), 0.8, 0.22, color="#ffd27f", zorder=4))
                  for k in range(CARROS_VISIVEIS)]
    excesso_pri = ax.text(-9.8, -2.1, "", fontsize=10, color="#333333")
    excesso_sec = ax.text(-0.4, -10.0, "", fontsize=10, color="#333333", ha="right")
    ax.set_title(titulo, fontsize=15, fontweight="bold", pad=4)
    info = ax.text(2.0, 8.3, "", fontsize=11.5, va="top", family="DejaVu Sans")
    return {"sem_pri": sem_pri, "sem_sec": sem_sec, "carros_pri": carros_pri, "carros_sec": carros_sec,
            "excesso_pri": excesso_pri, "excesso_sec": excesso_sec, "info": info}


def cor_semaforo(fase, via):
    if fase == "verde_%s" % via:
        return VERDE
    if fase == "amarelo_%s" % via:
        return AMBAR
    return VERMELHO


def video(fixo, fz):
    import imageio_ffmpeg
    matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
    inicio, fim = JANELA_VIDEO
    quadros = list(range(inicio, fim, PASSO_VIDEO))
    plt.rcParams.update({"font.size": 12})
    fig = plt.figure(figsize=(16, 9), dpi=100)
    ax_f = fig.add_axes([0.02, 0.36, 0.46, 0.52])
    ax_z = fig.add_axes([0.52, 0.36, 0.46, 0.52])
    paineis = [(desenha_cruzamento(ax_f, "Tempo fixo (verde de %d s)" % VERDE_BASE), fixo, None),
               (desenha_cruzamento(ax_z, "Controlador fuzzy"), fz, fz["decisoes"])]
    titulo = fig.text(0.5, 0.955, "", ha="center", fontsize=20, fontweight="bold")
    fig.text(0.5, 0.915, "mesmas chegadas de carros nos dois lados (semente %d) · pico de %d veículos/h na via secundária"
             % (SEMENTE_VIDEO, round(PICO_VIDEO * 3600)), ha="center", fontsize=12.5, color="#555555")

    tt = np.arange(inicio, fim) / 60
    parados = {id(r): np.array([r["linha"][t][1] + r["linha"][t][2] for t in range(inicio, fim)]) for r in (fixo, fz)}
    acumulado = {k: np.cumsum(v) / 3600 for k, v in parados.items()}
    graf_p = fig.add_axes([0.06, 0.07, 0.42, 0.22])
    graf_a = fig.add_axes([0.56, 0.07, 0.41, 0.22])
    curvas = []
    for graf, dados, titulo_graf in ((graf_p, parados, "carros parados agora (as duas vias)"),
                                     (graf_a, acumulado, "espera acumulada desde o início do vídeo (veículo·hora)")):
        for r, cor_clara, cor, rotulo in ((fixo, "#cccccc", CINZA, "tempo fixo"), (fz, "#cfdcf0", AZUL, "fuzzy")):
            graf.plot(tt, dados[id(r)], color=cor_clara, linewidth=1)
            curvas.append((graf.plot([], [], color=cor, linewidth=2, label=rotulo)[0], dados[id(r)]))
        curvas.append((graf.axvline(inicio / 60, color="#333333", linewidth=1), None))
        graf.set_xlim(inicio / 60, fim / 60)
        graf.set_title(titulo_graf, fontsize=12, loc="left")
        graf.set_xlabel("minuto da simulação")
        graf.legend(loc="upper left", fontsize=10.5)
        estilo(graf)

    def frame(t):
        i = t - inicio
        for p, r, decisoes in paineis:
            _, fila_sec, fila_pri, fase, verde = r["linha"][t]
            p["sem_pri"].set_color(cor_semaforo(fase, "pri"))
            p["sem_sec"].set_color(cor_semaforo(fase, "sec"))
            for k, carro in enumerate(p["carros_pri"]):
                carro.set_visible(k < fila_pri)
            for k, carro in enumerate(p["carros_sec"]):
                carro.set_visible(k < fila_sec)
            p["excesso_pri"].set_text("+%d" % (fila_pri - CARROS_VISIVEIS) if fila_pri > CARROS_VISIVEIS else "")
            p["excesso_sec"].set_text("+%d" % (fila_sec - CARROS_VISIVEIS) if fila_sec > CARROS_VISIVEIS else "")
            texto = ("parados agora: %d\n  secundária %d · principal %d\nespera acumulada: %.1f veíc·h\nverde da secundária: %d s"
                     % (fila_sec + fila_pri, fila_sec, fila_pri, acumulado[id(r)][i], verde))
            if decisoes:
                ultima = [d for d in decisoes if d[0] <= t]
                if ultima:
                    _, n, espera, ajuste, v = ultima[-1]
                    texto += "\n\núltima decisão:\nQueueSec %d · WaitTimeSec %.0f s\n→ GreenAdj %+.1f s → verde %d s" % (
                        n, espera, ajuste, v)
            p["info"].set_text(texto)
        for curva, dados in curvas:
            if dados is None:
                curva.set_xdata([t / 60, t / 60])
            else:
                curva.set_data(tt[:i + 1], dados[:i + 1])
        titulo.set_text("Minuto %d:%02d da simulação" % (t // 60, t % 60))
        return []

    animacao = FuncAnimation(fig, frame, frames=quadros, blit=False)
    destino = os.path.join(SAIDA, "simulacao_semaforo.mp4")
    animacao.save(destino, writer=FFMpegWriter(fps=30, bitrate=4000))
    plt.close(fig)
    return destino


def main():
    os.makedirs(SAIDA, exist_ok=True)
    tarefas = [("fixo", p, VERDE_BASE, s) for p in PICOS for s in range(SEMENTES)]
    tarefas += [("fuzzy", p, "centroide", s) for p in PICOS for s in range(SEMENTES)]
    tarefas += [("fixo", p, v, s) for p in PICOS for v in VERDES_FIXOS for s in range(SEMENTES_FIXO)
                if v != VERDE_BASE]
    tarefas += [("fuzzy", p, d, s) for p in PICOS for d in DEFUZZ if d != "centroide" for s in range(SEMENTES_FIXO)]
    with ProcessPoolExecutor() as ex:
        res = dict(ex.map(tarefa, tarefas, chunksize=8))

    def media(tipo, p, valor, n):
        return np.mean([res[(tipo, p, valor, s)] for s in range(n)], axis=0)

    cenarios = []
    print("Extra: tempo fixo x controlador fuzzy num cruzamento simulado (%d s, %d sementes)" % (DURACAO, SEMENTES))
    for p in PICOS:
        f30 = np.array([res[("fixo", p, VERDE_BASE, s)] for s in range(SEMENTES)])
        fz = np.array([res[("fuzzy", p, "centroide", s)] for s in range(SEMENTES)])
        fixos = {v: media("fixo", p, v, SEMENTES_FIXO) for v in VERDES_FIXOS}
        melhor = min(VERDES_FIXOS, key=lambda v: fixos[v][2])
        fz40 = media("fuzzy", p, "centroide", SEMENTES_FIXO)
        cen = {
            "pico_veic_h": round(p * 3600),
            "fixo30": {"sec": float(f30[:, 0].mean()), "pri": float(f30[:, 1].mean()), "todos": float(f30[:, 2].mean()),
                       "fila_max": float(f30[:, 3].mean())},
            "fuzzy": {"sec": float(fz[:, 0].mean()), "pri": float(fz[:, 1].mean()), "todos": float(fz[:, 2].mean()),
                      "fila_max": float(fz[:, 3].mean())},
            "fuzzy_melhor_que_fixo30_pct": {"sec": int(100 * (fz[:, 0] < f30[:, 0]).mean()),
                                             "pri": int(100 * (fz[:, 1] < f30[:, 1]).mean()),
                                             "todos": int(100 * (fz[:, 2] < f30[:, 2]).mean())},
            "melhor_fixo": {"verde": melhor, "sec": float(fixos[melhor][0]), "pri": float(fixos[melhor][1]),
                            "todos": float(fixos[melhor][2]), "fuzzy_mesmas_sementes": float(fz40[2])},
            "defuzz": {d: float(media("fuzzy", p, d, SEMENTES_FIXO)[2]) for d in DEFUZZ},
        }
        cenarios.append(cen)
        print("pico %4d veíc/h | fixo 30 s: sec %6.1f pri %5.1f todos %6.1f | fuzzy: sec %6.1f pri %5.1f todos %6.1f"
              " | fuzzy melhor (todos) em %3d%% | melhor fixo %d s: todos %.1f"
              % (cen["pico_veic_h"], cen["fixo30"]["sec"], cen["fixo30"]["pri"], cen["fixo30"]["todos"],
                 cen["fuzzy"]["sec"], cen["fuzzy"]["pri"], cen["fuzzy"]["todos"],
                 cen["fuzzy_melhor_que_fixo30_pct"]["todos"], melhor, cen["melhor_fixo"]["todos"]))
        print("    defuzzificação: " + "  ".join("%s %.1f" % kv for kv in cen["defuzz"].items()))

    fixo_v = Cruzamento(None, SEMENTE_VIDEO, PICO_VIDEO, registrar=True).roda()
    fz_v = Cruzamento(Controlador(), SEMENTE_VIDEO, PICO_VIDEO, registrar=True).roda()
    grafico_dia(fixo_v, fz_v)
    grafico_cenarios(cenarios)

    resumo = {
        "duracao_s": DURACAO, "sementes": SEMENTES, "sementes_fixo": SEMENTES_FIXO, "vazao_veic_s": VAZAO,
        "verde_base": VERDE_BASE, "verde_min": VERDE_MIN, "verde_max": VERDE_MAX, "verde_principal": VERDE_PRINCIPAL,
        "amarelo": AMARELO, "chegada_principal_veic_h": round(CHEGADA_PRINCIPAL * 3600), "cenarios": cenarios,
        "video": {"pico_veic_h": round(PICO_VIDEO * 3600), "semente": SEMENTE_VIDEO,
                  "janela_min": [JANELA_VIDEO[0] / 60, JANELA_VIDEO[1] / 60],
                  "fixo": {k: float(fixo_v[k]) for k in ("atraso_sec", "atraso_pri", "atraso_todos")},
                  "fuzzy": {k: float(fz_v[k]) for k in ("atraso_sec", "atraso_pri", "atraso_todos")},
                  "verdes_fuzzy": [min(fz_v["verdes"]), max(fz_v["verdes"])],
                  "duracao_s": round((JANELA_VIDEO[1] - JANELA_VIDEO[0]) / PASSO_VIDEO / 30),
                  "acumulado_veic_h": {nome: sum(l[1] + l[2] for l in r["linha"][JANELA_VIDEO[0]:JANELA_VIDEO[1]]) / 3600
                                       for nome, r in (("fixo", fixo_v), ("fuzzy", fz_v))},
                  "parados_max": {nome: max(l[1] + l[2] for l in r["linha"][JANELA_VIDEO[0]:JANELA_VIDEO[1]])
                                  for nome, r in (("fixo", fixo_v), ("fuzzy", fz_v))},
                  "fila_pri_max": {nome: max(l[2] for l in r["linha"][JANELA_VIDEO[0]:JANELA_VIDEO[1]])
                                   for nome, r in (("fixo", fixo_v), ("fuzzy", fz_v))},
                  "fila_max": {"fixo": fixo_v["fila_max_sec"], "fuzzy": fz_v["fila_max_sec"]}},
    }
    with open(os.path.join(SAIDA, "resumo_simulacao.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)

    if "--sem-video" not in sys.argv:
        print("vídeo:", video(fixo_v, fz_v))


if __name__ == "__main__":
    main()
