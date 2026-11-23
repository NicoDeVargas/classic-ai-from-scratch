# Otimização por Colônia de Formigas (ACO) — Problema do Caixeiro Viajante

Implementação do ACO para uma instância do TSP com 20 cidades, lida de
`distancia_matrix.csv`, com análise de sensibilidade ao tamanho da colônia e à taxa de
evaporação do feromônio.

## Parâmetros

| parâmetro | valor | papel | origem |
|---|---|---|---|
| α (alfa) | 1 | peso do feromônio na decisão | enunciado (Partes 2 e 3) |
| β (beta) | 5 | peso da heurística local (1 / distância) | enunciado (Partes 2 e 3) |
| Q | 100 | constante de depósito de feromônio | enunciado (Partes 2 e 3) |
| elitismo | não usado | — | enunciado (Partes 2 e 3) |
| iterações | 150 | limite máximo | enunciado |
| τ₀ | 1.0 | feromônio inicial em todas as arestas | escolha nossa |
| formigas (Parte 1) | 20 | tamanho da colônia | escolha nossa |
| ρ (Parte 1) | 0.5 | taxa de evaporação | escolha nossa |

O enunciado fixa `alfa = 1`, `beta = 5`, `Q = 100` e "não utilize elitismo" nas **Partes 2 e
3**. A Parte 1 não especifica operador nem parâmetro nenhum — só a matriz de entrada, as 150
iterações e as saídas a apresentar. Usamos os mesmos valores na Parte 1 por coerência, para
que a execução única seja comparável às varreduras das outras partes.

