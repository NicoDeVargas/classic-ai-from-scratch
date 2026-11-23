import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from fuzzy import (Controlador, TERMOS, REGRAS, FILA, ESPERA, AJUSTE, pertinencia)

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "saida")
EXEMPLO = (20.0, 70.0)

CORES = ["#2f6db5", "#e8a33d", "#d9534f"]
NOMES = {"fila": "QueueSec — fila na via secundária (veículos)",
         "espera": "WaitTimeSec — tempo médio de espera (s)",
         "ajuste": "GreenAdj — ajuste no tempo de verde (s)"}
UNIVERSO = {"fila": FILA, "espera": ESPERA, "ajuste": AJUSTE}

TERMOS_UNIFORMES = {
    "fila": {"Baixa": ("tri", (0, 0, 15)), "Média": ("tri", (0, 15, 30)), "Alta": ("tri", (15, 30, 30))},
    "espera": {"Curto": ("tri", (0, 0, 60)), "Médio": ("tri", (0, 60, 120)), "Longo": ("tri", (60, 120, 120))},
    "ajuste": TERMOS["ajuste"],
}
REGRAS_MINIMAS = [
    ("Baixa", "Curto", "Reduzir"),
    ("Baixa", "Longo", "Manter"),
    ("Média", "Médio", "Manter"),
    ("Média", "Longo", "Aumentar"),
    ("Alta", "Curto", "Aumentar"),
    ("Alta", "Longo", "Aumentar"),
]


def estilo(ax):
    ax.grid(alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


def grafico_pertinencia():
    fig, eixos = plt.subplots(3, 1, figsize=(10, 9.5))
    for ax, var in zip(eixos, ("fila", "espera", "ajuste")):
        x = UNIVERSO[var]
        for cor, termo in zip(CORES, TERMOS[var]):
            mu = pertinencia(var, termo, x)
            ax.plot(x, mu, color=cor, linewidth=2.4, label=termo)
            ax.fill_between(x, mu, color=cor, alpha=0.12)
            tipo, p = TERMOS[var][termo]
            pico = np.mean(p[1:3]) if tipo == "trap" else p[1]
            ax.text(pico, 1.06, termo, color=cor, ha="center", fontsize=12, fontweight="bold")
        ax.set_xlim(x[0], x[-1])
        ax.set_ylim(0, 1.2)
        ax.set_title(NOMES[var], fontsize=13, loc="left")
        ax.set_ylabel("pertinência")
        estilo(ax)
    eixos[2].axvline(0, color="#555555", linestyle=":", linewidth=1.2)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "pertinencia.png"), dpi=170)
    plt.close(fig)


def grafico_regras():
    fila_t, esp_t = list(TERMOS["fila"]), list(TERMOS["espera"])
    saida_t = list(TERMOS["ajuste"])
    m = np.zeros((3, 3), dtype=int)
    numeros = np.zeros((3, 3), dtype=int)
    for k, (f, w, s) in enumerate(REGRAS, 1):
        m[fila_t.index(f), esp_t.index(w)] = saida_t.index(s)
        numeros[fila_t.index(f), esp_t.index(w)] = k
    fig, ax = plt.subplots(figsize=(7.2, 5.6))
    ax.imshow(m, cmap=ListedColormap(["#d6e4f5", "#fbe6c4", "#f6cfcd"]), vmin=0, vmax=2)
    for i in range(3):
        for j in range(3):
            ax.text(j, i - 0.08, saida_t[m[i, j]], ha="center", va="center", fontsize=16, fontweight="bold",
                    color=CORES[m[i, j]])
            ax.text(j, i + 0.26, "regra %d" % numeros[i, j], ha="center", va="center", fontsize=10, color="#555555")
    ax.set_xticks(range(3))
    ax.set_xticklabels(esp_t, fontsize=13)
    ax.set_yticks(range(3))
    ax.set_yticklabels(fila_t, fontsize=13)
    ax.set_xlabel("WaitTimeSec (tempo de espera)", fontsize=12)
    ax.set_ylabel("QueueSec (fila)", fontsize=12)
    ax.set_xticks(np.arange(-0.5, 3), minor=True)
    ax.set_yticks(np.arange(-0.5, 3), minor=True)
    ax.grid(which="minor", color="white", linewidth=3)
    ax.tick_params(which="both", length=0)
    for lado in ax.spines.values():
        lado.set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "regras.png"), dpi=170)
    plt.close(fig)


