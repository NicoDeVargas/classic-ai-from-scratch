import json
import os

from arvore import ArvoreRegressao, carrega, divide
from extras import (grafico_corte_raiz, desenha_arvore, grafico_fora, grafico_k, grafico_modelos, grafico_importancia)
from fechamento_folga import grafico as grafico_fechamento
from trabalho import SAIDA, SEMENTES, VERMELHO, VERDE, grafico_divisoes, grafico_profundidade, grafico_quantidade


def le(nome):
    with open(os.path.join(SAIDA, nome), encoding="utf-8") as arq:
        return json.load(arq)


if __name__ == "__main__":
    t, e = le("resumo_trabalho.json"), le("resumo_extras.json")
    grafico_divisoes(t["parte1"], "parte1.png", VERMELHO)
    grafico_divisoes(t["parte2"], "parte2.png", VERDE)
    grafico_profundidade(t["parte3_arvore"], t["parte3_floresta"])
    grafico_quantidade(t["parte4"], t["melhor_floresta"])
    X, y = carrega()
    treino, _ = divide(len(y), SEMENTES[-1])
    grafico_corte_raiz(X[treino], y[treino])
    desenha_arvore(ArvoreRegressao(3).treina(X[treino], y[treino]), 3)
    grafico_fora(e["fora"])
    grafico_k(e["ks"])
    grafico_modelos(e["modelos"])
    grafico_importancia(e["importancia"])
    grafico_fechamento(le("resumo_folga.json"), le("resumo_fechamento.json"))
    print("figuras regeradas a partir dos resumos, sem repetir as simulações")
