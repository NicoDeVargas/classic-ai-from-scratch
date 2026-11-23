# Árvores de regressão e floresta aleatória no dataset Diabetes

Trabalho prático de árvore de decisão: prever a progressão do diabetes (um número) com uma árvore de
regressão e com uma floresta aleatória, e estudar o efeito da profundidade e do número de árvores.

O enunciado não proíbe bibliotecas. Mesmo assim, a árvore e a floresta foram escritas do zero, só com
numpy. O scikit-learn entra para carregar o dataset e, num script separado, para conferir o resultado.

## Como rodar

```
pip install numpy matplotlib scikit-learn imageio-ffmpeg
python trabalho.py
python confere_sklearn.py
python extras.py
python videos.py
python fechamento.py
python fechamento_folga.py
python extra_alvo_torto.py
python demo.py
```

`trabalho.py` leva cerca de 2 minutos, `extras.py` cerca de 4 e `fechamento.py` cerca de 15, usando 6 processos.

Slides (precisam do Node e do `python-pptx`):

```
cd slides
python figuras.py
python capas_video.py
node gerar_slides.js
python corrige_videos.py
```

Os slides leem os números dos arquivos `saida/resumo_*.json`. Nenhum valor é digitado à mão.

## Arquivos

| arquivo | o que é |
|---|---|
| `arvore.py` | a árvore de regressão, a floresta aleatória, a divisão treino/teste e o MAE |
| `trabalho.py` | as Partes 1 a 4 do enunciado, com os gráficos |
| `confere_sklearn.py` | compara a nossa árvore e a nossa floresta com as do scikit-learn |
| `extras.py` | o passo a passo da primeira pergunta, o desenho da árvore e os três extras |
| `videos.py` | os dois vídeos |
| `regera_figuras.py` | redesenha todos os gráficos a partir dos resumos, sem repetir as simulações |
| `fechamento.py` | o AG e o PSO ajustando a floresta, e a comparação com o Naive Bayes |
| `fechamento_folga.py` | o PSO ajustando a árvore e o AG escolhendo medidas para o Naive Bayes |
| `extra_alvo_torto.py` | floresta contra regressão linear em um alvo inventado, da reta aos degraus |
| `demo.py`, `demo/floresta_ao_vivo.html` | a demonstração ao vivo |
| `saida/trabalho_saida.txt` | tudo o que o enunciado pede, em texto |
| `saida/parte1.png`, `saida/parte2.png` | MAE de treino e de teste nas 10 divisões |
| `saida/parte3.png` | efeito da profundidade, para a árvore e para a floresta |
| `saida/parte4.png` | efeito do número de árvores |
| `saida/arvore_desenho.png` | uma árvore de profundidade 3 treinada nos dados |
| `saida/corte_raiz.png` | como a primeira pergunta é escolhida, medida por medida |
| `saida/extra_*.png` | os gráficos dos extras |
| `saida/arvore_crescendo.mp4` | vídeo: a árvore recortando o mapa e decorando os pacientes |
| `saida/floresta_media.mp4` | vídeo: a média das árvores ficando suave |
| `slides/apresentacao.pptx` | apresentação com os vídeos embutidos e as falas nas notas |

## Os modelos

**Árvore de regressão.** Em cada nó, testa todos os cortes possíveis de todas as medidas e fica com o que
mais reduz a variância (a soma dos erros quadráticos dos dois lados). A folha prevê a média dos pacientes
de treino que caíram nela.

**Floresta aleatória.** Cada árvore treina com uma amostra sorteada com reposição e, em cada nó, escolhe
o corte só entre algumas medidas sorteadas. A previsão é a média das árvores.

Escolhas nossas, que o enunciado deixa em aberto:
- **Parte 1 sem limite de profundidade**, que é o padrão do scikit-learn. A árvore cresce até não
  conseguir dividir mais.
- **Parte 2 com 100 árvores e 3 medidas sorteadas por nó.** 3 é aproximadamente √10, a regra do material.
- **Parte 3 também para a floresta.** O enunciado pede o efeito da profundidade "da árvore"; fizemos para
  a árvore e para a floresta.
- **Parte 4 com profundidade 6**, a melhor da floresta na Parte 3. A melhor de uma árvore sozinha é 3.
- **Divisão 80% / 20%** por sorteio, com as sementes de 0 a 9, as mesmas nas quatro partes.
- **Dados sem escala** (`scaled=False`), para as perguntas aparecerem em unidades reais.

Conferência com o scikit-learn:

| modelo | nosso | scikit-learn |
|---|---|---|
| árvore de profundidade 3 | 49,83 | 50,01 |
| árvore sem limite | 64,08 | 63,73 |
| floresta (100 árvores, 3 medidas) | 46,87 | 47,62 |

Na profundidade 3, as previsões são idênticas em 9 das 10 divisões; na outra, há um empate entre dois
cortes que cada implementação resolve de um jeito. A árvore funda e a floresta dependem de sorteios e de
desempates, então só as médias são comparáveis.

