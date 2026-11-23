const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const RAIZ = path.dirname(__dirname);
const IMG = path.join(__dirname, "img");
const SAIDA = path.join(RAIZ, "saida");

const p1 = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_parte1.json"), "utf-8"));
const an = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_analise.json"), "utf-8"));
const eq = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_equilibrio.json"), "utf-8"));

const ESCURO = "241F1C";
const ESCURO2 = "17130F";
const AMBAR = "C77F26";
const AMBAR_CLARO = "E8A94C";
const AZUL = "1B6CA8";
const TINTA = "2A2521";
const CINZA = "6B635B";
const CARTAO = "F3F0EB";
const BRANCO = "FFFFFF";
const CLARO = "D8D0C6";

const TITULO_FONTE = "Cambria";
const CORPO_FONTE = "Calibri";

const ALUNOS = [
  "David Lanza Melo Matos",
  "Lucca Molinari Barbosa",
  "Nicolas Rodrigues de Vargas",
];

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Trabalho prático - Colônia de Formigas";
pres.title = "Otimização por Colônia de Formigas aplicada ao TSP";

const L = 0.7;
const LARG = 11.9;

function tituloSlide(slide, texto, cor) {
  slide.addText(texto, {
    x: L, y: 0.42, w: LARG, h: 0.85,
    isTextBox: true, margin: 0,
    fontFace: TITULO_FONTE, fontSize: 33, bold: true,
    color: cor || TINTA, align: "left", valign: "middle",
  });
}

function rodape(slide, texto, cor) {
  slide.addText(texto, {
    x: L, y: 6.92, w: 5.0, h: 0.32,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 12.5, color: cor || CINZA, valign: "middle",
  });
}

function cartao(slide, o) {
  slide.addShape(pres.ShapeType.roundRect, {
    x: o.x, y: o.y, w: o.w, h: o.h,
    rectRadius: 0.09,
    fill: { color: o.fundo || CARTAO },
    line: { color: o.borda || (o.fundo || CARTAO), width: o.borda ? 1.75 : 0.75 },
  });
}

function circulo(slide, x, y, texto, corFundo, corTexto) {
  slide.addShape(pres.ShapeType.ellipse, {
    x: x, y: y, w: 0.42, h: 0.42,
    fill: { color: corFundo }, line: { color: corFundo, width: 0.75 },
  });
  slide.addText(texto, {
    x: x, y: y, w: 0.42, h: 0.42,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 15, bold: true,
    color: corTexto, align: "center", valign: "middle",
  });
}

function tabela(slide, opcoes) {
  const { x, y, w, colunas, larguras, linhas, destaque } = opcoes;
  const alturaCabecalho = 0.38;
  const alturaLinha = 0.36;

  slide.addShape(pres.ShapeType.rect, {
    x: x, y: y, w: w, h: alturaCabecalho,
    fill: { color: ESCURO }, line: { color: ESCURO, width: 0.5 },
  });
  let cursor = x;
  colunas.forEach((c, i) => {
    slide.addText(c, {
      x: cursor + 0.1, y: y, w: larguras[i] - 0.2, h: alturaCabecalho,
      isTextBox: true, margin: 0,
      fontFace: CORPO_FONTE, fontSize: 13.5, bold: true, color: BRANCO,
      align: i === 0 ? "left" : "right", valign: "middle",
    });
    cursor += larguras[i];
  });

  linhas.forEach((linha, k) => {
    const ly = y + alturaCabecalho + k * alturaLinha;
    const marcado = destaque !== undefined && destaque === k;
    if (marcado || k % 2 === 0) {
      slide.addShape(pres.ShapeType.rect, {
        x: x, y: ly, w: w, h: alturaLinha,
        fill: { color: marcado ? AMBAR_CLARO : CARTAO },
        line: { color: marcado ? AMBAR_CLARO : CARTAO, width: 0.5 },
      });
    }
    let cx = x;
    linha.forEach((celula, i) => {
      slide.addText(String(celula), {
        x: cx + 0.1, y: ly, w: larguras[i] - 0.2, h: alturaLinha,
        isTextBox: true, margin: 0,
        fontFace: CORPO_FONTE, fontSize: 13.5, bold: marcado,
        color: marcado ? ESCURO2 : TINTA,
        align: i === 0 ? "left" : "right", valign: "middle",
      });
      cx += larguras[i];
    });
  });
  return y + alturaCabecalho + linhas.length * alturaLinha;
}

/* --------------------------------------------------------------- 1 capa */
const s1 = pres.addSlide();
s1.background = { color: ESCURO };
s1.addImage({ path: path.join(IMG, "grafo_capa.png"), x: 8.05, y: 1.2, w: 4.8, h: 4.8 });

s1.addText("TRABALHO PRÁTICO · OTIMIZAÇÃO COMBINATÓRIA", {
  x: L, y: 1.5, w: 7.2, h: 0.34,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 14.5, bold: true, charSpacing: 2,
  color: AMBAR_CLARO, valign: "middle",
});
s1.addText("Otimização por\nColônia de Formigas", {
  x: L, y: 2.0, w: 7.2, h: 1.9,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.05,
  fontFace: TITULO_FONTE, fontSize: 42, bold: true, color: BRANCO, valign: "top",
});
s1.addText("Aplicada ao Problema do Caixeiro Viajante com " + p1.cidades + " cidades", {
  x: L, y: 3.98, w: 7.2, h: 0.8,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 18, color: CLARO, valign: "top",
});
s1.addText("ALUNOS", {
  x: L, y: 4.82, w: 7.2, h: 0.3,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 12, bold: true, charSpacing: 2,
  color: AMBAR_CLARO, valign: "middle",
});
s1.addText(ALUNOS.join("\n"), {
  x: L, y: 5.18, w: 7.2, h: 1.0,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.2,
  fontFace: CORPO_FONTE, fontSize: 15, color: BRANCO, valign: "top",
});

s1.addText("Menor distância encontrada: " + p1.melhor_distancia.toFixed(2)
           + "   ·   convergência na iteração " + p1.iteracao_convergencia, {
  x: L, y: 6.35, w: 7.2, h: 0.35,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 14.5, color: "9C938A", valign: "middle",
});

