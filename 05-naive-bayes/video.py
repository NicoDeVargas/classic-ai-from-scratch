import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter

from nb import FEATURES, NaiveBayesGaussiano, carrega, divide
from trabalho import AZUL, VERMELHO, CINZA, CORES, SAIDA, SEMENTES, gaussiana, rotulo, escolhe_amostra

FPS = 20
QUADROS_PASSO = 20
QUADROS_FINAL = 50


def escolhe_pacientes(modelo, X, y):
    p = modelo.probabilidades(X)
    previsto = modelo.classifica(X)
    a = escolhe_amostra(modelo, X, y)
    b = next(i for i in range(len(y)) if previsto[i] == y[i] == 0 and p[i, 0] > 0.97)
    c = next(i for i in range(len(y)) if previsto[i] != y[i] and p[i].max() > 0.9)
    return [a, b, c]


def main():
    import imageio_ffmpeg
    matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()
    X, y, _ = carrega()
    treino, teste = divide(len(y), SEMENTES[-1])
    modelo = NaiveBayesGaussiano().treina(X[treino], y[treino])
    pacientes = escolhe_pacientes(modelo, X[teste], y[teste])
    priori = modelo.log_priori[1] - modelo.log_priori[0]
    passos = []
    for letra, k in zip("ABC", pacientes):
        amostra = X[teste][k]
        dens = modelo.log_densidade(amostra)[0]
        contrib = [priori] + list(dens[1] - dens[0])
        passos.append({"letra": letra, "amostra": amostra, "real": int(y[teste][k]), "contrib": np.array(contrib),
                       "dens": dens})
    limite = max(np.abs(p["contrib"]).max() for p in passos) * 1.15
    limite_soma = max(np.abs(np.cumsum(p["contrib"])).max() for p in passos) * 1.15
    quadros = [(i, j, q) for i in range(len(passos)) for j in range(11)
               for q in range(QUADROS_PASSO + (QUADROS_FINAL if j == 10 else 0))]

    plt.rcParams.update({"font.size": 12})
    fig = plt.figure(figsize=(16, 9), dpi=100)
    titulo = fig.text(0.5, 0.95, "", ha="center", fontsize=21, fontweight="bold")
    sub = fig.text(0.5, 0.905, "", ha="center", fontsize=13.5, color="#555555")
    ax_g = fig.add_axes([0.05, 0.40, 0.40, 0.42])
    ax_c = fig.add_axes([0.56, 0.40, 0.40, 0.42])
    ax_r = fig.add_axes([0.08, 0.10, 0.84, 0.13])
    veredito = fig.text(0.5, 0.285, "", ha="center", fontsize=17, fontweight="bold")
    nomes = ["priori"] + FEATURES

    def frame(args):
        i, j, q = args
        p = passos[i]
        t = min(1.0, (q + 1) / (QUADROS_PASSO * 0.6))
        titulo.set_text("Paciente %s: o cabo de guerra do Naive Bayes" % p["letra"])
        sub.set_text("cada feature puxa para a classe em que o valor do paciente é mais provável · classe real: %d" % p["real"])

        ax_g.clear()
        if j == 0:
            pri = np.exp(modelo.log_priori) * 100
            ax_g.bar([0, 1], pri, color=CORES, width=0.55)
            for c in (0, 1):
                ax_g.text(c, pri[c] + 1.5, ("%.1f%%" % pri[c]).replace(".", ","), ha="center", fontsize=15, fontweight="bold")
            ax_g.set_xticks([0, 1], ["classe 0", "classe 1"], fontsize=13)
            ax_g.set_ylim(0, 75)
            ax_g.set_title("priori: quantos pacientes do treino há em cada classe", fontsize=14, fontweight="bold")
        else:
            f = j - 1
            desvio = np.sqrt(modelo.variancia[:, f].max())
            xs = np.linspace(X[:, f].min() - desvio, X[:, f].max() + desvio, 300)
            for c in (0, 1):
                ys = gaussiana(xs, modelo.media[c, f], modelo.variancia[c, f])
                ax_g.plot(xs, ys, color=CORES[c], linewidth=2.8)
                ax_g.fill_between(xs, ys, color=CORES[c], alpha=0.12)
                ax_g.plot(p["amostra"][f], np.exp(p["dens"][c, f]), "o", color=CORES[c], markersize=13,
                          markeredgecolor="black", zorder=5)
            ax_g.axvline(p["amostra"][f], color="black", linewidth=2)
            ax_g.set_title("%s = %s" % (rotulo(FEATURES[f]), ("%.4g" % p["amostra"][f]).replace(".", ",")),
                           fontsize=15, fontweight="bold")
            ax_g.set_ylim(0, None)
        ax_g.set_yticks([])
        for lado in ("top", "right", "left"):
            ax_g.spines[lado].set_visible(False)

        ax_c.clear()
        valores = p["contrib"][:j + 1].copy()
        valores[j] *= t
        ax_c.barh(range(j + 1), valores, color=[VERMELHO if v > 0 else AZUL for v in valores])
        ax_c.axvline(0, color="black", linewidth=1.2)
        ax_c.set_yticks(range(11), nomes, fontsize=12)
        ax_c.set_ylim(10.6, -0.6)
        ax_c.set_xlim(-limite, limite)
        ax_c.set_title("← puxa para a classe 0          puxa para a classe 1 →", fontsize=13)
        ax_c.set_xlabel("diferença dos logs (classe 1 − classe 0)")
        ax_c.grid(axis="x", alpha=0.3)
        for lado in ("top", "right"):
            ax_c.spines[lado].set_visible(False)

        soma = valores.sum()
        prob1 = 1 / (1 + np.exp(-soma))
        ax_r.clear()
        ax_r.axhline(0, color="#8a6d3b", linewidth=5, zorder=1)
        ax_r.axvline(0, color="black", linewidth=1.5, linestyle="--")
        ax_r.plot(soma, 0, "o", markersize=30, color=VERMELHO if soma > 0 else AZUL, markeredgecolor="black", zorder=5)
        ax_r.text(-limite_soma, 0.55, "CLASSE 0  %s" % ("%.1f%%" % ((1 - prob1) * 100)).replace(".", ","), color=AZUL,
                  fontsize=19, fontweight="bold", va="center")
        ax_r.text(limite_soma, 0.55, "%s  CLASSE 1" % ("%.1f%%" % (prob1 * 100)).replace(".", ","), color=VERMELHO,
                  fontsize=19, fontweight="bold", va="center", ha="right")
        ax_r.set_xlim(-limite_soma, limite_soma)
        ax_r.set_ylim(-1, 1)
        ax_r.axis("off")

        if j == 10 and q >= QUADROS_PASSO:
            classe = int(soma > 0)
            certo = classe == p["real"]
            veredito.set_text("previu classe %d com %s de certeza: %s" % (
                classe, ("%.1f%%" % (max(prob1, 1 - prob1) * 100)).replace(".", ","), "acertou" if certo else "ERROU"))
            veredito.set_color("#2e9e5b" if certo else VERMELHO)
        else:
            veredito.set_text("")
        return []

    animacao = FuncAnimation(fig, frame, frames=quadros, blit=False)
    destino = os.path.join(SAIDA, "cabo_de_guerra.mp4")
    animacao.save(destino, writer=FFMpegWriter(fps=FPS, bitrate=3500))
    plt.close(fig)

    resumo = {"duracao_s": round(len(quadros) / FPS), "pacientes": [
        {"letra": p["letra"], "real": p["real"], "prob1": float(1 / (1 + np.exp(-p["contrib"].sum()))),
         "maior_puxao": nomes[int(np.abs(p["contrib"]).argmax())]} for p in passos]}
    with open(os.path.join(SAIDA, "resumo_video.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)
    print("vídeo:", destino, resumo)


if __name__ == "__main__":
    main()