O τ₀ igual a 1 vem do material da aula ("no início, como não há feromônios depositados, o
nível de feromônio pode ser considerado 1 para todas as arestas"), não do enunciado do
exercício.

A regra de transição é a do enunciado:

    p(i→j) = [ τ(i,j)^α · η(i,j)^β ] / Σ_l [ τ(i,l)^α · η(i,l)^β ]     com η = 1 / d

e a atualização do feromônio combina evaporação e depósito:

    τ(i,j) ← (1 − ρ) · τ(i,j) + Σ_k Δτ_k(i,j)        Δτ_k = Q / L_k

onde `L_k` é o comprimento da rota da formiga k, e o depósito só ocorre nas arestas que
ela percorreu. Como o TSP aqui é simétrico, o depósito é aplicado em (i,j) e em (j,i).

## Critério de convergência

Conforme o enunciado: a melhor distância encontrada precisa ficar **estável por pelo
menos 30 iterações consecutivas**. A iteração de convergência reportada é aquela em que
a melhor distância foi atingida pela última vez — ou seja, o ponto em que ela estabilizou.

Nas Partes 2 e 3 a execução **encerra assim que a convergência é detectada**, sem
completar as 150 iterações. A Parte 1 executa as 150 iterações completas para que o
vídeo mostre a dinâmica do feromônio depois da convergência.

### Uma consequência de rodar as 150 iterações inteiras

Essa diferença entre parar cedo e rodar tudo não é apenas de custo. Uma execução que
encerra ao detectar a convergência nunca descobre o que teria acontecido depois.

Na semente 0, por exemplo, a melhor distância estabiliza na iteração 32 e passa 30
iterações sem mudar — pelo critério do enunciado, convergiu. Mas rodando as 150
iterações completas a busca **volta a melhorar na iteração 137**, caindo de 1329 para
1328. Ou seja, o critério de 30 iterações é um teste prático de parada, não uma garantia
de que o ótimo foi alcançado.

Por isso `iteracao_convergencia` é decidida no fim da execução, a partir da última
melhora observada, e não travada na primeira vez que a janela de 30 é satisfeita. Uma
execução que melhora tarde demais para fechar a janela é reportada como **não
convergida**, que é a leitura honesta do critério.

## Estrutura

| arquivo | conteúdo |
|---|---|
| `aco.py` | núcleo do algoritmo: construção de rotas, depósito e evaporação |
| `parte1.py` | execução única: menor distância, gráfico de convergência, melhor rota e vídeo |
| `analise.py` | Partes 2 e 3: varreduras de formigas e de evaporação, tabelas e gráficos |
| `equilibrio.py` | análise complementar: existe uma taxa de evaporação ideal? |
| `distancia_matrix.csv` | matriz de adjacência 20×20 fornecida no enunciado |
| `saida/` | gráficos, vídeo e log gerados |
| `slides/` | apresentação em pptx, figuras e scripts que a geram |

## Como executar

```
pip install numpy matplotlib imageio-ffmpeg
python parte1.py
python analise.py
python equilibrio.py
```

`parte1.py` leva alguns minutos porque renderiza o vídeo de 150 quadros.

Para regerar a apresentação:

```
python slides/figuras.py
npm install pptxgenjs
node slides/gerar_slides.js
```

## Saídas

### Validação da implementação

Comparamos a rota do ACO com duas referências na mesma instância:

| método | distância |
|---|---|
| rota aleatória (média de 2000) | 3082.0 |
| vizinho mais próximo (melhor início) | 1428.0 |
| 2-opt sobre vizinho mais próximo | 1331.0 |
| **ACO** (média de 10 execuções) | **1328.1** |

O ACO supera o 2-opt, que é uma heurística forte de melhoria local. Nas 10 execuções o
resultado variou apenas entre 1328.0 e 1329.0.

**Parte 1** — execução única com 20 formigas e ρ = 0.5:

- menor distância encontrada: **1328.00**, com a rota completa impressa no terminal
- convergência na **iteração 24**, indicada no terminal e marcada no gráfico
- `saida/parte1_convergencia.png` — evolução da melhor distância por iteração
- `saida/parte1_melhor_rota.png` — a rota encontrada sobre as 20 cidades
- `saida/parte1_feromonio.mp4` — as 20 cidades ligadas por arestas cuja **cor e
  espessura** acompanham o feromônio, em escala de cinza: branco = 0, preto = máximo
  atingido durante a execução

  Sobre o vídeo: as arestas cinzas são o feromônio, exatamente como o enunciado pede, e os
  dois painéis mostram os mesmos dados em disposições diferentes. A **linha azul**
  sobreposta é um acréscimo nosso — ela mostra a melhor rota encontrada até
  aquele instante. Ela muda de lugar algumas vezes no começo e depois fica cravada; o
  momento em que para de se mexer é a convergência. O título indica há quantas iterações
  a rota está inalterada, e o painel inferior marca essa iteração na curva.

### Por que as cidades aparecem em círculo

O enunciado fornece distâncias, não coordenadas. A primeira tentativa foi posicionar as
cidades por MDS (*multidimensional scaling*), que procura o arranjo 2D que melhor reproduz
as distâncias dadas. Não funciona aqui: a matriz fornecida **não é métrica** — ela tem 562
violações da desigualdade triangular (existem trios onde ir direto de A a B é mais longo do
que passar por C). O MDS erra 38% da distância média, ou seja, desenharia um mapa que mente
sobre a instância.

Usamos então um **layout circular**, que não faz nenhuma afirmação geométrica: as 20 cidades
ficam igualmente espaçadas numa circunferência e as 190 arestas aparecem como cordas. A
posição no desenho não representa distância — só o feromônio, que é o que o enunciado pede
para visualizar.

O vídeo mostra **dois painéis lado a lado**, com exatamente os mesmos dados:

- **à esquerda**, o círculo ordenado pela rota final encontrada;
- **à direita**, o círculo na ordem original das cidades (0 a 19).

Ordenar o círculo pela solução é uma escolha de legibilidade, não um resultado. Com uma
ordem arbitrária, as 20 arestas da rota vencedora se cruzam por dentro do círculo e o
desenho vira um emaranhado — é exatamente o que o painel da direita mostra. Ordenando pelo
resultado, a mesma rota coincide com o anel externo e tudo que **não** faz parte dela
aparece como corda interna.

O painel da direita está no vídeo justamente para deixar isso explícito: o que muda entre
os dois lados é só a posição das cidades no desenho, não o algoritmo nem o feromônio. Como
a matriz não é geométrica, qualquer disposição seria igualmente arbitrária.

**Partes 2 e 3** — 10 execuções por configuração, α = 1, β = 5, Q = 100, sem elitismo:

- `saida/parte2_a_distancia.png` — média ± desvio padrão da distância por número de formigas
- `saida/parte2_b_iteracoes.png` — média de iterações até a convergência por número de formigas
- `saida/parte3_a_distancia.png` — média ± desvio padrão da distância por taxa de evaporação
- `saida/parte3_b_iteracoes.png` — média de iterações até a convergência por taxa de evaporação
- `saida/analise_resultados.txt` — as duas matrizes de resultados

As tabelas também são impressas no terminal, com as colunas pedidas no enunciado:
parâmetro variado, média da distância, desvio padrão e média de iterações até a
convergência. Acrescentamos uma coluna com o número de execuções que **não** convergiram
dentro das 150 iterações, para que a média de iterações não seja lida fora de contexto.

### Análise complementar: existe uma taxa de evaporação ideal?

Com os parâmetros do enunciado (α = 1, β = 5), a curva da Parte 3 sai praticamente plana:
todas as taxas de evaporação chegam a distâncias quase iguais. A teoria diz que deveria
existir um ponto de equilíbrio — pouca evaporação deixa a colônia presa no que aprendeu
cedo demais, evaporação demais apaga a memória antes que ela sirva. Então investigamos por
que ele não aparece, e em que condições aparece. **Esta análise é um acréscimo nosso; a
Parte 3 exigida pelo enunciado continua sendo a de cima, com α = 1 e β = 5.**

**Por que a curva do enunciado é plana.** Com β = 5, a visibilidade (1 / distância) entra na
decisão elevada à quinta potência: a distância domina a escolha da formiga e o feromônio
quase não pesa. Se o feromônio não pesa, a taxa com que ele evapora também não importa.

**O que acontece quando o feromônio importa.** Com β = 1, a decisão passa a depender do
feromônio, e o α define de que lado a evaporação atrapalha. `equilibrio.py` mede isso com
60 execuções por ponto (sementes 3000 a 3059), 20 formigas, Q = 100 e sem elitismo:

| ρ | α=1, β=5 (enunciado) | α=1,25, β=1 | α=1,5, β=1 | α=2, β=1 |
|---|---|---|---|---|
| 0.00 | 1332.3 | 1413.7 | 1345.9 | 1333.2 |
| 0.05 | 1330.8 | 1339.5 | 1332.3 | 1332.6 |
| 0.10 | 1330.7 | 1336.5 | 1330.5 | 1334.6 |
| 0.15 | 1330.4 | 1332.2 | 1332.0 | 1336.0 |
| 0.20 | 1329.8 | 1332.2 | 1332.4 | 1340.8 |
| 0.30 | 1330.1 | 1332.1 | 1333.5 | 1347.3 |
| 0.40 | 1330.1 | 1333.5 | 1336.0 | 1351.8 |
| 0.50 | 1329.1 | 1333.2 | 1336.2 | 1355.4 |
| 0.60 | 1329.5 | 1333.4 | 1338.9 | 1372.2 |
| 0.70 | 1330.2 | 1334.3 | 1344.4 | 1383.6 |
| 0.80 | 1329.6 | 1334.2 | 1348.2 | 1380.6 |
| 0.90 | 1329.4 | 1335.9 | 1351.7 | 1392.2 |
| 1.00 | 1329.4 | 1334.2 | 1363.7 | 1425.2 |

- **α = 1,25** — só evaporar pouco atrapalha (ρ = 0 é muito pior; o resto é plano).
- **α = 1,5** — os dois lados atrapalham: a curva tem forma de **U**, com ótimo em
  **ρ = 0.10** (distância 1330.5). ρ = 0 fica 15.5 acima do ótimo e ρ = 1 fica 33.2 acima.
- **α = 2** — só evaporar demais atrapalha (a curva sobe da esquerda para a direita).

**Rigor.** Encontramos a configuração α = 1,5, β = 1 numa varredura com as sementes 1000 a
1029 e a confirmamos em dois conjuntos independentes, que a busca nunca viu: sementes 2000 a
2029 e sementes 3000 a 3059 (esta última é a que gera os gráficos). Nos três, o mínimo fica
entre ρ = 0,10 e ρ = 0,15 e as duas pontas são piores com z > 3. Uma primeira tentativa com
α = 1, β = 1 também parecia ter forma de U, mas o lado direito desapareceu com sementes
novas — era ruído, e por isso não foi usada.

- `saida/parte3_c_equilibrio.png` — a curva em U para α = 1,5, β = 1, com intervalo de
  confiança de 95%
- `saida/parte3_d_familia.png` — as quatro configurações lado a lado, mostrando a transição
- `saida/resumo_equilibrio.json` — os números usados nos gráficos e nos slides

## Apresentação

`slides/apresentacao.pptx` tem 13 slides, com as falas nas notas do apresentador divididas
em três partes:

| parte | slides | conteúdo |
|---|---|---|
| Integrante 1 | 1–4 | problema, regra de transição, atualização do feromônio |
| Integrante 2 | 5–8 | parâmetros, Parte 1 (resultado e vídeo), Parte 2 |
| Integrante 3 | 9–13 | análise da Parte 2, Parte 3, o equilíbrio da evaporação e a conclusão |

Os números dos slides são lidos de `saida/resumo_parte1.json`, `saida/resumo_analise.json` e
`saida/resumo_equilibrio.json`, gerados pelos scripts — nenhum valor é digitado à mão no
gerador.

O vídeo do feromônio está **embutido no slide 7** — basta clicar para reproduzir durante a
apresentação, sem depender de arquivo externo. Isso leva o `.pptx` a cerca de 5 MB. O mp4
avulso continua em `saida/parte1_feromonio.mp4` como alternativa, caso a máquina da
apresentação não reproduza mídia embutida (Google Slides e LibreOffice às vezes não
reproduzem; o PowerPoint reproduz).

Para regerar:

```
python slides/figuras.py
npm install pptxgenjs
node slides/gerar_slides.js
```

## Observação sobre o enunciado

A Parte 3 pede "dois gráficos comparativos com o número de formigas no eixo X", mas nessa
parte o número de formigas é fixo em 20 e o que varia é a taxa de evaporação — o texto
repete a frase da Parte 2. Geramos os dois gráficos com **a taxa de evaporação no eixo X**,
que é a leitura coerente com o objetivo da análise.

As páginas 38 e 39 do material descrevem a Parte 1 duas vezes, e só a página 38 pede o
vídeo do feromônio. Entregamos o vídeo.