s1.addNotes(
  "INTEGRANTE 1 (abertura)\n\n" +
  "Bom dia. Nosso trabalho é o de Colônia de Formigas, o ACO, aplicado ao Problema do Caixeiro Viajante com " + p1.cidades + " cidades.\n\n" +
  "Eu vou apresentar o problema e como o algoritmo funciona. Depois o " + "Integrante 2" + " mostra a implementação, o resultado da Parte 1 e a análise do número de formigas. " +
  "E o Integrante 3 fecha com a análise da taxa de evaporação e as conclusões.\n\n" +
  "Adiantando: a menor distância que encontramos foi " + p1.melhor_distancia.toFixed(2) + ", e o algoritmo convergiu na iteração " + p1.iteracao_convergencia + "."
);

/* ----------------------------------------------------------- 2 problema */
const s2 = pres.addSlide();
tituloSlide(s2, "O problema");

const itens = [
  ["Instância", p1.cidades + " cidades, grafo completo — " + (p1.cidades * (p1.cidades - 1) / 2) + " arestas possíveis"],
  ["Entrada", "matriz de adjacência distancia_matrix.csv"],
  ["Objetivo", "encontrar o ciclo que visita todas as cidades uma vez com a menor distância total"],
  ["Limite", p1.iteracoes + " iterações"],
  ["Dificuldade", "o número de rotas possíveis é 19! / 2 ≈ 6 × 10¹⁶"],
];
itens.forEach((item, i) => {
  const y = 1.55 + i * 0.95;
  circulo(s2, L, y, String(i + 1), i === 4 ? AMBAR : ESCURO, BRANCO);
  s2.addText(item[0], {
    x: L + 0.62, y: y - 0.06, w: 1.75, h: 0.55,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 15.5, bold: true, color: TINTA, valign: "middle",
  });
  s2.addText(item[1], {
    x: L + 2.45, y: y - 0.12, w: 4.55, h: 0.68,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
    fontFace: CORPO_FONTE, fontSize: 14.5, color: CINZA, valign: "middle",
  });
});

s2.addImage({ path: path.join(IMG, "grafo_inicial.png"), x: 7.75, y: 1.5, w: 4.85, h: 4.85 });
s2.addText("Estado inicial: feromônio igual em todas as arestas (τ₀ = 1).", {
  x: 7.75, y: 6.38, w: 4.85, h: 0.55,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 13, italic: true, color: CINZA, valign: "top",
});

s2.addNotes(
  "INTEGRANTE 1\n\n" +
  "O Problema do Caixeiro Viajante é o seguinte: dadas " + p1.cidades + " cidades e a distância entre cada par delas, qual é o ciclo mais curto que passa por todas exatamente uma vez e volta ao início?\n\n" +
  "A entrada é a matriz de adjacência que o professor forneceu. O grafo é completo, então são " + (p1.cidades * (p1.cidades - 1) / 2) + " arestas possíveis.\n\n" +
  "O que torna o problema difícil é a explosão combinatória: com 20 cidades existem cerca de 6 vezes 10 elevado a 16 rotas diferentes. Testar uma por uma é inviável — por isso se usa uma metaheurística.\n\n" +
  "À direita está o estado inicial: todas as arestas com o mesmo feromônio. Nesse momento as formigas decidem só pela distância."
);

/* ------------------------------------------------------- 3 como funciona */
const s3 = pres.addSlide();
tituloSlide(s3, "Como uma formiga escolhe o caminho");

cartao(s3, { x: L, y: 1.4, w: LARG, h: 1.1, fundo: ESCURO });
s3.addText("P(i → j)  =   [ τ(i,j)^α · η(i,j)^β ]   /   Σ  [ τ(i,l)^α · η(i,l)^β ]", {
  x: L + 0.3, y: 1.4, w: LARG - 0.6, h: 1.1,
  isTextBox: true, margin: 0,
  fontFace: "Courier New", fontSize: 17, color: BRANCO, align: "center", valign: "middle",
});

const fatores = [
  ["τ — feromônio", AMBAR,
   "O que a colônia aprendeu até agora. Cresce nas arestas que fizeram parte de boas rotas no passado. É a memória coletiva."],
  ["η — visibilidade", AZUL,
   "1 dividido pela distância. É a qualidade imediata da aresta, sem nenhuma memória: quanto mais perto, mais atrativa."],
];
fatores.forEach((f, i) => {
  const x = L + i * 4.05;
  cartao(s3, { x: x, y: 2.72, w: 3.8, h: 2.62 });
  s3.addText(f[0], {
    x: x + 0.28, y: 2.95, w: 3.25, h: 0.45,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 17.5, bold: true, color: f[1], valign: "middle",
  });
  s3.addText(f[2], {
    x: x + 0.28, y: 3.42, w: 3.25, h: 1.85,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
    fontFace: CORPO_FONTE, fontSize: 14.5, color: CINZA, valign: "top",
  });
});

cartao(s3, { x: L + 8.1, y: 2.72, w: 3.8, h: 2.62, fundo: ESCURO });
s3.addText("Analogia do restaurante", {
  x: L + 8.38, y: 2.88, w: 3.25, h: 0.5,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 16.5, bold: true, color: AMBAR_CLARO, valign: "middle",
});
s3.addText("η é a distância até o restaurante — a conveniência. τ é a avaliação dos outros clientes — a experiência acumulada. A escolha pesa os dois.", {
  x: L + 8.38, y: 3.42, w: 3.25, h: 1.85,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 14.5, color: CLARO, valign: "top",
});

s3.addText("A escolha é probabilística, feita por roleta — como na seleção dos algoritmos genéticos. Duas formigas na mesma cidade podem seguir por arestas diferentes.", {
  x: L, y: 5.5, w: LARG, h: 0.85,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 15, color: TINTA, valign: "top",
});

s3.addNotes(
  "INTEGRANTE 1\n\n" +
  "Esta é a regra de transição, o coração do algoritmo. Quando uma formiga está na cidade i e precisa escolher a próxima, ela combina dois fatores.\n\n" +
  "O tau é o feromônio da aresta: o que a colônia aprendeu até agora. Ele cresce nas arestas que fizeram parte de boas rotas.\n\n" +
  "O eta é a visibilidade, que é simplesmente um dividido pela distância. É a qualidade imediata da aresta, sem memória nenhuma.\n\n" +
  "A analogia que ajuda é a de escolher restaurante: o eta é a distância até lá, a conveniência; o tau é a avaliação dos outros clientes, a experiência coletiva. Você pesa os dois.\n\n" +
  "E a escolha é probabilística, por roleta — igual à seleção que a gente viu em algoritmos genéticos. Duas formigas na mesma cidade podem escolher caminhos diferentes, e é isso que mantém a exploração."
);

