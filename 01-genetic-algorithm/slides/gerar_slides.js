const path = require("path");
const pptxgen = require("pptxgenjs");

const RAIZ = path.dirname(__dirname);
const IMG = path.join(__dirname, "img");
const SAIDA = path.join(RAIZ, "saida");

const ESCURO = "2D1B4E";
const ESCURO2 = "1B1035";
const TEAL = "21918C";
const TEAL_CLARO = "4FC3B8";
const AMARELO = "FDE725";
const OURO = "8A6D00";
const TINTA = "231C33";
const CINZA = "5F5A6B";
const CARTAO = "F2F0F7";
const BRANCO = "FFFFFF";

const TITULO_FONTE = "Cambria";
const CORPO_FONTE = "Calibri";

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Trabalho prático - Algoritmo Genético";
pres.title = "Algoritmo Genético para a Schaffer's f6";

const L = 0.7;
const LARG = 11.9;

function tituloSlide(slide, texto, cor) {
  slide.addText(texto, {
    x: L, y: 0.42, w: LARG, h: 0.85,
    isTextBox: true, margin: 0,
    fontFace: TITULO_FONTE, fontSize: 32, bold: true,
    color: cor || TINTA, align: "left", valign: "middle",
  });
}

function rodape(slide, integrante, corTexto) {
  slide.addText(integrante, {
    x: L, y: 6.92, w: 4.0, h: 0.32,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 10.5, color: corTexto || CINZA, align: "left", valign: "middle",
  });
}

function cartao(slide, opcoes) {
  slide.addShape(pres.ShapeType.roundRect, {
    x: opcoes.x, y: opcoes.y, w: opcoes.w, h: opcoes.h,
    rectRadius: 0.09,
    fill: { color: opcoes.fundo || CARTAO },
    line: { color: opcoes.borda || (opcoes.fundo || CARTAO), width: opcoes.borda ? 1.75 : 0.75 },
  });
}

function circuloNumero(slide, x, y, texto, corFundo, corTexto) {
  slide.addShape(pres.ShapeType.ellipse, {
    x: x, y: y, w: 0.42, h: 0.42,
    fill: { color: corFundo }, line: { color: corFundo, width: 0.75 },
  });
  slide.addText(texto, {
    x: x, y: y, w: 0.42, h: 0.42,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 13, bold: true,
    color: corTexto, align: "center", valign: "middle",
  });
}

/* ------------------------------------------------------------------ 1 */
const s1 = pres.addSlide();
s1.background = { color: ESCURO };

s1.addImage({
  path: path.join(IMG, "f6_contorno_limpo.png"),
  x: 8.45, y: 1.65, w: 4.35, h: 4.35,
  transparency: 20,
});

s1.addText("TRABALHO PRÁTICO · OTIMIZAÇÃO DE FUNÇÃO", {
  x: L, y: 1.55, w: 7.4, h: 0.34,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 12.5, bold: true, charSpacing: 2,
  color: TEAL_CLARO, valign: "middle",
});
s1.addText("Algoritmo Genético\npara a Schaffer's f6", {
  x: L, y: 2.05, w: 7.4, h: 1.85,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.05,
  fontFace: TITULO_FONTE, fontSize: 40, bold: true, color: BRANCO, valign: "top",
});
s1.addText("Maximização com 50 indivíduos e 300 gerações, seleção por roleta e fitness sharing", {
  x: L, y: 4.05, w: 7.3, h: 0.75,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 16, color: "C9C2DC", valign: "top",
});

const nomes = ["Integrante 1", "Integrante 2", "Integrante 3"];
nomes.forEach((nome, i) => {
  s1.addText(nome, {
    x: L + i * 2.5, y: 5.55, w: 2.35, h: 0.4,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 14, bold: true, color: AMARELO, valign: "middle",
  });
});
s1.addText("Convergência para o máximo global em 59 de 100 execuções", {
  x: L, y: 6.15, w: 7.4, h: 0.35,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 12.5, color: "9A93B0", valign: "middle",
});

s1.addNotes(
  "INTEGRANTE 1 (abertura)\n\n" +
  "Bom dia. Nosso trabalho é o problema 3: implementar um algoritmo genético para maximizar a função Schaffer's f6.\n\n" +
  "Vou apresentar o problema, mostrar por que ele é bem mais difícil do que parece e explicar o algoritmo que implementamos. " +
  "Em seguida o Integrante 2 explica a decisão de projeto mais importante do trabalho, que foi como manter diversidade na população. " +
  "E o Integrante 3 fecha com os resultados das partes 1 e 2.\n\n" +
  "Adiantando o resultado: o algoritmo converge para o máximo global em 59 das 100 execuções, acima dos 50% exigidos no enunciado."
);

/* ------------------------------------------------------------------ 2 */
const s2 = pres.addSlide();
tituloSlide(s2, "O problema");