def grafico_inferencia(c, fila, espera):
    ativ = c.ativacoes(fila, espera)
    agregado = c.agrega(ativ)
    resultado = c.defuzzifica(agregado)
    n = len(REGRAS)
    fig, eixos = plt.subplots(n + 1, 3, figsize=(12, 13), gridspec_kw={"hspace": 0.35, "wspace": 0.12})
    for k, ((f, w, s), forca) in enumerate(zip(REGRAS, ativ)):
        for j, (var, termo, valor) in enumerate((("fila", f, fila), ("espera", w, espera))):
            ax = eixos[k, j]
            x = UNIVERSO[var]
            mu = pertinencia(var, termo, x)
            grau = float(pertinencia(var, termo, valor))
            cor = CORES[list(TERMOS[var]).index(termo)]
            ax.plot(x, mu, color=cor, linewidth=1.3)
            ax.fill_between(x, np.minimum(mu, grau), color=cor, alpha=0.55)
            ax.axvline(valor, color="#c0392b", linewidth=1.4)
            ax.text(0.98, 0.62, "%s: %.2f" % (termo, grau), transform=ax.transAxes, ha="right", fontsize=10.5)
        ax = eixos[k, 2]
        mu = c.saidas[s]
        cor = CORES[list(TERMOS["ajuste"]).index(s)]
        ax.plot(AJUSTE, mu, color=cor, linewidth=1.3)
        ax.fill_between(AJUSTE, np.minimum(mu, forca), color=cor, alpha=0.55)
        ax.text(0.98, 0.62, "%s: %.2f" % (s, forca), transform=ax.transAxes, ha="right", fontsize=10.5)
        eixos[k, 0].set_ylabel("R%d" % (k + 1), rotation=0, labelpad=16, fontsize=11, fontweight="bold")
    for ax in eixos.flat:
        ax.set_ylim(0, 1.05)
        ax.set_yticks([])
        ax.set_xticks([])
    for ax in eixos[n, :2]:
        ax.axis("off")
    ax = eixos[n, 2]
    ax.fill_between(AJUSTE, agregado, color="#555555", alpha=0.5)
    ax.plot(AJUSTE, agregado, color="#333333", linewidth=1.3)
    ax.axvline(resultado, color="#c0392b", linewidth=2.4)
    ax.set_xticks([-10, 0, 10, 20, 30])
    ax.text(resultado + 1, 0.8, "centroide = %.2f s" % resultado, fontsize=11, color="#c0392b", fontweight="bold")
    eixos[n, 1].text(0.98, 0.5, "agregação (máximo)\ne defuzzificação  →", transform=eixos[n, 1].transAxes,
                     ha="right", va="center", fontsize=11)
    eixos[0, 0].set_title("QueueSec = %g veículos" % fila, fontsize=12)
    eixos[0, 1].set_title("WaitTimeSec = %g s" % espera, fontsize=12)
    eixos[0, 2].set_title("GreenAdj = %.2f s" % resultado, fontsize=12)
    fig.savefig(os.path.join(SAIDA, "inferencia_exemplo.png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    return ativ, resultado


def grafico_superficie(fs, ws, z):
    z = np.round(z, 6)
    F, W = np.meshgrid(fs, ws)
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(111, projection="3d")
    sup = ax.plot_surface(F, W, z, cmap="RdYlBu_r", vmin=-10, vmax=20, linewidth=0.2, edgecolor="#ffffff33",
                          antialiased=True)
    ax.set_xlabel("QueueSec (veículos)", labelpad=10)
    ax.set_ylabel("WaitTimeSec (s)", labelpad=10)
    ax.set_zlabel("GreenAdj (s)", labelpad=8)
    ax.set_zlim(-10, 30)
    ax.view_init(elev=27, azim=-130)
    fig.colorbar(sup, ax=ax, shrink=0.55, pad=0.08, label="ajuste no verde (s)")
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "superficie_3d.png"), dpi=170)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 6.5))
    mapa = ax.contourf(F, W, z, levels=np.arange(-8, 20, 1), cmap="RdYlBu_r", vmin=-10, vmax=20)
    linhas = ax.contour(F, W, z, levels=[-4, 4, 8, 12, 16], colors="#222222", linewidths=0.8)
    ax.clabel(linhas, fmt="%+d s", fontsize=9)
    ax.plot([EXEMPLO[0]], [EXEMPLO[1]], marker="o", markersize=10, color="white", markeredgecolor="black")
    ax.annotate("exemplo da inferência", EXEMPLO, xytext=(EXEMPLO[0] - 11, EXEMPLO[1] + 25), fontsize=10,
                arrowprops=dict(arrowstyle="->", color="black"))
    ax.set_xlabel("QueueSec (veículos)")
    ax.set_ylabel("WaitTimeSec (s)")
    fig.colorbar(mapa, ax=ax, label="GreenAdj (s)")
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "superficie_mapa.png"), dpi=170)
    plt.close(fig)