## Resultados

MAE = erro médio absoluto. Prever sempre a média do treino dá um MAE de 67,3.

**Partes 1 e 2** (10 divisões):

| modelo | MAE de treino | MAE de teste | desvio do teste |
|---|---|---|---|
| uma árvore, sem limite | 0,0 | 64,1 | 4,2 |
| floresta de 100 árvores | 17,4 | 46,9 | 2,8 |

A árvore decora o treino e quase não ganha de prever a média. A floresta erra 27% menos e ganha nas 10
divisões. O MAE de cada divisão e os 5 exemplos do último modelo estão em `saida/trabalho_saida.txt`.

**Parte 3** (MAE de teste, média de 10 divisões):

| profundidade | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| uma árvore | 57,1 | 50,5 | **49,8** | 51,1 | 53,3 | 55,7 | 57,0 | 59,7 | 61,9 | 62,7 |
| floresta | 55,9 | 51,0 | 48,7 | 47,8 | 47,3 | **46,8** | 47,2 | 47,3 | 47,2 | 47,3 |

Uma árvore sozinha tem um ponto ótimo, na profundidade 3; depois o treino continua caindo e o teste sobe.
A floresta não piora: de 5 a 10 fica entre 46,8 e 47,3, uma diferença bem menor que o desvio padrão (2,8).
Não dá para dizer que 6 é melhor que 10.

**Parte 4** (floresta com profundidade 6):

| árvores | 5 | 10 | 20 | 40 | 80 |
|---|---|---|---|---|---|
| MAE de teste | 50,0 | 47,8 | 47,2 | 46,9 | 46,7 |
| desvio padrão | 3,7 | 3,5 | 3,1 | 2,9 | 2,8 |

Quase todo o ganho vem até 20 árvores.

## Extras

Vão além do enunciado.

**Um teste que vem de graça.** Cada árvore deixa de fora cerca de 37% dos pacientes do treino. Prevendo
cada paciente só com as árvores que não o viram, o MAE estimado é 47,3. O MAE medido no conjunto de teste
é 46,9. A floresta estima o próprio erro sem precisar separar um teste.

**Por dentro da floresta.** As medidas que mais reduzem a variância são s5 (23%), bmi (23%) e bp (12%): as
mesmas três melhores do trabalho de Naive Bayes. Já o sorteio de medidas rende pouco aqui (30 divisões):

| medidas sorteadas por nó | 1 | 3 | 5 | 10 (só bagging) |
|---|---|---|---|---|
| MAE de teste | 48,5 | 47,0 | 46,9 | 47,1 |

**A floresta é o melhor modelo?** Em 30 divisões:

| modelo | MAE de teste |
|---|---|
| prever sempre a média | 67,3 |
| uma árvore sem limite | 63,3 |
| uma árvore de profundidade 3 | 50,5 |
| bagging (100 árvores, todas as medidas) | 47,1 |
| floresta aleatória (100 árvores, 3 medidas) | 47,0 |
| boosting (100 árvores de profundidade 2, taxa 0,1) | 46,2 |
| regressão linear | **44,7** |

A regressão linear ganha de todos. A explicação provável é que o efeito das medidas é quase uma reta, e
árvores só fazem degraus. O boosting e a regressão linear também foram escritos à mão; o boosting usa uma
configuração padrão, sem ajuste.

**E se os dados não fossem uma reta?** `extra_alvo_torto.py` mantém os mesmos pacientes e as mesmas 10
divisões e troca só o alvo por um alvo inventado por nós, com o mesmo ruído dos dados reais. Ele mistura
uma reta (o ajuste linear dos dados reais) com um alvo torto (IMC e s5 altos ao mesmo tempo, pressão alta
com s3 baixo, e uma onda no s6):

| quanto do alvo é torto | 0% | 25% | 50% | 75% | 100% |
|---|---|---|---|---|---|
| regressão linear | 42,5 | 43,2 | 45,2 | 48,3 | 52,3 |
| floresta | 44,5 | 44,6 | 45,3 | 46,4 | 47,5 |
| divisões em que a floresta ganha | 0 de 10 | 3 de 10 | 5 de 10 | 8 de 10 | 9 de 10 |

Na reta pura a regressão linear ganha por 2,0, quase a diferença vista nos dados reais. Quando o alvo
entorta, ela piora 9,8 e a floresta só 3,0. O desvio entre divisões é grande e as faixas se sobrepõem;
o que sustenta a conclusão é a contagem de vitórias. É uma demonstração do porquê, não um resultado
sobre diabetes.

**Os vídeos** usam só bmi e s5, para dar para desenhar o mapa, então os números deles são diferentes dos
resultados acima. `arvore_crescendo.mp4` (20 s) mostra a árvore da profundidade 0 à 10: o erro de teste
é mínimo na profundidade 3 e depois sobe. `floresta_media.mp4` (24 s) mostra cada árvore sozinha, com erro
em torno de 63, e a média delas, que chega a 51 com 100 árvores.

## Fechamento: os trabalhos do semestre se encontram