cartao(s2, { x: L, y: 1.45, w: 7.2, h: 1.15, fundo: ESCURO });
s2.addText("f(x, y) = 0.5 − ( sin²(√(x² + y²)) − 0.5 ) / ( 1 + 0.001·(x² + y²) )²", {
  x: L + 0.25, y: 1.45, w: 6.7, h: 1.15,
  isTextBox: true, margin: 0,
  fontFace: "Courier New", fontSize: 14, color: BRANCO, valign: "middle",
});

const itensProblema = [
  ["Espaço de busca", "−10 ≤ x ≤ 10  e  −10 ≤ y ≤ 10"],
  ["Máximo global", "f(0, 0) = 1.0"],
  ["Critério de convergência", "−0.09 ≤ x ≤ 0.09  e  −0.09 ≤ y ≤ 0.09"],
  ["Orçamento", "no máximo 50 indivíduos e 300 gerações"],
  ["Exigência", "convergir em pelo menos 50% das 100 execuções"],
];
itensProblema.forEach((item, i) => {
  const y = 2.95 + i * 0.72;
  circuloNumero(s2, L, y, String(i + 1), TEAL, BRANCO);
  s2.addText(item[0], {
    x: L + 0.62, y: y - 0.12, w: 2.35, h: 0.46,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 13, bold: true, color: TINTA, valign: "middle",
  });
  s2.addText(item[1], {
    x: L + 3.05, y: y - 0.12, w: 4.35, h: 0.46,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 13, color: CINZA, valign: "middle",
  });
});

s2.addImage({ path: path.join(IMG, "f6_contorno.png"), x: 8.35, y: 1.45, w: 4.25, h: 4.25 });
s2.addText("O ótimo está no centro; os anéis claros são máximos locais.", {
  x: 8.35, y: 5.78, w: 4.25, h: 0.55,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 11, italic: true, color: CINZA, valign: "top",
});

rodape(s2, "Integrante 1");
s2.addNotes(
  "INTEGRANTE 1\n\n" +
  "A f6 é uma função de duas variáveis, x e y, e ela só depende da distância até a origem. Por isso o gráfico à direita é todo formado por anéis concêntricos.\n\n" +
  "O enunciado pede maximização. O máximo global está exatamente na origem e vale 1.0.\n\n" +
  "O enunciado também fixa três restrições: o espaço de busca vai de menos 10 a 10 nos dois eixos, a população tem no máximo 50 indivíduos e o número de gerações é no máximo 300. " +
  "Isso dá um orçamento total de 15 mil avaliações da função.\n\n" +
  "E o critério de sucesso é bem apertado: a execução só conta como convergida se o melhor indivíduo terminar dentro da caixa de mais ou menos 0.09 em x e em y. " +
  "O enunciado exige que isso aconteça em pelo menos metade das 100 execuções."
);

/* ------------------------------------------------------------------ 3 */
const s3 = pres.addSlide();
tituloSlide(s3, "Por que a f6 é enganosa");

const numeros = [
  ["0.99027", "valor do anel r = π", TEAL],
  ["r < 0.0985", "para superar esse anel", OURO],
  ["0.29", "fitness em r = 1.0", "B03030"],
];
numeros.forEach((n, i) => {
  const x = L + i * 4.0;
  cartao(s3, { x: x, y: 1.42, w: 3.75, h: 1.12 });
  s3.addText(n[0], {
    x: x + 0.22, y: 1.5, w: 3.3, h: 0.55,
    isTextBox: true, margin: 0,
    fontFace: TITULO_FONTE, fontSize: 26, bold: true, color: n[2], valign: "middle",
  });
  s3.addText(n[1], {
    x: x + 0.22, y: 2.02, w: 3.3, h: 0.42,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 12, color: CINZA, valign: "middle",
  });
});

s3.addImage({ path: path.join(IMG, "f6_corte_radial.png"), x: 2.05, y: 2.72, w: 9.2, h: 4.03 });

rodape(s3, "Integrante 1");
s3.addNotes(
  "INTEGRANTE 1\n\n" +
  "Este corte mostra o fitness em função da distância até a origem. É aqui que está a dificuldade do problema.\n\n" +
  "O pico da esquerda, em r igual a zero, é o máximo global e vale 1.0. Mas ele é muito estreito. " +
  "Logo ao lado existe um vale profundo: em r igual a 1, ou seja, ainda bem perto do centro, o fitness já caiu para 0.29.\n\n" +
  "E o primeiro anel de máximos locais, em r igual a pi, vale 0.99027, quase o mesmo valor do ótimo global.\n\n" +
  "Juntando as duas coisas: um indivíduo só passa a valer mais do que o anel quando chega a r menor que 0.0985 — que é praticamente já estar dentro da caixa de tolerância. " +
  "Ou seja, qualquer indivíduo que caia perto do centro, mas não em cima dele, tem fitness muito menor que o resto da população e é eliminado pela seleção antes de conseguir descer até a origem.\n\n" +
  "É por isso que um AG comum fica preso no anel."
);

/* ------------------------------------------------------------------ 4 */
const s4 = pres.addSlide();
tituloSlide(s4, "O algoritmo implementado");

