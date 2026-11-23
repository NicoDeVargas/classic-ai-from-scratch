const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const RAIZ = path.dirname(__dirname);
const IMG = path.join(__dirname, "img");
const SAIDA = path.join(RAIZ, "saida");

const tr = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_trabalho.json"), "utf-8"));
const ext = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_extras.json"), "utf-8"));
const vid = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_video.json"), "utf-8"));

const ESCURO = "16242F";
const DESTAQUE = "E8A33D";
const VERDE = "2E9E5B";
const VERMELHO = "D9534F";
const AZUL = "2F6DB5";
const TINTA = "1F2933";
const CINZA = "5F6B76";
const CARTAO = "EEF1F3";
const BRANCO = "FFFFFF";
const CLARO = "CBD2D9";

const TITULO_FONTE = "Cambria";
const CORPO_FONTE = "Calibri";

const ALUNOS = [
  "David Lanza Melo Matos",
  "Lucca Molinari Barbosa",
  "Nicolas Rodrigues de Vargas",
];

function v(x, casas) {
  return x.toFixed(casas).replace(".", ",");
}

function pct(x, casas) {
  return v(x * 100, casas === undefined ? 1 : casas) + "%";
}

const p1 = tr.parte1;
const p3 = tr.parte3;
const am = tr.amostra;
const top3 = p3.features;
const rank = tr.parte2;
const m = p1.matriz;
const curva = ext.curva;
const melhorK = ext.melhor_k;
const cal10 = ext.calibracao_10[ext.calibracao_10.length - 1];
const cal3 = ext.calibracao_3[ext.calibracao_3.length - 1];
const corr = ext.correlacoes[0];
const mod = ext.modelos;
const FEATURES = Object.keys(am.valores);
const idx = (f) => FEATURES.indexOf(f);
const decisiva = FEATURES.map((f, i) => [f, am.log_densidade[1][i] - am.log_densidade[0][i]])
  .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))[0][0];

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Trabalho prático - Naive Bayes";
pres.title = "Naive Bayes Gaussiano no dataset Diabetes";

const L = 0.7;
const LARG = 11.9;

function tituloSlide(slide, texto) {
  slide.addText(texto, {
    x: L, y: 0.38, w: LARG, h: 0.85,
    isTextBox: true, margin: 0,
    fontFace: TITULO_FONTE, fontSize: 32, bold: true, color: TINTA, valign: "middle",
  });
}

function texto(slide, t, o) {
  slide.addText(t, Object.assign({
    isTextBox: true, margin: 0, fontFace: CORPO_FONTE, fontSize: 15, color: TINTA,
    valign: "top", lineSpacingMultiple: 1.12,
  }, o));
}

function cartao(slide, o) {
  slide.addShape(pres.ShapeType.roundRect, {
    x: o.x, y: o.y, w: o.w, h: o.h, rectRadius: 0.09,
    fill: { color: o.fundo || CARTAO },
    line: { color: o.borda || o.fundo || CARTAO, width: o.borda ? 1.75 : 0.75 },
  });
}

function faixa(slide, x, y, h, cor) {
  slide.addShape(pres.ShapeType.rect, { x: x, y: y, w: 0.08, h: h, fill: { color: cor }, line: { color: cor, width: 0.5 } });
}

function imagem(slide, arquivo, x, y, w, proporcao) {
  slide.addImage({ path: path.join(SAIDA, arquivo), x: x, y: y, w: w, h: w * proporcao });
}

function topicos(slide, itens, x, y, w, passo, alturaTexto) {
  itens.forEach((l, i) => {
    const yy = y + i * passo;
    faixa(slide, x, yy, passo - 0.2, l[0]);
    texto(slide, l[1], { x: x + 0.28, y: yy, w: w - 0.28, h: 0.38, fontSize: 15.5, bold: true });
    texto(slide, l[2], { x: x + 0.28, y: yy + 0.4, w: w - 0.28, h: alturaTexto || passo - 0.65, fontSize: 13.5, color: CINZA });
  });
}

function rodape(slide, t, y) {
  cartao(slide, { x: L, y: y, w: LARG, h: 7.2 - y, fundo: ESCURO });
  texto(slide, t, { x: L + 0.3, y: y, w: LARG - 0.6, h: 7.2 - y, fontSize: 14.5, color: CLARO, valign: "middle" });
}

