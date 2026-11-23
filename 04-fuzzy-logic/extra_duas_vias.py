import json
import os
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from fuzzy import Controlador, TERMOS
from simulacao import Cruzamento, medidas_fila, VERDE_BASE, VERDE_MIN, VERDE_MAX, VERDE_PRINCIPAL

RAIZ = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(RAIZ, "saida")
PICOS = [0.06, 0.12, 0.20, 0.28]
SEMENTES = range(100)
SEMENTES_VALIDACAO = range(100, 200)
PRINCIPAL_MIN = 20
PRINCIPAL_MAX = 75

TERMOS_COMPARA = {"fila": TERMOS["fila"], "espera": TERMOS["fila"], "ajuste": TERMOS["ajuste"]}
REGRAS_COMPARA = [
    ("Baixa", "Baixa", "Reduzir"),
    ("Baixa", "Média", "Reduzir"),
    ("Baixa", "Alta", "Reduzir"),
    ("Média", "Baixa", "Aumentar"),
    ("Média", "Média", "Manter"),
    ("Média", "Alta", "Reduzir"),
    ("Alta", "Baixa", "Aumentar"),
    ("Alta", "Média", "Aumentar"),
    ("Alta", "Alta", "Manter"),
]

VERSOES = {
    "trabalho": "só a via secundária (o trabalho)",
    "duas": "as duas vias, cada uma olhando a si mesma",
    "compara": "as duas vias, comparando as filas",
    "misto": "misto: média das duas opiniões",
    "misto_mom": "misto com média dos máximos",
}

CINZA = "#7f8c8d"
AMBAR = "#e8a33d"
AZUL_CLARO = "#9dbbe3"
AZUL = "#2f6db5"
VERDE = "#2e9e5b"


class CruzamentoDuasVias(Cruzamento):
    def __init__(self, modo, semente, pico, defuzz="centroide"):
        super().__init__(Controlador(defuzz=defuzz), semente, pico)
        self.modo = modo
        self.comparador = Controlador(TERMOS_COMPARA, REGRAS_COMPARA, defuzz=defuzz)

    def ajuste(self, propria, outra, t):
        n, espera = medidas_fila(propria, t)
        propria_opiniao = self.controlador.calcula(n, espera)
        if self.modo == "duas":
            return propria_opiniao
        comparacao = self.comparador.calcula(n, min(len(outra), 30))
        if self.modo == "compara":
            return comparacao
        return 0.5 * propria_opiniao + 0.5 * comparacao

    def decide(self, fila, t, decisoes):
        ajuste = self.ajuste(fila["sec"], fila["pri"], t)
        verde = int(round(np.clip(VERDE_BASE + ajuste, VERDE_MIN, VERDE_MAX)))
        decisoes.append((t, len(fila["sec"]), 0.0, ajuste, verde))
        return verde

    def decide_principal(self, fila, t):
        ajuste = self.ajuste(fila["pri"], fila["sec"], t)
        return int(round(np.clip(VERDE_PRINCIPAL + ajuste, PRINCIPAL_MIN, PRINCIPAL_MAX)))


def roda(versao, semente, pico):
    if versao == "fixo30":
        return Cruzamento(None, semente, pico).roda()
    if versao == "trabalho":
        return Cruzamento(Controlador(), semente, pico).roda()
    if versao == "misto_mom":
        return CruzamentoDuasVias("misto", semente, pico, defuzz="mom").roda()
    return CruzamentoDuasVias(versao, semente, pico).roda()


def tarefa(args):
    r = roda(*args)
    return args, (r["atraso_sec"], r["atraso_pri"], r["atraso_todos"])


def media(res, versao, pico, sementes):
    m = np.mean([res[(versao, s, pico)] for s in sementes], axis=0)
    return {"sec": float(m[0]), "pri": float(m[1]), "todos": float(m[2])}