/* --------------------------------------------------- 4 atualiza feromonio */
const s4 = pres.addSlide();
tituloSlide(s4, "Como o feromônio é atualizado");

cartao(s4, { x: L, y: 1.4, w: LARG, h: 1.1, fundo: ESCURO });
s4.addText("τ(i,j)  ←  (1 − ρ) · τ(i,j)  +  Σ  Δτ(i,j)          Δτ = Q / L", {
  x: L + 0.3, y: 1.4, w: LARG - 0.6, h: 1.1,
  isTextBox: true, margin: 0,
  fontFace: "Courier New", fontSize: 17, color: BRANCO, align: "center", valign: "middle",
});

const eventos = [
  ["1", "Evaporação", "(1 − ρ) · τ", AMBAR,
   "Todas as arestas perdem uma fração ρ do feromônio. É o que permite à colônia esquecer decisões ruins do passado e impede que o feromônio cresça sem limite."],
  ["2", "Depósito", "Q / L", AZUL,
   "Cada formiga deposita Q dividido pelo comprimento da rota dela, e só nas arestas que percorreu. Rota mais curta deposita mais — é aí que a qualidade vira reforço."],
];
eventos.forEach((e, i) => {
  const y = 2.75 + i * 1.85;
  cartao(s4, { x: L, y: y, w: LARG, h: 1.6 });
  circulo(s4, L + 0.3, y + 0.28, e[0], e[3], BRANCO);
  s4.addText(e[1], {
    x: L + 0.92, y: y + 0.22, w: 2.0, h: 0.5,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 18, bold: true, color: TINTA, valign: "middle",
  });
  s4.addText(e[2], {
    x: L + 3.05, y: y + 0.22, w: 1.6, h: 0.5,
    isTextBox: true, margin: 0,
    fontFace: "Courier New", fontSize: 15, color: e[3], valign: "middle",
  });
  s4.addText(e[4], {
    x: L + 0.92, y: y + 0.76, w: 10.5, h: 0.72,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
    fontFace: CORPO_FONTE, fontSize: 14.5, color: CINZA, valign: "top",
  });
});

s4.addText("Sem evaporação a colônia nunca esquece; com evaporação demais ela nunca aprende. É esse equilíbrio que a Parte 3 investiga.", {
  x: L, y: 6.25, w: LARG, h: 0.6,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 14.5, italic: true, color: CINZA, valign: "middle",
});

s4.addNotes(
  "INTEGRANTE 1\n\n" +
  "Depois que todas as formigas terminam suas rotas, o feromônio é atualizado, e acontecem duas coisas.\n\n" +
  "Primeiro a evaporação: toda aresta perde uma fração rô do feromônio que tinha. Isso serve para dois propósitos — impedir que o feromônio cresça indefinidamente, e permitir que a colônia esqueça decisões ruins que tomou no começo da busca.\n\n" +
  "Depois o depósito: cada formiga deposita Q dividido pelo comprimento da rota dela, e só nas arestas por onde ela passou. Repare que quanto MENOR a rota, MAIOR o depósito. É exatamente aí que a qualidade da solução vira reforço.\n\n" +
  "O equilíbrio entre esquecer e aprender é controlado pelo rô, e é isso que a gente investiga na Parte 3.\n\n" +
  "Passo para o Integrante 2."
);

/* -------------------------------------------------- 5 parametros/converg */
const s5 = pres.addSlide();
tituloSlide(s5, "Parâmetros e critério de convergência");

const parametros = [
  ["α = 1", "peso do feromônio"],
  ["β = 5", "peso da visibilidade"],
  ["Q = 100", "constante de depósito"],
  ["τ₀ = 1", "feromônio inicial (aula)"],
  ["sem elitismo", "exigido nas Partes 2 e 3"],
  [p1.iteracoes + " iterações", "limite máximo"],
];
parametros.forEach((p, i) => {
  const col = i % 3;
  const lin = Math.floor(i / 3);
  const x = L + col * 4.0;
  const y = 1.5 + lin * 1.25;
  cartao(s5, { x: x, y: y, w: 3.75, h: 1.05 });
  s5.addText(p[0], {
    x: x + 0.28, y: y + 0.12, w: 3.2, h: 0.45,
    isTextBox: true, margin: 0,
    fontFace: TITULO_FONTE, fontSize: 20, bold: true, color: lin === 0 ? AMBAR : ESCURO,
    valign: "middle",
  });
  s5.addText(p[1], {
    x: x + 0.28, y: y + 0.58, w: 3.2, h: 0.36,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 14, color: CINZA, valign: "middle",
  });
});

cartao(s5, { x: L, y: 4.2, w: LARG, h: 2.45, fundo: ESCURO });
s5.addText("Critério de convergência", {
  x: L + 0.35, y: 4.42, w: 6.0, h: 0.45,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 18, bold: true, color: AMBAR_CLARO, valign: "middle",
});
s5.addText("A melhor distância encontrada precisa ficar estável por pelo menos "
  + p1.janela_convergencia + " iterações consecutivas. A iteração reportada é aquela em que a "
  + "melhor distância foi atingida pela última vez — o ponto em que ela estabilizou.\n\n"
  + "Nas Partes 2 e 3 a execução encerra assim que isso acontece. A Parte 1 roda as "
  + p1.iteracoes + " iterações inteiras para o vídeo mostrar o feromônio depois da convergência.", {
  x: L + 0.35, y: 4.92, w: LARG - 0.7, h: 1.6,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 14.5, color: CLARO, valign: "top",
});