/* ------------------------------------------------------------- 1 capa */
const s1 = pres.addSlide();
s1.background = { color: ESCURO };
s1.addImage({ path: path.join(IMG, "capa.png"), x: 7.6, y: 1.3, w: 5.4, h: 4.05 });
[AZUL, VERMELHO].forEach((cor, i) => {
  s1.addShape(pres.ShapeType.ellipse, { x: L + i * 0.42, y: 1.0, w: 0.28, h: 0.28, fill: { color: cor }, line: { color: cor, width: 0.5 } });
});
texto(s1, "TRABALHO PRÁTICO · NAIVE BAYES", {
  x: L, y: 1.5, w: 7.2, h: 0.34, fontSize: 14.5, bold: true, charSpacing: 2, color: DESTAQUE, valign: "middle",
});
texto(s1, "Naive Bayes Gaussiano\nno dataset Diabetes", {
  x: L, y: 1.95, w: 7.3, h: 1.9, fontFace: TITULO_FONTE, fontSize: 40, bold: true, color: BRANCO,
  lineSpacingMultiple: 1.05,
});
texto(s1, "Um classificador feito à mão para prever se a doença vai progredir acima da média", {
  x: L, y: 3.95, w: 6.6, h: 0.8, fontSize: 18, color: CLARO,
});
texto(s1, "ALUNOS", {
  x: L, y: 4.85, w: 7.2, h: 0.3, fontSize: 12, bold: true, charSpacing: 2, color: DESTAQUE, valign: "middle",
});
texto(s1, ALUNOS.join("\n"), {
  x: L, y: 5.2, w: 7.2, h: 1.0, fontSize: 15, color: BRANCO, lineSpacingMultiple: 1.2,
});
s1.addNotes(
  "INTEGRANTE 1 (abertura)\n\n" +
  "Bom dia. Nosso trabalho é sobre o Naive Bayes. Nós programamos o classificador do zero e usamos no dataset Diabetes, para prever se a doença de um paciente vai progredir acima ou abaixo da média.\n\n" +
  "Eu apresento os dados, como o classificador decide e o resultado da Parte 1. Depois vem um paciente analisado passo a passo, com um vídeo, e por fim a escolha das features, os extras e as conclusões."
);

/* ------------------------------------------------------------ 2 dados */
const s2 = pres.addSlide();
tituloSlide(s2, "Os dados e as duas classes");
imagem(s2, "classes.png", L, 1.3, 7.6, 4.6 / 10);
topicos(s2, [
  [CINZA, "O dataset", (tr.classes[0] + tr.classes[1]) + " pacientes, 10 medidas de cada um: idade, sexo, IMC, pressão e 6 exames de sangue."],
  [DESTAQUE, "De regressão para classificação", "O target é um número: a progressão da doença em um ano. Cortamos na média, " + v(tr.media_target, 1) + "."],
  [AZUL, "Classe 0: " + tr.classes[0] + " pacientes", "Progressão abaixo ou igual à média."],
  [VERMELHO, "Classe 1: " + tr.classes[1] + " pacientes", "Progressão acima da média."],
], 8.65, 1.35, 4.0, 1.12);
rodape(s2, "Em cada rodada, " + tr.n_treino + " pacientes treinam o modelo e " + tr.n_teste + " ficam de fora para o teste (80% / 20%).", 6.0);
s2.addNotes(
  "INTEGRANTE 1\n\n" +
  "O dataset tem " + (tr.classes[0] + tr.classes[1]) + " pacientes, com dez medidas de cada um: idade, sexo, IMC, pressão arterial e seis exames de sangue.\n\n" +
  "O que queremos prever é um número: quanto a doença progrediu em um ano. Como o enunciado pede, cortamos esse número na média, que é " + v(tr.media_target, 1) + ". Quem ficou acima é classe 1, quem ficou abaixo ou igual é classe 0.\n\n" +
  "Ficaram " + tr.classes[0] + " pacientes na classe 0, em azul, e " + tr.classes[1] + " na classe 1, em vermelho. Em todos os testes, 80% dos pacientes treinam o modelo e 20% ficam para o teste."
);