const blocos = [
  ["Codificação", "Binária em código de Gray,\n16 bits por variável\n(resolução 3.05 × 10⁻⁴)"],
  ["Seleção", "Roleta proporcional ao fitness,\nescolha do grupo"],
  ["Diversidade", "Fitness sharing com raio\nde nicho σ = 1.0"],
  ["Cruzamento", "Dois pontos, taxa 0.9"],
  ["Mutação", "Inversão de bit, taxa 0.09"],
  ["Elitismo", "2 indivíduos preservados\npor geração"],
];
blocos.forEach((b, i) => {
  const col = i % 3;
  const lin = Math.floor(i / 3);
  const x = L + col * 4.0;
  const y = 1.75 + lin * 2.05;
  cartao(s4, { x: x, y: y, w: 3.75, h: 1.75 });
  circuloNumero(s4, x + 0.25, y + 0.25, String(i + 1), lin === 0 ? TEAL : ESCURO, BRANCO);
  s4.addText(b[0], {
    x: x + 0.8, y: y + 0.25, w: 2.7, h: 0.42,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 15, bold: true, color: TINTA, valign: "middle",
  });
  s4.addText(b[1], {
    x: x + 0.25, y: y + 0.82, w: 3.25, h: 1.2,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
    fontFace: CORPO_FONTE, fontSize: 12.5, color: CINZA, valign: "top",
  });
});

s4.addText("População de 50 indivíduos × 300 gerações = 15.000 avaliações da função objetivo.", {
  x: L, y: 6.05, w: LARG, h: 0.35,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 12, italic: true, color: CINZA, valign: "middle",
});

rodape(s4, "Integrante 1");
s4.addNotes(
  "INTEGRANTE 1\n\n" +
  "Este é o algoritmo que entregamos.\n\n" +
  "Cada indivíduo é uma cadeia de 32 bits: 16 bits para x e 16 para y, em código de Gray. " +
  "Usamos Gray porque em binário comum valores vizinhos podem diferir em muitos bits ao mesmo tempo, o que atrapalha a busca fina perto do ótimo. " +
  "Com 16 bits a resolução é de cerca de 3 décimos de milésimo, muito mais fina que a tolerância de 0.09 que precisamos atingir.\n\n" +
  "A seleção é por roleta, proporcional ao fitness. O enunciado não define os operadores do AG, então isso foi escolha nossa: a roleta é o método que vimos em aula, e definimos como objetivo bater a meta de 50% usando ela.\n\n" +
  "O cruzamento é de dois pontos com taxa 0.9, a mutação é por inversão de bit com taxa 0.09 e guardamos os 2 melhores indivíduos de cada geração por elitismo.\n\n" +
  "O item 3, fitness sharing, é a peça que faz o algoritmo funcionar, e é sobre ela que o Integrante 2 vai falar agora."
);

/* ------------------------------------------------------------------ 5 */
const s5 = pres.addSlide();
tituloSlide(s5, "Os quatro esquemas que testamos");

const esquemas = [
  ["Torneio (k = 3) + elitismo", "28%", "Pressão seletiva alta: a população colapsa no anel r = π em poucas gerações.", false],
  ["Roleta + elitismo", "48%", "Pressão baixa e mais diversidade, mas ainda converge para o anel.", false],
  ["Roleta + fitness sharing", "59%", "Escolhido. Mantém a seleção por roleta e faz os nichos coexistirem.", true],
  ["Deterministic crowding", "80%", "Melhor resultado, mas troca a seleção por roleta por outro mecanismo.", false],
];
esquemas.forEach((e, i) => {
  const col = i % 2;
  const lin = Math.floor(i / 2);
  const x = L + col * 6.05;
  const y = 1.55 + lin * 2.05;
  cartao(s5, {
    x: x, y: y, w: 5.8, h: 1.75,
    fundo: e[3] ? ESCURO : CARTAO,
    borda: e[3] ? AMARELO : null,
  });
  s5.addText(e[0], {
    x: x + 0.3, y: y + 0.22, w: 3.5, h: 0.45,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 15, bold: true,
    color: e[3] ? BRANCO : TINTA, valign: "middle",
  });
  s5.addText(e[1], {
    x: x + 3.85, y: y + 0.18, w: 1.7, h: 0.55,
    isTextBox: true, margin: 0,
    fontFace: TITULO_FONTE, fontSize: 26, bold: true,
    color: e[3] ? AMARELO : TEAL, align: "right", valign: "middle",
  });
  s5.addText(e[2], {
    x: x + 0.3, y: y + 0.82, w: 5.2, h: 1.0,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
    fontFace: CORPO_FONTE, fontSize: 12.5,
    color: e[3] ? "C9C2DC" : CINZA, valign: "top",
  });
});

s5.addText("Mesmos parâmetros nos quatro: 16 bits em Gray, 50 × 300, cruzamento de dois pontos 0.9, mutação 0.09, elitismo 2 — 100 execuções cada.", {
  x: L, y: 5.9, w: LARG, h: 0.4,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 11.5, italic: true, color: CINZA, valign: "middle",
});

