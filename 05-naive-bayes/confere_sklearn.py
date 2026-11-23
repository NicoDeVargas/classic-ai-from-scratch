import numpy as np
from sklearn.naive_bayes import GaussianNB

from nb import NaiveBayesGaussiano, carrega, divide

if __name__ == "__main__":
    X, y, _ = carrega()
    maior = 0.0
    iguais = 0
    total = 0
    for semente in range(10):
        treino, teste = divide(len(y), semente)
        nosso = NaiveBayesGaussiano().treina(X[treino], y[treino])
        pronto = GaussianNB(var_smoothing=0).fit(X[treino], y[treino])
        maior = max(maior, np.abs(nosso.probabilidades(X[teste]) - pronto.predict_proba(X[teste])).max())
        iguais += (nosso.classifica(X[teste]) == pronto.predict(X[teste])).sum()
        total += len(teste)
    print("previsões iguais às do scikit-learn: %d de %d" % (iguais, total))
    print("maior diferença nas probabilidades: %.1e" % maior)