/* ----------------------------------------------------- 3 como decide */
const s3 = pres.addSlide();
tituloSlide(s3, "Como o Naive Bayes decide");
cartao(s3, { x: L, y: 1.35, w: LARG, h: 0.95, fundo: ESCURO });
texto(s3, "P(classe | paciente)  ∝  P(classe) × P(age | classe) × P(sex | classe) × … × P(s6 | classe)", {
  x: L, y: 1.35, w: LARG, h: 0.95, fontSize: 20, bold: true, color: BRANCO, align: "center", valign: "middle", fontFace: "Cambria Math",
});
const passos3 = [
  [CINZA, "1", "A priori", "Antes de olhar o paciente: que fração do treino é de cada classe?"],
  [AZUL, "2", "A verossimilhança", "Para cada feature, a altura da curva gaussiana da classe no valor do paciente."],
  [DESTAQUE, "3", "A parte ingênua", "Multiplica tudo como se as features não tivessem relação entre si."],
  [VERDE, "4", "A decisão", "Com logs a multiplicação vira soma. Ganha a classe com a maior soma."],
];
passos3.forEach((p, i) => {
  const x = L + i * 3.0;
  cartao(s3, { x: x, y: 2.65, w: 2.8, h: 3.0 });
  s3.addShape(pres.ShapeType.ellipse, { x: x + 0.25, y: 2.9, w: 0.62, h: 0.62, fill: { color: p[0] }, line: { color: p[0], width: 0.5 } });
  texto(s3, p[1], { x: x + 0.25, y: 2.9, w: 0.62, h: 0.62, fontSize: 20, bold: true, color: BRANCO, align: "center", valign: "middle" });
  texto(s3, p[2], { x: x + 0.25, y: 3.7, w: 2.35, h: 0.4, fontSize: 17, bold: true });
  texto(s3, p[3], { x: x + 0.25, y: 4.15, w: 2.35, h: 1.4, fontSize: 14, color: CINZA });
});
rodape(s3, "Por que log? Multiplicar 11 números pequenos dá um número minúsculo. Somar os logs dá a mesma resposta, sem perder precisão, e deixa ver quanto cada feature contribuiu.", 5.95);
s3.addNotes(
  "INTEGRANTE 1\n\n" +
  "Como o Naive Bayes decide. São quatro passos.\n\n" +
  "Primeiro, o palpite inicial, que se chama priori. Antes de olhar qualquer exame, o modelo já sabe que tem mais pacientes da classe 0 no treino, então começa apostando na classe 0.\n\n" +
  "Segundo, ele olha cada medida do paciente e pergunta: esse valor é mais comum na classe 0 ou na classe 1? Para responder, cada classe tem uma curva em forma de sino para cada medida, e o que conta é a altura da curva no valor do paciente.\n\n" +
  "Terceiro, a parte ingênua, que dá nome ao método: ele junta as dez respostas como se as medidas não tivessem relação entre si. Isso nem sempre é verdade, e no fim da apresentação mostramos a consequência.\n\n" +
  "Quarto, a decisão. Em vez de multiplicar vários números pequenos, somamos os logaritmos, que dá o mesmo resultado. Ganha a classe com a maior soma."
);

/* --------------------------------------------------------- 4 treino */
const s4 = pres.addSlide();
tituloSlide(s4, "Treinar é só medir médias e desvios");
imagem(s4, "gaussianas.png", L, 1.25, 11.9, 6.6 / 16);
cartao(s4, { x: L, y: 6.3, w: 7.3, h: 0.9 });
faixa(s4, L, 6.3, 0.9, AZUL);
texto(s4, "Para cada classe e cada feature: uma média e uma variância. São 40 números mais as duas prioris, e o modelo está pronto.", {
  x: L + 0.3, y: 6.3, w: 6.9, h: 0.9, fontSize: 14, valign: "middle",
});
cartao(s4, { x: 8.2, y: 6.3, w: 4.4, h: 0.9, fundo: ESCURO });
texto(s4, "Conferido com o scikit-learn: as 880 previsões de teste saíram idênticas.", {
  x: 8.4, y: 6.3, w: 4.0, h: 0.9, fontSize: 13.5, color: CLARO, valign: "middle",
});
s4.addNotes(
  "INTEGRANTE 1\n\n" +
  "Treinar esse modelo é muito simples: para cada classe e cada medida, calculamos a média e a variância dos pacientes de treino. Só isso, e o modelo está pronto.\n\n" +
  "Cada quadro é uma medida. A curva azul é a classe 0 e a vermelha é a classe 1. Onde as duas curvas estão separadas, como no bmi e no s5, a medida ajuda a distinguir as classes. Onde estão uma em cima da outra, como na idade e no sexo, ela quase não ajuda.\n\n" +
  "Escrevemos o classificador do zero e comparamos com o do scikit-learn: as 880 previsões de teste saíram idênticas."
);