rodape(s5, "Integrante 2");
s5.addNotes(
  "INTEGRANTE 2\n\n" +
  "Antes de escolher, nós medimos. Testamos quatro esquemas diferentes, todos com exatamente os mesmos parâmetros — mesma codificação, mesmo cruzamento, mesma mutação, mesmo elitismo. " +
  "A única coisa que muda entre eles é como a seleção e a diversidade são tratadas. Cada número aqui é o resultado de 100 execuções independentes.\n\n" +
  "O torneio com k igual a 3 converge em só 28% das vezes. A roleta pura sobe para 48%, ainda abaixo do exigido. " +
  "A roleta com fitness sharing chega a 59% e é a versão que entregamos. " +
  "E o deterministic crowding chega a 80%, mas ele substitui a seleção por roleta, então ficou só como comparação.\n\n" +
  "Nos próximos slides eu explico por que cada um se comporta assim."
);

/* ------------------------------------------------------------------ 6 */
const s6 = pres.addSlide();
tituloSlide(s6, "Pressão seletiva: torneio × roleta");

const colunas = [
  ["Torneio (k = 3)", "28%", ESCURO, BRANCO, AMARELO,
    "Sorteia 3 indivíduos e o melhor deles vira pai.\n\nComo o anel r = π vale 0.99 e quase todo o resto vale menos, os indivíduos do anel ganham praticamente todos os torneios.\n\nEm poucas gerações a população inteira está no anel e a região central deixa de ser amostrada."],
  ["Roleta", "48%", CARTAO, TINTA, TEAL,
    "A chance de ser pai é proporcional ao fitness.\n\nComo quase toda a população fica entre 0.5 e 0.99, as fatias da roleta são parecidas e a pressão é fraca — a diversidade dura bem mais.\n\nMesmo assim, com 300 gerações a população acaba convergindo para o anel."],
];
colunas.forEach((c, i) => {
  const x = L + i * 6.05;
  cartao(s6, { x: x, y: 1.45, w: 5.8, h: 3.75, fundo: c[2] });
  s6.addText(c[0], {
    x: x + 0.35, y: 1.7, w: 3.4, h: 0.5,
    isTextBox: true, margin: 0,
    fontFace: TITULO_FONTE, fontSize: 20, bold: true, color: c[3], valign: "middle",
  });
  s6.addText(c[1], {
    x: x + 3.8, y: 1.68, w: 1.65, h: 0.55,
    isTextBox: true, margin: 0,
    fontFace: TITULO_FONTE, fontSize: 26, bold: true, color: c[4], align: "right", valign: "middle",
  });
  s6.addText(c[5], {
    x: x + 0.35, y: 2.4, w: 5.1, h: 2.65,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.2,
    fontFace: CORPO_FONTE, fontSize: 13,
    color: i === 0 ? "C9C2DC" : CINZA, valign: "top",
  });
});

s6.addText("Nos dois casos o problema é o mesmo: a população perde diversidade e para de amostrar a bacia central.", {
  x: L, y: 5.6, w: LARG, h: 0.4,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 12.5, italic: true, color: CINZA, valign: "middle",
});

rodape(s6, "Integrante 2");
s6.addNotes(
  "INTEGRANTE 2\n\n" +
  "Vamos comparar os dois esquemas de seleção clássicos.\n\n" +
  "No torneio, a gente sorteia três indivíduos e o melhor deles vira pai. Como quem está no anel vale 0.99 e quase todo o resto vale bem menos, os indivíduos do anel ganham quase todos os torneios. " +
  "Em poucas gerações a população inteira está no anel, e a partir daí ninguém mais amostra a região central. Resultado: 28%.\n\n" +
  "Na roleta, a chance de ser escolhido é proporcional ao fitness. Aqui a pressão é bem mais fraca, porque quase toda a população fica entre 0.5 e 0.99 — as fatias da roleta são parecidas. " +
  "Isso preserva mais diversidade e sobe o resultado para 48%. Mas com 300 gerações a população acaba convergindo do mesmo jeito.\n\n" +
  "Repare que o problema nunca foi falta de pressão seletiva. É falta de diversidade. Por isso a solução não é mexer na seleção, é mexer em como o fitness é calculado."
);

/* ------------------------------------------------------------------ 7 */
const s7 = pres.addSlide();
tituloSlide(s7, "Fitness sharing: a peça que resolve");

cartao(s7, { x: L, y: 1.42, w: LARG, h: 1.15, fundo: ESCURO });
const formula = [
  ["f′(i) = f(i) / Σⱼ sh(dᵢⱼ)", L + 0.4, 4.4],
  ["sh(d) = máx(0, 1 − d/σ)", L + 4.9, 4.4],
  ["σ = 1.0", L + 9.4, 2.1],
];
formula.forEach((f) => {
  s7.addText(f[0], {
    x: f[1], y: 1.42, w: f[2], h: 1.15,
    isTextBox: true, margin: 0,
    fontFace: "Courier New", fontSize: 15, color: BRANCO, align: "center", valign: "middle",
  });
});

