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
    X = dados.data
    y = (dados.target > dados.target.mean()).astype(int)
    return X, y, dados.target


def divide(n, semente, teste=TESTE):
    ordem = np.random.default_rng(semente).permutation(n)
    corte = int(round(n * teste))
    return ordem[corte:], ordem[:corte]


class NaiveBayesGaussiano:
    def treina(self, X, y):
        self.classes = np.unique(y)
        self.log_priori = np.log(np.array([(y == c).mean() for c in self.classes]))
        self.media = np.array([X[y == c].mean(axis=0) for c in self.classes])
        self.variancia = np.array([X[y == c].var(axis=0) for c in self.classes])
        return self

    def log_densidade(self, X):
        X = np.atleast_2d(X)[:, None, :]
        return -0.5 * np.log(2 * np.pi * self.variancia) - (X - self.media) ** 2 / (2 * self.variancia)

    def log_posteriori(self, X):
        return self.log_priori + self.log_densidade(X).sum(axis=2)

    def probabilidades(self, X):
        lp = self.log_posteriori(X)
        lp = lp - lp.max(axis=1, keepdims=True)
        p = np.exp(lp)
        return p / p.sum(axis=1, keepdims=True)

    def classifica(self, X):
        return self.classes[self.log_posteriori(X).argmax(axis=1)]


def acuracias(X, y, colunas, sementes):
    resultado = []
    for s in sementes:
        treino, teste = divide(len(y), s)
        modelo = NaiveBayesGaussiano().treina(X[treino][:, colunas], y[treino])
        resultado.append((modelo.classifica(X[teste][:, colunas]) == y[teste]).mean())
    return np.array(resultado)