/* --------------------------------------------------------- 5 parte 1 */
const s5 = pres.addSlide();
tituloSlide(s5, "Parte 1: o resultado em 10 divisões");
imagem(s5, "parte1.png", L, 1.3, 8.3, 5 / 13);
cartao(s5, { x: 9.35, y: 1.3, w: 3.25, h: 3.2, fundo: ESCURO });
texto(s5, "ACURÁCIA MÉDIA", { x: 9.55, y: 1.5, w: 2.85, h: 0.3, fontSize: 12, bold: true, charSpacing: 2, color: DESTAQUE });
texto(s5, pct(p1.media), { x: 9.55, y: 1.85, w: 2.85, h: 0.9, fontSize: 44, bold: true, color: BRANCO, fontFace: TITULO_FONTE });
texto(s5, "desvio padrão de " + v(p1.desvio * 100, 1) + " pontos", { x: 9.55, y: 2.8, w: 2.85, h: 0.4, fontSize: 14.5, color: CLARO });
texto(s5, "da pior divisão, " + pct(Math.min(...p1.acuracias)) + ", à melhor, " + pct(Math.max(...p1.acuracias)), {
  x: 9.55, y: 3.3, w: 2.85, h: 0.9, fontSize: 13.5, color: CLARO,
});
topicos(s5, [
  [AZUL, "Acertos na última divisão", m[0][0] + " da classe 0 e " + m[1][1] + " da classe 1, de " + tr.n_teste + " pacientes."],
  [VERMELHO, "Erros", m[0][1] + " alarmes falsos (previu 1, era 0) e " + m[1][0] + " casos que passaram (previu 0, era 1)."],
], L, 4.75, 8.3, 1.15);
cartao(s5, { x: 9.35, y: 4.75, w: 3.25, h: 2.1 });
texto(s5, "Chutar sempre a classe 0 acertaria " + pct(tr.classes[0] / (tr.classes[0] + tr.classes[1]), 0) + ". O modelo aprende, mas o problema é difícil: são pacientes perto da média.", {
  x: 9.55, y: 4.85, w: 2.85, h: 1.9, fontSize: 13.5, color: CINZA, valign: "middle",
});
s5.addNotes(
  "INTEGRANTE 1\n\n" +
  "Este é o resultado da Parte 1. Treinamos dez vezes, cada vez com uma divisão diferente entre treino e teste. A acurácia média foi de " + pct(p1.media) + ", com desvio padrão de " + v(p1.desvio * 100, 1) + " pontos.\n\n" +
  "Ao lado está a matriz de confusão do último treinamento. Dos " + tr.n_teste + " pacientes de teste, o modelo acertou " + m[0][0] + " da classe 0 e " + m[1][1] + " da classe 1, e errou " + (m[0][1] + m[1][0]) + ".\n\n" +
  "Para comparar: chutar sempre a classe 0 acertaria " + pct(tr.classes[0] / (tr.classes[0] + tr.classes[1]), 0) + ". Então o modelo aprende, mas o problema é difícil, porque muitos pacientes estão perto da média.\n\n" +
  "Agora vamos ver como ele decide um paciente."
);

/* --------------------------------------------------- 6 passo a passo */
const s6 = pres.addSlide();
tituloSlide(s6, "Um paciente, feature por feature");
imagem(s6, "passo_a_passo.png", L, 1.2, 11.9, 6.6 / 16);
rodape(s6, [
  { text: "A linha preta é o valor do paciente. ", options: { bold: true, color: BRANCO } },
  { text: "A bolinha mais alta mostra a classe em que esse valor é mais provável, e a borda do quadro fica da cor dela. Aqui, " + am.a_favor_1.length + " features apontam para a classe 1 e " + am.a_favor_0.length + " para a classe 0.", options: { color: CLARO } },
], 6.2);
s6.addNotes(
  "INTEGRANTE 2\n\n" +
  "O enunciado pede para escolher uma amostra do teste e mostrar a conta por dentro. Escolhemos este paciente porque as features dele discordam entre si, então dá para ver a disputa. A classe real dele é " + am.real + ".\n\n" +
  "Cada quadro é uma feature, com as duas curvas que o modelo aprendeu. A linha preta é o valor do paciente. As bolinhas marcam a altura de cada curva nesse valor: é a densidade de probabilidade. Embaixo de cada quadro está o log dessas duas alturas.\n\n" +
  "A borda do quadro tem a cor da classe que ganhou naquela feature. Por exemplo, o IMC dele é " + v(am.valores.bmi, 1) + ", mais típico da classe 0, então o quadro do bmi é azul. Já o " + decisiva + " é " + v(am.valores[decisiva], 2) + ", bem dentro da curva vermelha e quase fora da azul: ponto para a classe 1, e com muita diferença.\n\n" +
  "No total, " + am.a_favor_1.length + " features apontam para a classe 1 e " + am.a_favor_0.length + " para a classe 0. Mas não é uma votação: o que importa é o tamanho de cada diferença. É o que mostra o próximo slide."
);