const passos = [
  ["dᵢⱼ é a distância", "Distância euclidiana entre os indivíduos i e j no espaço (x, y) já decodificado."],
  ["Quem está sozinho não divide", "Um indivíduo isolado só tem a si mesmo como vizinho, então o fitness dele fica intacto."],
  ["Quem está no meio da multidão perde", "Os 40 indivíduos amontoados no anel dividem o fitness entre si e cada um fica com uma fração."],
  ["O resultado", "Um indivíduo sozinho na bacia central sobrevive mesmo com fitness bruto 0.29 — e a linhagem dele consegue descer até a origem. De 48% para 59%."],
];
passos.forEach((p, i) => {
  const y = 2.92 + i * 1.0;
  circuloNumero(s7, L, y, String(i + 1), i === 3 ? OURO : TEAL, BRANCO);
  s7.addText(p[0], {
    x: L + 0.62, y: y - 0.05, w: 3.5, h: 0.5,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 13.5, bold: true, color: TINTA, valign: "middle",
  });
  s7.addText(p[1], {
    x: L + 4.25, y: y - 0.1, w: 7.3, h: 0.62,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.1,
    fontFace: CORPO_FONTE, fontSize: 12.5, color: CINZA, valign: "middle",
  });
});

rodape(s7, "Integrante 2");
s7.addNotes(
  "INTEGRANTE 2\n\n" +
  "O fitness sharing não mexe na seleção — a seleção continua sendo roleta. Ele mexe no valor de fitness que entra na roleta.\n\n" +
  "A ideia é: antes de girar a roleta, o fitness de cada indivíduo é dividido pelo número de vizinhos que ele tem. " +
  "Vizinho aqui é medido pela distância euclidiana em x e y, e o raio de nicho que usamos é 1.0.\n\n" +
  "Quem está sozinho não divide com ninguém e mantém o fitness inteiro. Quem está amontoado no anel divide com todos os outros e sobra pouco para cada um.\n\n" +
  "Na prática isso muda tudo. Um indivíduo que cai sozinho na bacia central tem fitness bruto de 0.29, muito menor que os 0.99 do anel. " +
  "Mas se tem 40 indivíduos no anel, cada um deles fica com 0.99 dividido por 40, que dá 0.025 — e o indivíduo isolado, com 0.29 inteiros, passa a ser o mais atraente da roleta.\n\n" +
  "É isso que dá tempo para a linhagem dele descer até a origem. E é o que leva o algoritmo de 48% para 59%, acima do exigido."
);

/* ------------------------------------------------------------------ 8 */
const s8 = pres.addSlide();
tituloSlide(s8, "O que ficou de fora: deterministic crowding");

cartao(s8, { x: L, y: 1.45, w: 7.0, h: 4.6 });
s8.addText("Como funciona", {
  x: L + 0.35, y: 1.72, w: 6.3, h: 0.45,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 16, bold: true, color: TINTA, valign: "middle",
});
const crowd = [
  "A população é pareada aleatoriamente a cada geração.",
  "Cada par gera dois filhos por cruzamento e mutação.",
  "Cada filho é comparado com o pai mais parecido, medindo a distância de Hamming entre os cromossomos.",
  "O filho só substitui esse pai se tiver fitness maior — o elitismo passa a ser implícito.",
];
crowd.forEach((t, i) => {
  const y = 2.4 + i * 0.85;
  circuloNumero(s8, L + 0.35, y, String(i + 1), ESCURO, BRANCO);
  s8.addText(t, {
    x: L + 0.97, y: y - 0.12, w: 5.65, h: 0.66,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.1,
    fontFace: CORPO_FONTE, fontSize: 12.5, color: CINZA, valign: "middle",
  });
});

cartao(s8, { x: 8.05, y: 1.45, w: 4.55, h: 4.6, fundo: ESCURO });
s8.addText("80%", {
  x: 8.4, y: 1.85, w: 3.85, h: 1.0,
  isTextBox: true, margin: 0,
  fontFace: TITULO_FONTE, fontSize: 54, bold: true, color: AMARELO, valign: "middle",
});
s8.addText("de convergência — o melhor resultado que medimos", {
  x: 8.4, y: 2.9, w: 3.85, h: 0.7,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 13, color: "C9C2DC", valign: "top",
});
s8.addText("Por que não usamos", {
  x: 8.4, y: 3.85, w: 3.85, h: 0.4,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 14, bold: true, color: BRANCO, valign: "middle",
});
s8.addText("O crowding elimina a etapa de seleção proporcional: não existe roleta nele. Testamos para medir o teto do problema, mas a entrega é a versão com roleta.", {
  x: 8.4, y: 4.3, w: 3.85, h: 1.5,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 12.5, color: "C9C2DC", valign: "top",
});

