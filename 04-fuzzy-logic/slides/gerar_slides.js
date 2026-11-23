const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const RAIZ = path.dirname(__dirname);
const IMG = path.join(__dirname, "img");
const SAIDA = path.join(RAIZ, "saida");

const tr = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_trabalho.json"), "utf-8"));
const sim = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_simulacao.json"), "utf-8"));
const dvias = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_duas_vias.json"), "utf-8"));

const ESCURO = "1E2328";
const AMBAR = "E8A33D";
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

function sinal(x, casas) {
  return (x >= 0 ? "+" : "−") + v(Math.abs(x), casas);
}

const ex = tr.exemplo;
const ativas = ex.ativacoes.filter((a) => a.forca > 0);
const sMin = tr.superficie.min;
const sMax = tr.superficie.max;
const deg = tr.degrau;
const mom = tr.variacoes.find((x) => x.titulo.startsWith("Defuzz"));
const cen = sim.cenarios;
const leve = cen[0];
const medio = cen[2];
const forte = cen[3];

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Trabalho prático - Lógica Fuzzy";
pres.title = "Controle fuzzy do tempo de verde de um semáforo";

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

/* ------------------------------------------------------------- 1 capa */
const s1 = pres.addSlide();
s1.background = { color: ESCURO };
s1.addImage({ path: path.join(IMG, "capa.png"), x: 7.9, y: 0.95, w: 5.1, h: 5.1 });
["D9534F", "E8A33D", "2E9E5B"].forEach((cor, i) => {
  s1.addShape(pres.ShapeType.ellipse, { x: L + i * 0.42, y: 1.0, w: 0.28, h: 0.28, fill: { color: cor }, line: { color: cor, width: 0.5 } });
});
texto(s1, "TRABALHO PRÁTICO · LÓGICA FUZZY", {
  x: L, y: 1.5, w: 7.2, h: 0.34, fontSize: 14.5, bold: true, charSpacing: 2, color: AMBAR, valign: "middle",
});
texto(s1, "Controle fuzzy do\ntempo de semáforo", {
  x: L, y: 1.95, w: 7.3, h: 1.9, fontFace: TITULO_FONTE, fontSize: 42, bold: true, color: BRANCO,
  lineSpacingMultiple: 1.05,
});
texto(s1, "Ajuste do tempo de verde da via secundária a partir da fila e do tempo de espera", {
  x: L, y: 3.95, w: 7.0, h: 0.8, fontSize: 18, color: CLARO,
});
texto(s1, "ALUNOS", {
  x: L, y: 4.85, w: 7.2, h: 0.3, fontSize: 12, bold: true, charSpacing: 2, color: AMBAR, valign: "middle",
});
texto(s1, ALUNOS.join("\n"), {
  x: L, y: 5.2, w: 7.2, h: 1.0, fontSize: 15, color: BRANCO, lineSpacingMultiple: 1.2,
});
s1.addNotes(
  "INTEGRANTE 1 (abertura)\n\n" +
  "Bom dia. Nosso trabalho é de lógica fuzzy: um controlador que ajusta o tempo de verde de um semáforo na via secundária, a partir do tamanho da fila e do tempo que os carros estão esperando.\n\n" +
  "Eu apresento o problema, a ideia da lógica fuzzy e as funções de pertinência. Depois vêm as regras, um exemplo de inferência passo a passo e a superfície de controle. Por fim, as variações, uma simulação de cruzamento que fizemos como extra e as conclusões.\n\n" +
  "A imagem da capa já é o resultado: a superfície de controle que vamos analisar."
);

