# Controle fuzzy do tempo de semáforo

Trabalho prático de lógica fuzzy: um controlador que ajusta o tempo de verde da via secundária de um
cruzamento (GreenAdj) a partir do tamanho da fila (QueueSec) e do tempo médio de espera (WaitTimeSec).

| tipo | variável | intervalo | termos |
|---|---|---|---|
| entrada | QueueSec | 0 a 30 veículos | Baixa, Média, Alta |
| entrada | WaitTimeSec | 0 a 120 s | Curto, Médio, Longo |
| saída | GreenAdj | −10 a +30 s | Reduzir, Manter, Aumentar |

O enunciado pede: os gráficos das funções de pertinência, no mínimo 6 regras, a superfície 3D e a
análise dos resultados. A simulação do cruzamento (`extra_simulacao.py`) vai além do que foi pedido.

## Como rodar

```
pip install numpy matplotlib scikit-fuzzy imageio-ffmpeg
python trabalho.py
python confere_skfuzzy.py
python extra_simulacao.py
python extra_duas_vias.py
```

`extra_simulacao.py` roda cerca de 7.600 simulações em paralelo e gera o vídeo; leva uns 5 minutos.
Para pular o vídeo: `python extra_simulacao.py --sem-video`.

Slides (precisam do Node e do `python-pptx`):

```
cd slides
python figuras.py
python capas_video.py
node gerar_slides.js
python corrige_videos.py
```

Os slides leem os números de `saida/resumo_trabalho.json`, `saida/resumo_simulacao.json` e
`saida/resumo_duas_vias.json`. Nenhum
valor é digitado à mão. O `corrige_videos.py` corrige dois defeitos do pptxgenjs com vídeo (ids de
forma repetidos e a falta do bloco de timing que liga o clique ao play).

## Arquivos

| arquivo | o que é |
|---|---|
| `fuzzy.py` | o motor fuzzy (Mamdani) e o controlador: funções de pertinência e as 9 regras |
| `trabalho.py` | as tarefas do enunciado: gráficos, regras, exemplo de inferência, superfície e variações |
| `confere_skfuzzy.py` | compara o nosso motor com a biblioteca scikit-fuzzy |
| `simulacao.py` | o modelo do cruzamento |
| `extra_simulacao.py` | tempo fixo × fuzzy em 100 simulações por cenário, gráficos e vídeo |
| `extra_duas_vias.py` | versões que controlam também a via principal (slide de reserva) |
| `saida/pertinencia.png` | funções de pertinência das três variáveis |
| `saida/regras.png` | a base de 9 regras |
| `saida/inferencia_exemplo.png` | uma inferência passo a passo, no formato do visualizador do MATLAB |
| `saida/superficie_3d.png`, `saida/superficie_mapa.png` | a superfície de controle |
| `saida/extremos.png` | por que a saída não chega a −10 nem a +30 |
| `saida/variacoes.png` | a superfície com outras funções, só 6 regras e outra defuzzificação |
| `saida/simulacao_semaforo.mp4` | vídeo: os dois semáforos lado a lado no pico |
| `saida/duas_vias.png` | espera média das versões que controlam as duas vias |
| `saida/*_saida.txt` | a saída de texto dos scripts |
| `slides/apresentacao.pptx` | apresentação com o vídeo embutido e as falas nas notas |

## O controlador

**Inferência de Mamdani**, a mesma estrutura do exemplo do ventilador da aula:
- o E das regras é o **mínimo** dos graus;
- cada conjunto de saída é cortado na força da sua regra;
- as saídas das regras se juntam pelo **máximo**;
- a defuzzificação é pelo **centroide**.

O motor foi escrito do zero em `fuzzy.py`, para dar para explicar cada passo. Ele foi conferido com o
scikit-fuzzy em 961 pontos da superfície: a maior diferença foi de 0,015 s.

**Funções de pertinência.** Os intervalos e os nomes dos termos são do enunciado; o formato é escolha
nossa.