rodape(s8, "Integrante 2");
s8.addNotes(
  "INTEGRANTE 2\n\n" +
  "Vale registrar o esquema que deu o melhor resultado, mesmo não sendo o que entregamos.\n\n" +
  "No deterministic crowding não existe roleta. A população é pareada aleatoriamente, cada par gera dois filhos, e cada filho compete diretamente com o pai mais parecido com ele — a semelhança é medida pela distância de Hamming entre os cromossomos. " +
  "O filho só entra na população se for melhor que aquele pai específico.\n\n" +
  "Como a competição é sempre local, entre indivíduos parecidos, os nichos se preservam sozinhos, sem precisar de nenhum raio ajustado à mão. " +
  "Isso levou a convergência para 80%.\n\n" +
  "Mas ele não usa roleta em momento nenhum. Como a gente tinha definido como objetivo chegar aos 50% com a roleta, ele ficou como referência, para sabermos quanto ainda dava para ganhar nesse problema."
);

/* ------------------------------------------------------------------ 9 */
const s9 = pres.addSlide();
tituloSlide(s9, "A decisão");

const barras = [
  ["Torneio (k = 3) + elitismo", 28, "9A93B0"],
  ["Roleta + elitismo", 48, "7E7691"],
  ["Roleta + fitness sharing", 59, TEAL],
  ["Deterministic crowding", 80, "C9C2DC"],
];
const xBarra = 4.55;
const largMax = 6.6;
barras.forEach((b, i) => {
  const y = 1.75 + i * 0.92;
  s9.addText(b[0], {
    x: L, y: y, w: 3.65, h: 0.5,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 13, bold: i === 2,
    color: i === 2 ? TINTA : CINZA, align: "right", valign: "middle",
  });
  s9.addShape(pres.ShapeType.roundRect, {
    x: xBarra, y: y + 0.07, w: (b[1] / 100) * largMax, h: 0.36,
    rectRadius: 0.05,
    fill: { color: b[2] }, line: { color: b[2], width: 0.5 },
  });
  s9.addText(b[1] + "%", {
    x: xBarra + (b[1] / 100) * largMax + 0.12, y: y, w: 1.0, h: 0.5,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 13, bold: i === 2,
    color: i === 2 ? TEAL : CINZA, valign: "middle",
  });
});

s9.addShape(pres.ShapeType.line, {
  x: xBarra + 0.5 * largMax, y: 1.6, w: 0, h: 3.9,
  line: { color: "B03030", width: 1.5, dashType: "dash" },
});
s9.addText("mínimo exigido: 50%", {
  x: xBarra + 0.5 * largMax - 1.05, y: 5.5, w: 2.2, h: 0.35,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 11, color: "B03030", align: "center", valign: "middle",
});

cartao(s9, { x: L, y: 5.8, w: LARG, h: 0.9, fundo: ESCURO });
s9.addText("Escolhemos roleta + fitness sharing: cumpre o objetivo de bater os 50% usando seleção por roleta, chegando a 59%.", {
  x: L + 0.35, y: 5.8, w: LARG - 0.7, h: 0.9,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 14, color: BRANCO, valign: "middle",
});

rodape(s9, "Integrante 2", "9A93B0");
s9.addNotes(
  "INTEGRANTE 2\n\n" +
  "Resumindo a comparação, com a linha tracejada marcando os 50% que o enunciado exige.\n\n" +
  "Torneio e roleta pura ficam abaixo da linha. Roleta com fitness sharing passa, com 59%. O crowding chega a 80%, mas com outra seleção.\n\n" +
  "A nossa escolha foi a roleta com fitness sharing. O enunciado não obriga nenhuma seleção específica, mas a roleta é o que vimos em aula e quisemos chegar na meta com ela. É a configuração que faz isso, com folga.\n\n" +
  "Passo para o Integrante 3, que vai mostrar os resultados."
);

/* ------------------------------------------------------------------ 10 */
const s10 = pres.addSlide();
tituloSlide(s10, "Parte 1 — o melhor indivíduo");

const resultados = [
  ["x", "0.002289"],
  ["y", "−0.000153"],
  ["fitness", "0.99999473"],
];
resultados.forEach((r, i) => {
  const y = 1.5 + i * 1.15;
  cartao(s10, { x: L, y: y, w: 3.9, h: 0.98, fundo: i === 2 ? ESCURO : CARTAO });
  s10.addText(r[0], {
    x: L + 0.28, y: y, w: 0.9, h: 0.98,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 14, bold: true,
    color: i === 2 ? "C9C2DC" : CINZA, valign: "middle",
  });
  s10.addText(r[1], {
    x: L + 1.3, y: y, w: 2.35, h: 0.98,
    isTextBox: true, margin: 0,
    fontFace: TITULO_FONTE, fontSize: 20, bold: true,
    color: i === 2 ? AMARELO : TINTA, align: "right", valign: "middle",
  });
});

s10.addText("Dentro da caixa de tolerância de ±0.09 em x e em y: a execução converge para o máximo global.", {
  x: L, y: 5.0, w: 3.9, h: 1.1,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 12.5, color: CINZA, valign: "top",
});