s5.addNotes(
  "INTEGRANTE 2\n\n" +
  "O enunciado fixa alfa igual a 1, beta igual a 5, Q igual a 100 e diz, literalmente, «não utilize elitismo». " +
  "Vale registrar que ele exige isso nas Partes 2 e 3; a Parte 1 não especifica parâmetro nenhum, só a matriz de entrada, as " + p1.iteracoes + " iterações e as saídas. " +
  "Nós usamos os mesmos valores na Parte 1 por coerência, para a execução única ser comparável com as varreduras das outras partes.\n\n" +
  "O feromônio inicial é 1 em todas as arestas, que vem do material da aula, não do enunciado do exercício.\n\n" +
  "Repare que beta é cinco vezes maior que alfa. Isso significa que a visibilidade, ou seja, a distância, pesa muito mais que o feromônio na decisão. " +
  "Na prática o algoritmo começa bem guloso e o feromônio vai ganhando influência com o tempo.\n\n" +
  "Sobre convergência, o enunciado define: a melhor distância precisa ficar estável por pelo menos " + p1.janela_convergencia + " iterações seguidas. " +
  "A gente reporta como iteração de convergência aquela em que a melhor distância foi atingida pela última vez — o ponto onde ela parou de melhorar.\n\n" +
  "Nas Partes 2 e 3 a execução para assim que isso é detectado, como o enunciado permite. Na Parte 1 a gente roda as " + p1.iteracoes + " iterações inteiras, porque o vídeo precisa mostrar o que acontece com o feromônio depois que a rota já foi encontrada."
);

/* ------------------------------------------------------ 6 parte 1 result */
const s6 = pres.addSlide();
tituloSlide(s6, "Parte 1 — resultado");

const metricas = [
  [p1.melhor_distancia.toFixed(2), "menor distância encontrada", AMBAR],
  ["iteração " + p1.iteracao_convergencia, "convergência", AZUL],
  [p1.formigas + " formigas", "ρ = " + p1.evaporacao, ESCURO],
];
metricas.forEach((m, i) => {
  const y = 1.5 + i * 1.3;
  cartao(s6, { x: L, y: y, w: 4.5, h: 1.12 });
  s6.addText(m[0], {
    x: L + 0.3, y: y + 0.14, w: 3.9, h: 0.5,
    isTextBox: true, margin: 0,
    fontFace: TITULO_FONTE, fontSize: 26, bold: true, color: m[2], valign: "middle",
  });
  s6.addText(m[1], {
    x: L + 0.3, y: y + 0.66, w: 3.9, h: 0.34,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 14, color: CINZA, valign: "middle",
  });
});

s6.addText("A busca cai de " + p1.distancia_inicial.toFixed(2) + " para "
  + p1.melhor_distancia.toFixed(2) + " nas primeiras iterações e não melhora mais depois disso.", {
  x: L, y: 5.5, w: 4.5, h: 0.85,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 14.5, color: CINZA, valign: "top",
});

s6.addImage({ path: path.join(SAIDA, "parte1_convergencia.png"), x: 5.5, y: 1.5, w: 7.1, h: 4.26 });
s6.addText("A linha tracejada marca a iteração em que a melhor distância estabilizou.", {
  x: 5.5, y: 5.9, w: 7.1, h: 0.4,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 13, italic: true, color: CINZA, valign: "top",
});

s6.addNotes(
  "INTEGRANTE 2\n\n" +
  "Com " + p1.formigas + " formigas e taxa de evaporação " + p1.evaporacao + ", a menor distância que o algoritmo encontrou foi " + p1.melhor_distancia.toFixed(2) + ".\n\n" +
  "O gráfico à direita é a evolução da melhor distância a cada iteração, que é o que o enunciado pede. Repare no formato: a curva despenca nas primeiras iterações e depois fica completamente plana.\n\n" +
  "A melhor distância foi atingida na iteração " + p1.iteracao_convergencia + " e não melhorou mais em nenhuma das iterações seguintes — por isso marcamos ali a convergência, com a linha tracejada.\n\n" +
  "Vale dizer que a gente validou esse resultado comparando com duas referências na mesma instância: o vizinho mais próximo chega em 1428, e uma busca 2-opt, que é uma heurística forte de melhoria local, chega em 1331. O ACO chegou em 1328, melhor que as duas."
);

/* --------------------------------------------------------- 7 parte 1 video */
const s7 = pres.addSlide();
tituloSlide(s7, "Parte 1 — o feromônio ao longo das iterações");

s7.addMedia({
  type: "video",
  path: path.join(SAIDA, "parte1_feromonio.mp4"),
  cover: "data:image/png;base64,"
         + fs.readFileSync(path.join(IMG, "video_capa.png")).toString("base64"),
  x: 0.7, y: 1.42, w: 7.62, h: 4.75,
});
s7.addText("clique para reproduzir · mesmos dados nos dois painéis, muda só a posição das cidades", {
  x: 0.7, y: 6.3, w: 7.62, h: 0.3,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 12, italic: true, color: CINZA,
  align: "center", valign: "middle",
});

cartao(s7, { x: 8.55, y: 1.42, w: 4.05, h: 2.42, fundo: ESCURO });
s7.addText("A escala de cinza", {
  x: 8.85, y: 1.62, w: 3.45, h: 0.45,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 17, bold: true, color: AMBAR_CLARO, valign: "middle",
});
s7.addText("Branco = 0; preto = o máximo da execução (" + p1.feromonio_maximo + ").\n\n"
  + "A espessura segue a mesma escala.", {
  x: 8.85, y: 2.1, w: 3.45, h: 1.6,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 14, color: CLARO, valign: "top",
});

cartao(s7, { x: 8.55, y: 4.04, w: 4.05, h: 2.76 });
s7.addText("Os dois painéis", {
  x: 8.85, y: 4.24, w: 3.45, h: 0.45,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 17, bold: true, color: TINTA, valign: "middle",
});
s7.addText("Mesmos dados nos dois. À esquerda, o círculo ordenado pela rota final; "
  + "à direita, a ordem original.\n\n"
  + "A rota azul para de mudar na iteração " + p1.iteracao_convergencia + ".", {
  x: 8.85, y: 4.72, w: 3.45, h: 2.02,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 14, color: CINZA, valign: "top",
});

