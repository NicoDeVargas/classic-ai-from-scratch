from collections import deque

import numpy as np

from fuzzy import Controlador

DURACAO = 7200
VAZAO = 0.5
AMARELO = 3
VERDE_PRINCIPAL = 45
VERDE_BASE = 30
VERDE_MIN = 15
VERDE_MAX = 60
CHEGADA_PRINCIPAL = 0.25
CHEGADA_SECUNDARIA_BASE = 0.06
CHEGADA_SECUNDARIA_PICO = 0.20
PICO = 3600
LARGURA_PICO = 900


def taxa_secundaria(t, pico=CHEGADA_SECUNDARIA_PICO):
    return CHEGADA_SECUNDARIA_BASE + (pico - CHEGADA_SECUNDARIA_BASE) * np.exp(-0.5 * ((t - PICO) / LARGURA_PICO) ** 2)


class Cruzamento:
    def __init__(self, controlador=None, semente=0, pico=CHEGADA_SECUNDARIA_PICO, registrar=False,
                 verde_fixo=VERDE_BASE):
        self.controlador = controlador
        self.verde_fixo = verde_fixo
        self.rng = np.random.default_rng(semente)
        self.pico = pico
        self.registrar = registrar

    def roda(self):
        fila = {"sec": deque(), "pri": deque()}
        atrasos = {"sec": [], "pri": []}
        credito = {"sec": 0.0, "pri": 0.0}
        verde_atual = VERDE_BASE if self.controlador else self.verde_fixo
        fase, restante = "verde_sec", verde_atual
        verdes, linha, decisoes = [], [], []
        for t in range(DURACAO):
            if self.rng.random() < taxa_secundaria(t, self.pico):
                fila["sec"].append(t)
            if self.rng.random() < CHEGADA_PRINCIPAL:
                fila["pri"].append(t)

            aberta = {"verde_sec": "sec", "verde_pri": "pri"}.get(fase)
            for via in ("sec", "pri"):
                if via == aberta:
                    credito[via] = min(credito[via] + VAZAO, 1.0)
                    if fila[via] and credito[via] >= 1.0:
                        atrasos[via].append(t - fila[via].popleft())
                        credito[via] -= 1.0
                else:
                    credito[via] = 0.0

            if self.registrar:
                linha.append((t, len(fila["sec"]), len(fila["pri"]), fase, verde_atual))

            restante -= 1
            if restante == 0:
                if fase == "verde_sec":
                    fase, restante = "amarelo_sec", AMARELO
                elif fase == "amarelo_sec":
                    fase, restante = "verde_pri", self.decide_principal(fila, t)
                elif fase == "verde_pri":
                    fase, restante = "amarelo_pri", AMARELO
                else:
                    verde_atual = self.decide(fila, t, decisoes)
                    fase, restante = "verde_sec", verde_atual
                    verdes.append(verde_atual)

        return {
            "atraso_sec": float(np.mean(atrasos["sec"])),
            "atraso_pri": float(np.mean(atrasos["pri"])),
            "atraso_todos": float(np.mean(atrasos["sec"] + atrasos["pri"])),
            "fila_max_sec": max(l[1] for l in linha) if linha else None,
            "atendidos_sec": len(atrasos["sec"]),
            "atendidos_pri": len(atrasos["pri"]),
            "restam_sec": len(fila["sec"]),
            "restam_pri": len(fila["pri"]),
            "verdes": verdes,
            "linha": linha,
            "decisoes": decisoes,
        }

    def decide(self, fila, t, decisoes):
        if self.controlador is None:
            return self.verde_fixo
        n, espera = medidas_fila(fila["sec"], t)
        ajuste = self.controlador.calcula(n, espera)
        verde = int(round(np.clip(VERDE_BASE + ajuste, VERDE_MIN, VERDE_MAX)))
        decisoes.append((t, n, espera, ajuste, verde))
        return verde

    def decide_principal(self, fila, t):
        return VERDE_PRINCIPAL


def medidas_fila(fila, t):
    n = min(len(fila), 30)
    espera = min(float(np.mean([t - c for c in fila])) if fila else 0.0, 120.0)
    return n, espera