/* --------------------------------------------------------- 2 problema */
const s2 = pres.addSlide();
tituloSlide(s2, "O problema");
texto(s2, "Semáforos de tempo fixo são ajustados para um trânsito médio. Quando o fluxo muda ao longo do dia, "
  + "o tempo de verde fica sobrando em horário vazio e faltando no pico.", {
  x: L, y: 1.35, w: LARG, h: 0.8, fontSize: 16, color: CINZA,
});
const vars = [
  ["Entrada", "QueueSec", "0 a 30 veículos", "Baixa, Média, Alta", "fila atual na via secundária", AZUL],
  ["Entrada", "WaitTimeSec", "0 a 120 s", "Curto, Médio, Longo", "tempo médio de espera dos veículos", AZUL],
  ["Saída", "GreenAdj", "−10 a +30 s", "Reduzir, Manter, Aumentar", "ajuste aplicado ao tempo de verde", VERMELHO],
];
const larg2 = [1.4, 2.2, 2.2, 3.1, 3.0];
const y2 = 2.4;
s2.addShape(pres.ShapeType.rect, { x: L, y: y2, w: LARG, h: 0.45, fill: { color: ESCURO }, line: { color: ESCURO, width: 0.5 } });
["Tipo", "Variável", "Intervalo", "Termos linguísticos", "O que é"].forEach((c, i) => {
  const x = L + larg2.slice(0, i).reduce((a, b) => a + b, 0);
  texto(s2, c, { x: x + 0.15, y: y2, w: larg2[i] - 0.3, h: 0.45, fontSize: 14.5, bold: true, color: BRANCO, valign: "middle" });
});
vars.forEach((linha, k) => {
  const y = y2 + 0.45 + k * 0.72;
  if (k % 2 === 0) {
    s2.addShape(pres.ShapeType.rect, { x: L, y: y, w: LARG, h: 0.72, fill: { color: CARTAO }, line: { color: CARTAO, width: 0.5 } });
  }
  linha.slice(0, 5).forEach((c, i) => {
    const x = L + larg2.slice(0, i).reduce((a, b) => a + b, 0);
    texto(s2, c, { x: x + 0.15, y: y, w: larg2[i] - 0.3, h: 0.72, fontSize: 15, bold: i < 2,
      color: i === 0 ? linha[5] : (i === 1 ? TINTA : CINZA), valign: "middle", fontFace: i === 1 ? "Consolas" : CORPO_FONTE });
  });
});
cartao(s2, { x: L, y: 5.2, w: LARG, h: 1.25 });
faixa(s2, L, 5.2, 1.25, AMBAR);
texto(s2, "A cada ciclo, o controlador olha a via secundária e responde com uma saída contínua: "
  + "aumentar, reduzir ou manter o verde, e em quantos segundos.", {
  x: L + 0.35, y: 5.35, w: LARG - 0.6, h: 0.95, fontSize: 16, valign: "middle",
});
s2.addNotes(
  "INTEGRANTE 1\n\n" +
  "O problema é o seguinte. A maioria dos semáforos funciona com tempo fixo: alguém calculou um tempo de verde para um trânsito médio, e ele vale o dia inteiro. Só que o trânsito não é médio o dia inteiro. No horário vazio sobra verde, e no pico ele falta.\n\n" +
  "O enunciado pede um controlador fuzzy para a via secundária de um cruzamento. Ele tem duas entradas: a fila, que vai de 0 a 30 veículos, e o tempo médio de espera, de 0 a 120 segundos. E uma saída, o GreenAdj, que é quanto somar ou tirar do tempo de verde, de menos 10 a mais 30 segundos.\n\n" +
  "Cada variável tem três termos linguísticos, como mostra a tabela. Reparem que a saída não é simétrica: dá para tirar no máximo 10 segundos, mas acrescentar até 30. Isso vai ter consequência mais adiante."
);

/* ---------------------------------------------------- 3 logica fuzzy */
const s3 = pres.addSlide();
tituloSlide(s3, "Como o controlador decide");
const passos = [
  ["1", "Fuzzificação", AZUL, "Cada entrada vira graus de pertinência. 20 veículos não é \"alta\" ou \"média\": é um pouco das duas."],
  ["2", "Inferência", AMBAR, "Cada regra SE… E… ENTÃO… dispara com a força da condição mais fraca (o E é o mínimo)."],
  ["3", "Defuzzificação", VERMELHO, "As saídas das regras são somadas por máximo e viram um número pelo centroide da área."],
];
passos.forEach((p, i) => {
  const x = L + i * 4.05;
  cartao(s3, { x: x, y: 1.4, w: 3.8, h: 3.05 });
  s3.addShape(pres.ShapeType.ellipse, { x: x + 0.25, y: 1.62, w: 0.55, h: 0.55, fill: { color: p[2] }, line: { color: p[2], width: 0.5 } });
  texto(s3, p[0], { x: x + 0.25, y: 1.62, w: 0.55, h: 0.55, fontSize: 18, bold: true, color: BRANCO, align: "center", valign: "middle" });
  texto(s3, p[1], { x: x + 0.95, y: 1.62, w: 2.7, h: 0.55, fontSize: 19, bold: true, valign: "middle" });
  texto(s3, p[3], { x: x + 0.25, y: 2.4, w: 3.35, h: 1.95, fontSize: 15, color: CINZA });
});
cartao(s3, { x: L, y: 4.75, w: LARG, h: 1.7, fundo: ESCURO });
texto(s3, "Nossa implementação", { x: L + 0.35, y: 4.9, w: 5, h: 0.4, fontSize: 17, bold: true, color: AMBAR });
texto(s3, "Mamdani, como no exemplo do ventilador da aula: E = mínimo, agregação = máximo, defuzzificação pelo centroide. "
  + "Escrevemos o motor do zero em Python e conferimos com a biblioteca scikit-fuzzy: na superfície inteira, a maior diferença foi de 0,015 s.", {
  x: L + 0.35, y: 5.35, w: LARG - 0.7, h: 1.0, fontSize: 15, color: CLARO,
});
s3.addNotes(
  "INTEGRANTE 1\n\n" +
  "Antes das funções, a ideia geral. Na lógica clássica, 20 veículos ou é fila alta ou não é. Na lógica fuzzy, uma entrada pode pertencer a vários conjuntos ao mesmo tempo, com graus entre 0 e 1. É isso que permite um controle suave, sem saltos.\n\n" +
  "O controlador funciona em três passos. Primeiro a fuzzificação: as entradas viram graus de pertinência. Depois a inferência: cada regra do tipo SE, E, ENTÃO dispara com uma força, e como a condição é um E, a força é o mínimo entre os dois graus. Por último a defuzzificação: as saídas de todas as regras são juntadas pelo máximo, e o centroide dessa área vira o número final, em segundos.\n\n" +
  "Usamos a mesma estrutura do exemplo do ventilador da aula, o modelo de Mamdani com centroide. A gente escreveu o motor do zero em Python, para entender cada passo, e conferiu com a biblioteca scikit-fuzzy: a diferença máxima na superfície inteira foi de 0,015 segundo."
);