s7.addNotes(
  "INTEGRANTE 2\n\n" +
  "[DAR PLAY NO VÍDEO — ele está embutido no slide, é só clicar. Dura 12 segundos.]\n\n" +
  "Aqui está o vídeo que o enunciado pede. São " + p1.iteracoes + " quadros, um por iteração, com as " + p1.cidades + " cidades ligadas por todas as arestas possíveis.\n\n" +
  "A cor e a espessura de cada aresta acompanham o feromônio, na escala de cinza pedida: branco é feromônio zero, e preto é o máximo atingido durante toda a execução, que nesta rodada foi " + p1.feromonio_maximo + ".\n\n" +
  "O importante é que a normalização é pelo máximo da execução inteira, não de cada quadro. Se fosse por quadro, a imagem ficaria sempre igual e não daria para ver a evolução.\n\n" +
  "No começo as " + (p1.cidades * (p1.cidades - 1) / 2) + " arestas estão todas iguais. Em poucas iterações a rota vencedora aparece preta e grossa, e todo o resto desaparece no branco.\n\n" +
  "A linha azul é a melhor rota encontrada até aquele momento.\n\n" +
  "Sobre os dois painéis: eles mostram exatamente os mesmos dados. A única diferença é onde cada cidade foi desenhada. " +
  "À direita, as cidades estão na ordem original, de 0 a 19, e a rota vira um emaranhado de linhas cruzando o círculo — não dá para enxergar nada. " +
  "À esquerda, nós ordenamos o círculo pela rota final, e aí a mesma rota coincide com o anel externo.\n\n" +
  "Como a matriz de distâncias não é geométrica, qualquer disposição seria igualmente arbitrária. Deixamos o painel da direita no vídeo justamente para deixar claro que o que muda é só o desenho, não o algoritmo.\n\n" +
  "Na prática, a linha azul começa cruzando o círculo e vai se fechando no anel externo conforme a colônia converge. Ela salta de lugar algumas vezes no começo, quando o algoritmo ainda está achando rotas melhores, e depois trava. " +
  "O instante em que ela para de se mexer é exatamente a convergência: foi na iteração " + p1.iteracao_convergencia + ". O título do vídeo mostra há quantas iterações a rota está inalterada.\n\n" +
  "Isso é exatamente a estagnação que o material descreve: o feromônio fica tão concentrado que as formigas passam a repetir sempre o mesmo percurso. Aqui ela é desejável, porque a rota que ficou é a melhor que existe. Mas em uma instância maior essa mesma estagnação poderia travar a busca num ótimo local."
);

/* ------------------------------------------------------- 8 parte 2 tabela */
const s8 = pres.addSlide();
tituloSlide(s8, "Parte 2 — número de formigas");

const linhas2 = an.parte2.formigas.map((f, i) => {
  const l = an.parte2.linhas[i];
  return [String(f), l.media.toFixed(2), l.desvio.toFixed(2), l.iteracoes.toFixed(1),
          Math.round(f * l.iteracoes)];
});
tabela(s8, {
  x: L, y: 1.5, w: 5.75,
  colunas: ["formigas", "média", "desvio", "iterações", "rotas"],
  larguras: [1.15, 1.25, 1.05, 1.2, 1.1],
  linhas: linhas2,
});

s8.addText("ρ fixo em 0.5 · " + an.execucoes + " execuções por configuração\n"
  + "«rotas» = formigas × iterações, o custo total de construção", {
  x: L, y: 4.32, w: 5.75, h: 0.95,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 13.5, italic: true, color: CINZA, valign: "top",
});

s8.addImage({ path: path.join(SAIDA, "parte2_a_distancia.png"), x: 6.7, y: 1.5, w: 5.9, h: 3.6 });
s8.addText("Colônias pequenas erram mais e erram de forma imprevisível: com 3 formigas o desvio padrão é "
  + an.parte2.linhas[0].desvio.toFixed(2) + ", contra "
  + an.parte2.linhas[3].desvio.toFixed(2) + " com 20.", {
  x: 6.7, y: 5.22, w: 5.9, h: 1.0,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 14, color: CINZA, valign: "top",
});

s8.addNotes(
  "INTEGRANTE 2\n\n" +
  "A Parte 2 pede para fixar a evaporação em 0.5 e variar o número de formigas, rodando " + an.execucoes + " vezes cada configuração.\n\n" +
  "Esta é a matriz de resultados que o enunciado pede no terminal: número de formigas, média da distância, desvio padrão e média de iterações até a convergência. " +
  "A última coluna é um extra nosso, e eu volto nela já já.\n\n" +
  "O que salta aos olhos é o desvio padrão. Com 3 formigas ele é " + an.parte2.linhas[0].desvio.toFixed(2) + ", e com 20 formigas ele é " + an.parte2.linhas[3].desvio.toFixed(2) + ". " +
  "Ou seja, colônia pequena não é só pior na média — ela é imprevisível. Cada execução termina num lugar diferente.\n\n" +
  "O motivo é amostragem: com 3 formigas você constrói 3 rotas por iteração, e o feromônio passa a refletir uma amostra minúscula do espaço de busca. Se as primeiras rotas forem ruins, o reforço vai para as arestas erradas e a colônia se convence de algo que não é verdade.\n\n" +
  "Passo para o " + "Integrante 3" + ", que vai fazer a leitura crítica disso."
);

/* -------------------------------------------------- 9 parte 2 analise */
const s9 = pres.addSlide();
tituloSlide(s9, "Parte 2 — a leitura crítica");

s9.addImage({ path: path.join(SAIDA, "parte2_b_iteracoes.png"), x: L, y: 1.45, w: 6.3, h: 3.85 });

const custoMin = an.parte2.formigas[0] * an.parte2.linhas[0].iteracoes;
const custoMax = an.parte2.formigas[an.parte2.formigas.length - 1]
                 * an.parte2.linhas[an.parte2.linhas.length - 1].iteracoes;

cartao(s9, { x: 7.35, y: 1.45, w: 5.25, h: 2.0, fundo: ESCURO });
s9.addText("Menos iterações ≠ mais barato", {
  x: 7.63, y: 1.65, w: 4.7, h: 0.45,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 17, bold: true, color: AMBAR_CLARO, valign: "middle",
});
s9.addText("Colônias grandes convergem em menos iterações, mas cada iteração constrói mais rotas. "
  + "Com 3 formigas são ~" + Math.round(custoMin) + " rotas construídas no total; com 80, ~"
  + Math.round(custoMax) + ".", {
  x: 7.63, y: 2.08, w: 4.7, h: 1.3,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 14, color: CLARO, valign: "top",
});

