import numpy as np

from ag import AlgoritmoGenetico, CROMOSSOMO, decodifica, avalia, no_maximo_global

EXECUCOES = 100


class Torneio(AlgoritmoGenetico):
    def __init__(self, k=3, **kwargs):
        super().__init__(**kwargs)
        self.k = k

    def roleta(self, aptidoes):
        competidores = self.rng.integers(0, len(aptidoes), size=(self.tamanho_populacao, self.k))
        vencedores = np.argmax(aptidoes[competidores], axis=1)
        return competidores[np.arange(self.tamanho_populacao), vencedores]


class Crowding(AlgoritmoGenetico):
    def executa(self, historico=False):
        n = self.tamanho_populacao
        populacao = self.rng.integers(0, 2, size=(n, CROMOSSOMO), dtype=np.uint8)
        aptidoes = avalia(decodifica(populacao))

        for _ in range(self.geracoes):
            ordem = self.rng.permutation(n)
            a, b = ordem[0::2], ordem[1::2]

            pais = np.empty_like(populacao)
            pais[0::2] = populacao[a]
            pais[1::2] = populacao[b]
            filhos = self._muta(self._cruza(pais))
            fa, fb = filhos[0::2], filhos[1::2]
            apt_a, apt_b = avalia(decodifica(fa)), avalia(decodifica(fb))

            distancia = lambda u, v: np.count_nonzero(u != v, axis=1)
            troca = (distancia(populacao[a], fb) + distancia(populacao[b], fa)
                     < distancia(populacao[a], fa) + distancia(populacao[b], fb))

            rival_a = np.where(troca[:, None], fb, fa)
            apt_rival_a = np.where(troca, apt_b, apt_a)
            rival_b = np.where(troca[:, None], fa, fb)
            apt_rival_b = np.where(troca, apt_a, apt_b)

            vence_a = apt_rival_a > aptidoes[a]
            vence_b = apt_rival_b > aptidoes[b]
            populacao[a[vence_a]] = rival_a[vence_a]
            aptidoes[a[vence_a]] = apt_rival_a[vence_a]
            populacao[b[vence_b]] = rival_b[vence_b]
            aptidoes[b[vence_b]] = apt_rival_b[vence_b]

        melhor = int(np.argmax(aptidoes))
        x, y = decodifica(populacao[melhor:melhor + 1])[0]
        return {"x": float(x), "y": float(y), "aptidao": float(aptidoes[melhor]), "historico": []}


def taxa(fabrica, execucoes=EXECUCOES):
    acertos = 0
    for semente in range(execucoes):
        r = fabrica(semente).executa()
        acertos += no_maximo_global(r["x"], r["y"])
    return acertos


def tabela_esquemas():
    esquemas = [
        ("torneio (k=3) + elitismo", lambda s: Torneio(raio_nicho=0, semente=s)),
        ("roleta + elitismo", lambda s: AlgoritmoGenetico(raio_nicho=0, semente=s)),
        ("roleta + fitness sharing", lambda s: AlgoritmoGenetico(semente=s)),
        ("deterministic crowding", lambda s: Crowding(semente=s)),
    ]
    print("Esquemas de selecao / diversidade")
    print("todos com 16 bits em Gray, 50 individuos, 300 geracoes,")
    print("cruzamento de dois pontos 0.9, mutacao 0.09, elitismo 2")
    print("")
    for nome, fabrica in esquemas:
        marca = "  <- usado" if nome == "roleta + fitness sharing" else ""
        print("  %-26s %3d/%d%s" % (nome, taxa(fabrica), EXECUCOES, marca))


def tabela_mutacao():
    print("")
    print("Sensibilidade a taxa de mutacao (roleta + fitness sharing, sigma = 1.0)")
    print("")
    for tm in [0.02, 0.05, 0.07, 0.09, 0.12]:
        marca = "  <- usado" if tm == 0.09 else ""
        print("  taxa %.2f                   %3d/%d%s"
              % (tm, taxa(lambda s, t=tm: AlgoritmoGenetico(taxa_mutacao=t, semente=s)),
                 EXECUCOES, marca))


def tabela_nicho():
    print("")
    print("Sensibilidade ao raio de nicho (roleta + fitness sharing, mutacao 0.09)")
    print("")
    for raio in [0, 0.5, 1.0, 1.5, 2.5]:
        nome = "sem sharing" if raio == 0 else "sigma %.1f" % raio
        marca = "  <- usado" if raio == 1.0 else ""
        print("  %-26s %3d/%d%s"
              % (nome, taxa(lambda s, r=raio: AlgoritmoGenetico(raio_nicho=r, semente=s)),
                 EXECUCOES, marca))


if __name__ == "__main__":
    tabela_esquemas()
    tabela_mutacao()
    tabela_nicho()