def grafico(cenarios, melhores):
    series = [("tempo fixo (30 s)", CINZA, [c["fixo30"]["todos"] for c in cenarios]),
              ("melhor tempo fixo do cenário", AMBAR, [m["todos"] for m in melhores]),
              ("fuzzy do trabalho (só a secundária)", AZUL_CLARO, [c["trabalho"]["todos"] for c in cenarios]),
              ("fuzzy misto nas duas vias", AZUL, [c["misto"]["todos"] for c in cenarios]),
              ("fuzzy misto + média dos máximos", VERDE, [c["misto_mom"]["todos"] for c in cenarios])]
    fig, ax = plt.subplots(figsize=(12, 5.8))
    x = np.arange(len(PICOS))
    largura = 0.16
    for k, (rotulo, cor, valores) in enumerate(series):
        barras = ax.bar(x + (k - 2) * largura, valores, largura, color=cor, label=rotulo,
                        edgecolor="#1f2933" if k == 4 else cor, linewidth=1.4 if k == 4 else 0)
        for b, v in zip(barras, valores):
            ax.text(b.get_x() + b.get_width() / 2, v + 1.2, ("%.1f" % v).replace(".", ","), ha="center", fontsize=9,
                    fontweight="bold" if k == 4 else "normal")
    ax.set_xticks(x)
    ax.set_xticklabels([("sem pico (%d veíc./h)" if p <= 0.06 else "pico de %d veíc./h") % round(p * 3600)
                        for p in PICOS], fontsize=11)
    ax.set_ylabel("espera média por veículo (s)\nas duas vias")
    ax.legend(loc="upper left", fontsize=10.5)
    ax.grid(axis="y", alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    fig.tight_layout()
    fig.savefig(os.path.join(SAIDA, "duas_vias.png"), dpi=160)
    plt.close(fig)


def main():
    versoes = ["fixo30"] + list(VERSOES)
    tarefas = [(v, s, p) for v in versoes for p in PICOS for s in list(SEMENTES) + list(SEMENTES_VALIDACAO)]
    with ProcessPoolExecutor(max_workers=6) as ex:
        res = dict(ex.map(tarefa, tarefas, chunksize=8))

    with open(os.path.join(SAIDA, "resumo_simulacao.json"), encoding="utf-8") as arq:
        anterior = json.load(arq)
    melhores = [{"verde": c["melhor_fixo"]["verde"], "todos": c["melhor_fixo"]["todos"]} for c in anterior["cenarios"]]

    cenarios, validacao = [], []
    print("Extra: o fuzzy controlando as duas vias (espera média, as duas vias)")
    print("%-46s" % "" + "".join("%10d" % round(p * 3600) for p in PICOS))
    for p in PICOS:
        cenarios.append({"pico_veic_h": round(p * 3600), **{v: media(res, v, p, SEMENTES) for v in versoes}})
        validacao.append({"pico_veic_h": round(p * 3600), **{v: media(res, v, p, SEMENTES_VALIDACAO) for v in versoes}})
    for v in versoes:
        print("%-46s" % VERSOES.get(v, "tempo fixo 30 s") + "".join("%10.1f" % c[v]["todos"] for c in cenarios))
    print("%-46s" % "melhor tempo fixo" + "".join("%10.1f" % m["todos"] for m in melhores))
    print("\nvalidação com outras %d sementes" % len(SEMENTES_VALIDACAO))
    for v in versoes:
        print("%-46s" % VERSOES.get(v, "tempo fixo 30 s") + "".join("%10.1f" % c[v]["todos"] for c in validacao))

    grafico(cenarios, melhores)
    resumo = {"sementes": len(SEMENTES), "sementes_validacao": len(SEMENTES_VALIDACAO),
              "verde_principal_limites": [PRINCIPAL_MIN, PRINCIPAL_MAX], "versoes": VERSOES,
              "regras_comparacao": REGRAS_COMPARA, "cenarios": cenarios, "validacao": validacao,
              "melhor_fixo": melhores}
    with open(os.path.join(SAIDA, "resumo_duas_vias.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