/* ------------------------------------------------------ 4 pertinencia */
const s4 = pres.addSlide();
tituloSlide(s4, "Funções de pertinência");
imagem(s4, "pertinencia.png", L + 0.3, 1.25, 6.25, 9.5 / 10);
const just = [
  ["Pontas em trapézio", "Até 6 veículos a fila é baixa com certeza; a partir de 24, alta com certeza. O mesmo vale para a espera."],
  ["Meio em triângulo", "Média e Médio têm um único ponto típico (15 veículos, 60 s) e se sobrepõem aos vizinhos: a transição é gradual."],
  ["Saída assimétrica", "Reduzir vai até −10 s; Aumentar ocupa de 0 a +30 s. Por isso Aumentar tem uma área bem maior."],
];
just.forEach((j, i) => {
  const y = 1.4 + i * 1.75;
  faixa(s4, 8.0, y, 1.5, [AZUL, AMBAR, VERMELHO][i]);
  texto(s4, j[0], { x: 8.3, y: y, w: 4.3, h: 0.4, fontSize: 17, bold: true });
  texto(s4, j[1], { x: 8.3, y: y + 0.42, w: 4.3, h: 1.1, fontSize: 14.5, color: CINZA });
});
s4.addNotes(
  "INTEGRANTE 1\n\n" +
  "Aqui estão as funções de pertinência das três variáveis. O enunciado define os intervalos e os nomes dos termos; o formato de cada função foi escolha nossa.\n\n" +
  "Nas pontas usamos trapézios. Por exemplo, até 6 veículos a fila é baixa com certeza, grau 1, e a partir de 24 é alta com certeza. Na espera, até 25 segundos é curto e a partir de 95 é longo.\n\n" +
  "No meio usamos triângulos, porque média e médio têm um ponto típico, 15 veículos e 60 segundos, e se sobrepõem aos vizinhos. Essa sobreposição é o que faz a passagem de um termo para o outro ser gradual.\n\n" +
  "Na saída, Reduzir vai até menos 10, Manter fica em torno de zero e Aumentar ocupa de zero até mais 30. Como o enunciado permite aumentar bem mais do que reduzir, o conjunto Aumentar ficou com uma área muito maior. Guardem isso, porque explica dois comportamentos que vamos ver na superfície."
);

/* ------------------------------------------------------------ 5 regras */
const s5 = pres.addSlide();
tituloSlide(s5, "Base de regras: 9 regras");
imagem(s5, "regras.png", L, 1.3, 6.2, 5.6 / 7.2);
const leituras5 = [
  [VERMELHO, "Fila alta", "aumenta o verde, qualquer que seja a espera (regras 7, 8 e 9)."],
  [AMBAR, "Fila média", "mantém, a não ser que a espera já esteja longa: aí aumenta (regra 6)."],
  [AZUL, "Fila baixa", "reduz o verde e devolve tempo para a via principal; com espera longa, mantém (regra 3)."],
];
leituras5.forEach((l, i) => {
  const y = 1.45 + i * 1.45;
  faixa(s5, 7.3, y, 1.2, l[0]);
  texto(s5, l[1], { x: 7.6, y: y, w: 5, h: 0.4, fontSize: 17, bold: true });
  texto(s5, l[2], { x: 7.6, y: y + 0.42, w: 5, h: 0.85, fontSize: 14.5, color: CINZA });
});
cartao(s5, { x: 7.3, y: 5.9, w: 5.3, h: 0.95 });
texto(s5, "O enunciado pede no mínimo 6. Com 9, toda combinação de termos tem uma regra.", {
  x: 7.5, y: 5.98, w: 4.95, h: 0.8, fontSize: 14, color: TINTA, valign: "middle",
});
s5.addNotes(
  "INTEGRANTE 2\n\n" +
  "Agora a base de regras. O enunciado pede no mínimo 6; nós usamos 9, uma para cada combinação de fila e espera. Assim nenhuma situação fica sem resposta, e mais adiante vamos mostrar o que acontece quando faltam regras.\n\n" +
  "A tabela se lê assim: a linha é a fila, a coluna é a espera, e o quadrado diz o que fazer com o verde. Por exemplo, a regra 6: SE a fila é média E a espera é longa, ENTÃO aumentar.\n\n" +
  "A lógica é simples. Fila alta sempre aumenta o verde. Fila média mantém, a não ser que os carros já estejam esperando muito; aí aumenta. Fila baixa reduz o verde e devolve tempo para a via principal, mas se a espera já está longa a gente mantém, para não castigar quem está esperando."
);