def grafico_extremos(c, z):
    casos = [("menor saída", np.unravel_index(np.argmin(z), z.shape)),
             ("maior saída", np.unravel_index(np.argmax(z), z.shape))]
    fig, eixos = plt.subplots(1, 2, figsize=(13, 4.4))
    fs, ws = np.linspace(0, 30, z.shape[1]), np.linspace(0, 120, z.shape[0])
    resumo = []
    for ax, (rotulo, (i, j)) in zip(eixos, casos):
        f, w = fs[j], ws[i]
        agregado = c.agrega(c.ativacoes(f, w))
        r = c.defuzzifica(agregado)
        ax.fill_between(AJUSTE, agregado, color="#555555", alpha=0.35)
        ax.plot(AJUSTE, agregado, color="#333333")
        ax.axvline(r, color="#c0392b", linewidth=2.4)
        limite = -10 if r < 0 else 30
        ax.axvline(limite, color="#2f6db5", linestyle="--", linewidth=1.6)
        ax.annotate("", xy=(limite, 0.5), xytext=(r, 0.5),
                    arrowprops=dict(arrowstyle="<->", color="#2f6db5"))
        ax.text(r + (1 if limite < 0 else -1), 0.72, "%.1f s que o\ncentroide não alcança" % abs(limite - r),
                ha="left" if limite < 0 else "right", fontsize=10.5, color="#2f6db5")
        ax.text(r, 1.08, "centroide %.2f s" % r, ha="center", color="#c0392b", fontsize=11, fontweight="bold")
        ax.set_title("%s: QueueSec = %g, WaitTimeSec = %g" % (rotulo, f, w), fontsize=11.5)
        ax.set_ylim(0, 1.2)
        ax.set_xlabel("GreenAdj (s)")
        estilo(ax)
        resumo.append({"rotulo": rotulo, "fila": float(f), "espera": float(w), "saida": r})
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "extremos.png"), dpi=170)
    plt.close(fig)
    return resumo


def grafico_variacoes(variacoes):
    fig = plt.figure(figsize=(14, 10.5))
    for k, (titulo, (fs, ws, z)) in enumerate(variacoes):
        ax = fig.add_subplot(2, 2, k + 1, projection="3d")
        F, W = np.meshgrid(fs, ws)
        ax.plot_surface(F, W, z, cmap="RdYlBu_r", vmin=-10, vmax=20, linewidth=0.15, edgecolor="#ffffff33")
        ax.set_title(titulo, fontsize=13, pad=2)
        ax.set_xlabel("QueueSec", labelpad=4)
        ax.set_ylabel("WaitTimeSec", labelpad=4)
        ax.set_zlabel("GreenAdj", labelpad=2)
        ax.set_zlim(-10, 30)
        ax.view_init(elev=27, azim=-130)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "variacoes.png"), dpi=150)
    plt.close(fig)


