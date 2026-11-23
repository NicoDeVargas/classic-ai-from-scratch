import base64
import json
import os

import numpy as np

from arvore import FEATURES, DESCRICAO, ArvoreRegressao, Floresta, carrega, divide
from trabalho import SEMENTES, ARVORES, K

RAIZ = os.path.dirname(os.path.abspath(__file__))
PASTA = os.path.join(RAIZ, "demo")
PROFUNDIDADE_FLORESTA = 6
PASSO = {"age": 1, "sex": 1, "bmi": 0.1, "bp": 1, "s1": 1, "s2": 1, "s3": 1, "s4": 0.05, "s5": 0.01, "s6": 1}
CASAS = {"age": 0, "sex": 0, "bmi": 1, "bp": 0, "s1": 0, "s2": 0, "s3": 0, "s4": 2, "s5": 2, "s6": 0}


def marca():
    tipos = {".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg"}
    for extensao, tipo in tipos.items():
        caminho = os.path.join(PASTA, "logo" + extensao)
        if os.path.exists(caminho):
            with open(caminho, "rb") as arq:
                return '<img alt="UFCI-MG" src="data:%s;base64,%s">' % (tipo, base64.b64encode(arq.read()).decode())
    return '<div class="sigla">UFCI-MG</div>'


def exporta(arvore):
    return {"f": arvore.feature.tolist(), "t": arvore.limiar.tolist(), "l": arvore.esq.tolist(),
            "r": arvore.dir.tolist(), "v": np.round(arvore.valor, 2).tolist()}


def main():
    X, y = carrega()
    treino, teste = divide(len(y), SEMENTES[-1])
    arvore3 = ArvoreRegressao(3).treina(X[treino], y[treino])
    funda = ArvoreRegressao().treina(X[treino], y[treino])
    floresta = Floresta(ARVORES, PROFUNDIDADE_FLORESTA, K, SEMENTES[-1]).treina(X[treino], y[treino])
    medio = np.median(X[treino], axis=0)
    dados = {
        "nomes": FEATURES, "descricao": [DESCRICAO[f] for f in FEATURES],
        "min": X.min(axis=0).tolist(), "max": X.max(axis=0).tolist(),
        "passo": [PASSO[f] for f in FEATURES], "casas": [CASAS[f] for f in FEATURES],
        "medio": [round(float(v) / PASSO[f]) * PASSO[f] for v, f in zip(medio, FEATURES)],
        "arvore3": exporta(arvore3), "funda": exporta(funda), "floresta": [exporta(a) for a in floresta.arvores],
        "teste": [{"indice": int(i), "x": X[i].tolist(), "y": float(y[i]),
                   "p3": float(arvore3.preve(X[i:i + 1])[0]), "pf": float(funda.preve(X[i:i + 1])[0]),
                   "pm": float(floresta.preve(X[i:i + 1])[0])} for i in teste],
    }
    with open(os.path.join(PASTA, "pagina.html"), encoding="utf-8") as arq:
        pagina = arq.read()
    destino = os.path.join(PASTA, "floresta_ao_vivo.html")
    with open(destino, "w", encoding="utf-8") as arq:
        arq.write(pagina.replace("/*LOGO*/", marca()).replace("/*DADOS*/", json.dumps(dados, ensure_ascii=False, separators=(",", ":"))))
    print("demonstração gerada:", destino, "(%d KB)" % (os.path.getsize(destino) // 1024))


if __name__ == "__main__":
    main()
