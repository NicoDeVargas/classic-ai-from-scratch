import numpy as np

FILA = np.linspace(0, 30, 301)
ESPERA = np.linspace(0, 120, 1201)
AJUSTE = np.linspace(-10, 30, 801)


def trapezio(x, a, b, c, d):
    x = np.asarray(x, dtype=float)
    subida = np.ones_like(x) if a == b else np.clip((x - a) / (b - a), 0, 1)
    descida = np.ones_like(x) if c == d else np.clip((d - x) / (d - c), 0, 1)
    return np.minimum(subida, descida)


def triangulo(x, a, b, c):
    return trapezio(x, a, b, b, c)


TERMOS = {
    "fila": {
        "Baixa": ("trap", (0, 0, 6, 12)),
        "Média": ("tri", (6, 15, 24)),
        "Alta": ("trap", (18, 24, 30, 30)),
    },
    "espera": {
        "Curto": ("trap", (0, 0, 25, 50)),
        "Médio": ("tri", (25, 60, 95)),
        "Longo": ("trap", (70, 95, 120, 120)),
    },
    "ajuste": {
        "Reduzir": ("trap", (-10, -10, -6, 0)),
        "Manter": ("tri", (-6, 0, 6)),
        "Aumentar": ("trap", (0, 12, 30, 30)),
    },
}

REGRAS = [
    ("Baixa", "Curto", "Reduzir"),
    ("Baixa", "Médio", "Reduzir"),
    ("Baixa", "Longo", "Manter"),
    ("Média", "Curto", "Manter"),
    ("Média", "Médio", "Manter"),
    ("Média", "Longo", "Aumentar"),
    ("Alta", "Curto", "Aumentar"),
    ("Alta", "Médio", "Aumentar"),
    ("Alta", "Longo", "Aumentar"),
]


def pertinencia(variavel, termo, x, termos=TERMOS):
    tipo, p = termos[variavel][termo]
    return triangulo(x, *p) if tipo == "tri" else trapezio(x, *p)


class Controlador:
    def __init__(self, termos=TERMOS, regras=REGRAS, e="min", defuzz="centroide"):
        self.termos = termos
        self.regras = regras
        self.e = e
        self.defuzz = defuzz
        self.saidas = {t: pertinencia("ajuste", t, AJUSTE, termos) for t in termos["ajuste"]}

    def fuzzifica(self, fila, espera):
        return ({t: float(pertinencia("fila", t, fila, self.termos)) for t in self.termos["fila"]},
                {t: float(pertinencia("espera", t, espera, self.termos)) for t in self.termos["espera"]})

    def ativacoes(self, fila, espera):
        gf, ge = self.fuzzifica(fila, espera)
        juntar = min if self.e == "min" else (lambda a, b: a * b)
        return [juntar(gf[f], ge[w]) for f, w, _ in self.regras]

    def agrega(self, ativacoes):
        agregado = np.zeros_like(AJUSTE)
        for (_, _, saida), forca in zip(self.regras, ativacoes):
            agregado = np.maximum(agregado, np.minimum(forca, self.saidas[saida]))
        return agregado

    def defuzzifica(self, agregado):
        if agregado.sum() == 0:
            return 0.0
        if self.defuzz == "centroide":
            return float((AJUSTE * agregado).sum() / agregado.sum())
        if self.defuzz == "bissetor":
            acumulado = np.cumsum(agregado)
            return float(AJUSTE[np.searchsorted(acumulado, acumulado[-1] / 2)])
        topo = agregado >= agregado.max() - 1e-12
        return float(AJUSTE[topo].mean())

    def calcula(self, fila, espera):
        return self.defuzzifica(self.agrega(self.ativacoes(fila, espera)))

    def superficie(self, n_fila=61, n_espera=61):
        fs = np.linspace(0, 30, n_fila)
        ws = np.linspace(0, 120, n_espera)
        z = np.array([[self.calcula(f, w) for f in fs] for w in ws])
        return fs, ws, z
