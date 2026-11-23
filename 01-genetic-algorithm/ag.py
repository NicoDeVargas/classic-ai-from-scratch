import numpy as np

LIMITE = 10.0
BITS = 16
N_VARS = 2
CROMOSSOMO = BITS * N_VARS
TOLERANCIA = 0.09

POTENCIAS = 2 ** np.arange(BITS - 1, -1, -1, dtype=np.int64)
ESCALA = (2.0 * LIMITE) / (2 ** BITS - 1)


def schaffer_f6(x, y):
    r2 = x * x + y * y
    return 0.5 - (np.sin(np.sqrt(r2)) ** 2 - 0.5) / (1.0 + 0.001 * r2) ** 2


def decodifica(populacao):
    genes = populacao.reshape(populacao.shape[0], N_VARS, BITS)
    binario = np.bitwise_xor.accumulate(genes, axis=2)
    return -LIMITE + (binario.astype(np.int64) @ POTENCIAS) * ESCALA


def avalia(pontos):
    return schaffer_f6(pontos[:, 0], pontos[:, 1])


def no_maximo_global(x, y, tolerancia=TOLERANCIA):
    return abs(x) <= tolerancia and abs(y) <= tolerancia


class AlgoritmoGenetico:
    def __init__(self, tamanho_populacao=50, geracoes=300, taxa_cruzamento=0.9,
                 taxa_mutacao=0.09, raio_nicho=1.0, elite=2, semente=None):
        self.tamanho_populacao = tamanho_populacao
        self.geracoes = geracoes
        self.taxa_cruzamento = taxa_cruzamento
        self.taxa_mutacao = taxa_mutacao
        self.raio_nicho = raio_nicho
        self.elite = elite
        self.rng = np.random.default_rng(semente)

    def executa(self, historico=False):
        n = self.tamanho_populacao
        populacao = self.rng.integers(0, 2, size=(n, CROMOSSOMO), dtype=np.uint8)
        pontos = decodifica(populacao)
        aptidoes = avalia(pontos)

        registro = [self._instantanea(0, pontos, aptidoes)] if historico else []

        for geracao in range(1, self.geracoes + 1):
            elites = populacao[np.argsort(aptidoes)[::-1][:self.elite]].copy()

            pais = populacao[self.roleta(self._compartilha(aptidoes, pontos))]
            filhos = self._cruza(pais)
            filhos = self._muta(filhos)
            filhos[:self.elite] = elites

            populacao = filhos
            pontos = decodifica(populacao)
            aptidoes = avalia(pontos)

            if historico:
                registro.append(self._instantanea(geracao, pontos, aptidoes))

        melhor = int(np.argmax(aptidoes))
        x, y = pontos[melhor]
        return {
            "x": float(x),
            "y": float(y),
            "aptidao": float(aptidoes[melhor]),
            "historico": registro,
        }

    def _compartilha(self, aptidoes, pontos):
        if not self.raio_nicho:
            return aptidoes
        distancias = np.linalg.norm(pontos[:, None, :] - pontos[None, :, :], axis=2)
        nicho = np.maximum(0.0, 1.0 - distancias / self.raio_nicho).sum(axis=1)
        return aptidoes / nicho

    def roleta(self, aptidoes):
        fatias = np.maximum(aptidoes, 1e-12)
        return self.rng.choice(len(fatias), size=self.tamanho_populacao,
                               p=fatias / fatias.sum())

    def _cruza(self, pais):
        pares = len(pais) // 2
        cortes = np.sort(self.rng.integers(1, CROMOSSOMO, size=(pares, 2)), axis=1)
        colunas = np.arange(CROMOSSOMO)[None, :]
        ativo = self.rng.random(pares) < self.taxa_cruzamento
        troca = (colunas >= cortes[:, :1]) & (colunas < cortes[:, 1:]) & ativo[:, None]

        a, b = pais[0::2], pais[1::2]
        filhos = np.empty_like(pais)
        filhos[0::2] = np.where(troca, b, a)
        filhos[1::2] = np.where(troca, a, b)
        return filhos

    def _muta(self, filhos):
        sorteio = self.rng.random(filhos.shape) < self.taxa_mutacao
        return np.bitwise_xor(filhos, sorteio.astype(np.uint8))

    @staticmethod
    def _instantanea(geracao, pontos, aptidoes):
        return {
            "geracao": geracao,
            "pontos": pontos,
            "melhor": float(np.max(aptidoes)),
            "pior": float(np.min(aptidoes)),
            "media": float(np.mean(aptidoes)),
        }