/* --------------------------------------------------- 7 contribuicoes */
const s7 = pres.addSlide();
tituloSlide(s7, "A conta desse paciente");
imagem(s7, "contribuicoes.png", L, 1.2, 8.6, 6 / 16);
topicos(s7, [
  [CINZA, "a) Log da priori", "classe 0: " + v(am.log_priori[0], 2) + "   ·   classe 1: " + v(am.log_priori[1], 2)],
  [AZUL, "b) Log de cada feature", "Em ordem, da que mais ajuda a classe para a que menos ajuda."],
  [DESTAQUE, "c) Probabilidades", "soma dos logs: " + v(am.log_posteriori[0], 2) + " e " + v(am.log_posteriori[1], 2) + "  →  " + pct(am.probabilidades[0]) + " e " + pct(am.probabilidades[1])],
  [VERDE, "d) Classe escolhida: " + am.classe, "A classe real era " + am.real + ": o modelo acertou."],
], 9.5, 1.25, 3.15, 1.22);
rodape(s7, "Quem decide é o " + decisiva + ": na classe 0 ele vale " + v(am.log_densidade[0][idx(decisiva)], 2) + ", e na classe 1, " + v(am.log_densidade[1][idx(decisiva)], 2) + ". Essa diferença sozinha vira o resultado.", 6.3);
s7.addNotes(
  "INTEGRANTE 2\n\n" +
  "Aqui estão os quatro itens que o enunciado pede para essa amostra.\n\n" +
  "Item a, o log da priori: " + v(am.log_priori[0], 2) + " para a classe 0 e " + v(am.log_priori[1], 2) + " para a classe 1. A classe 0 começa na frente, porque tem mais pacientes no treino.\n\n" +
  "Item b, o log da densidade de cada feature, em ordem decrescente para cada classe. Todos os valores são negativos, porque são logs de números pequenos. Quanto mais perto de zero, mais aquela feature combina com a classe. Nas duas classes o sexo aparece no topo, mas com valores quase iguais, então ele não muda nada.\n\n" +
  "O que muda é o " + decisiva + ". Na classe 0 ele vale " + v(am.log_densidade[0][idx(decisiva)], 2) + ", e na classe 1 vale " + v(am.log_densidade[1][idx(decisiva)], 2) + ". É uma diferença de mais de dois pontos em log, maior do que a de todas as outras features juntas.\n\n" +
  "Item c: somando tudo, a classe 0 fica com " + v(am.log_posteriori[0], 2) + " e a classe 1 com " + v(am.log_posteriori[1], 2) + ". Convertendo de volta e normalizando para somar 100%, dá " + pct(am.probabilidades[0]) + " para a classe 0 e " + pct(am.probabilidades[1]) + " para a classe 1.\n\n" +
  "Item d: a classe escolhida é a " + am.classe + ", que é a classe real do paciente."
);

/* ----------------------------------------------------------- 8 video */
const s8 = pres.addSlide();
tituloSlide(s8, "O cabo de guerra, em vídeo");
s8.addMedia({
  type: "video",
  path: path.join(SAIDA, "cabo_de_guerra.mp4"),
  cover: "data:image/png;base64," + fs.readFileSync(path.join(IMG, "capa_cabo_de_guerra.png")).toString("base64"),
  x: L, y: 1.25, w: 8.4, h: 8.4 * 9 / 16,
});
texto(s8, "clique para reproduzir · " + vid.duracao_s + " s · três pacientes do teste", {
  x: L, y: 6.05, w: 8.4, h: 0.3, fontSize: 12.5, italic: true, color: CINZA, align: "center",
});
cartao(s8, { x: 9.35, y: 1.25, w: 3.25, h: 5.1, fundo: ESCURO });
texto(s8, "O que observar", { x: 9.6, y: 1.4, w: 2.8, h: 0.4, fontSize: 17, bold: true, color: DESTAQUE });
texto(s8, [
  "cada feature entra e puxa a corda para um lado",
  "paciente A: o do slide anterior, virado pelo " + decisiva,
  "paciente B: tudo puxa para a classe 0",
  "paciente C: " + pct(Math.max(vid.pacientes[2].prob1, 1 - vid.pacientes[2].prob1)) + " de certeza, e errou",
].map((t) => "• " + t).join("\n\n"), {
  x: 9.6, y: 1.9, w: 2.85, h: 4.3, fontSize: 13.5, color: CLARO,
});
s8.addNotes(
  "INTEGRANTE 2\n\n" +
  "[DAR PLAY NO VÍDEO — ele está embutido no slide, é só clicar. Dura " + vid.duracao_s + " segundos.]\n\n" +
  "Para visualizar essa conta, montamos um cabo de guerra. À esquerda aparece uma feature de cada vez, com as duas curvas e o valor do paciente. À direita, cada barra é a diferença entre os logs das duas classes: vermelha puxa para a classe 1, azul puxa para a classe 0. Embaixo, a bolinha na corda é a soma, e os percentuais são a probabilidade de cada classe naquele momento.\n\n" +
  "O paciente A é o do slide anterior. A corda começa do lado azul, por causa da priori, e fica lá até entrar o " + decisiva + ", que puxa tudo para a classe 1.\n\n" +
  "No paciente B, quase todas as features puxam para o mesmo lado, e o modelo termina com quase 100% de certeza na classe 0. Acertou.\n\n" +
  "O paciente C é o mais interessante. O modelo termina com " + pct(Math.max(vid.pacientes[2].prob1, 1 - vid.pacientes[2].prob1)) + " de certeza na classe 1, e erra: o paciente era da classe 0. Guardem esse caso, porque um dos nossos extras é exatamente sobre isso: o quanto dá para confiar na certeza que o Naive Bayes declara."
);

