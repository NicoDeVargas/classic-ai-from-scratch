# Naive Bayes Gaussiano no dataset Diabetes

Trabalho prático de Naive Bayes (Atividade prática 2): um classificador Naive Bayes Gaussiano escrito à
mão, sem biblioteca de aprendizado de máquina, para prever se a progressão do diabetes de um paciente fica
acima da média (classe 1) ou abaixo ou igual à média (classe 0).

O scikit-learn entra só para carregar o dataset e, num script separado, para conferir o nosso resultado.

## Como rodar

```
pip install numpy matplotlib scikit-learn imageio-ffmpeg
python trabalho.py
python confere_sklearn.py
python extras.py
python video.py
```

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
| `nb.py` | o classificador (treino, log das densidades, probabilidades) e a divisão treino/teste |
| `trabalho.py` | as Partes 1, 2 e 3 do enunciado, com os gráficos |
| `confere_sklearn.py` | compara o nosso classificador com o `GaussianNB` do scikit-learn |
| `extras.py` | os três estudos extras, em 300 divisões |
| `video.py` | o vídeo do cabo de guerra |
| `saida/trabalho_saida.txt` | tudo o que o enunciado pede, em texto |
| `saida/classes.png` | o target e as duas classes |
| `saida/gaussianas.png` | as curvas que o modelo aprende para cada feature |
| `saida/parte1.png` | acurácia das 10 divisões e a matriz de confusão |
| `saida/passo_a_passo.png`, `saida/contribuicoes.png` | a amostra analisada, feature por feature |
| `saida/parte2.png`, `saida/parte3.png` | o ranking das features e as 3 melhores contra as 10 |
| `saida/extra_*.png` | os gráficos dos extras |
| `saida/cabo_de_guerra.mp4` | vídeo: três pacientes sendo classificados |
| `slides/apresentacao.pptx` | apresentação com o vídeo embutido e as falas nas notas |

## O classificador

Para cada classe e cada feature, o treino guarda a média e a variância dos pacientes de treino, mais a
priori da classe. Para classificar, soma o log da priori com o log da densidade gaussiana de cada feature
e escolhe a classe com a maior soma. As probabilidades saem dessas somas, normalizadas.

Escolhas nossas, que o enunciado deixa em aberto:
- **Dados sem escala** (`scaled=False`), para os gráficos mostrarem idade em anos, IMC etc. O resultado é
  o mesmo com os dados normalizados.
- **Divisão 80% / 20%** por sorteio, com as sementes de 0 a 9. As Partes 1, 2 e 3 usam as mesmas dez
  divisões.
- **Variância populacional**, sem suavização. É o que o scikit-learn faz com `var_smoothing=0`.
- **A amostra analisada** é a primeira do teste em que o modelo acerta, a certeza fica entre 75% e 92% e
  pelo menos 3 features apontam para cada lado. Assim dá para ver as features disputando.

Conferência: nas 10 divisões, as 880 previsões de teste são iguais às do `GaussianNB`, e a maior
diferença nas probabilidades é de 4 × 10⁻¹⁵.

## Resultados

**Parte 1.** A média do target é 152,1: ficam 247 pacientes na classe 0 e 195 na classe 1.

| | acurácia média | desvio padrão |
|---|---|---|
| 10 divisões, todas as features | 73,1% | 3,8 pontos |

Matriz de confusão da última divisão (88 pacientes de teste):

| | previu 0 | previu 1 |
|---|---|---|
| **real 0** | 37 | 14 |
| **real 1** | 8 | 29 |

A amostra analisada (índice 125 do dataset, classe real 1):
- **log da priori:** −0,59 (classe 0) e −0,81 (classe 1);
- **log da posteriori:** −32,05 (classe 0) e −30,86 (classe 1);
- **probabilidades:** 23,4% e 76,6%;
- **classe escolhida:** 1.

Quem decide é o s5: o log da densidade é −3,27 na classe 0 e −0,97 na classe 1. Os logs de todas as
features, em ordem decrescente, estão em `saida/trabalho_saida.txt` e em `saida/contribuicoes.png`.

**Parte 2.** Uma feature por vez, nas mesmas 10 divisões:

| feature | acurácia média |
|---|---|
| s5 (log dos triglicerídeos) | 73,2% |
| bmi (IMC) | 71,0% |
| bp (pressão arterial) | 68,2% |
| s6 (glicose) | 65,9% |
| s4 (colesterol/HDL) | 64,7% |
| s3 (HDL) | 63,0% |
| s2 (LDL) | 57,8% |
| s1 (colesterol total) | 57,6% |
| age (idade) | 56,6% |
| sex (sexo) | 55,1% |

O s5 sozinho acerta tanto quanto o modelo com as 10 features.

**Parte 3.** Só com s5, bmi e bp:

| modelo | acurácia média | desvio padrão |
|---|---|---|
| 3 features | 73,1% | 5,5 pontos |
| 10 features | 73,1% | 3,8 pontos |

A média é a mesma. Com 3 features o modelo ganhou em 4 divisões, empatou em 1 e perdeu em 5. As outras 7
features não acrescentaram acurácia, mas 10 divisões é pouco para dizer qual dos dois é melhor.

## Extras

Vão além do enunciado. Todos usam 300 divisões (sementes de 1000 a 1299).

**Quantas features usar?** Acrescentando as features na ordem do ranking, a acurácia sobe até 5 features
(75,0%) e depois cai, até 72,6% com as 10. Com as 3 do enunciado dá 73,5%. O motivo provável é a
correlação: s1 e s2 têm correlação de 0,90, e o Naive Bayes, que supõe independência, conta a mesma
informação duas vezes. Ressalva: o ranking foi feito com os mesmos dados, então esse ganho pode estar um
pouco otimista.

**Dá para confiar na certeza do modelo?** Agrupando as previsões pela certeza declarada:

| modelo | certeza declarada | acerto real |
|---|---|---|
| 10 features | 99% | 82% |
| 3 features | 98% | 93% |

A hipótese ingênua quase não muda a classe escolhida, mas infla a probabilidade.

**E sem a hipótese ingênua?**

| modelo | acurácia média |
|---|---|
| Naive Bayes, 10 features | 72,6% |
| Naive Bayes depois de tirar a correlação com PCA | 73,0% |
| Bayes com covariância, uma por classe | 72,5% |
| Bayes com covariância, a mesma nas duas classes | 73,5% |
| Naive Bayes, as 5 melhores features | 75,0% |

Modelos mais sofisticados ganharam no máximo 0,9 ponto. Escolher as features rendeu 2,3.

**O vídeo** (`saida/cabo_de_guerra.mp4`, 40 s) mostra três pacientes do teste da última divisão. Cada
feature entra e puxa a soma dos logs para uma classe. O paciente A é a amostra analisada; no B quase todas as
features puxam para a classe 0; no C o modelo declara 98,8% de certeza e erra.