const leituras = [
  ["Retornos decrescentes", "De 20 para 80 formigas a distância cai "
   + (100 * (an.parte2.linhas[3].media - an.parte2.linhas[5].media) / an.parte2.linhas[3].media).toFixed(2)
   + "%, enquanto o custo sobe de " + Math.round(20 * an.parte2.linhas[3].iteracoes)
   + " para " + Math.round(80 * an.parte2.linhas[5].iteracoes) + " rotas."],
  ["O ponto de equilíbrio", "Em 20 formigas o desvio já cai para "
   + an.parte2.linhas[3].desvio.toFixed(2) + ", contra "
   + an.parte2.linhas[0].desvio.toFixed(2) + " com 3 — sem o custo de uma colônia grande."],
];
leituras.forEach((l, i) => {
  const y = 3.62 + i * 1.62;
  cartao(s9, { x: 7.35, y: y, w: 5.25, h: 1.55 });
  s9.addText(l[0], {
    x: 7.63, y: y + 0.16, w: 4.7, h: 0.42,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 16, bold: true, color: TINTA, valign: "middle",
  });
  s9.addText(l[1], {
    x: 7.63, y: y + 0.6, w: 4.7, h: 0.85,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
    fontFace: CORPO_FONTE, fontSize: 13.5, color: CINZA, valign: "top",
  });
});

s9.addNotes(
  "INTEGRANTE 3\n\n" +
  "Este é o segundo gráfico da Parte 2: a média de iterações até a convergência.\n\n" +
  "A leitura óbvia é que colônia maior converge em menos iterações, e isso é verdade. Mas é uma leitura enganosa, e por isso a gente acrescentou aquela coluna extra na tabela anterior.\n\n" +
  "O que interessa não é o número de iterações, é o trabalho total — quantas rotas foram construídas. E esse número é formigas vezes iterações. " +
  "Com 3 formigas dá cerca de " + Math.round(custoMin) + " rotas construídas no total. Com 80 formigas dá cerca de " + Math.round(custoMax) + ". " +
  "Ou seja, a colônia grande converge em menos iterações mas faz muito mais trabalho para chegar lá.\n\n" +
  "A segunda leitura é de retornos decrescentes: entre 20 e 80 formigas a distância final não melhora mais nada. O ganho de aumentar a colônia se esgota.\n\n" +
  "A segunda leitura é de retornos decrescentes: de 20 para 80 formigas a distância melhora só " + (100 * (an.parte2.linhas[3].media - an.parte2.linhas[5].media) / an.parte2.linhas[3].media).toFixed(2) + " por cento, e para isso o custo sobe de " + Math.round(20 * an.parte2.linhas[3].iteracoes) + " para " + Math.round(80 * an.parte2.linhas[5].iteracoes) + " rotas construídas.\n\n" +
  "Juntando as duas coisas, o ponto de equilíbrio nesta instância fica em torno de 20 formigas: é onde o desvio padrão já despencou, de " + an.parte2.linhas[0].desvio.toFixed(2) + " para " + an.parte2.linhas[3].desvio.toFixed(2) + ", sem pagar o custo de uma colônia grande."
);

/* ------------------------------------------------- 10 parte 3 tabela */
const s10 = pres.addSlide();
tituloSlide(s10, "Parte 3 — taxa de evaporação");

const linhas3 = an.parte3.evaporacoes.map((p, i) => {
  const l = an.parte3.linhas[i];
  return [p.toFixed(2), l.media.toFixed(2), l.desvio.toFixed(2), l.iteracoes.toFixed(1)];
});
tabela(s10, {
  x: L, y: 1.5, w: 5.2,
  colunas: ["ρ", "média", "desvio", "iterações"],
  larguras: [1.1, 1.45, 1.25, 1.4],
  linhas: linhas3,
});

s10.addText("20 formigas · " + an.execucoes + " execuções por configuração", {
  x: L, y: 3.9, w: 5.2, h: 0.4,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 13.5, italic: true, color: CINZA, valign: "top",
});

cartao(s10, { x: L, y: 4.45, w: 5.2, h: 2.05, fundo: ESCURO });
s10.addText("Os dois extremos", {
  x: L + 0.3, y: 4.7, w: 4.6, h: 0.42,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 16.5, bold: true, color: AMBAR_CLARO, valign: "middle",
});
s10.addText("ρ = 0 — o feromônio só acumula, nada evapora: a colônia nunca esquece.\n"
  + "ρ = 1 — tudo evapora a cada iteração: a colônia só enxerga a última rodada.", {
  x: L + 0.3, y: 5.12, w: 4.6, h: 1.3,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 14, color: CLARO, valign: "top",
});

s10.addImage({ path: path.join(SAIDA, "parte3_a_distancia.png"), x: 6.25, y: 1.85, w: 6.35, h: 3.88 });
s10.addText("A escala do eixo Y é estreita: todas as configurações chegam praticamente à mesma distância nesta instância.", {
  x: 6.25, y: 5.85, w: 6.35, h: 0.6,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 13.5, italic: true, color: CINZA, valign: "top",
});

s10.addNotes(
  "INTEGRANTE 3\n\n" +
  "A Parte 3 fixa a colônia em 20 formigas e varia a taxa de evaporação entre 0 e 1.\n\n" +
  "Antes dos números, vale entender o que significam os extremos.\n\n" +
  "Com rô igual a zero não existe evaporação: o feromônio só acumula, para sempre. A colônia nunca esquece nada — inclusive as decisões ruins que tomou nas primeiras iterações, quando ainda não sabia nada. " +
  "Aquilo que foi reforçado no começo por acaso fica registrado no grafo o resto da execução.\n\n" +
  "Com rô igual a um a evaporação é total: o feromônio de cada iteração é apagado inteiro e substituído só pelo depósito daquela rodada. A colônia perde a memória de longo prazo e passa a decidir quase só pela visibilidade.\n\n" +
  "A tabela mostra a média, o desvio e as iterações para cada valor. No próximo slide eu faço a leitura."
);

/* -------------------------------------------- 11 parte 3 analise */
const s11 = pres.addSlide();
tituloSlide(s11, "Parte 3 — a leitura crítica");