/* --------------------------------------------------------- 9 parte 2 */
const s9 = pres.addSlide();
tituloSlide(s9, "Parte 2: cada feature sozinha");
imagem(s9, "parte2.png", L, 1.25, 8.0, 5.4 / 11);
topicos(s9, [
  [VERDE, "As três melhores", top3.map((f, i) => f + " (" + pct(rank[i].media) + ")").join(", ") + "."],
  [CINZA, "As piores", rank.slice(-2).map((r) => r.feature).join(" e ") + ": pouco acima de 50%, quase um chute."],
  [DESTAQUE, "A surpresa", "O " + rank[0].feature + " sozinho acerta " + pct(rank[0].media) + ". O modelo com as 10 features acerta " + pct(p1.media) + "."],
], 9.0, 1.35, 3.6, 1.45);
rodape(s9, "O ranking repete o que as curvas do treino já mostravam: quanto mais separadas as duas gaussianas, mais a feature acerta sozinha.", 5.9);
s9.addNotes(
  "INTEGRANTE 2\n\n" +
  "Na Parte 2 treinamos dez modelos, cada um enxergando uma única feature, e medimos a acurácia média de cada um nas mesmas dez divisões.\n\n" +
  "O gráfico está em ordem. As três melhores são " + top3[0] + ", com " + pct(rank[0].media) + ", " + top3[1] + ", com " + pct(rank[1].media) + ", e " + top3[2] + ", com " + pct(rank[2].media) + ". Ou seja: o logaritmo dos triglicerídeos, o IMC e a pressão arterial. As piores são " + rank[8].feature + " e " + rank[9].feature + ", pouco acima de 50%, quase um chute.\n\n" +
  "Isso bate com o slide do treinamento: as features em que as duas curvas estavam separadas são as que acertam mais sozinhas.\n\n" +
  "E tem uma surpresa. O " + rank[0].feature + " sozinho acerta " + pct(rank[0].media) + ". O modelo completo, com as dez features, acerta " + pct(p1.media) + ". Uma feature só empata com as dez juntas. Isso levanta a pergunta da Parte 3: será que as outras features estão ajudando?"
);

/* -------------------------------------------------------- 10 parte 3 */
const s10 = pres.addSlide();
tituloSlide(s10, "Parte 3: três features contra dez");
imagem(s10, "parte3.png", L, 1.25, 7.6, 5 / 11);
const yq = 1.35;
[["10 FEATURES", pct(p1.media), "desvio " + v(p1.desvio * 100, 1), CINZA], ["3 FEATURES", pct(p3.media), "desvio " + v(p3.desvio * 100, 1), VERDE]].forEach((q, i) => {
  const x = 8.6 + i * 2.05;
  cartao(s10, { x: x, y: yq, w: 1.95, h: 1.9, fundo: ESCURO });
  texto(s10, q[0], { x: x, y: yq + 0.15, w: 1.95, h: 0.3, fontSize: 11.5, bold: true, charSpacing: 1.5, color: q[3] === CINZA ? CLARO : "7FD4A3", align: "center" });
  texto(s10, q[1], { x: x, y: yq + 0.5, w: 1.95, h: 0.75, fontSize: 30, bold: true, color: BRANCO, align: "center", fontFace: TITULO_FONTE });
  texto(s10, q[2], { x: x, y: yq + 1.3, w: 1.95, h: 0.4, fontSize: 13, color: CLARO, align: "center" });
});
topicos(s10, [
  [VERDE, "Mesma média", "Com " + top3.join(", ") + " o modelo acerta o mesmo que com as 10."],
  [DESTAQUE, "Mais instável", "Ganhou em " + p3.melhor + " divisões, empatou em " + p3.igual + " e perdeu em " + p3.pior + "."],
], 8.6, 3.5, 4.0, 1.2);
rodape(s10, "Sete features a mais não melhoraram a acurácia. Com só 10 divisões não dá para dizer quem é melhor, então fomos além do enunciado.", 5.9);
s10.addNotes(
  "INTEGRANTE 3\n\n" +
  "Na Parte 3 pegamos as três melhores features do ranking, " + top3.join(", ") + ", e treinamos o modelo só com elas, nas mesmas dez divisões.\n\n" +
  "O resultado: acurácia média de " + pct(p3.media) + ", com desvio de " + v(p3.desvio * 100, 1) + " pontos. O modelo com as dez features tinha dado " + pct(p1.media) + ", com desvio de " + v(p1.desvio * 100, 1) + ". A média é a mesma. Com três features o modelo oscila mais de uma divisão para outra: ganhou em " + p3.melhor + ", empatou em " + p3.igual + " e perdeu em " + p3.pior + ".\n\n" +
  "A leitura que fazemos é: as outras sete features não acrescentaram acurácia. Um modelo com três medidas, mais simples e mais barato, chega no mesmo lugar.\n\n" +
  "Mas dez divisões é pouco para dizer qual dos dois é melhor, a diferença fica dentro do ruído. Por isso fizemos três estudos extras, que vêm agora."
);

