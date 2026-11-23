# Algoritmo Genético — Schaffer's f6

Maximização de

    f(x, y) = 0.5 − ( sin²(√(x² + y²)) − 0.5 ) / ( 1 + 0.001·(x² + y²) )²

no espaço de busca `[-10, 10]` em x e y, com no máximo 50 indivíduos e 300 gerações.
O máximo global vale `1.0` em `(0, 0)`.

Uma execução conta como convergida quando o melhor indivíduo termina em
`-0.09 ≤ x ≤ 0.09` e `-0.09 ≤ y ≤ 0.09`. O enunciado exige que isso aconteça em pelo
menos 50% de 100 execuções.

**Resultado: 59 de 100 execuções (59%).**

## O que o enunciado fixa e o que foi escolha nossa

O enunciado define apenas o espaço de busca `[-10, 10]`, o limite de 50 indivíduos, o
limite de 300 gerações, a meta de 50% de convergência e as saídas a apresentar. Ele
**não define nenhum operador do AG** — nem seleção, nem cruzamento, nem mutação.

Escolhemos **seleção por roleta** porque é o método que vimos em aula, e tratamos como
objetivo do trabalho atingir a meta de 50% usando ela. Isso não é trivial nesta função,
e as seções abaixo mostram o que foi necessário para chegar lá.

O deterministic crowding aparece na comparação porque quisemos testar um esquema mais
eficiente e medir quanto ainda dava para ganhar no mesmo orçamento. Ele não é a entrega.

---

## O algoritmo entregue: roleta + fitness sharing

| componente | escolha |
|---|---|
| codificação | binária em código de Gray, 16 bits por variável (32 bits por indivíduo) |
| resolução | 20 / (2¹⁶ − 1) = 3.05 × 10⁻⁴ |
| **seleção** | **roleta, proporcional ao fitness** |
| **diversidade** | **fitness sharing, raio de nicho σ = 1.0** |
| cruzamento | dois pontos, taxa 0.9 |
| mutação | inversão de bit, taxa 0.09 |
| elitismo | 2 indivíduos por geração |
| população / gerações | 50 × 300 = 15.000 avaliações |

Tudo isso está em `ag.py`, em uma classe só (`AlgoritmoGenetico`).

### Uma geração, passo a passo

1. Guarda uma cópia dos 2 melhores indivíduos (elitismo).
2. Calcula o **fitness compartilhado**: divide o fitness de cada indivíduo pelo número
   de vizinhos dentro do raio σ = 1.0 (`_compartilha`).
3. Gira a **roleta** sobre esse fitness compartilhado e sorteia 50 pais (`roleta`).
4. Cruza os pais dois a dois, com dois pontos de corte, em 90% dos pares (`_cruza`).
5. Muta cada bit dos filhos com probabilidade 0.09 (`_muta`).
6. Reinsere os 2 elites no lugar dos 2 primeiros filhos.

### Por que fitness sharing

Os máximos locais da f6 formam anéis em `r = k·π`, e o primeiro anel já vale `0.99027`.
Um ponto só passa a valer mais que esse anel quando `r < 0.0985` — ou seja, quando já
está praticamente dentro da caixa de tolerância. Quem cai na bacia central mas ainda
longe da origem tem fitness baixo (em `r = 1.0` o fitness é `0.29`) e é eliminado pela
seleção antes de conseguir descer até o centro.

O sharing **não substitui a roleta**: ele apenas transforma o fitness que entra nela.
A fórmula é

    f'(i) = f(i) / Σⱼ sh(dᵢⱼ)        com   sh(d) = máx(0, 1 − d/σ)

onde `dᵢⱼ` é a distância euclidiana entre os indivíduos i e j em (x, y).

Um indivíduo isolado na bacia central não divide o fitness com ninguém e mantém os
`0.29` inteiros. Os 40 amontoados no anel dividem entre si e ficam com `0.99 / 40 ≈ 0.025`
cada. O isolado passa a ser o mais atraente da roleta, e a linhagem dele tem tempo de
descer até a origem.

Sem sharing a taxa cai de 59% para 48%, abaixo do exigido.

### Por que a mutação é 0.09

Esta é a diferença mais visível em relação a um AG de livro-texto, que costuma usar algo
como `1/L ≈ 0.03`. Aqui a mutação alta é intencional e tem a mesma função do sharing:
impedir que a população convirja cedo demais para o anel.

Mutação baixa deixa a população convergir, e uma vez convergida no anel ela para de
amostrar a região central — que é justamente onde está a resposta. Medido com o resto
da configuração fixa, 100 execuções cada:

| taxa de mutação | convergência |
|---|---|
| 0.02 | 37% |
| 0.05 | 40% |
| 0.07 | 60% |
| **0.09** (usado) | **59%** |
| 0.12 | 70% |

Abaixo de 0.05 o desempenho desaba. De 0.07 para cima o resultado estabiliza acima dos
50% exigidos; as diferenças dentro dessa faixa estão na margem de erro de 100 execuções
(cerca de 5 pontos percentuais). Ficamos com 0.09 por ser o valor que validamos em uma
amostra maior: 300 sementes independentes deram 59% e 58%.