/* --------------------------------------------------------- 6 inferencia */
const s6 = pres.addSlide();
tituloSlide(s6, "Um exemplo passo a passo");
s6.addImage({ path: path.join(SAIDA, "inferencia_exemplo.png"), x: L, y: 1.2, w: 5.65, h: 5.95 });
const gf = ex.graus_fila;
const ge = ex.graus_espera;
const passos6 = [
  ["Entradas", "fila de " + v(ex.fila, 0) + " veículos e espera de " + v(ex.espera, 0) + " s"],
  ["Fuzzificação", "fila: Média " + v(gf["Média"], 2) + " e Alta " + v(gf["Alta"], 2) + "; espera: Médio " + v(ge["Médio"], 2)],
  ["Regras ativas", ativas.map((a) => "R" + a.regra + " (" + a.se_fila + " e " + a.e_espera + " → " + a.entao + "): " + v(a.forca, 2)).join("\n")],
  ["Resultado", "o centroide da área dá " + sinal(ex.saida, 2) + " s"],
];
passos6.forEach((p, i) => {
  const y = 1.3 + i * 1.32;
  faixa(s6, 6.75, y, 1.12, [AZUL, AZUL, AMBAR, VERMELHO][i]);
  texto(s6, p[0], { x: 7.05, y: y, w: 5.6, h: 0.38, fontSize: 16, bold: true });
  texto(s6, p[1], { x: 7.05, y: y + 0.4, w: 5.6, h: 0.75, fontSize: 14, color: CINZA });
});
cartao(s6, { x: 6.75, y: 6.6, w: 5.85, h: 0.65, fundo: ESCURO });
texto(s6, "Manter disparou mais forte, mas a saída foi puxada para Aumentar: o centroide pesa pela área.", {
  x: 6.95, y: 6.6, w: 5.5, h: 0.65, fontSize: 13, color: CLARO, valign: "middle",
});
s6.addNotes(
  "INTEGRANTE 2\n\n" +
  "Vamos ver o controlador funcionando num caso só: fila de " + v(ex.fila, 0) + " veículos e espera de " + v(ex.espera, 0) + " segundos. A figura é no mesmo formato do visualizador de regras do MATLAB que vimos em aula: cada linha é uma regra.\n\n" +
  "Primeiro a fuzzificação. " + v(ex.fila, 0) + " veículos está entre média e alta: grau " + v(gf["Média"], 2) + " em média e " + v(gf["Alta"], 2) + " em alta. " + v(ex.espera, 0) + " segundos é médio com grau " + v(ge["Médio"], 2) + ".\n\n" +
  "Depois a inferência. Só duas regras disparam. " + ativas.map((a) => "A regra " + a.regra + ", fila " + a.se_fila.toLowerCase() + " e espera " + a.e_espera.toLowerCase() + ", manda " + a.entao.toLowerCase() + ", com força " + v(a.forca, 2) + ", que é o mínimo entre os dois graus").join(". ") + ".\n\n" +
  "Por último, cada conjunto de saída é cortado na altura da força da sua regra, as áreas são juntadas pelo máximo, e o centroide dá " + sinal(ex.saida, 2) + " segundos.\n\n" +
  "Tem um detalhe interessante aqui. A regra de Manter disparou mais forte, mas o resultado foi bem para o lado de Aumentar. Isso porque o centroide é uma média ponderada pela área, e o conjunto Aumentar é muito mais largo. Mesmo cortado mais baixo, ele tem mais área."
);

/* --------------------------------------------------------- 7 superficie */
const s7 = pres.addSlide();
tituloSlide(s7, "A superfície de controle");
imagem(s7, "superficie_3d.png", L, 1.2, 6.6, 8 / 11);
imagem(s7, "superficie_mapa.png", 7.45, 1.25, 5.15, 6.5 / 9);
const leituras7 = [
  [AZUL, "Platô azul", "fila baixa: reduz cerca de 6 s"],
  [AMBAR, "Platô central em 0 s", "fila média com espera curta ou média: mantém"],
  [VERMELHO, "Platô vermelho", "fila alta, ou média com espera longa: aumenta até ~18 s"],
];
leituras7.forEach((l, i) => {
  const y = 5.05 + i * 0.72;
  faixa(s7, 7.45, y, 0.6, l[0]);
  s7.addText([
    { text: l[1], options: { bold: true, color: TINTA, breakLine: true } },
    { text: l[2], options: { color: CINZA, fontSize: 12.5 } },
  ], { x: 7.7, y: y, w: 5.0, h: 0.6, isTextBox: true, margin: 0, fontFace: CORPO_FONTE, fontSize: 13.5,
    valign: "middle", lineSpacingMultiple: 1.0 });
});
s7.addNotes(
  "INTEGRANTE 2\n\n" +
  "Aqui está a superfície que o enunciado pede: a fila e a espera nos eixos x e y, e o ajuste do verde no eixo z. À direita, a mesma superfície vista de cima, como um mapa, com o ponto do exemplo anterior marcado.\n\n" +
  "Dá para ler três regiões. O platô azul é a fila baixa: o verde é reduzido em cerca de 6 segundos. No centro tem um platô em zero: fila média com espera curta ou média, o controlador mantém o verde. E o platô vermelho é a fila alta, ou a fila média com espera longa: o verde aumenta, até uns 18 segundos.\n\n" +
  "A superfície sobe quando a fila ou a espera aumentam, que é o que a gente quer de um semáforo. E as transições são suaves, por causa da sobreposição das funções. A exceção é uma subida mais brusca perto de 6 a 8 veículos com espera longa: com espera de " + v(deg.espera, 0) + " segundos, ir de " + v(deg.antes.fila, 0) + " para " + v(deg.depois.fila, 0) + " veículos leva o ajuste de " + sinal(deg.antes.saida, 1) + " para " + sinal(deg.depois.saida, 1) + " segundos, mesmo com a regra de aumentar disparando com força de só " + v(deg.forca_aumentar, 1) + ". É de novo o efeito da área grande do conjunto Aumentar."
);