| variável | termo | forma | pontos |
|---|---|---|---|
| QueueSec | Baixa | trapézio | 0, 0, 6, 12 |
| | Média | triângulo | 6, 15, 24 |
| | Alta | trapézio | 18, 24, 30, 30 |
| WaitTimeSec | Curto | trapézio | 0, 0, 25, 50 |
| | Médio | triângulo | 25, 60, 95 |
| | Longo | trapézio | 70, 95, 120, 120 |
| GreenAdj | Reduzir | trapézio | −10, −10, −6, 0 |
| | Manter | triângulo | −6, 0, 6 |
| | Aumentar | trapézio | 0, 12, 30, 30 |

**Regras.** São 9, uma para cada combinação de termos; o enunciado pede no mínimo 6.

| fila \ espera | Curto | Médio | Longo |
|---|---|---|---|
| **Baixa** | Reduzir | Reduzir | Manter |
| **Média** | Manter | Manter | Aumentar |
| **Alta** | Aumentar | Aumentar | Aumentar |

## Resultados

**Exemplo de inferência** (fila de 20 veículos, espera de 70 s):
- **fuzzificação:** a fila é Média 0,44 e Alta 0,33; a espera é Médio 0,71;
- **regras ativas:** a 5 (Manter, força 0,44) e a 8 (Aumentar, força 0,33);
- **saída:** o centroide dá **+11,69 s**.

A regra de Manter disparou mais forte, mas a saída foi puxada para Aumentar. O centroide pesa pela
área, e o conjunto Aumentar é muito mais largo.

**Superfície.** O verde cresce com a fila e com a espera, em três platôs:
- **fila baixa:** reduz cerca de 6 s;
- **fila média, com espera curta ou média:** mantém;
- **fila alta, ou média com espera longa:** aumenta até cerca de 18 s.

O mesmo efeito de área cria uma subida mais brusca perto de 6 a 8 veículos com espera longa. Com
espera de 75 s, o ajuste vai de −4,2 para +5,7 s, mesmo com a regra de aumentar a uma força de só 0,2.

**A saída fica entre −6,30 e +17,76 s**, num universo de −10 a +30 s. Mesmo com Aumentar em 100%, o
centro de massa de um trapézio que vai de 0 a 30 fica longe da borda. É a pergunta do exercício da
gorjeta ("o maior valor é igual a 20%?"): com centroide, não é.

**Variações** (`saida/variacoes.png`):

| variação | faixa da saída | o que acontece |
|---|---|---|
| triângulos uniformes nas entradas | −6,3 a +17,8 s | a superfície vira uma rampa, sem platôs |
| só 6 regras | −6,3 a +17,8 s | em 11,6% das combinações nenhuma regra dispara: aparecem buracos |
| média dos máximos | −8 a +21 s | chega mais perto das bordas, mas a superfície vira degraus |

## Extra: o controlador num cruzamento simulado

O modelo, que é nosso e fica fora do enunciado:
- 2 horas de trânsito, com chegadas aleatórias nas duas vias;
- no verde, sai 1 carro a cada 2 s;
- amarelo de 3 s;
- a via principal recebe 900 veículos/h e tem verde fixo de 45 s;
- a via secundária tem um pico no meio das 2 horas.

A cada ciclo, o fuzzy lê a fila e a espera média dos carros parados na secundária e define o verde
como 30 s + GreenAdj, limitado entre 15 e 60 s. O tempo fixo usa sempre 30 s. Também testamos o
melhor tempo fixo de cada cenário, procurando de 15 a 60 s. São 100 simulações por configuração, e as
mesmas chegadas de carros valem para todos os semáforos.

Espera média por veículo, contando as duas vias:

| pico na secundária | fixo 30 s | melhor fixo | fuzzy |
|---|---|---|---|
| sem pico (216 veíc./h) | 25,6 s | **11,8 s** (verde 15 s) | 17,2 s |
| 432 veíc./h | 25,5 s | **15,3 s** (verde 18 s) | 18,0 s |
| 720 veíc./h | 31,3 s | 31,3 s (verde 30 s) | **24,4 s** |
| 1008 veíc./h | 108,5 s | 102,0 s (verde 36 s) | **77,3 s** |

- **Contra o tempo fixo de 30 s, o fuzzy ganha em todos os cenários.** Fora do pico ele encurta o
  verde da secundária, o ciclo fica mais curto e a via principal abre mais vezes. No pico ele estica o
  verde e esvazia a fila.
- **Contra o melhor tempo fixo, ele perde no trânsito leve.** O ideal seria um verde de 15 a 18 s, e
  o fuzzy não desce de uns 24 s, porque a saída do centroide nunca passa de −6,3 s. A média dos
  máximos, que alcança −8 s, melhora um pouco: 15,9 s no cenário sem pico.
- **Nos picos, ele ganha até do melhor fixo.** E o melhor fixo muda de 15 a 36 s conforme o cenário;
  na prática ninguém sabe o pico de antemão, e o fuzzy se ajusta sozinho.
- **O custo aparece no pico forte.** A espera na secundária cai de 267 para 87 s, mas a da principal
  sobe de 27 para 72 s. O controlador só enxerga a via secundária.

### E se o fuzzy controlasse as duas vias?

`extra_duas_vias.py` testa versões que também decidem o verde da via principal (partindo de 45 s,
entre 20 e 75 s). A melhor é o **misto**: o ajuste de cada via é a média de duas opiniões. Uma é a do
nosso controlador, com fila e espera da própria via. A outra é a de um comparador fuzzy de 9 regras, com
a fila da própria via e a da outra. Com a **média dos máximos** no lugar do centroide, ela fica assim
(espera média nas duas vias, 100 simulações; a última linha repete o teste com outras 100):

| versão | sem pico | 432 veíc./h | 720 veíc./h | 1008 veíc./h |
|---|---|---|---|---|
| tempo fixo de 30 s | 25,6 s | 25,5 s | 31,3 s | 108,5 s |
| melhor tempo fixo | **11,8 s** | **15,3 s** | 31,3 s | 102,0 s |
| fuzzy do trabalho (só a secundária) | 17,2 s | 18,0 s | 24,4 s | 77,3 s |
| duas vias, cada uma olhando a si mesma | 17,7 s | 18,3 s | 23,4 s | 63,1 s |
| duas vias, comparando as filas | 16,1 s | 18,0 s | 23,5 s | 68,6 s |
| misto, centroide | 16,4 s | 17,5 s | 22,5 s | 63,9 s |
| misto, média dos máximos | 15,7 s | 16,5 s | **21,5 s** | **60,8 s** |
| misto, média dos máximos (outras 100) | 15,7 s | 16,6 s | 21,8 s | 63,9 s |

Entre as versões fuzzy, o misto com média dos máximos tem a menor espera nos quatro cenários, e no pico
forte a via principal volta de 72 para 36 s. Mesmo assim, perde do melhor tempo fixo no trânsito leve. No
pico forte o cruzamento está no limite: o verde que uma via ganha, a outra perde. Isso fica num slide de
reserva (13), para as perguntas.

### O vídeo

O vídeo `saida/simulacao_semaforo.mp4` mostra os minutos 42 a 80 do cenário de 720 veíc./h (semente
0), com os dois semáforos lado a lado. Embaixo ficam os carros parados nas duas vias e a espera
acumulada. No pico, o fuzzy estica o verde da secundária e a fila da principal cresce (24 carros
contra 18), então o total de parados fica parecido. Quando o pico passa, o fuzzy esvazia a fila uns
dez minutos antes. No fim do trecho, a espera acumulada é de 11,4 veículo-hora contra 14,4 do tempo
fixo, 21% a menos.