s11.addImage({ path: path.join(SAIDA, "parte3_b_iteracoes.png"), x: L, y: 1.45, w: 6.3, h: 3.85 });
s11.addText("α e β governam o mesmo equilíbrio: α alto faz a colônia confiar na trilha, β alto a torna gulosa. Com α = 1 e β = 5 o enunciado já nos coloca no lado guloso.", {
  x: L, y: 5.45, w: 6.3, h: 0.85,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.15,
  fontFace: CORPO_FONTE, fontSize: 14, italic: true, color: CINZA, valign: "top",
});

const pontos3 = [
  ["1", "ρ = 0 é o pior caso",
   "Sem evaporação a convergência leva " + an.parte3.linhas[0].iteracoes.toFixed(1)
   + " iterações, contra " + an.parte3.linhas[2].iteracoes.toFixed(1)
   + " com ρ = 0.5. O reforço das primeiras iterações nunca é apagado.", AMBAR],
  ["2", "ρ = 1 funcionar bem diz algo sobre β",
   "O feromônio dura uma iteração e ainda assim dá a melhor média ("
   + an.parte3.linhas[4].media.toFixed(1) + "). Com β = 5 a visibilidade já carrega a busca.", AMBAR],
  ["3", "O efeito é maior na velocidade",
   "Todas as configurações ficam dentro de "
   + (100 * (Math.max.apply(null, an.parte3.linhas.map(l => l.media)) - Math.min.apply(null, an.parte3.linhas.map(l => l.media))) / Math.min.apply(null, an.parte3.linhas.map(l => l.media))).toFixed(2)
   + "% entre si. O que ρ muda de verdade é quantas iterações são necessárias.", ESCURO],
];
pontos3.forEach((p, i) => {
  const y = 1.45 + i * 1.74;
  cartao(s11, { x: 7.35, y: y, w: 5.25, h: 1.64 });
  circulo(s11, 7.63, y + 0.2, p[0], p[3], BRANCO);
  s11.addText(p[1], {
    x: 8.22, y: y + 0.1, w: 4.1, h: 0.56,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 15.5, bold: true, color: TINTA, valign: "middle",
  });
  s11.addText(p[2], {
    x: 7.63, y: y + 0.68, w: 4.7, h: 0.92,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
    fontFace: CORPO_FONTE, fontSize: 13.5, color: CINZA, valign: "top",
  });
});

s11.addNotes(
  "INTEGRANTE 3\n\n" +
  "Três leituras da Parte 3.\n\n" +
  "A primeira é a mais clara nos números: rô igual a zero é o pior caso. Sem evaporação a convergência leva " + an.parte3.linhas[0].iteracoes.toFixed(1) + " iterações, contra " + an.parte3.linhas[2].iteracoes.toFixed(1) + " com rô igual a 0.5. " +
  "O motivo é que o feromônio depositado nas primeiras iterações, quando a colônia ainda não sabia nada, nunca é apagado — a busca gasta dezenas de iterações só para superar o próprio reforço inicial.\n\n" +
  "A segunda é contraintuitiva e vale explicar com cuidado. Rô igual a 1 significa evaporação total: o feromônio de cada iteração é apagado inteiro. A gente esperava que isso fosse ruim, porque a colônia perde a memória de longo prazo. " +
  "Mas foi a configuração com a melhor média, " + an.parte3.linhas[4].media.toFixed(1) + ", e o menor desvio. O motivo é o beta: com beta igual a 5, a visibilidade domina a decisão e a busca já é guiada pela distância. " +
  "Perder a memória de longo prazo custa pouco justamente porque nesta configuração o feromônio nunca foi o fator principal.\n\n" +
  "A terceira é a ressalva: todas as configurações ficam muito próximas em qualidade. O que a taxa de evaporação muda de verdade, aqui, é a velocidade de convergência, não a rota final.\n\n" +
  "E vale lembrar que o rô não age sozinho: o alfa e o beta governam o mesmo equilíbrio. Com alfa 1 e beta 5, que é o que o enunciado fixa, a gente já começa bem do lado guloso da balança — e é justamente por isso que a curva sai plana. No próximo slide a gente mostra o que acontece quando o feromônio passa a importar."
);

/* ------------------------------------------------ 12 parte 3 equilibrio */
const sEq = pres.addSlide();
tituloSlide(sEq, "Parte 3 — existe uma evaporação ideal?");

const e = eq.equilibrio;
const virgula = (v) => String(v).replace(".", ",");

sEq.addImage({ path: path.join(SAIDA, "parte3_d_familia.png"), x: L, y: 1.38, w: 5.85, h: 3.51 });
sEq.addImage({ path: path.join(SAIDA, "parte3_c_equilibrio.png"), x: 6.75, y: 1.38, w: 5.85, h: 3.51 });

cartao(sEq, { x: L, y: 5.08, w: 5.85, h: 1.72 });
sEq.addText("Com β = 5 a curva é plana", {
  x: L + 0.3, y: 5.2, w: 5.3, h: 0.45,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 15.5, bold: true, color: TINTA, valign: "middle",
});
sEq.addText("A distância domina a decisão e o feromônio quase não pesa. Com β = 1 ele passa "
  + "a importar, e α decide de que lado a evaporação atrapalha.", {
  x: L + 0.3, y: 5.68, w: 5.3, h: 1.02,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
  fontFace: CORPO_FONTE, fontSize: 13.5, color: CINZA, valign: "top",
});

cartao(sEq, { x: 6.75, y: 5.08, w: 5.85, h: 1.72, fundo: ESCURO });
sEq.addText("Com α = " + virgula(e.alfa) + " e β = " + virgula(e.beta) + ": ótimo em ρ = "
  + virgula(e.rho_otimo.toFixed(2)), {
  x: 7.05, y: 5.2, w: 5.3, h: 0.45,
  isTextBox: true, margin: 0,
  fontFace: CORPO_FONTE, fontSize: 15.5, bold: true, color: AMBAR_CLARO, valign: "middle",
});
sEq.addText("ρ = 0 fica " + virgula(e.excesso_esquerda.toFixed(1))
  + " acima do ótimo e ρ = 1 fica " + virgula(e.excesso_direita.toFixed(1))
  + " acima. " + eq.execucoes + " execuções por ponto, confirmado em três conjuntos de sementes.", {
  x: 7.05, y: 5.68, w: 5.3, h: 1.02,
  isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
  fontFace: CORPO_FONTE, fontSize: 13.5, color: CLARO, valign: "top",
});