### Por que 16 bits e não 22

Com 16 bits a resolução é `3.05 × 10⁻⁴`, cerca de 300 vezes mais fina que a tolerância
de `0.09` que precisamos atingir — precisão de sobra. Subir para 22 bits multiplica o
espaço de busca por 64 sem ganho útil, e a convergência piora dentro do orçamento de
15.000 avaliações.

O código de Gray importa: em binário comum, `32767` e `32768` são vizinhos mas diferem
em 16 bits, e nenhuma mutação de um bit faz essa travessia. Em Gray, valores vizinhos
diferem sempre em exatamente 1 bit.

### Por que σ = 1.0

| raio de nicho | convergência |
|---|---|
| sem sharing | 48% |
| 0.5 | 60% |
| **1.0** (usado) | **59%** |
| 1.5 | 50% |
| 2.5 | 51% |

Abaixo de 0.5 o sharing quase não age. Acima de 1.5 ele começa a penalizar indivíduos
que estão em anéis diferentes e que deveriam ser nichos separados.

---

## Comparação com outros esquemas

Para saber onde a nossa configuração se situa, medimos quatro esquemas com **os mesmos
parâmetros nos quatro** (16 bits em Gray, 50 × 300, cruzamento de dois pontos 0.9,
mutação 0.09, elitismo 2), variando apenas o mecanismo de seleção e diversidade.
100 execuções cada:

| esquema | convergência |
|---|---|
| torneio (k = 3) + elitismo | 28% |
| roleta + elitismo | 48% |
| **roleta + fitness sharing** (entregue) | **59%** |
| deterministic crowding | 80% |

- **Torneio** tem pressão seletiva alta demais: a população colapsa no anel `r = π` em
  poucas gerações.
- **Roleta pura** tem pressão fraca e preserva mais diversidade, mas com 300 gerações
  ainda converge para o anel. Fica em 48%, abaixo da meta.
- **Deterministic crowding** chega a 80% e é o melhor dos quatro. Ele não usa roleta em
  momento nenhum: cada filho compete diretamente com o pai mais parecido, e a competição
  local preserva os nichos sem precisar de nenhum raio ajustado à mão. Testamos ele para
  medir o teto do problema, mas a entrega é a versão com roleta, que era o objetivo que
  tínhamos definido.

Essa tabela é reproduzível — `comparativo.py` a gera do zero, junto com as duas tabelas
de sensibilidade acima:

```
python comparativo.py
```

---

## Estrutura

| arquivo | conteúdo |
|---|---|
| `ag.py` | função objetivo, codificação e operadores do AG entregue |
| `parte1.py` | execução única: melhor indivíduo, gráficos de fitness e vídeo da população |
| `parte2.py` | 100 execuções independentes e taxa de convergência |
| `comparativo.py` | reproduz as tabelas de comparação e de sensibilidade |
| `saida/` | gráficos, vídeo e log gerados |
| `slides/` | apresentação em pptx, figuras e scripts que a geram |

## Como executar

```
pip install numpy matplotlib imageio-ffmpeg
python parte1.py
python parte2.py
```

`parte1.py` demora alguns minutos porque renderiza o vídeo de 301 quadros.
`comparativo.py` demora mais, porque roda 1.400 execuções do AG.

## Saídas

Parte 1 (execução única, semente 0):

- melhor indivíduo: `x = 0.002289`, `y = -0.000153`, fitness `0.99999473`
- `saida/parte1_fitness_populacao.png` — melhor, médio e pior fitness por geração
- `saida/parte1_melhor_individuo.png` — fitness do melhor indivíduo por geração
- `saida/parte1_populacao.mp4` — população sobre as curvas de nível da f6, geração a
  geração, com o melhor indivíduo destacado em vermelho e um zoom na caixa de tolerância

> No vídeo e no gráfico da população, note que a população **não** converge: no fim,
> apenas 2 dos 50 indivíduos estão dentro da caixa de tolerância e os outros 48 seguem
> espalhados pelos anéis. Isso é o efeito pretendido do sharing com mutação 0.09 — se a
> população convergisse, o algoritmo ficaria preso no anel. O critério do enunciado é
> sobre o melhor indivíduo, não sobre a população.

Parte 2 (100 execuções):

- **59 de 100 convergiram (59%)**, fitness médio `0.99568179`
- `saida/parte2_resultados.txt` — x, y e fitness finais de cada execução, com a
  indicação de se atingiu o máximo global
- `saida/parte2_dispersao.png` — solução final de cada execução; as 41 que falharam
  formam o anel de raio π

## Apresentação

`slides/apresentacao.pptx` tem 13 slides com as falas de cada integrante nas notas do
apresentador (Integrante 1: slides 1–4, Integrante 2: slides 5–9, Integrante 3:
slides 10–13).

Para regerar:

```
python slides/figuras.py
npm install pptxgenjs
node slides/gerar_slides.js
```