/* ---------------------------------------------------------- 8 extremos */
const s8 = pres.addSlide();
tituloSlide(s8, "A saída nunca chega a +30 s nem a −10 s");
imagem(s8, "extremos.png", L, 1.25, LARG, 4.4 / 13);
cartao(s8, { x: L, y: 5.45, w: 5.8, h: 1.55, fundo: ESCURO });
texto(s8, "Faixa real da saída", { x: L + 0.3, y: 5.58, w: 5.3, h: 0.4, fontSize: 16, bold: true, color: AMBAR });
texto(s8, "de " + sinal(sMin, 1) + " s a " + sinal(sMax, 1) + " s, num universo de −10 a +30 s", {
  x: L + 0.3, y: 6.02, w: 5.3, h: 0.85, fontSize: 18, bold: true, color: BRANCO,
});
cartao(s8, { x: 6.8, y: 5.45, w: 5.8, h: 1.55 });
texto(s8, "O centroide é o \"centro de massa\" da área. Mesmo com Aumentar em 100%, o centro da área fica no meio dela, longe da borda de +30.", {
  x: 7.05, y: 5.58, w: 5.35, h: 1.35, fontSize: 14.5, color: CINZA, valign: "middle",
});
s8.addNotes(
  "INTEGRANTE 2\n\n" +
  "Um resultado que chama a atenção: o universo da saída vai de menos 10 a mais 30 segundos, mas a superfície inteira fica entre " + sinal(sMin, 1) + " e " + sinal(sMax, 1) + ".\n\n" +
  "À direita está o caso de maior saída: fila de " + v(tr.extremos[1].fila, 0) + " veículos e espera de " + v(tr.extremos[1].espera, 0) + ". Só a regra de aumentar dispara, e com força total. Mesmo assim a saída é " + sinal(sMax, 2) + ". O motivo é o centroide: ele é o centro de massa da área, e o centro de um trapézio que vai de 0 a 30 fica no meio dele, não na borda. Do lado esquerdo acontece o mesmo com o reduzir: o mínimo é " + sinal(sMin, 2) + ", e não menos 10.\n\n" +
  "É a mesma pergunta que o material faz no exercício da gorjeta, se o maior valor é igual a 20%. Com centroide, não é. Para chegar perto das bordas, seria preciso mudar o formato dos conjuntos de saída ou o método de defuzzificação, e isso aparece no próximo slide. E essa limitação vai ter efeito prático na simulação."
);

/* ---------------------------------------------------------- 9 variacoes */
const s9 = pres.addSlide();
tituloSlide(s9, "O que muda a superfície");
imagem(s9, "variacoes.png", L, 1.2, 7.4, 10.5 / 14);
const var9 = [
  [AZUL, "Outras funções de pertinência", "Triângulos uniformes: a superfície vira uma rampa, sem platôs."],
  [VERMELHO, "Só 6 regras", "Em " + v(tr.buracos_6_regras_pct, 1) + "% das combinações nenhuma regra dispara e a saída cai para 0: aparecem buracos."],
  [AMBAR, "Média dos máximos", "Alcança de " + sinal(mom.min, 0) + " a " + sinal(mom.max, 0) + " s e vira degraus, mas na simulação se saiu melhor que o centroide."],
];
var9.forEach((l, i) => {
  const y = 1.35 + i * 1.65;
  faixa(s9, 8.35, y, 1.4, l[0]);
  texto(s9, l[1], { x: 8.65, y: y, w: 4.0, h: 0.4, fontSize: 16, bold: true });
  texto(s9, l[2], { x: 8.65, y: y + 0.42, w: 4.0, h: 1.0, fontSize: 14, color: CINZA });
});
cartao(s9, { x: 8.35, y: 6.3, w: 4.25, h: 0.85, fundo: ESCURO });
texto(s9, "Como no slide 29 da aula, mais a defuzzificação.", { x: 8.55, y: 6.3, w: 3.9, h: 0.85, fontSize: 13.5, color: CLARO, valign: "middle" });
s9.addNotes(
  "INTEGRANTE 3\n\n" +
  "O material de aula mostra, para o ventilador, como a superfície muda com outras funções de pertinência e outras regras. Fizemos o mesmo com o nosso controlador.\n\n" +
  "Em cima à esquerda está o original. Em cima à direita, trocamos as funções de pertinência das entradas por triângulos igualmente espaçados: a superfície vira quase uma rampa contínua, sem os platôs. Nenhuma das duas está errada; o formato das funções é o que define o comportamento.\n\n" +
  "Embaixo à esquerda, ficamos só com 6 regras, o mínimo do enunciado. Em " + v(tr.buracos_6_regras_pct, 1) + "% das combinações de entrada nenhuma regra dispara, e a saída cai para zero. São esses buracos na superfície. Por isso usamos as 9.\n\n" +
  "E embaixo à direita trocamos o centroide pela média dos máximos. Ela chega mais perto das bordas, de " + sinal(mom.min, 0) + " a " + sinal(mom.max, 0) + " segundos, e a superfície vira degraus. Parece pior, mas na simulação que vem a seguir ela se saiu melhor que o centroide: no trânsito leve, a espera média cai de " + v(leve.defuzz.centroide, 1) + " para " + v(leve.defuzz.mom, 1) + " segundos, justamente porque a saída desce mais."
);