def buracos(regras):
    c = Controlador(regras=regras)
    fs, ws = np.linspace(0, 30, 121), np.linspace(0, 120, 121)
    vazios = sum(max(c.ativacoes(f, w)) == 0 for f in fs for w in ws)
    return 100.0 * vazios / (len(fs) * len(ws))


def main():
    os.makedirs(SAIDA, exist_ok=True)
    c = Controlador()
    grafico_pertinencia()
    grafico_regras()
    ativ, resultado = grafico_inferencia(c, *EXEMPLO)
    fs, ws, z = c.superficie()
    grafico_superficie(fs, ws, z)
    extremos = grafico_extremos(c, z)

    variacoes = [
        ("Original (9 regras, centroide)", (fs, ws, z)),
        ("Funções de pertinência diferentes\n(triângulos uniformes)", Controlador(termos=TERMOS_UNIFORMES).superficie()),
        ("Só 6 regras (o mínimo do enunciado)", Controlador(regras=REGRAS_MINIMAS).superficie()),
        ("Defuzzificação pela média dos máximos", Controlador(defuzz="mom").superficie()),
    ]
    grafico_variacoes(variacoes)

    gf, ge = c.fuzzifica(*EXEMPLO)
    resumo = {
        "exemplo": {"fila": EXEMPLO[0], "espera": EXEMPLO[1], "graus_fila": gf, "graus_espera": ge,
                    "ativacoes": [{"regra": k + 1, "se_fila": f, "e_espera": w, "entao": s, "forca": a}
                                  for k, ((f, w, s), a) in enumerate(zip(REGRAS, ativ))],
                    "saida": resultado},
        "superficie": {"min": float(z.min()), "max": float(z.max())},
        "extremos": extremos,
        "variacoes": [{"titulo": t.replace("\n", " "), "min": float(v[2].min()), "max": float(v[2].max())}
                      for t, v in variacoes],
        "degrau": {"espera": 75.0, "antes": {"fila": 6.0, "saida": c.calcula(6, 75)},
                   "depois": {"fila": 8.0, "saida": c.calcula(8, 75)},
                   "forca_aumentar": max(a for (f, w, s), a in zip(REGRAS, c.ativacoes(8, 75)) if s == "Aumentar")},
        "buracos_6_regras_pct": buracos(REGRAS_MINIMAS),
        "buracos_9_regras_pct": buracos(REGRAS),
        "termos": {v: {t: list(p) for t, (_, p) in TERMOS[v].items()} for v in TERMOS},
        "regras": [list(r) for r in REGRAS],
    }
    with open(os.path.join(SAIDA, "resumo_trabalho.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)

    print("Controlador fuzzy do tempo de verde (Mamdani: E = mínimo, agregação = máximo, centroide)")
    print("")
    print("Exemplo: QueueSec = %g veículos, WaitTimeSec = %g s" % EXEMPLO)
    print("  fila:   " + "  ".join("%s %.2f" % kv for kv in gf.items()))
    print("  espera: " + "  ".join("%s %.2f" % kv for kv in ge.items()))
    for k, ((f, w, s), a) in enumerate(zip(REGRAS, ativ), 1):
        if a > 0:
            print("  regra %d: SE fila é %s E espera é %s ENTÃO %s  -> força %.2f" % (k, f, w, s, a))
    print("  GreenAdj = %.2f s" % resultado)
    print("")
    print("Superfície: de %.2f s a %.2f s (o universo vai de -10 a +30 s)" % (z.min(), z.max()))
    for e in extremos:
        print("  %s em QueueSec = %g, WaitTimeSec = %g: %.2f s" % (e["rotulo"], e["fila"], e["espera"], e["saida"]))
    print("")
    print("Variações:")
    for v in resumo["variacoes"]:
        print("  %-55s de %6.2f a %6.2f" % (v["titulo"], v["min"], v["max"]))
    print("Pontos do domínio sem nenhuma regra ativa: %.1f%% com 6 regras, %.1f%% com 9"
          % (resumo["buracos_6_regras_pct"], resumo["buracos_9_regras_pct"]))


if __name__ == "__main__":
    main()
