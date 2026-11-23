import numpy as np
import skfuzzy as fz
from skfuzzy import control as ctrl

import fuzzy as F

if __name__ == "__main__":
    nosso = F.Controlador()
    fila = ctrl.Antecedent(F.FILA, "fila")
    espera = ctrl.Antecedent(F.ESPERA, "espera")
    ajuste = ctrl.Consequent(F.AJUSTE, "ajuste")
    for variavel, nome in ((fila, "fila"), (espera, "espera"), (ajuste, "ajuste")):
        for termo, (tipo, p) in F.TERMOS[nome].items():
            variavel[termo] = (fz.trimf if tipo == "tri" else fz.trapmf)(variavel.universe, list(p))
    regras = [ctrl.Rule(fila[f] & espera[w], ajuste[s]) for f, w, s in F.REGRAS]
    simulacao = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras))

    diferencas = []
    for f in np.linspace(0, 30, 31):
        for w in np.linspace(0, 120, 31):
            simulacao.input["fila"] = f
            simulacao.input["espera"] = w
            simulacao.compute()
            diferencas.append(abs(simulacao.output["ajuste"] - nosso.calcula(f, w)))
    print("pontos comparados: %d" % len(diferencas))
    print("maior diferença entre o nosso motor e o scikit-fuzzy: %.3f s" % max(diferencas))