/* ------------------------------------------------------- 10 sim video */
const s10 = pres.addSlide();
tituloSlide(s10, "Extra: o controlador num cruzamento simulado");
const vv = sim.video;
s10.addMedia({
  type: "video",
  path: path.join(SAIDA, "simulacao_semaforo.mp4"),
  cover: "data:image/png;base64," + fs.readFileSync(path.join(IMG, "capa_simulacao_semaforo.png")).toString("base64"),
  x: L, y: 1.25, w: 8.4, h: 8.4 * 9 / 16,
});
texto(s10, "clique para reproduzir · " + vv.duracao_s + " s · minutos " + v(vv.janela_min[0], 0) + " a " + v(vv.janela_min[1], 0) + " do pico", {
  x: L, y: 6.05, w: 8.4, h: 0.3, fontSize: 12.5, italic: true, color: CINZA, align: "center",
});
cartao(s10, { x: 9.35, y: 1.25, w: 3.25, h: 5.1, fundo: ESCURO });
texto(s10, "O modelo", { x: 9.6, y: 1.4, w: 2.8, h: 0.4, fontSize: 17, bold: true, color: AMBAR });
texto(s10, [
  "2 horas de trânsito, 1 carro a cada 2 s no verde",
  "via principal: " + sim.chegada_principal_veic_h + " veíc/h, verde fixo de " + sim.verde_principal + " s",
  "secundária: pico no meio das 2 horas",
  "a cada ciclo o fuzzy lê fila e espera e define o verde = " + sim.verde_base + " s + GreenAdj",
].map((t) => "• " + t).join("\n\n"), {
  x: 9.6, y: 1.9, w: 2.85, h: 4.3, fontSize: 13.5, color: CLARO,
});
s10.addNotes(
  "INTEGRANTE 3\n\n" +
  "[DAR PLAY NO VÍDEO — ele está embutido no slide, é só clicar. Dura " + vv.duracao_s + " segundos.]\n\n" +
  "Isso aqui foi além do enunciado. A superfície mostra o que o controlador decide, mas não se essas decisões são boas. Então a gente simulou um cruzamento e colocou o controlador para trabalhar.\n\n" +
  "O modelo é simples: duas horas de trânsito, carros chegando aleatoriamente nas duas vias, e no verde sai um carro a cada 2 segundos. A via principal recebe " + sim.chegada_principal_veic_h + " veículos por hora e tem verde fixo de " + sim.verde_principal + " segundos. A secundária tem um horário de pico no meio das duas horas. A cada ciclo, o controlador fuzzy lê a fila e a espera da secundária e define o verde como " + sim.verde_base + " segundos mais o GreenAdj.\n\n" +
  "No vídeo, à esquerda é o semáforo de tempo fixo e à direita o fuzzy. Os dois recebem exatamente os mesmos carros, na mesma hora. Durante o pico, quando a fila da secundária cresce, o fuzzy estica o verde dela, e esse tempo sai da via principal: reparem que a fila da principal no fuzzy chega a " + vv.fila_pri_max.fuzzy + " carros, contra " + vv.fila_pri_max.fixo + " no fixo. Por isso, no gráfico da esquerda, o total de carros parados fica quase igual nos dois enquanto o pico está forte.\n\n" +
  "A diferença aparece quando o pico passa: o fuzzy esvazia a fila uns dez minutos antes, enquanto o tempo fixo continua com perto de 30 carros parados. O gráfico da direita soma a espera de todo mundo: as duas curvas andam juntas e depois se separam. No fim do vídeo, o fuzzy somou " + v(vv.acumulado_veic_h.fuzzy, 1) + " veículo-hora de espera, contra " + v(vv.acumulado_veic_h.fixo, 1) + " do fixo: " + v(100 * (1 - vv.acumulado_veic_h.fuzzy / vv.acumulado_veic_h.fixo), 0) + "% a menos."
);

