import numpy as np
from sklearn.datasets import load_diabetes

FEATURES = ["age", "sex", "bmi", "bp", "s1", "s2", "s3", "s4", "s5", "s6"]
DESCRICAO = {
    "age": "idade", "sex": "sexo", "bmi": "IMC", "bp": "pressão arterial", "s1": "colesterol total",
    "s2": "LDL", "s3": "HDL", "s4": "colesterol/HDL", "s5": "log dos triglicerídeos", "s6": "glicose",
}
TESTE = 0.2


def carrega():
    dados = load_diabetes(scaled=False)
    return dados.data, dados.target


def divide(n, semente, teste=TESTE):
    ordem = np.random.default_rng(semente).permutation(n)
    corte = int(round(n * teste))
    return ordem[corte:], ordem[:corte]


def mae(real, previsto):
    return float(np.abs(real - previsto).mean())


def melhores_cortes(X, y):
    ordem = np.argsort(X, axis=0, kind="stable")
    xs = np.take_along_axis(X, ordem, axis=0)
    ys = y[ordem]
    n = len(y)
    soma = np.cumsum(ys, axis=0)
    quadrados = np.cumsum(ys ** 2, axis=0)
    esquerda = np.arange(1, n)[:, None]
    sse = (quadrados[:-1] - soma[:-1] ** 2 / esquerda) + (quadrados[-1] - quadrados[:-1]
                                                            - (soma[-1] - soma[:-1]) ** 2 / (n - esquerda))
    sse[xs[1:] == xs[:-1]] = np.inf
    k = np.argmin(sse, axis=0)
    colunas = np.arange(X.shape[1])
    return sse[k, colunas], (xs[k, colunas] + xs[k + 1, colunas]) / 2


class ArvoreRegressao:
    def __init__(self, profundidade=None, minimo=2, k=None, semente=0):
        self.profundidade = profundidade
        self.minimo = minimo
        self.k = k
        self.rng = np.random.default_rng(semente)

    def treina(self, X, y):
        self.feature, self.limiar, self.esq, self.dir, self.valor, self.n, self.nivel, self.ganho = ([] for _ in range(8))
        self._cresce(X, y, 0)
        for nome in ("feature", "limiar", "esq", "dir", "valor", "n", "nivel", "ganho"):
            setattr(self, nome, np.array(getattr(self, nome)))
        return self

    def _cresce(self, X, y, nivel):
        no = len(self.valor)
        for lista, v in ((self.feature, -1), (self.limiar, 0.0), (self.esq, -1), (self.dir, -1),
                         (self.valor, float(y.mean())), (self.n, len(y)), (self.nivel, nivel), (self.ganho, 0.0)):
            lista.append(v)
        if len(y) < self.minimo or (self.profundidade is not None and nivel >= self.profundidade) or np.all(y == y[0]):
            return no
        candidatas = np.arange(X.shape[1]) if self.k is None else self.rng.choice(X.shape[1], self.k, replace=False)
        total = float(((y - y.mean()) ** 2).sum())
        candidatas = np.asarray(candidatas)
        erros, limiares = melhores_cortes(X[:, candidatas], y)
        c = int(np.argmin(erros))
        if not erros[c] < total - 1e-9:
            return no
        sse, f, limiar = float(erros[c]), int(candidatas[c]), float(limiares[c])
        lado = X[:, f] <= limiar
        self.feature[no], self.limiar[no], self.ganho[no] = f, limiar, total - sse
        self.esq[no] = self._cresce(X[lado], y[lado], nivel + 1)
        self.dir[no] = self._cresce(X[~lado], y[~lado], nivel + 1)
        return no

    def preve(self, X):
        nos = np.zeros(len(X), dtype=int)
        while True:
            internos = self.feature[nos] >= 0
            if not internos.any():
                return self.valor[nos]
            i = np.where(internos)[0]
            atual = nos[i]
            vai_esq = X[i, self.feature[atual]] <= self.limiar[atual]
            nos[i] = np.where(vai_esq, self.esq[atual], self.dir[atual])

    def folhas(self):
        return int((self.feature < 0).sum())


class Floresta:
    def __init__(self, arvores=100, profundidade=None, k=None, semente=0, bootstrap=True, minimo=2):
        self.n_arvores = arvores
        self.minimo = minimo
        self.profundidade = profundidade
        self.k = k
        self.semente = semente
        self.bootstrap = bootstrap

    def treina(self, X, y):
        rng = np.random.default_rng(self.semente)
        self.arvores, self.amostras = [], []
        for _ in range(self.n_arvores):
            sorteio = rng.integers(0, len(y), len(y)) if self.bootstrap else np.arange(len(y))
            arvore = ArvoreRegressao(self.profundidade, self.minimo, self.k, int(rng.integers(1 << 31)))
            self.arvores.append(arvore.treina(X[sorteio], y[sorteio]))
            self.amostras.append(sorteio)
        return self

    def preve_cada(self, X):
        return np.array([a.preve(X) for a in self.arvores])

    def preve(self, X):
        return self.preve_cada(X).mean(axis=0)

    def erro_fora_da_sacola(self, X, y):
        fora = np.array([~np.isin(np.arange(len(y)), a) for a in self.amostras])
        previsto = (self.preve_cada(X) * fora).sum(axis=0) / np.maximum(fora.sum(axis=0), 1)
        visto = fora.any(axis=0)
        return mae(y[visto], previsto[visto])