s10.addImage({ path: path.join(SAIDA, "parte1_melhor_individuo.png"), x: 5.0, y: 1.5, w: 7.6, h: 4.56 });
s10.addText("O patamar em 0.9903 é o anel r = π; o salto para 1.0 acontece quando um indivíduo finalmente entra na bacia central.", {
  x: 5.0, y: 6.15, w: 7.6, h: 0.55,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 11.5, italic: true, color: CINZA, valign: "top",
});

rodape(s10, "Integrante 3");
s10.addNotes(
  "INTEGRANTE 3\n\n" +
  "Esta é uma execução única, que é o que a parte 1 do enunciado pede.\n\n" +
  "O melhor indivíduo terminou em x igual a 0.0023 e y igual a menos 0.00015, com fitness 0.99999473. " +
  "Está bem dentro da caixa de mais ou menos 0.09, então essa execução converge para o máximo global.\n\n" +
  "O gráfico à direita é o fitness do melhor indivíduo em cada geração, que o enunciado pede em um gráfico separado. " +
  "Repare no formato: ele sobe rápido até cerca de 0.99 nas primeiras gerações e fica parado ali por quase 90 gerações. " +
  "Esse patamar é exatamente o anel de máximos locais.\n\n" +
  "Depois há um salto seco para 1.0. Esse é o momento em que um indivíduo finalmente cai dentro da bacia central e o fitness sharing consegue mantê-lo vivo."
);

/* ------------------------------------------------------------------ 11 */
const s11 = pres.addSlide();
tituloSlide(s11, "Parte 1 — a população ao longo das gerações");

s11.addImage({ path: path.join(SAIDA, "parte1_fitness_populacao.png"), x: L, y: 1.45, w: 7.6, h: 4.56 });
s11.addText("Melhor, média e pior fitness em cada uma das 300 gerações.", {
  x: L, y: 6.1, w: 7.6, h: 0.4,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 11.5, italic: true, color: CINZA, valign: "top",
});

cartao(s11, { x: 8.55, y: 1.45, w: 4.05, h: 2.5 });
s11.addText("A população nunca converge", {
  x: 8.85, y: 1.62, w: 3.45, h: 0.75,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 15, bold: true, color: TINTA, valign: "middle",
});
s11.addText("O melhor chega a 1.0, mas a média fica em torno de 0.6 e o pior perto de zero até o fim. Com sharing e mutação alta a diversidade é mantida de propósito — é ela que mantém a busca viva.", {
  x: 8.85, y: 2.42, w: 3.45, h: 1.45,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 12.5, color: CINZA, valign: "top",
});

cartao(s11, { x: 8.55, y: 4.15, w: 4.05, h: 1.86, fundo: ESCURO });
s11.addText("Vídeo da população", {
  x: 8.85, y: 4.38, w: 3.45, h: 0.42,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 15, bold: true, color: BRANCO, valign: "middle",
});
s11.addText("saida/parte1_populacao.mp4\n301 quadros com a população sobre as curvas de nível da f6, geração a geração.", {
  x: 8.85, y: 4.85, w: 3.45, h: 1.0,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 12, color: "C9C2DC", valign: "top",
});

rodape(s11, "Integrante 3");
s11.addNotes(
  "INTEGRANTE 3\n\n" +
  "Aqui está o gráfico com o melhor, a média e o pior fitness da população em cada geração, também pedido no enunciado.\n\n" +
  "Ele é bem diferente do que se espera de um AG comum. Normalmente as três curvas se encontram lá pelo fim, quando a população converge. Aqui isso nunca acontece: " +
  "a curva do melhor vai a 1.0, mas a média fica oscilando em torno de 0.6 e o pior fica perto de zero até a geração 300.\n\n" +
  "Isso não é defeito, é o efeito do fitness sharing somado à mutação de 0.09. A população é mantida espalhada de propósito. " +
  "Se ela convergisse, pararia de amostrar a região central e o algoritmo ficaria preso no anel, que foi exatamente o que aconteceu nos esquemas sem sharing.\n\n" +
  "Nós também geramos o vídeo pedido no enunciado. São 301 quadros, um por geração, mostrando os 50 indivíduos sobre as curvas de nível da f6.\n\n" +
  "Duas coisas para reparar no vídeo. O ponto vermelho grande é o melhor indivíduo da geração — ele é quem chega ao centro e fica lá. " +
  "Os pontos brancos continuam espalhados pelos anéis até o fim, e isso é o esperado, pelo mesmo motivo do gráfico deste slide.\n\n" +
  "E no canto inferior esquerdo tem um zoom de mais ou menos 0.4 em torno da origem, com a caixa de tolerância de 0.09 desenhada tracejada. " +
  "O contador mostra quantos indivíduos estão dentro dela: nesta execução são 2 no fim, e um deles é o melhor indivíduo. " +
  "Basta um para a execução contar como convergida, porque o enunciado pergunta pelo melhor indivíduo, não pela população."
);

/* ------------------------------------------------------------------ 12 */
const s12 = pres.addSlide();
tituloSlide(s12, "Parte 2 — 100 execuções independentes");

