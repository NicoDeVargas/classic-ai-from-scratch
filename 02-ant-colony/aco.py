import numpy as np

ALFA = 1.0
BETA = 5.0
Q = 100.0
TAU0 = 1.0
ITERACOES = 150
JANELA_CONVERGENCIA = 30


def carrega_matriz(caminho):
    d = np.loadtxt(caminho, delimiter=",", dtype=float)
    if d.shape[0] != d.shape[1]:
        raise ValueError("a matriz de distancias precisa ser quadrada")
    return d


def comprimento(rota, distancias):
    return float(distancias[rota, np.roll(rota, -1)].sum())


class ColoniaFormigas:
    def __init__(self, distancias, n_formigas=20, evaporacao=0.5, alfa=ALFA, beta=BETA,
                 q=Q, tau0=TAU0, iteracoes=ITERACOES,
                 janela_convergencia=JANELA_CONVERGENCIA, semente=None):
        self.distancias = np.asarray(distancias, dtype=float)
        self.n = self.distancias.shape[0]
        self.n_formigas = n_formigas
        self.evaporacao = evaporacao
        self.alfa = alfa
        self.beta = beta
        self.q = q
        self.tau0 = tau0
        self.iteracoes = iteracoes
        self.janela_convergencia = janela_convergencia
        self.rng = np.random.default_rng(semente)

        with np.errstate(divide="ignore"):
            self.visibilidade = np.where(self.distancias > 0, 1.0 / self.distancias, 0.0)
        np.fill_diagonal(self.visibilidade, 0.0)

    def constroi_rotas(self, feromonio):
        n, m = self.n, self.n_formigas
        peso = (feromonio ** self.alfa) * (self.visibilidade ** self.beta)

        rotas = np.empty((m, n), dtype=np.int64)
        rotas[:, 0] = self.rng.integers(0, n, size=m)
        disponivel = np.ones((m, n), dtype=bool)
        disponivel[np.arange(m), rotas[:, 0]] = False

        for passo in range(1, n):
            atual = rotas[:, passo - 1]
            preferencia = peso[atual] * disponivel
            total = preferencia.sum(axis=1, keepdims=True)

            uniforme = disponivel / np.maximum(disponivel.sum(axis=1, keepdims=True), 1)
            probabilidade = np.where(total > 0, preferencia / np.maximum(total, 1e-300), uniforme)

            sorteio = self.rng.random((m, 1))
            escolha = (probabilidade.cumsum(axis=1) < sorteio).sum(axis=1)
            escolha = np.minimum(escolha, n - 1)

            rotas[:, passo] = escolha
            disponivel[np.arange(m), escolha] = False

        return rotas

    def deposita(self, rotas, comprimentos):
        delta = np.zeros((self.n, self.n))
        origem = rotas
        destino = np.roll(rotas, -1, axis=1)
        contribuicao = np.repeat(self.q / comprimentos, self.n)
        np.add.at(delta, (origem.ravel(), destino.ravel()), contribuicao)
        return delta + delta.T

    def executa(self, historico=False, parar_na_convergencia=False):
        feromonio = np.full((self.n, self.n), self.tau0)
        np.fill_diagonal(feromonio, 0.0)

        melhor_rota = None
        melhor_distancia = np.inf
        ultima_melhora = 0

        curva = []
        registro = []
        primeira_estabilizacao = None

        for iteracao in range(1, self.iteracoes + 1):
            rotas = self.constroi_rotas(feromonio)
            comprimentos = np.array([comprimento(r, self.distancias) for r in rotas])

            indice = int(np.argmin(comprimentos))
            if comprimentos[indice] < melhor_distancia - 1e-12:
                melhor_distancia = float(comprimentos[indice])
                melhor_rota = rotas[indice].copy()
                ultima_melhora = iteracao

            feromonio = (1.0 - self.evaporacao) * feromonio + self.deposita(rotas, comprimentos)
            np.fill_diagonal(feromonio, 0.0)

            curva.append(melhor_distancia)
            if historico:
                registro.append({
                    "iteracao": iteracao,
                    "feromonio": feromonio.copy(),
                    "melhor_distancia": melhor_distancia,
                    "melhor_rota": melhor_rota.copy(),
                    "media_iteracao": float(comprimentos.mean()),
                })

            if iteracao - ultima_melhora >= self.janela_convergencia:
                if primeira_estabilizacao is None:
                    primeira_estabilizacao = ultima_melhora
                if parar_na_convergencia:
                    break

        executadas = len(curva)
        convergiu = executadas - ultima_melhora >= self.janela_convergencia

        return {
            "melhor_rota": melhor_rota,
            "melhor_distancia": melhor_distancia,
            "curva": np.array(curva),
            "iteracoes_executadas": executadas,
            "iteracao_convergencia": ultima_melhora if convergiu else None,
            "primeira_estabilizacao": primeira_estabilizacao,
            "ultima_melhora": ultima_melhora,
            "convergiu": convergiu,
            "historico": registro,
        }


def coordenadas(distancias):
    n = np.asarray(distancias).shape[0]
    angulos = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False) - np.pi / 2.0
    return np.column_stack([np.cos(angulos), np.sin(angulos)])


def coordenadas_por_rota(rota):
    rota = np.asarray(rota)
    circulo = coordenadas(np.zeros((len(rota), len(rota))))
    pontos = np.empty_like(circulo)
    pontos[rota] = circulo
    return pontos


def violacoes_triangulares(distancias):
    d = np.asarray(distancias, dtype=float)
    soma = d[:, :, None] + d[None, :, :]
    direta = d[:, None, :]
    n = d.shape[0]
    indices = np.arange(n)
    distintos = ((indices[:, None, None] != indices[None, :, None])
                 & (indices[None, :, None] != indices[None, None, :])
                 & (indices[:, None, None] != indices[None, None, :]))
    return int(np.count_nonzero((direta > soma + 1e-9) & distintos))