/* --------------------------------------------- 11 extra: quantas */
const s11 = pres.addSlide();
tituloSlide(s11, "Extra: quantas features usar?");
imagem(s11, "extra_curva.png", L, 1.25, 7.9, 5.2 / 11);
imagem(s11, "extra_correlacao.png", 8.75, 1.2, 3.9, 6 / 6.6);
rodape(s11, [
  { text: "Em " + ext.divisoes + " divisões, o melhor são " + melhorK + " features (" + pct(curva[melhorK - 1].media) + "). ", options: { bold: true, color: BRANCO } },
  { text: "Depois disso, cada feature a mais piora, até os " + pct(curva[9].media) + " das 10. O motivo está à direita: " + corr.a + " e " + corr.b + " têm correlação de " + v(corr.valor, 2) + ", e o modelo ingênuo conta a mesma informação duas vezes.", options: { color: CLARO } },
], 5.25);
s11.addNotes(
  "INTEGRANTE 3\n\n" +
  "Primeiro extra. Para tirar o ruído, repetimos o teste com " + ext.divisoes + " divisões em vez de dez, e fomos acrescentando as features uma a uma, na ordem do ranking.\n\n" +
  "A curva sobe até " + melhorK + " features, onde chega a " + pct(curva[melhorK - 1].media) + ", e depois desce. Com as dez, cai para " + pct(curva[9].media) + ". Com as três do enunciado dá " + pct(curva[2].media) + ". Ou seja, com mais divisões a diferença aparece: três features são um pouco melhores do que dez, e o melhor ponto fica em " + melhorK + ".\n\n" +
  "Por que mais informação piora? A resposta está na matriz de correlação. O s1, colesterol total, e o s2, o LDL, têm correlação de " + v(corr.valor, 2) + ": são quase a mesma medida. O Naive Bayes supõe que as features são independentes, então ele conta essa informação duas vezes. É a hipótese ingênua cobrando o preço. E as features fracas, como idade e sexo, só acrescentam ruído.\n\n" +
  "Uma ressalva honesta: o ranking foi feito com os mesmos dados, então esse ganho pode estar um pouco otimista."
);

/* ------------------------------------------- 12 extra: certeza */
const s12 = pres.addSlide();
tituloSlide(s12, "Extra: dá para confiar na certeza dele?");
imagem(s12, "extra_calibracao.png", L, 1.2, 7.0, 6 / 8.6);
topicos(s12, [
  [VERMELHO, "Com as 10 features", "Quando o modelo declara " + pct(cal10.certeza, 0) + " de certeza, acerta só " + pct(cal10.acerto, 0) + "."],
  [VERDE, "Com as 3 features", "Declara " + pct(cal3.certeza, 0) + " e acerta " + pct(cal3.acerto, 0) + ": bem mais perto do ideal."],
  [DESTAQUE, "Por quê?", "Features correlacionadas repetem a mesma evidência. A soma dos logs cresce, e a certeza infla."],
], 8.1, 1.35, 4.5, 1.45);
cartao(s12, { x: 8.1, y: 5.85, w: 4.5, h: 1.3, fundo: ESCURO });
texto(s12, "A hipótese ingênua quase não estraga a classe escolhida. O que ela estraga é a probabilidade.", {
  x: 8.3, y: 5.85, w: 4.1, h: 1.3, fontSize: 14.5, bold: true, color: BRANCO, valign: "middle",
});
s12.addNotes(
  "INTEGRANTE 3\n\n" +
  "Segundo extra, e o que mais nos surpreendeu. Lembram do paciente C do vídeo, em que o modelo tinha quase 99% de certeza e errou? Fomos ver se aquilo era azar ou padrão.\n\n" +
  "Nas " + ext.divisoes + " divisões, agrupamos as previsões pela certeza que o modelo declarou, e medimos quanto ele acertou de verdade em cada grupo. Num modelo ideal os pontos ficariam na linha tracejada: quem diz 90% acerta 90%.\n\n" +
  "A linha vermelha é o modelo com as dez features. Ele fica muito abaixo do ideal: quando declara " + pct(cal10.certeza, 0) + " de certeza, acerta só " + pct(cal10.acerto, 0) + ". Ele é confiante demais.\n\n" +
  "A linha verde é o modelo com três features. Quando declara " + pct(cal3.certeza, 0) + ", acerta " + pct(cal3.acerto, 0) + ". Bem mais honesto.\n\n" +
  "A explicação é a mesma do slide anterior. Features correlacionadas repetem a mesma evidência, a soma dos logs cresce além do que deveria, e a probabilidade final vai para perto de 0 ou de 100%. Então a hipótese ingênua quase não muda a classe escolhida, mas estraga a probabilidade. Num problema médico isso importa: 99% de certeza é diferente de 82%."
);