const metricas = [
  ["59 de 100", "convergiram para o máximo global", TEAL],
  ["≥ 50%", "exigido pelo enunciado: atendido", OURO],
  ["0.99568", "fitness médio das 100 execuções", ESCURO],
];
metricas.forEach((m, i) => {
  const y = 1.5 + i * 1.42;
  cartao(s12, { x: L, y: y, w: 5.5, h: 1.22 });
  s12.addText(m[0], {
    x: L + 0.3, y: y + 0.14, w: 5.0, h: 0.6,
    isTextBox: true, margin: 0,
    fontFace: TITULO_FONTE, fontSize: 28, bold: true, color: m[2], valign: "middle",
  });
  s12.addText(m[1], {
    x: L + 0.3, y: y + 0.72, w: 5.0, h: 0.38,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 12.5, color: CINZA, valign: "middle",
  });
});

s12.addText("As 41 execuções que falharam pararam no anel r = π, o mesmo máximo local de sempre.", {
  x: L, y: 5.85, w: 5.5, h: 0.7,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 12.5, color: CINZA, valign: "top",
});

s12.addImage({ path: path.join(SAIDA, "parte2_dispersao.png"), x: 7.05, y: 1.45, w: 5.05, h: 5.05 });

rodape(s12, "Integrante 3");
s12.addNotes(
  "INTEGRANTE 3\n\n" +
  "A parte 2 pede 100 execuções independentes e a contagem de quantas convergem para o máximo global.\n\n" +
  "O resultado foi 59 de 100, ou seja, 59%. O enunciado exige pelo menos 50%, então o requisito está atendido com margem. " +
  "O fitness médio das 100 execuções ficou em 0.99568.\n\n" +
  "O gráfico à direita mostra onde cada uma das 100 execuções terminou. Os pontos azuis, todos empilhados no centro, são as 59 que convergiram. " +
  "Os pontos vermelhos formam um círculo perfeito de raio pi — são as 41 que ficaram presas no primeiro anel de máximos locais.\n\n" +
  "O arquivo parte2_resultados.txt tem a lista completa: x, y e fitness finais de cada execução, com a indicação de se atingiu ou não o máximo global, como o enunciado pede."
);

/* ------------------------------------------------------------------ 13 */
const s13 = pres.addSlide();
s13.background = { color: ESCURO };
tituloSlide(s13, "Conclusão", BRANCO);

const fechamento = [
  ["O gargalo é diversidade, não pressão seletiva", "A f6 esconde o ótimo global dentro de um vale. Qualquer esquema que deixe a população convergir fica preso no anel r = π."],
  ["Roleta sozinha não basta", "Com os mesmos parâmetros, roleta + elitismo converge em 48% das execuções — abaixo do exigido."],
  ["Fitness sharing resolve sem trocar a seleção", "Dividir o fitness pelo número de vizinhos protege quem está isolado na bacia central e leva o resultado a 59%."],
  ["Há espaço para mais", "Deterministic crowding chega a 80% no mesmo orçamento, mas abre mão da seleção por roleta."],
];
fechamento.forEach((f, i) => {
  const y = 1.55 + i * 1.28;
  circuloNumero(s13, L, y, String(i + 1), i === 2 ? AMARELO : TEAL, i === 2 ? ESCURO2 : BRANCO);
  s13.addText(f[0], {
    x: L + 0.68, y: y - 0.05, w: 11.0, h: 0.45,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 16, bold: true, color: BRANCO, valign: "middle",
  });
  s13.addText(f[1], {
    x: L + 0.68, y: y + 0.42, w: 11.0, h: 0.68,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
    fontFace: CORPO_FONTE, fontSize: 13, color: "C9C2DC", valign: "top",
  });
});

s13.addText("Obrigado. Perguntas?", {
  x: L, y: 6.75, w: LARG, h: 0.45,
  isTextBox: true, margin: 0,
  fontFace: TITULO_FONTE, fontSize: 17, bold: true, color: AMARELO, valign: "middle",
});

s13.addNotes(
  "INTEGRANTE 3 (fechamento)\n\n" +
  "Fechando: o que esse trabalho mostrou é que na f6 o gargalo não é pressão seletiva, é diversidade. " +
  "A função esconde o ótimo global dentro de um vale, então qualquer esquema que deixe a população convergir cedo fica preso no anel.\n\n" +
  "A roleta sozinha, com os mesmos parâmetros de todo o resto, converge em 48% das execuções — abaixo do que o enunciado exige.\n\n" +
  "O fitness sharing resolve isso sem trocar a seleção: ele só divide o fitness pelo número de vizinhos antes de girar a roleta. " +
  "Isso protege quem está isolado perto do centro e leva o resultado para 59%.\n\n" +
  "E ainda sobra espaço: o deterministic crowding chega a 80% com o mesmo orçamento de 15 mil avaliações, mas abrindo mão da seleção por roleta.\n\n" +
  "Obrigado. Estamos à disposição para perguntas."
);

pres.writeFile({ fileName: path.join(__dirname, "apresentacao.pptx") }).then((f) => {
  console.log("gerado:", f);
});