/* --------------------------------------------------- 11 sim resultados */
const s11 = pres.addSlide();
tituloSlide(s11, "Extra: quando o fuzzy ganha, e quando não");
imagem(s11, "simulacao_cenarios.png", L, 1.2, 7.7, 5.6 / 12);
const res11 = [
  [VERDE, "Contra o tempo fixo de 30 s", "o fuzzy reduz a espera média em todos os cenários (" + sim.sementes + " simulações cada)."],
  [AMBAR, "Contra o melhor tempo fixo", "no trânsito leve o fixo ganha: o melhor verde seria " + leve.melhor_fixo.verde + " s, e o fuzzy não desce de ~" + v(sim.verde_base + sMin, 0) + " s (o limite do slide 8)."],
  [VERMELHO, "No pico forte", "a secundária cai de " + v(forte.fixo30.sec, 0) + " para " + v(forte.fuzzy.sec, 0) + " s, mas a principal sobe de " + v(forte.fixo30.pri, 0) + " para " + v(forte.fuzzy.pri, 0) + " s: o fuzzy só olha uma via."],
];
res11.forEach((l, i) => {
  const y = 1.35 + i * 1.6;
  faixa(s11, 8.65, y, 1.35, l[0]);
  texto(s11, l[1], { x: 8.95, y: y, w: 3.7, h: 0.4, fontSize: 15.5, bold: true });
  texto(s11, l[2], { x: 8.95, y: y + 0.42, w: 3.7, h: 0.95, fontSize: 13.5, color: CINZA });
});
cartao(s11, { x: L, y: 5.0, w: 7.7, h: 1.9 });
texto(s11, "O melhor tempo fixo muda de " + leve.melhor_fixo.verde + " s a " + forte.melhor_fixo.verde + " s conforme o pico, e na rua ninguém sabe o pico de antemão. "
  + "O fuzzy não precisa saber: ele se ajusta sozinho e, nos picos, ganha até do melhor fixo ("
  + v(medio.fuzzy.todos, 0) + " contra " + v(medio.melhor_fixo.todos, 0) + " s e " + v(forte.fuzzy.todos, 0) + " contra " + v(forte.melhor_fixo.todos, 0) + " s).", {
  x: L + 0.3, y: 5.12, w: 7.1, h: 1.65, fontSize: 14.5, color: TINTA, valign: "middle",
});
s11.addNotes(
  "INTEGRANTE 3\n\n" +
  "Para não depender de uma execução só, rodamos " + sim.sementes + " simulações para cada nível de pico na via secundária, e comparamos três semáforos: o tempo fixo de 30 segundos, o melhor tempo fixo possível para cada cenário, que achamos testando de 15 a 60 segundos, e o fuzzy. O gráfico mostra a espera média por veículo, contando as duas vias.\n\n" +
  "Primeiro: contra o tempo fixo de 30 segundos, o fuzzy ganha em todos os cenários. No trânsito leve, ele encurta o verde da secundária, o ciclo fica mais curto e a via principal abre mais vezes. No pico, ele estica o verde e esvazia a fila.\n\n" +
  "Mas a comparação justa é com o melhor tempo fixo, e aí a história é outra. No trânsito leve, o melhor fixo ganha: o ideal seria um verde de " + leve.melhor_fixo.verde + " segundos, e o nosso fuzzy não consegue descer de uns " + v(sim.verde_base + sMin, 0) + " segundos. É exatamente o limite do centroide que mostramos antes: a saída nunca passa de " + sinal(sMin, 1) + ".\n\n" +
  "Já nos picos o fuzzy ganha até do melhor fixo: " + v(medio.fuzzy.todos, 0) + " contra " + v(medio.melhor_fixo.todos, 0) + " segundos no pico médio, e " + v(forte.fuzzy.todos, 0) + " contra " + v(forte.melhor_fixo.todos, 0) + " no pico forte. E o melhor fixo muda de " + leve.melhor_fixo.verde + " a " + forte.melhor_fixo.verde + " segundos conforme o cenário; na prática ninguém sabe o pico de antemão, e o fuzzy se ajusta sozinho.\n\n" +
  "O último ponto é um custo. No pico forte, a espera na secundária cai de " + v(forte.fixo30.sec, 0) + " para " + v(forte.fuzzy.sec, 0) + " segundos, mas a via principal sobe de " + v(forte.fixo30.pri, 0) + " para " + v(forte.fuzzy.pri, 0) + ". O controlador só enxerga a via secundária. Um controlador completo teria que olhar as duas."
);

/* -------------------------------------------------------- 12 conclusoes */
const s12 = pres.addSlide();
s12.background = { color: ESCURO };
texto(s12, "Conclusões", { x: L, y: 0.45, w: LARG, h: 0.85, fontFace: TITULO_FONTE, fontSize: 32, bold: true, color: BRANCO, valign: "middle" });
const concl = [
  ["O controlador", "3 termos por variável, 9 regras e Mamdani com centroide: a superfície sobe com a fila e a espera, em platôs com transições suaves."],
  ["O centroide", "Limita a saída a " + sinal(sMin, 1) + " a " + sinal(sMax, 1) + " s e dá peso à área: Aumentar, largo, puxa a saída para cima."],
  ["Regras e funções", "Mudam a superfície por completo. Com só 6 regras aparecem buracos; por isso usamos 9."],
  ["Na prática", "O fuzzy se adapta sem conhecer o trânsito e ganha nos picos, mas perde no trânsito leve e só enxerga uma via."],
];
concl.forEach((c, i) => {
  const y = 1.6 + i * 1.15;
  texto(s12, c[0], { x: L, y: y, w: 2.8, h: 0.9, fontSize: 17, bold: true, color: AMBAR, valign: "middle" });
  texto(s12, c[1], { x: L + 2.9, y: y, w: 9.0, h: 0.9, fontSize: 16, color: BRANCO, valign: "middle" });
});
texto(s12, "Obrigado!", { x: L, y: 6.5, w: LARG, h: 0.5, fontSize: 18, bold: true, color: AMBAR });
s12.addNotes(
  "INTEGRANTE 3\n\n" +
  "Para fechar.\n\n" +
  "Construímos o controlador com três termos por variável, nove regras e o modelo de Mamdani com centroide. A superfície faz o que se espera de um semáforo: o verde cresce com a fila e com a espera, em platôs com transições suaves.\n\n" +
  "O centroide tem duas consequências que vale entender: a saída fica entre " + sinal(sMin, 1) + " e " + sinal(sMax, 1) + " segundos, e não entre menos 10 e mais 30, e conjuntos mais largos puxam o resultado para o lado deles.\n\n" +
  "As regras e as funções de pertinência mudam a superfície por completo. Com só as 6 regras mínimas, aparecem buracos.\n\n" +
  "E na simulação, o controlador fuzzy se adapta sem precisar conhecer o trânsito, e ganha nos picos até do melhor tempo fixo. Mas perde no trânsito leve, por causa do limite do centroide, e como só enxerga a via secundária, no pico forte ele piora a via principal.\n\n" +
  "Obrigado. Estamos à disposição para perguntas."
);