/* --------------------------------------- 13 extra: nao ingenuo */
const s13 = pres.addSlide();
tituloSlide(s13, "Extra: e se ele não fosse ingênuo?");
imagem(s13, "extra_modelos.png", L, 1.3, 7.8, 4.6 / 10);
topicos(s13, [
  [DESTAQUE, "Tirando a correlação antes", "Giramos os dados com PCA para as features ficarem sem correlação: " + pct(mod[1].media) + "."],
  [DESTAQUE, "Bayes com covariância", "A gaussiana completa, que enxerga a relação entre as features: " + pct(mod[2].media) + " e " + pct(mod[3].media) + "."],
  [VERDE, "Escolhendo as features", "O Naive Bayes simples com as " + melhorK + " melhores: " + pct(mod[4].media) + "."],
], 8.8, 1.35, 3.85, 1.45);
rodape(s13, "Trocar o modelo por um mais sofisticado rendeu no máximo " + v((Math.max(mod[1].media, mod[2].media, mod[3].media) - mod[0].media) * 100, 1) + " ponto. Escolher bem as features rendeu " + v((mod[4].media - mod[0].media) * 100, 1) + ". O ingênuo, bem alimentado, ganhou.", 5.9);
s13.addNotes(
  "INTEGRANTE 3\n\n" +
  "Terceiro extra. Se o problema é a hipótese ingênua, a pergunta natural é: e um Bayes que não seja ingênuo? Testamos três alternativas, nas mesmas " + ext.divisoes + " divisões.\n\n" +
  "A primeira tira a correlação antes: giramos os dados com PCA, de modo que as novas features não tenham correlação, e aí aplicamos o Naive Bayes. Deu " + pct(mod[1].media) + ".\n\n" +
  "A segunda e a terceira abandonam a hipótese de vez. Em vez de uma curva por feature, cada classe ganha uma gaussiana completa, com matriz de covariância, que enxerga a relação entre as features. Com uma covariância para cada classe deu " + pct(mod[2].media) + ", e com a mesma covariância nas duas classes, " + pct(mod[3].media) + ".\n\n" +
  "O Naive Bayes com as dez features tinha " + pct(mod[0].media) + ". Então os modelos mais sofisticados ganharam no máximo um ponto, e um deles até perdeu, porque tem muito mais parâmetros para estimar com poucos pacientes.\n\n" +
  "E o Naive Bayes simples, só com as " + melhorK + " melhores features, chegou a " + pct(mod[4].media) + ". A conclusão é curiosa: neste problema, escolher bem as features valeu mais do que trocar o modelo."
);

/* ------------------------------------------------------ 14 conclusoes */
const s14 = pres.addSlide();
s14.background = { color: ESCURO };
texto(s14, "Conclusões", { x: L, y: 0.45, w: LARG, h: 0.85, fontFace: TITULO_FONTE, fontSize: 32, bold: true, color: BRANCO, valign: "middle" });
const concl = [
  ["O classificador", "Feito à mão, igual ao do scikit-learn. Acurácia média de " + pct(p1.media) + " em 10 divisões, com desvio de " + v(p1.desvio * 100, 1) + " pontos."],
  ["Por dentro", "Somando logs dá para ver quanto cada feature pesa. No paciente analisado, o " + decisiva + " decidiu quase sozinho."],
  ["As features", top3.join(", ") + " são as melhores. Com só essas três, a acurácia é a mesma das dez."],
  ["O lado ingênuo", "Features correlacionadas contam em dobro: a classe quase não muda, mas a certeza infla. " + pct(cal10.certeza, 0) + " declarados viram " + pct(cal10.acerto, 0) + " de acerto."],
];
concl.forEach((c, i) => {
  const y = 1.6 + i * 1.15;
  texto(s14, c[0], { x: L, y: y, w: 2.8, h: 0.9, fontSize: 17, bold: true, color: DESTAQUE, valign: "middle" });
  texto(s14, c[1], { x: L + 2.9, y: y, w: 9.0, h: 0.9, fontSize: 16, color: BRANCO, valign: "middle" });
});
texto(s14, "Obrigado!", { x: L, y: 6.5, w: LARG, h: 0.5, fontSize: 18, bold: true, color: DESTAQUE });
s14.addNotes(
  "INTEGRANTE 3\n\n" +
  "Para fechar.\n\n" +
  "Programamos o Naive Bayes Gaussiano do zero, e ele dá exatamente as mesmas respostas do scikit-learn. No dataset Diabetes, a acurácia média foi de " + pct(p1.media) + " em dez divisões.\n\n" +
  "Trabalhar com a soma dos logs deixa o modelo transparente: dá para ver quanto cada feature pesou em cada decisão. No paciente que analisamos, o " + decisiva + " decidiu quase sozinho.\n\n" +
  "Testando uma feature por vez, as melhores são " + top3.join(", ") + ". Com só essas três, a acurácia é a mesma do modelo com dez.\n\n" +
  "E os extras mostraram o custo da hipótese ingênua. Features correlacionadas contam em dobro. Isso quase não muda a classe escolhida, mas infla a certeza: quando o modelo declara " + pct(cal10.certeza, 0) + ", acerta " + pct(cal10.acerto, 0) + ". Usar menos features, e bem escolhidas, melhora as duas coisas.\n\n" +
  "Obrigado. Estamos à disposição para perguntas."
);

pres.writeFile({ fileName: path.join(__dirname, "apresentacao.pptx") }).then((f) => {
  console.log("gerado:", f);
});