sEq.addNotes(
  "INTEGRANTE 3\n\n" +
  "Com os parâmetros que o enunciado fixa, alfa 1 e beta 5, a curva da evaporação sai praticamente plana. A pergunta natural é: existe uma taxa de evaporação ideal, ou não? Então a gente fez uma análise complementar.\n\n" +
  "A explicação para a curva plana está no beta. Com beta igual a 5, a visibilidade entra na decisão elevada à quinta potência: a distância domina, e o feromônio quase não pesa. Se o feromônio não pesa, mexer na evaporação dele também não muda nada.\n\n" +
  "O gráfico da esquerda mostra o que acontece quando a gente baixa o beta para 1, e o feromônio passa a importar. Aí o alfa decide de que lado a evaporação atrapalha. " +
  "Com alfa 1,25 só atrapalha evaporar pouco. Com alfa 2 só atrapalha evaporar demais. E com alfa 1,5 aparecem os dois efeitos ao mesmo tempo — é a curva em U.\n\n" +
  "O gráfico da direita é essa curva em detalhe. O ótimo fica em rô igual a " + virgula(e.rho_otimo.toFixed(2)) + ". " +
  "À esquerda, pouca evaporação: o feromônio das primeiras iterações, quando a colônia ainda não sabia nada, nunca é esquecido, e a busca fica presa nele. Rô igual a zero fica " + virgula(e.excesso_esquerda.toFixed(1)) + " acima do ótimo. " +
  "À direita, evaporação demais: a colônia apaga a própria memória a cada iteração e não consegue acumular aprendizado. Rô igual a um fica " + virgula(e.excesso_direita.toFixed(1)) + " acima.\n\n" +
  "Sobre o rigor: cada ponto é a média de " + eq.execucoes + " execuções, e a faixa azul é o intervalo de confiança de 95%. A gente encontrou essa configuração num conjunto de sementes e confirmou em outros dois, independentes, para ter certeza de que o U não era coincidência."
);

/* ----------------------------------------------------- 13 conclusao */
const s12 = pres.addSlide();
s12.background = { color: ESCURO };
tituloSlide(s12, "Conclusão", BRANCO);

const fim = [
  ["O ACO resolveu a instância", "Menor distância " + p1.melhor_distancia.toFixed(2)
   + ", convergindo na iteração " + p1.iteracao_convergencia
   + ", melhor que a busca 2-opt que usamos como referência (1331)."],
  ["Colônia pequena é imprevisível, não só pior", "O desvio padrão cai de "
   + an.parte2.linhas[0].desvio.toFixed(2) + " com 3 formigas para "
   + an.parte2.linhas[3].desvio.toFixed(2) + " com 20."],
  ["Menos iterações não significa menos trabalho", "O custo real é formigas × iterações. Colônias grandes convergem antes e gastam mais."],
  ["A evaporação tem um ponto ótimo — quando o feromônio importa", "Com os parâmetros do enunciado a curva é plana; com α = "
   + virgula(eq.equilibrio.alfa) + " e β = " + virgula(eq.equilibrio.beta) + " o ótimo aparece em ρ = "
   + virgula(eq.equilibrio.rho_otimo.toFixed(2)) + ": pouca evaporação prende, evaporação demais apaga a memória."],
];
fim.forEach((f, i) => {
  const y = 1.5 + i * 1.3;
  circulo(s12, L, y, String(i + 1), i === 3 ? AMBAR : "3C332C", BRANCO);
  s12.addText(f[0], {
    x: L + 0.68, y: y - 0.05, w: 11.0, h: 0.45,
    isTextBox: true, margin: 0,
    fontFace: CORPO_FONTE, fontSize: 17.5, bold: true, color: BRANCO, valign: "middle",
  });
  s12.addText(f[1], {
    x: L + 0.68, y: y + 0.42, w: 11.0, h: 0.68,
    isTextBox: true, margin: 0, lineSpacingMultiple: 1.12,
    fontFace: CORPO_FONTE, fontSize: 14.5, color: CLARO, valign: "top",
  });
});

s12.addText("Obrigado. Perguntas?", {
  x: L, y: 6.75, w: LARG, h: 0.45,
  isTextBox: true, margin: 0,
  fontFace: TITULO_FONTE, fontSize: 19, bold: true, color: AMBAR_CLARO, valign: "middle",
});

s12.addNotes(
  "INTEGRANTE 3 (fechamento)\n\n" +
  "Fechando com quatro pontos.\n\n" +
  "Primeiro: o ACO resolveu a instância. A menor distância foi " + p1.melhor_distancia.toFixed(2) + ", com convergência na iteração " + p1.iteracao_convergencia + ". E a gente comparou com uma busca 2-opt, que é uma heurística forte de referência: o 2-opt chegou em 1331, e o ACO chegou em 1328, ou seja, melhor.\n\n" +
  "Segundo: colônia pequena não é só pior, é imprevisível. O desvio padrão cai de " + an.parte2.linhas[0].desvio.toFixed(2) + " com 3 formigas para " + an.parte2.linhas[3].desvio.toFixed(2) + " com 20.\n\n" +
  "Terceiro, e é o ponto que a gente acha mais interessante: menos iterações não significa menos trabalho. O custo real é formigas vezes iterações, e por essa métrica a colônia grande sai mais cara.\n\n" +
  "Quarto: a evaporação tem um ponto ótimo, mas ele só aparece quando o feromônio importa na decisão. Com os parâmetros do enunciado a curva é plana; com alfa " + virgula(eq.equilibrio.alfa) + " e beta " + virgula(eq.equilibrio.beta) + " o ótimo aparece em rô igual a " + virgula(eq.equilibrio.rho_otimo.toFixed(2)) + ". Pouca evaporação prende a colônia no que ela aprendeu cedo demais, e evaporação demais apaga a memória antes que ela sirva para alguma coisa.\n\n" +
  "Obrigado. Estamos à disposição para perguntas."
);

pres.writeFile({ fileName: path.join(__dirname, "apresentacao.pptx") }).then((f) => {
  console.log("gerado:", f);
});