`fechamento.py` usa os métodos dos trabalhos anteriores para tentar melhorar a floresta:
- **Algoritmo genético (trabalho 1):** cada cromossomo tem 10 bits e diz quais medidas a floresta usa.
  População de 12, 8 gerações, roleta, cruzamento de dois pontos (0,9), mutação (0,05 por bit), elite de 2.
- **Enxame de partículas (trabalho 3):** cada partícula é uma configuração: profundidade (1 a 12), medidas
  sorteadas por nó (1 a 10) e mínimo de pacientes para dividir um nó (2 a 40). 8 partículas, 10 iterações,
  inércia de 0,9 a 0,4, c1 = c2 = 2.

A busca só enxerga o treino de cada divisão: a aptidão é o erro fora da sacola de uma floresta de 40
árvores. O conjunto de teste só é usado no fim, com 100 árvores. São cerca de 195 configurações avaliadas
por divisão.

| floresta | erro estimado na busca | MAE de teste | melhor que a padrão em |
|---|---|---|---|
| padrão (10 medidas, sem limite, 3 sorteadas) | | 46,9 ± 2,8 | |
| com o AG escolhendo as medidas | 47,6 → 46,5 | 48,0 ± 3,5 | 3 de 10 divisões |
| com o PSO escolhendo a configuração | 46,5 → 45,8 | 47,3 ± 3,0 | 4 de 10 divisões |
| AG + PSO | | 48,0 ± 3,5 | 3 de 10 divisões |

A busca melhora o erro estimado, mas nenhuma versão ajustada ganha no teste. Ela escolhe a melhor entre
quase 200 configurações medidas nos mesmos pacientes, e parte desse ganho é sorte da amostra: a busca
também decora o treino. O AG manteve bmi e s5 nas 10 divisões.

Na pergunta do trabalho de Naive Bayes (acima ou abaixo da média), nas mesmas 10 divisões:

| modelo | acurácia |
|---|---|
| Naive Bayes | 73,1% ± 3,8 |
| árvore de profundidade 3 | 70,9% ± 3,3 |
| floresta aleatória | 74,2% ± 3,8 |

A floresta e o Naive Bayes empatam, dentro do desvio padrão.

### A busca onde há folga

`fechamento_folga.py` repete a ideia em dois lugares onde havia o que melhorar. A busca continua só
enxergando o treino: a aptidão é uma validação cruzada em 5 partes dentro do treino de cada divisão.

**O PSO ajustando uma árvore sozinha** (profundidade de 1 a 12, mínimo para dividir de 2 a 60):

| árvore | MAE de teste, 10 divisões | MAE de teste, outras 100 divisões |
|---|---|---|
| sem limite | 64,1 | 63,3 |
| ajustada pelo PSO | 50,7 | 50,5 |
| profundidade 3 fixa (referência da Parte 3) | 49,8 | 50,3 |

A árvore ajustada ganha da árvore sem limite em 10 de 10 divisões, e em 100 de 100 nas extras. O PSO não
conhece o resultado da Parte 3 e chega sozinho em árvores rasas (profundidade mediana 4).

**O AG escolhendo as medidas do Naive Bayes** (a pergunta do trabalho anterior):

| Naive Bayes | acurácia, 10 divisões | acurácia, outras 100 divisões |
|---|---|---|
| com as 10 medidas | 73,1% | 73,0% |
| com as medidas escolhidas pelo AG | 73,3% | 73,7% |

O ganho é pequeno: nas 100 divisões o AG é melhor em 53, igual em 16 e pior em 31. Mas ele usa em média
5,7 medidas em vez de 10, e mantém s5 em 100% das vezes, bmi em 91% e bp em 91%.

No trabalho de Naive Bayes, as 5 melhores medidas davam 75,0%. Aquele número era otimista, porque o
ranking tinha sido feito com os mesmos dados do teste. Com a escolha feita só no treino, o ganho real é
este, menor.

**A leitura:** a busca ajuda muito quando o modelo está mal ajustado (a árvore sem limite) e não ajuda
quando ele já está no limite (a floresta).

## Demonstração ao vivo

`demo/floresta_ao_vivo.html` é uma página só, que abre com dois cliques em qualquer navegador, sem internet.
Dentro dela estão três modelos treinados na última divisão: a árvore de profundidade 3, a árvore sem limite
e uma floresta de 100 árvores com profundidade 6. Mexendo nas 10 medidas do paciente, a página mostra:
- as três previsões;
- o caminho do paciente na árvore de 3 perguntas;
- o voto de cada uma das 100 árvores e a média;
- como a previsão muda quando só uma medida varia: a árvore sem limite dá saltos, a floresta muda suave.

O botão "Sortear um paciente real do teste" carrega um dos 88 pacientes de teste e mostra o valor real e o
erro de cada modelo. As previsões da página foram conferidas com as do Python (diferença máxima de 0,005,
por arredondamento).

Para gerar de novo: `python demo.py` (usa o modelo de página `demo/pagina.html`).
