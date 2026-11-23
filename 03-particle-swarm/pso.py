import numpy as np

A = 10.0
LIMITE = 5.12
N_PARTICULAS = 15
ITERACOES = 100
W_MAX = 0.9
W_MIN = 0.4
FRACAO_VMAX = 0.2
TOLERANCIA = 1e-2


def rastrigin(x):
    x = np.asarray(x, dtype=float)
    return A * x.shape[-1] + np.sum(x ** 2 - A * np.cos(2 * np.pi * x), axis=-1)


def raio(x):
    diferencas = x[:, None, :] - x[None, :, :]
    return float(np.sqrt((diferencas ** 2).sum(-1)).max())


class EnxameParticulas:
    def __init__(self, c1, c2, n_particulas=N_PARTICULAS, iteracoes=ITERACOES,
                 w_max=W_MAX, w_min=W_MIN, fracao_vmax=FRACAO_VMAX, constricao=1.0,
                 dimensoes=2, semente=None):
        self.c1 = c1
        self.c2 = c2
        self.n = n_particulas
        self.iteracoes = iteracoes
        self.w_max = w_max
        self.w_min = w_min
        self.vmax = fracao_vmax * 2 * LIMITE if fracao_vmax else np.inf
        self.constricao = constricao
        self.dimensoes = dimensoes
        self.rng = np.random.default_rng(semente)

    def inercia(self, k):
        return self.w_max - k * (self.w_max - self.w_min) / self.iteracoes

    def executa(self, historico=False):
        rng = self.rng
        x = rng.uniform(-LIMITE, LIMITE, (self.n, self.dimensoes))
        escala = min(self.vmax, LIMITE)
        v = rng.uniform(-escala, escala, (self.n, self.dimensoes))
        f = rastrigin(x)
        p, fp = x.copy(), f.copy()
        g = int(np.argmin(fp))

        curva = [float(fp[g])]
        raios = [raio(x)]
        quadros = []

        def registra(k, w):
            if historico:
                quadros.append({"iteracao": k, "w": w, "x": x.copy(), "p": p.copy(),
                                "g": p[g].copy(), "fg": float(fp[g])})

        registra(0, self.inercia(0))
        for k in range(self.iteracoes):
            w = self.inercia(k)
            r1 = rng.random((self.n, self.dimensoes))
            r2 = rng.random((self.n, self.dimensoes))
            v = self.constricao * (w * v + self.c1 * r1 * (p - x) + self.c2 * r2 * (p[g] - x))
            v = np.clip(v, -self.vmax, self.vmax)
            x = x + v
            fora = np.abs(x) > LIMITE
            x = np.clip(x, -LIMITE, LIMITE)
            v[fora] = 0.0

            f = rastrigin(x)
            melhorou = f < fp
            p[melhorou] = x[melhorou]
            fp[melhorou] = f[melhorou]
            g = int(np.argmin(fp))

            curva.append(float(fp[g]))
            raios.append(raio(x))
            registra(k + 1, w)

        curva = np.array(curva)
        abaixo = np.flatnonzero(curva < TOLERANCIA)
        return {
            "gbest": p[g].copy(),
            "f_gbest": float(fp[g]),
            "convergiu": bool(fp[g] < TOLERANCIA),
            "iteracao_tolerancia": int(abaixo[0]) if len(abaixo) else None,
            "curva": curva,
            "raio": np.array(raios),
            "historico": quadros,
        }
