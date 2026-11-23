import json
import os

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor

from arvore import ArvoreRegressao, carrega, divide, mae
from trabalho import SAIDA, SEMENTES, ARVORES, K

if __name__ == "__main__":
    X, y = carrega()
    with open(os.path.join(SAIDA, "resumo_trabalho.json"), encoding="utf-8") as arq:
        nosso = json.load(arq)
    iguais, total, deles_arvore, nossa3, deles3, deles_floresta = 0, 0, [], [], [], []
    for s in SEMENTES:
        treino, teste = divide(len(y), s)
        a = ArvoreRegressao(3).treina(X[treino], y[treino]).preve(X[teste])
        b = DecisionTreeRegressor(max_depth=3, random_state=0).fit(X[treino], y[treino]).predict(X[teste])
        iguais += int(np.allclose(a, b))
        total += 1
        nossa3.append(mae(y[teste], a))
        deles3.append(mae(y[teste], b))
        deles_arvore.append(mae(y[teste], DecisionTreeRegressor(random_state=0).fit(X[treino], y[treino]).predict(X[teste])))
        floresta = RandomForestRegressor(ARVORES, max_features=K, random_state=s).fit(X[treino], y[treino])
        deles_floresta.append(mae(y[teste], floresta.predict(X[teste])))
    resumo = {"iguais3": iguais, "total3": total, "nossa3": float(np.mean(nossa3)), "deles3": float(np.mean(deles3)),
              "nossa_arvore": nosso["parte1"]["media_teste"], "deles_arvore": float(np.mean(deles_arvore)),
              "nossa_floresta": nosso["parte2"]["media_teste"], "deles_floresta": float(np.mean(deles_floresta))}
    print("árvore de profundidade 3: previsões idênticas às do scikit-learn em %d de %d divisões" % (iguais, total))
    print("  MAE médio de teste: nossa %.2f   scikit-learn %.2f" % (resumo["nossa3"], resumo["deles3"]))
    print("árvore sem limite: nossa %.2f   scikit-learn %.2f" % (resumo["nossa_arvore"], resumo["deles_arvore"]))
    print("floresta (%d árvores, %d features): nossa %.2f   scikit-learn %.2f"
          % (ARVORES, K, resumo["nossa_floresta"], resumo["deles_floresta"]))
    print("(a árvore funda e a floresta dependem de sorteios e de desempates, então só as médias são comparáveis)")
    with open(os.path.join(SAIDA, "resumo_confere.json"), "w", encoding="utf-8") as arq:
        json.dump(resumo, arq, indent=2)