/* ------------------------------------------------- 13 reserva duas vias */
const s13 = pres.addSlide();
tituloSlide(s13, "Extra: o fuzzy controlando as duas vias");
const dv = dvias.cenarios;
const dvVal = dvias.validacao;
const ganho = dv.map((c) => 100 * (1 - c.misto_mom.todos / c.trabalho.todos));
cartao(s13, { x: 10.55, y: 0.55, w: 2.05, h: 0.45, fundo: AMBAR });
texto(s13, "RESERVA · PERGUNTAS", { x: 10.55, y: 0.55, w: 2.05, h: 0.45, fontSize: 11.5, bold: true, color: ESCURO, align: "center", valign: "middle", charSpacing: 1 });
imagem(s13, "duas_vias.png", L, 1.25, 7.9, 5.8 / 12);
const passos13 = [
  [AZUL, "1. O fuzzy nas duas vias", "O verde da principal também passa a ser decidido, a partir de " + sim.verde_principal + " s."],
  [AZUL, "2. Duas opiniões, meio a meio", "A do nosso controlador (fila e espera da via) e a de um comparador: esta via está pior que a outra?"],
  [VERDE, "3. Média dos máximos", "No lugar do centroide: a saída desce mais, e o verde encurta quando o trânsito está leve."],
];
passos13.forEach((l, i) => {
  const y = 1.3 + i * 1.32;
  faixa(s13, 8.9, y, 1.12, l[0]);
  texto(s13, l[1], { x: 9.15, y: y, w: 3.5, h: 0.38, fontSize: 15, bold: true });
  texto(s13, l[2], { x: 9.15, y: y + 0.4, w: 3.5, h: 0.75, fontSize: 12.5, color: CINZA });
});
cartao(s13, { x: L, y: 5.25, w: LARG, h: 1.7, fundo: ESCURO });
texto(s13, [
  { text: "Entre as versões fuzzy, a menor espera nos quatro cenários: ", options: { bold: true, color: BRANCO } },
  { text: "de " + v(Math.min(...ganho), 0) + "% a " + v(Math.max(...ganho), 0) + "% menos espera que o fuzzy do trabalho, e o resultado se repetiu em outras " + dvias.sementes_validacao + " simulações.", options: { color: CLARO } },
  { text: "\nAinda perde do melhor tempo fixo no trânsito leve (" + v(dv[0].misto_mom.todos, 1) + " contra " + v(dvias.melhor_fixo[0].todos, 1) + " s), e no pico forte ninguém escapa: o cruzamento está no limite, e o verde que uma via ganha a outra perde.", options: { color: CLARO } },
], { x: L + 0.3, y: 5.35, w: LARG - 0.6, h: 1.5, fontSize: 14.5, valign: "middle", paraSpaceAfter: 6 });
s13.addNotes(
  "SLIDE DE RESERVA — só abrir se perguntarem sobre a via principal, sobre controlar as duas vias ou sobre a média dos máximos.\n\n" +
  "No slide 11 a gente admitiu que o controlador só enxerga a via secundária, e que no pico forte isso piora a principal. Então testamos versões que controlam as duas vias.\n\n" +
  "A melhor foi o que chamamos de misto. O verde de cada via é decidido somando duas opiniões, meio a meio. A primeira é a do nosso controlador, que olha a fila e a espera daquela via. A segunda é de um comparador, um outro controlador fuzzy com 9 regras que olha a fila daquela via e a fila da outra, e responde se esta via está pior ou melhor. E trocamos o centroide pela média dos máximos, que deixa a saída descer mais e encurta o verde quando o trânsito está leve.\n\n" +
  "No gráfico, a barra verde é essa versão. Entre as versões fuzzy, ela teve a menor espera nos quatro cenários: de " + v(Math.min(...ganho), 0) + "% a " + v(Math.max(...ganho), 0) + "% menos que o fuzzy do trabalho, a barra azul clara. No pico forte, a via principal volta de " + v(dv[3].trabalho.pri, 0) + " para " + v(dv[3].misto_mom.pri, 0) + " segundos de espera. Como o peso meio a meio foi escolhido olhando essas simulações, rodamos outras " + dvias.sementes_validacao + " com carros diferentes, e o resultado se repetiu.\n\n" +
  "Mas não resolve tudo. No trânsito leve, o melhor tempo fixo ainda ganha, " + v(dvias.melhor_fixo[0].todos, 1) + " contra " + v(dv[0].misto_mom.todos, 1) + " segundos. E no pico forte o cruzamento está no limite: o verde que uma via ganha, a outra perde, então a secundária espera mais do que no trabalho. Um controlador completo usaria fila e espera das duas vias ao mesmo tempo."
);

pres.writeFile({ fileName: path.join(__dirname, "apresentacao.pptx") }).then((f) => {
  console.log("gerado:", f);
});
