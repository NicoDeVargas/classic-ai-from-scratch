const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const RAIZ = path.dirname(__dirname);
const IMG = path.join(__dirname, "img");
const SAIDA = path.join(RAIZ, "saida");

const p1 = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_parte1.json"), "utf-8"));
const p2 = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_parte2.json"), "utf-8"));
const ex = JSON.parse(fs.readFileSync(path.join(IMG, "extras.json"), "utf-8"));

const ESCURO = "16202E";
const TEAL = "21918C";
const TEAL_CLARO = "7AD3B5";
const AMARELO = "E8C547";
const VERMELHO = "E5483B";
const TINTA = "1F2933";
const CINZA = "5F6B76";
const CARTAO = "EEF2F4";
const BRANCO = "FFFFFF";
const CLARO = "CBD5DD";

const TITULO_FONTE = "Cambria";
const CORPO_FONTE = "Calibri";

const ALUNOS = [
  "David Lanza Melo Matos",
  "Lucca Molinari Barbosa",
  "Nicolas Rodrigues de Vargas",
];

const CORES_PAR = {
  "[0, 1]": "8E44AD", "[1, 0]": "7F8C8D", "[1, 1]": "2E86C1",
  "[1, 0.1]": "E67E22", "[2, 2]": "27AE60", "[4, 4]": "C0392B",
};

function v(x, casas) {
  return x.toFixed(casas).replace(".", ",");
}

const SOBRESCRITO = { "-": "⁻", "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
  "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹" };

function cientifico(x) {
  const [mantissa, expoente] = x.toExponential(1).split("e");
  const e = String(parseInt(expoente, 10)).split("").map((c) => SOBRESCRITO[c]).join("");
  return mantissa.replace(".", ",") + " × 10" + e;
}

function falado(x) {
  const [mantissa, expoente] = x.toExponential(1).split("e");
  return mantissa.replace(".", ",") + " vezes 10 elevado a menos " + Math.abs(parseInt(expoente, 10));
}

function nomePar(p) {
  return "[" + v(p.c1, p.c1 % 1 ? 1 : 0) + "; " + v(p.c2, p.c2 % 1 ? 1 : 0) + "]";
}

const PAR = {};
p2.pares.forEach((p) => { PAR[p.nome] = p; });
const N = p2.execucoes;
const CONSTR = {};
p2.constricao.forEach((c) => { CONSTR[String(c.chi)] = c; });

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Trabalho prático - PSO";
pres.title = "Otimização por Enxame de Partículas na função de Rastrigin";

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

function video(slide, arquivo, x, y, w) {
  const nome = arquivo.replace(".mp4", "");
  slide.addMedia({
    type: "video",
    path: path.join(SAIDA, arquivo),
    cover: "data:image/png;base64,"
           + fs.readFileSync(path.join(IMG, "capa_" + nome + ".png")).toString("base64"),
    x: x, y: y, w: w, h: w * 9 / 16,
  });
}

/* ------------------------------------------------------------- 1 capa */
const s1 = pres.addSlide();
s1.background = { color: ESCURO };
s1.addImage({ path: path.join(IMG, "capa.png"), x: 8.15, y: 1.15, w: 4.7, h: 4.7 });
texto(s1, "TRABALHO PRÁTICO · INTELIGÊNCIA DE ENXAMES", {
  x: L, y: 1.35, w: 7.2, h: 0.34, fontSize: 14.5, bold: true, charSpacing: 2, color: TEAL_CLARO,
  valign: "middle",
});
texto(s1, "Otimização por\nEnxame de Partículas", {
  x: L, y: 1.85, w: 7.3, h: 1.9, fontFace: TITULO_FONTE, fontSize: 42, bold: true,
  color: BRANCO, lineSpacingMultiple: 1.05,
});
texto(s1, "PSO em busca do mínimo global da função de Rastrigin (n = 2)", {
  x: L, y: 3.85, w: 7.2, h: 0.8, fontSize: 18, color: CLARO,
});
texto(s1, "ALUNOS", {
  x: L, y: 4.75, w: 7.2, h: 0.3, fontSize: 12, bold: true, charSpacing: 2, color: TEAL_CLARO,
  valign: "middle",
});
texto(s1, ALUNOS.join("\n"), {
  x: L, y: 5.1, w: 7.2, h: 1.0, fontSize: 15, color: BRANCO, lineSpacingMultiple: 1.2,
});
texto(s1, "Parte 1: f(gbest) = " + cientifico(p1.f_gbest) + " ao fim das " + p1.iteracoes
  + " iterações   ·   Parte 2: 6 pares de c1, c2 × " + N + " execuções", {
  x: L, y: 6.4, w: 11.9, h: 0.35, fontSize: 14, color: "8B9AA6", valign: "middle",
});
s1.addNotes(
  "INTEGRANTE 1 (abertura)\n\n" +
  "Bom dia. Nosso trabalho é o de Otimização por Enxame de Partículas, o PSO. O objetivo é encontrar o mínimo global da função de Rastrigin em duas dimensões.\n\n" +
  "Eu apresento o problema, a ideia do algoritmo e as escolhas da nossa implementação. Depois vem a Parte 1, com o vídeo do enxame, e o resultado da Parte 2. Por fim, a explicação de cada par de c1 e c2 com os vídeos e as conclusões.\n\n" +
  "A imagem da capa já é o algoritmo rodando: os pontos brancos são as partículas, a estrela vermelha é a melhor posição que o enxame encontrou até ali."
);

/* --------------------------------------------------------- 2 problema */
const s2 = pres.addSlide();
tituloSlide(s2, "O problema: a função de Rastrigin");
cartao(s2, { x: L, y: 1.4, w: 6.75, h: 1.05, fundo: ESCURO });
texto(s2, "f(x, y) = 20 + x² − 10·cos(2πx) + y² − 10·cos(2πy)", {
  x: L + 0.2, y: 1.4, w: 6.35, h: 1.05, fontFace: "Cambria Math", fontSize: 18, color: BRANCO,
  align: "center", valign: "middle",
});
const itens2 = [
  ["Domínio", "x e y entre −5,12 e 5,12"],
  ["Mínimo global", "f(0, 0) = 0 — é o que o enunciado pede para encontrar"],
  ["A armadilha", ex.minimos_locais + " mínimos locais, um perto de cada ponto de coordenadas inteiras"],
  ["O mais traiçoeiro", "o vizinho de (0, 0), em (±1, 0), vale " + v(ex.f_minimo_vizinho, 3)
    + " — quase zero, mas não é o global"],
];
itens2.forEach((it, i) => {
  const y = 2.75 + i * 0.95;
  s2.addShape(pres.ShapeType.rect, { x: L, y: y, w: 0.08, h: 0.72, fill: { color: i >= 2 ? VERMELHO : TEAL },
    line: { color: i >= 2 ? VERMELHO : TEAL, width: 0.5 } });
  texto(s2, it[0], { x: L + 0.28, y: y - 0.02, w: 6.4, h: 0.34, fontSize: 16, bold: true });
  texto(s2, it[1], { x: L + 0.28, y: y + 0.32, w: 6.4, h: 0.6, fontSize: 14.5, color: CINZA });
});
s2.addImage({ path: path.join(IMG, "rastrigin_contorno.png"), x: 7.75, y: 1.3, w: 4.85, h: 4.85 });
texto(s2, "Contorno da função. A cruz vermelha marca o mínimo global; cada mancha escura é um mínimo local.", {
  x: 7.75, y: 6.2, w: 4.85, h: 0.85, fontSize: 13, italic: true, color: CINZA,
});
s2.addNotes(
  "INTEGRANTE 1\n\n" +
  "A função de Rastrigin é uma função de teste clássica para algoritmos de otimização. Ela é uma parábola, x ao quadrado mais y ao quadrado, somada a um cosseno que cria ondulações por toda a superfície.\n\n" +
  "O enunciado pede n igual a 2, então são duas variáveis, x e y, cada uma entre menos 5,12 e 5,12. O mínimo global fica na origem, em (0, 0), onde a função vale exatamente zero.\n\n" +
  "O que torna o problema difícil são as ondulações: dentro do domínio existem " + ex.minimos_locais + " mínimos locais, um perto de cada ponto de coordenadas inteiras. Dá para ver na figura: cada mancha escura é um vale.\n\n" +
  "E os vales vizinhos da origem são traiçoeiros. O mínimo local em (1, 0) vale " + v(ex.f_minimo_vizinho, 3) + ". É quase zero, mas não é o global. Um algoritmo que cai ali acha que chegou e para de procurar. Essa é exatamente a armadilha que vamos ver nos vídeos."
);

/* ------------------------------------------------------------ 3 o PSO */
const s3 = pres.addSlide();
tituloSlide(s3, "Como uma partícula se move");
cartao(s3, { x: L, y: 1.35, w: LARG, h: 1.3, fundo: ESCURO });
s3.addText([
  { text: "v  ←  ", options: { color: BRANCO } },
  { text: "w·v", options: { color: AMARELO, bold: true } },
  { text: "  +  ", options: { color: BRANCO } },
  { text: "c1·r1·(pbest − x)", options: { color: TEAL_CLARO, bold: true } },
  { text: "  +  ", options: { color: BRANCO } },
  { text: "c2·r2·(gbest − x)", options: { color: "FF8A80", bold: true, breakLine: true } },
  { text: "x  ←  x + v", options: { color: BRANCO } },
], {
  x: L + 0.2, y: 1.35, w: LARG - 0.4, h: 1.3, isTextBox: true, margin: 0,
  fontFace: "Consolas", fontSize: 21, align: "center", valign: "middle",
});
const comps = [
  ["Inércia (w)", AMARELO, "A partícula tende a continuar na direção em que já vinha. No nosso código w cai de 0,9 para 0,4: passos largos no começo, curtos no fim."],
  ["Cognitivo (c1)", TEAL, "Puxa a partícula de volta para o melhor ponto que ela mesma já visitou, o pbest. É a memória individual."],
  ["Social (c2)", VERMELHO, "Puxa a partícula para o melhor ponto que o enxame inteiro já encontrou, o gbest. É a informação compartilhada."],
];
comps.forEach((c, i) => {
  const x = L + i * 4.05;
  cartao(s3, { x: x, y: 2.95, w: 3.8, h: 2.55 });
  s3.addShape(pres.ShapeType.rect, { x: x, y: 2.95, w: 3.8, h: 0.1, fill: { color: c[1] }, line: { color: c[1], width: 0.5 } });
  texto(s3, c[0], { x: x + 0.25, y: 3.2, w: 3.3, h: 0.45, fontSize: 18, bold: true });
  texto(s3, c[2], { x: x + 0.25, y: 3.72, w: 3.3, h: 1.7, fontSize: 14.5, color: CINZA });
});
texto(s3, "r1 e r2 são sorteados entre 0 e 1 a cada passo. A cada iteração: mover todas as partículas → avaliar f → atualizar pbest e gbest. Repetimos " + p1.iteracoes + " vezes.", {
  x: L, y: 5.8, w: LARG, h: 0.8, fontSize: 15, color: TINTA,
});
s3.addNotes(
  "INTEGRANTE 1\n\n" +
  "O PSO se inspira em bandos de pássaros. Cada partícula é uma posição candidata no plano, com uma velocidade. A cada iteração ela se move, e essa equação diz como a velocidade é atualizada.\n\n" +
  "São três termos. O primeiro, em amarelo, é a inércia: a partícula tende a seguir na direção em que já vinha. Nós usamos a inércia decrescente do material de aula, que começa em 0,9 e cai até 0,4. No começo os passos são largos, para explorar. No fim são curtos, para refinar.\n\n" +
  "O segundo termo, o cognitivo, puxa a partícula de volta ao melhor ponto que ela mesma já visitou, o pbest. O peso dele é o c1.\n\n" +
  "O terceiro, o social, puxa a partícula para o melhor ponto que o enxame inteiro já achou, o gbest. O peso é o c2.\n\n" +
  "O r1 e o r2 são números aleatórios entre 0 e 1, sorteados a cada passo. Eles dão a variação que impede todo mundo de andar em linha reta. A Parte 2 do trabalho é justamente sobre o que acontece quando a gente muda o equilíbrio entre c1 e c2."
);

/* ---------------------------------------------------- 4 implementacao */
const s4 = pres.addSlide();
tituloSlide(s4, "De onde vem cada escolha");
const linhas4 = [
  ["Função, domínio, dimensões", "Rastrigin, [−5,12; 5,12], n = 2", "enunciado"],
  ["Partículas · iterações", p1.particulas + " · " + p1.iteracoes + " (critério de parada)", "enunciado"],
  ["Pares de c1, c2 na Parte 2", "[0; 1] [1; 0] [1; 1] [1; 0,1] [2; 2] [4; 4]", "enunciado"],
  ["Inércia w", "cai de " + v(p1.w_max, 1) + " para " + v(p1.w_min, 1) + " em linha reta", "material de aula"],
  ["c1, c2 na Parte 1", v(p1.c1, 0) + " e " + v(p1.c2, 0), "material de aula"],
  ["Partícula saiu do domínio", "volta para a borda e tem a velocidade zerada", "material de aula"],
  ["Velocidade máxima", v(p1.vmax, 3) + " (20% da largura do domínio)", "nossa escolha"],
  ["Velocidade inicial", "sorteada entre −Vmax e +Vmax", "nossa escolha"],
  ["O que é \"convergir\"", "f(gbest) < " + v(p1.tolerancia, 2) + " ao fim das " + p1.iteracoes + " iterações", "nossa escolha"],
];
const larg4 = [3.6, 5.6, 2.7];
const y4 = 1.4;
s4.addShape(pres.ShapeType.rect, { x: L, y: y4, w: LARG, h: 0.42, fill: { color: ESCURO }, line: { color: ESCURO, width: 0.5 } });
["Item", "Valor", "De onde vem"].forEach((c, i) => {
  const x = L + larg4.slice(0, i).reduce((a, b) => a + b, 0);
  texto(s4, c, { x: x + 0.15, y: y4, w: larg4[i] - 0.3, h: 0.42, fontSize: 14.5, bold: true, color: BRANCO, valign: "middle" });
});
linhas4.forEach((linha, k) => {
  const y = y4 + 0.42 + k * 0.44;
  if (k % 2 === 0) {
    s4.addShape(pres.ShapeType.rect, { x: L, y: y, w: LARG, h: 0.44, fill: { color: CARTAO }, line: { color: CARTAO, width: 0.5 } });
  }
  linha.forEach((c, i) => {
    const x = L + larg4.slice(0, i).reduce((a, b) => a + b, 0);
    const cor = i < 2 ? TINTA : (c === "enunciado" ? TEAL : (c === "nossa escolha" ? VERMELHO : "B7791F"));
    texto(s4, c, { x: x + 0.15, y: y, w: larg4[i] - 0.3, h: 0.44, fontSize: 14, bold: i === 2,
      color: cor, valign: "middle" });
  });
});
texto(s4, "O enunciado não define \"convergir\". Escolhemos f < " + v(p1.tolerancia, 2)
  + " porque nenhum mínimo local chega perto disso: o melhor deles vale " + v(ex.f_minimo_vizinho, 3) + ".", {
  x: L, y: 5.95, w: LARG, h: 0.7, fontSize: 14.5, italic: true, color: CINZA,
});
s4.addNotes(
  "INTEGRANTE 1\n\n" +
  "Antes dos resultados, deixo claro de onde veio cada parâmetro, porque nem tudo está no enunciado.\n\n" +
  "Do enunciado vêm a função, o domínio, n igual a 2, as " + p1.particulas + " partículas, as " + p1.iteracoes + " iterações como critério de parada e os seis pares de c1 e c2 da Parte 2.\n\n" +
  "Do material de aula vêm três coisas: a inércia decrescente de 0,9 para 0,4, os valores c1 igual a c2 igual a 2 que o slide de inércia recomenda, e que usamos na Parte 1, e a regra de borda: se a partícula sai do domínio, ela volta para a borda e tem a velocidade zerada.\n\n" +
  "E três escolhas foram nossas. O material cita uma velocidade máxima mas não dá valor; usamos 20% da largura do domínio. A velocidade inicial é sorteada nessa mesma faixa. E, principalmente, o critério de convergência. O enunciado pede para contar quantas vezes houve convergência para o mínimo global, mas não diz o que isso significa. Nós consideramos que convergiu quando o melhor valor final fica abaixo de 0,01. A justificativa é que nenhum mínimo local chega perto disso: o melhor deles vale " + v(ex.f_minimo_vizinho, 3) + ". Então abaixo de 0,01 o enxame com certeza está no vale certo e já refinou a posição."
);

/* ------------------------------------------------- 5 parte 1 - video */
const s5 = pres.addSlide();
tituloSlide(s5, "Parte 1 — o enxame sobre o contorno");
video(s5, "parte1_enxame.mp4", L, 1.35, 8.5);
texto(s5, "clique para reproduzir · 16 s · c1 = c2 = 2 · semente " + p1.semente, {
  x: L, y: 6.2, w: 8.5, h: 0.3, fontSize: 12.5, italic: true, color: CINZA, align: "center",
});
cartao(s5, { x: 9.45, y: 1.35, w: 3.15, h: 2.45, fundo: ESCURO });
texto(s5, "Como ler", { x: 9.7, y: 1.5, w: 2.7, h: 0.4, fontSize: 17, bold: true, color: TEAL_CLARO });
texto(s5, "Pontos brancos: partículas\nEstrela vermelha: gbest\nCruz branca: mínimo global\nDireita: zoom que acompanha o enxame", {
  x: 9.7, y: 1.95, w: 2.75, h: 1.75, fontSize: 13.5, color: CLARO, lineSpacingMultiple: 1.2,
});
cartao(s5, { x: 9.45, y: 3.95, w: 3.15, h: 2.55 });
texto(s5, "Resultado", { x: 9.7, y: 4.1, w: 2.7, h: 0.4, fontSize: 17, bold: true });
texto(s5, "f(gbest) = " + cientifico(p1.f_gbest) + "\n\nAbaixo de " + v(p1.tolerancia, 2)
  + " a partir da iteração " + p1.iteracao_tolerancia + ".\n\nRaio do enxame: " + v(p1.raio_inicial, 1)
  + " → " + v(p1.raio_final, 2), {
  x: 9.7, y: 4.55, w: 2.75, h: 1.9, fontSize: 14, color: CINZA,
});
s5.addNotes(
  "INTEGRANTE 2\n\n" +
  "[DAR PLAY NO VÍDEO — ele está embutido no slide, é só clicar. Dura 16 segundos.]\n\n" +
  "Esse é o vídeo que a Parte 1 pede: as partículas se movendo sobre o gráfico de contorno da função, iteração por iteração.\n\n" +
  "Os pontos brancos são as " + p1.particulas + " partículas, com um rastro curto mostrando de onde vieram. A estrela vermelha é o gbest, o melhor ponto encontrado até o momento. A cruz branca marca o mínimo global, em (0, 0).\n\n" +
  "No começo as partículas estão espalhadas pelo domínio inteiro e se movem com passos largos. Aos poucos elas são puxadas para o gbest e o enxame se junta no vale central.\n\n" +
  "O painel da direita é um zoom que acompanha o gbest. Conforme o enxame se fecha, a janela vai diminuindo. No fim ela tem só 0,04 de largura, e dá para ver as partículas ainda ajustando a posição em volta do mínimo.\n\n" +
  "Embaixo estão duas curvas: o melhor valor encontrado, em escala logarítmica, e o raio do enxame, que é a maior distância entre duas partículas.\n\n" +
  "O resultado final foi f igual a " + falado(p1.f_gbest) + ", praticamente zero. O valor ficou abaixo de 0,01 na iteração " + p1.iteracao_tolerancia + "."
);

/* ------------------------------------------- 6 parte 1 - o que mostra */
const s6 = pres.addSlide();
tituloSlide(s6, "Parte 1 — explorar primeiro, refinar depois");
s6.addImage({ path: path.join(SAIDA, "parte1_instantes.png"), x: L, y: 1.3, w: LARG, h: LARG * 690 / 2520 });
const fases = [
  ["Iterações 0 a 10", "Exploração", "Partículas espalhadas, passos largos (w ≈ 0,9). f(gbest) cai de "
    + v(ex.f["0"], 1) + " para " + v(ex.f["10"], 2) + "."],
  ["Iterações 10 a 30", "O enxame se junta", "O gbest chega ao vale central e puxa os outros. Raio: "
    + v(ex.raio["10"], 1) + " → " + v(ex.raio["30"], 1) + "."],
  ["Iterações 30 a 100", "Refinamento", "Com w perto de 0,4 os passos ficam curtos. f(gbest) chega a "
    + cientifico(p1.f_gbest) + "."],
];
fases.forEach((f, i) => {
  const x = L + i * 4.05;
  cartao(s6, { x: x, y: 4.85, w: 3.8, h: 1.95 });
  texto(s6, f[0], { x: x + 0.25, y: 4.97, w: 3.3, h: 0.32, fontSize: 13, bold: true, color: TEAL });
  texto(s6, f[1], { x: x + 0.25, y: 5.28, w: 3.3, h: 0.4, fontSize: 17, bold: true });
  texto(s6, f[2], { x: x + 0.25, y: 5.72, w: 3.35, h: 1.05, fontSize: 14, color: CINZA });
});
s6.addNotes(
  "INTEGRANTE 2\n\n" +
  "Aqui estão quatro quadros do vídeo, para resumir o que aconteceu.\n\n" +
  "Na iteração 0 as partículas estão espalhadas e o melhor valor é " + v(ex.f["0"], 1) + ". Até a iteração 10 é a fase de exploração: a inércia ainda está perto de 0,9 e os passos são largos. O melhor valor já cai para " + v(ex.f["10"], 2) + ".\n\n" +
  "Entre as iterações 10 e 30, o gbest chega ao vale central e começa a puxar as outras partículas. O raio do enxame cai de " + v(ex.raio["10"], 1) + " para " + v(ex.raio["30"], 1) + ".\n\n" +
  "Da iteração 30 em diante é o refinamento. A inércia já está perto de 0,4, os passos ficam curtos e as partículas ajustam a posição em volta do mínimo. No final o valor é " + falado(p1.f_gbest) + ".\n\n" +
  "Essa sequência, explorar primeiro e refinar depois, é exatamente o que a inércia decrescente foi feita para produzir. E ela é a chave para entender a Parte 2."
);

/* -------------------------------------------- 7 parte 2 - resultado */
const s7 = pres.addSlide();
tituloSlide(s7, "Parte 2 — convergência por par de c1, c2");
s7.addImage({ path: path.join(SAIDA, "parte2_convergencias.png"), x: L, y: 1.3, w: 8.0, h: 8.0 * 5.6 / 12 });
const melhor = p2.pares.reduce((a, b) => (b.convergiu > a.convergiu ? b : a));
cartao(s7, { x: 8.95, y: 1.3, w: 3.65, h: 2.3, fundo: ESCURO });
texto(s7, "Como medimos", { x: 9.2, y: 1.45, w: 3.2, h: 0.4, fontSize: 17, bold: true, color: TEAL_CLARO });
texto(s7, "Sementes 0 a " + (N - 1) + " em todos os pares: os mesmos " + N
  + " enxames iniciais. Convergiu = f(gbest) < " + v(p2.tolerancia, 2) + " no fim.", {
  x: 9.2, y: 1.9, w: 3.25, h: 1.6, fontSize: 14, color: CLARO,
});
cartao(s7, { x: 8.95, y: 3.75, w: 3.65, h: 2.0 });
texto(s7, "É robusto?", { x: 9.2, y: 3.9, w: 3.2, h: 0.4, fontSize: 17, bold: true });
texto(s7, "Mais " + p2.turmas + " lotes de " + N
  + " execuções (barras pretas): [1; 1] e [2; 2] sempre no topo, [0; 1] no meio, os outros três sempre abaixo de 20.", {
  x: 9.2, y: 4.35, w: 3.25, h: 1.35, fontSize: 14, color: CINZA,
});
texto(s7, "Cinza claro: o gbest chegou ao vale do mínimo global (f < " + v(p2.bacia, 1)
  + "), mesmo sem refinar até 0,01.", {
  x: L, y: 5.15, w: 8.0, h: 0.6, fontSize: 13.5, italic: true, color: CINZA,
});
texto(s7, "Melhor par: " + nomePar(melhor) + ", com " + melhor.convergiu + " de " + N + ".", {
  x: L, y: 5.95, w: LARG, h: 0.5, fontSize: 19, bold: true, color: TINTA,
});
s7.addNotes(
  "INTEGRANTE 2\n\n" +
  "Na Parte 2 o enunciado pede para rodar o algoritmo " + N + " vezes com cada um dos seis pares de c1 e c2 e contar quantas vezes ele convergiu para o mínimo global.\n\n" +
  "Usamos as sementes 0 a " + (N - 1) + " para todos os pares. Isso quer dizer que os seis pares partem dos mesmos " + N + " enxames iniciais, e a única coisa que muda entre eles é o c1 e o c2.\n\n" +
  "As barras coloridas mostram quantas execuções convergiram, com o critério de f menor que 0,01. " +
  p2.pares.map((p) => "O par " + nomePar(p) + " convergiu " + p.convergiu + " vezes").join(". ") + ".\n\n" +
  "A parte cinza clara mostra outra coisa: quantas vezes o gbest pelo menos chegou ao vale do mínimo global, mesmo sem refinar até 0,01. Isso vai ser importante para o par [4; 4], que chega ao vale em " + PAR["[4, 4]"].bacia + " execuções, mas converge em só " + PAR["[4, 4]"].convergiu + ".\n\n" +
  "Para ter certeza de que não foi sorte, repetimos tudo com outros " + p2.turmas + " lotes de " + N + " execuções, com sementes diferentes. As barrinhas pretas mostram a faixa de resultados nesses lotes. Os números variam um pouco, mas os grupos não mudam: o [1; 1] e o [2; 2] ficam sempre no topo, acima de 80; o [0; 1] fica sempre no meio, perto de 50; e os outros três ficam sempre abaixo de 20.\n\n" +
  "Agora, o porquê de cada resultado, com os vídeos."
);

/* ------------------------------------------ 8 parte 2 - video grade */
const s8 = pres.addSlide();
tituloSlide(s8, "Parte 2 — seis pares, o mesmo enxame");
video(s8, "parte2_comparativo.mp4", 1.75, 1.3, 9.8);
texto(s8, "clique para reproduzir · as seis execuções partem das mesmas posições (semente " + p2.semente_video + ")", {
  x: L, y: 6.88, w: LARG, h: 0.3, fontSize: 12.5, italic: true, color: CINZA, align: "center",
});
s8.addNotes(
  "INTEGRANTE 2\n\n" +
  "[DAR PLAY NO VÍDEO — dura 16 segundos.]\n\n" +
  "Antes de olhar par por par, esse vídeo mostra os seis ao mesmo tempo. As seis execuções partem exatamente das mesmas posições iniciais. A única diferença é o c1 e o c2.\n\n" +
  "Reparem como o comportamento muda. No [0; 1], em cima à esquerda, todas as partículas se juntam num ponto só, mas fora da origem. No [1; 0] ninguém se junta. No [1; 1] e no [2; 2] o enxame se fecha em cima da cruz branca. E no [4; 4] o enxame fica agitado o tempo todo em volta do mínimo, sem parar.\n\n" +
  "Escolhemos a semente " + p2.semente_video + " para os vídeos porque nela cada par mostra o seu desfecho mais comum na tabela. A exceção é o [0; 1], que converge em cerca de metade das execuções; aqui ele mostra o modo de falha, que é o mais instrutivo."
);

/* ---------------------------------------------- pares lado a lado */
function slidePares(titulo, nomes, explicacoes, notas) {
  const s = pres.addSlide();
  tituloSlide(s, titulo);
  nomes.forEach((nome, i) => {
    const p = PAR[nome];
    const x = L + i * 6.1;
    video(s, p.video, x, 1.3, 5.8);
    const yb = 1.3 + 5.8 * 9 / 16 + 0.2;
    s.addShape(pres.ShapeType.rect, { x: x, y: yb, w: 0.09, h: 2.05, fill: { color: CORES_PAR[nome] },
      line: { color: CORES_PAR[nome], width: 0.5 } });
    s.addText([
      { text: "c1, c2 = " + nomePar(p) + "   ", options: { color: TINTA } },
      { text: p.convergiu + " de " + N, options: { color: CORES_PAR[nome] } },
    ], { x: x + 0.25, y: yb - 0.02, w: 5.5, h: 0.42, isTextBox: true, margin: 0, fontFace: CORPO_FONTE,
      fontSize: 19, bold: true, valign: "middle" });
    texto(s, explicacoes[i], { x: x + 0.25, y: yb + 0.45, w: 5.5, h: 1.6, fontSize: 14, color: CINZA });
  });
  s.addNotes(notas);
  return s;
}

const a01 = PAR["[0, 1]"], a10 = PAR["[1, 0]"], a11 = PAR["[1, 1]"], a101 = PAR["[1, 0.1]"];
const a22 = PAR["[2, 2]"], a44 = PAR["[4, 4]"];

slidePares("Só social × só cognitivo", ["[0, 1]", "[1, 0]"], [
  "Sem memória própria, todas correm para o gbest e o enxame vira um ponto (raio final mediano "
    + cientifico(a01.raio_final_mediana) + "). Se esse ponto não é a origem, ninguém sai: neste vídeo, (−0,995; 0).",
  "Sem trocar informação: são " + p1.particulas + " buscas locais independentes. O enxame nunca se junta (raio final mediano "
    + v(a10.raio_final_mediana, 1) + ") e o gbest raramente chega ao centro.",
], "INTEGRANTE 2\n\n" +
  "[DAR PLAY NOS DOIS VÍDEOS — cada um dura 16 segundos.]\n\n" +
  "Começando pelos dois extremos.\n\n" +
  "À esquerda, c1 igual a 0 e c2 igual a 1: só o termo social. Nenhuma partícula lembra do próprio melhor ponto; todas correm atrás do gbest. O resultado é que o enxame vira um ponto só. O raio final mediano é praticamente zero. Isso é a convergência prematura: o enxame converge, mas converge para onde o gbest estava, e não necessariamente para o mínimo global. Nesse vídeo ele colapsou em (−0,995; 0), o mínimo local vizinho da origem, e ficou preso ali. Como todo mundo está no mesmo ponto, não sobra ninguém para explorar. Convergiu para o global em " + a01.convergiu + " de " + N + " execuções, mais ou menos metade.\n\n" +
  "À direita, o oposto: c1 igual a 1 e c2 igual a 0. Só o termo cognitivo. Cada partícula volta para o seu próprio melhor ponto e ignora o resto do enxame. Na prática são " + p1.particulas + " buscas locais independentes, cada uma presa no vale onde começou. O enxame nunca se junta, e o raio final continua perto de " + v(a10.raio_final_mediana, 0) + ". Só converge quando alguma partícula já nasce perto da origem: " + a10.convergiu + " de " + N + "."
);

slidePares("Social fraco × equilibrado", ["[1, 0.1]", "[1, 1]"], [
  "O c2 é dez vezes menor que o c1: cada partícula fica presa ao próprio pbest e o gbest quase não puxa. "
    + "Chega ao vale central em " + a101.bacia + " execuções, mas sem tempo de refinar.",
  "Com os dois pesos iguais, o enxame se junta no vale do gbest e ainda refina. Raio final mediano "
    + v(a11.raio_final_mediana, 2) + ": juntos, mas sem colapsar num ponto.",
], "INTEGRANTE 3\n\n" +
  "[DAR PLAY NOS DOIS VÍDEOS.]\n\n" +
  "Agora dois casos intermediários.\n\n" +
  "À esquerda, c1 igual a 1 e c2 igual a 0,1. Tem componente social, mas dez vezes mais fraco que o cognitivo. O comportamento fica parecido com o do [1; 0]: cada partícula oscila em volta do próprio pbest, e o gbest puxa tão pouco que em " + p1.iteracoes + " iterações o enxame não chega a se juntar. Ele até alcança o vale central em " + a101.bacia + " execuções, mas converge até 0,01 em só " + a101.convergiu + ".\n\n" +
  "À direita, c1 e c2 iguais a 1. Aqui os dois termos têm o mesmo peso. As partículas são puxadas para o gbest, mas cada uma ainda lembra do seu melhor ponto, então o enxame não colapsa de uma vez. Ele se junta no vale central e continua refinando. Convergiu em " + a11.convergiu + " de " + N + "."
);

slidePares("Intensidade: [2; 2] × [4; 4]", ["[2, 2]", "[4, 4]"], [
  "O valor recomendado no material de aula. Passos largos o bastante para explorar e a inércia decrescente "
    + "deixa refinar no fim. O melhor dos seis pares.",
  "Chega ao vale do mínimo em " + a44.bacia + " execuções, mas converge em " + a44.convergiu
    + ": os passos são tão grandes que as partículas saltam por cima do mínimo e o enxame não assenta.",
], "INTEGRANTE 3\n\n" +
  "[DAR PLAY NOS DOIS VÍDEOS.]\n\n" +
  "Por último, a intensidade. Os dois pares são equilibrados, mas com pesos diferentes.\n\n" +
  "À esquerda, c1 e c2 iguais a 2, o valor recomendado no material de aula. Os pesos maiores dão passos mais largos no começo, então o enxame explora mais antes de se juntar, e a inércia decrescente deixa refinar no fim. Foi o melhor par: " + a22.convergiu + " de " + N + ".\n\n" +
  "À direita, c1 e c2 iguais a 4. Aqui está o caso mais interessante. O gbest chega ao vale do mínimo global em " + a44.bacia + " das " + N + " execuções, ou seja, o enxame encontra a região certa quase sempre. Mas converge em só " + a44.convergiu + ". No vídeo dá para ver: as partículas ficam pulando de um lado para o outro do mínimo. Os coeficientes são tão grandes que cada passo passa por cima do alvo, e o enxame nunca assenta. É o que o material de aula diz: valores altos de c1 e c2 mantêm a amplitude do movimento alta, e o enxame explora sem conseguir fazer a busca local."
);

/* -------------------------------------------- 12 o raio explica tudo */
const s12 = pres.addSlide();
tituloSlide(s12, "O raio do enxame explica os seis resultados");
s12.addImage({ path: path.join(SAIDA, "parte2_curvas.png"), x: 1.45, y: 1.2, w: 10.4, h: 10.4 * 5.2 / 13 });
const leituras = [
  ["Colapsa cedo", "[0; 1]", "converge rápido, mas onde o gbest estiver"],
  ["Nunca fecha", "[1; 0] · [1; 0,1] · [4; 4]", "não há busca local em volta do mínimo"],
  ["Fecha devagar", "[1; 1] · [2; 2]", "explora primeiro, refina depois"],
];
leituras.forEach((l, i) => {
  const x = L + i * 4.05;
  cartao(s12, { x: x, y: 5.5, w: 3.8, h: 1.65 });
  texto(s12, l[0], { x: x + 0.2, y: 5.6, w: 3.45, h: 0.36, fontSize: 16, bold: true });
  texto(s12, l[1], { x: x + 0.2, y: 5.96, w: 3.45, h: 0.34, fontSize: 14, bold: true, color: TEAL });
  texto(s12, l[2], { x: x + 0.2, y: 6.34, w: 3.45, h: 0.75, fontSize: 14, color: CINZA });
});
s12.addNotes(
  "INTEGRANTE 3\n\n" +
  "Esse slide junta os seis pares em duas curvas, cada uma com a mediana das " + N + " execuções. À esquerda o melhor valor encontrado; à direita o raio do enxame, que é a maior distância entre duas partículas.\n\n" +
  "O raio é o que explica tudo. O [0; 1], em roxo, é o único em que o raio despenca até quase zero: o enxame colapsa num ponto. Converge rápido, mas para onde o gbest estiver.\n\n" +
  "O [1; 0], o [1; 0,1] e o [4; 4] fazem o contrário: o raio nunca fecha. Nos dois primeiros, porque ninguém é puxado para o gbest. No [4; 4], porque os passos são grandes demais. Em todos eles não há uma busca local em volta do mínimo, e por isso a curva da esquerda não desce até 0,01.\n\n" +
  "O [1; 1] e o [2; 2] ficam no meio: o raio fecha devagar. O enxame explora enquanto está aberto e refina quando se fecha. São os dois pares que mais convergem.\n\n" +
  "Tem um detalhe curioso na curva da esquerda: quando acerta, o [1; 1], em azul, refina mais rápido que o [2; 2], em verde. Mas o [2; 2] acerta mais vezes, " + a22.convergiu + " contra " + a11.convergiu + ". Os passos maiores do [2; 2] custam precisão no fim, mas fazem o enxame explorar mais antes de se fechar, e isso evita cair no vale errado.\n\n" +
  "A conclusão é que o PSO precisa das duas coisas: um puxão social para juntar o enxame e uma memória individual que segure a diversidade por tempo suficiente."
);

/* ------------------------------------------------ 13 extra constricao */
const s13 = pres.addSlide();
tituloSlide(s13, "Extra: dá para salvar o [4; 4]?");
s13.addImage({ path: path.join(SAIDA, "parte2_constricao.png"), x: L, y: 1.3, w: 8.0, h: 4.0 });
const melhorChi = p2.constricao.reduce((a, b) => (b.convergiu > a.convergiu ? b : a));
cartao(s13, { x: 8.95, y: 1.3, w: 3.65, h: 1.95, fundo: ESCURO });
texto(s13, "A pergunta da aula", { x: 9.2, y: 1.45, w: 3.2, h: 0.4, fontSize: 17, bold: true, color: TEAL_CLARO });
texto(s13, "\"Há como amortecer a velocidade das partículas para valores mais altos de c1 e c2?\"", {
  x: 9.2, y: 1.9, w: 3.25, h: 1.25, fontSize: 14, italic: true, color: CLARO,
});
const depois = p2.constricao.filter((c) => c.chi < melhorChi.chi);
cartao(s13, { x: 8.95, y: 3.4, w: 3.65, h: 1.95 });
texto(s13, "A resposta", { x: 9.2, y: 3.52, w: 3.2, h: 0.4, fontSize: 17, bold: true });
texto(s13, "Sim. Com χ = " + v(melhorChi.chi, 1) + ", o [4; 4] passa de " + CONSTR["1"].convergiu
  + " para " + melhorChi.convergiu + " de " + N + ". Depois do ideal, volta a cair: "
  + depois.map((c) => c.convergiu).join(" → ") + ".", {
  x: 9.2, y: 3.95, w: 3.25, h: 1.35, fontSize: 14, color: CINZA,
});
texto(s13, "O fator de constrição χ multiplica a nova velocidade inteira: v ← χ·(w·v + c1·r1·(pbest − x) + c2·r2·(gbest − x)). "
  + "Fora do pedido do enunciado: mesmas " + N + " sementes, só o χ muda.", {
  x: L, y: 5.55, w: LARG, h: 0.9, fontSize: 14, color: CINZA,
});
s13.addNotes(
  "INTEGRANTE 3\n\n" +
  "Isso aqui foi além do enunciado. O material de aula faz uma pergunta logo depois da análise de c1 e c2: há como amortecer a velocidade das partículas para valores mais altos de c1 e c2? E a resposta da aula é o fator de constrição.\n\n" +
  "Nós testamos no nosso pior caso, o [4; 4]. O fator de constrição, chamado de qui, multiplica a nova velocidade inteira. Com qui igual a 1 é o algoritmo original. Rodamos as mesmas " + N + " sementes, mudando só o qui.\n\n" +
  "Sem constrição, o [4; 4] converge " + CONSTR["1"].convergiu + " vezes. Com qui igual a " + v(melhorChi.chi, 1) + ", converge " + melhorChi.convergiu + " vezes. Ou seja, os mesmos coeficientes altos passam a funcionar quando a velocidade é amortecida: as partículas continuam explorando bem no começo, mas agora conseguem assentar no mínimo.\n\n" +
  "E existe um ponto ideal: depois dele, amortecer mais volta a atrapalhar. Testamos mais dois valores além do 0,5 para confirmar a queda: com qui igual a " + depois.map((c) => v(c.chi, 1)).join(", ") + " o [4; 4] converge " + depois.map((c) => c.convergiu).join(", ") + " vezes. A queda continua.\n\n" +
  "O motivo é o mesmo do par [0; 1]: com a velocidade amortecida demais, o enxame colapsa num ponto cedo demais. Com qui igual a 0,3 o raio final do enxame fica em torno de " + falado(CONSTR["0.3"].raio_final_mediana) + ", ou seja, todas as partículas no mesmo lugar. Se esse lugar não for o mínimo global, ninguém sai dali."
);

/* ------------------------------------------- 14 extra constricao video */
const vc = p2.video_constricao;
const sV = pres.addSlide();
tituloSlide(sV, "Extra: sem ajuste, ajuste ideal e ajuste demais");
video(sV, "parte2_constricao.mp4", 1.55, 1.25, 10.25);
texto(sV, "clique para reproduzir · c1 = c2 = 4 nos três · mesmo enxame inicial (semente " + vc.semente + ")", {
  x: L, y: 7.05, w: LARG, h: 0.3, fontSize: 12.5, italic: true, color: CINZA, align: "center",
});
const vcs = vc.casos;
sV.addNotes(
  "INTEGRANTE 3\n\n" +
  "[DAR PLAY NO VÍDEO — dura 16 segundos.]\n\n" +
  "Esse vídeo mostra o mesmo [4; 4] três vezes, partindo exatamente das mesmas posições. Só o qui muda.\n\n" +
  "À esquerda, sem constrição: as partículas ficam pulando de um vale para o outro em volta do mínimo e nunca assentam. O raio do enxame termina em " + v(vcs[0].raio_final, 1) + ".\n\n" +
  "No meio, com qui igual a " + v(vcs[1].chi, 1) + ": o enxame explora no começo, se junta no vale central e refina. Termina praticamente no mínimo global.\n\n" +
  "À direita, com qui igual a " + v(vcs[2].chi, 1) + ": o amortecimento é tão forte que o enxame colapsa num ponto logo nas primeiras iterações. Reparem que na iteração 12 ele já está todo junto. E ele colapsou no vale errado, com f igual a " + v(vcs[2].f_gbest, 3) + ", então fica preso ali até o fim.\n\n" +
  "Embaixo de cada painel está quantas vezes cada configuração converge nas " + N + " execuções: " + CONSTR["1"].convergiu + ", " + CONSTR[String(vcs[1].chi)].convergiu + " e " + CONSTR[String(vcs[2].chi)].convergiu + ". Escolhemos a semente " + vc.semente + " para o vídeo porque é a primeira em que os três mostram o desfecho mais comum de cada um."
);

/* ------------------------------------------------------ 15 conclusoes */
const s14 = pres.addSlide();
s14.background = { color: ESCURO };
texto(s14, "Conclusões", { x: L, y: 0.45, w: LARG, h: 0.85, fontFace: TITULO_FONTE, fontSize: 32, bold: true, color: BRANCO, valign: "middle" });
const concl = [
  ["Parte 1", "O PSO com c1 = c2 = 2 encontrou o mínimo global: f = " + cientifico(p1.f_gbest) + " em " + p1.iteracoes + " iterações, com " + p1.particulas + " partículas."],
  ["Social demais", "[0; 1] converge cedo e às vezes no lugar errado: " + a01.convergiu + " de " + N + "."],
  ["Social de menos", "[1; 0] e [1; 0,1] nunca juntam o enxame: " + a10.convergiu + " e " + a101.convergiu + " de " + N + "."],
  ["Equilíbrio", "[1; 1] e [2; 2] exploram e depois refinam: " + a11.convergiu + " e " + a22.convergiu + " de " + N + "."],
  ["Intensidade demais", "[4; 4] acha a região, mas não assenta: " + a44.convergiu + " de " + N + ". A constrição corrige: " + melhorChi.convergiu + "."],
];
concl.forEach((c, i) => {
  const y = 1.55 + i * 1.0;
  texto(s14, c[0], { x: L, y: y, w: 2.9, h: 0.8, fontSize: 17, bold: true, color: TEAL_CLARO, valign: "middle" });
  texto(s14, c[1], { x: L + 3.0, y: y, w: 8.9, h: 0.8, fontSize: 16, color: BRANCO, valign: "middle" });
});
texto(s14, "Obrigado!", { x: L, y: 6.6, w: LARG, h: 0.5, fontSize: 18, bold: true, color: AMARELO });
s14.addNotes(
  "INTEGRANTE 3\n\n" +
  "Para fechar.\n\n" +
  "Na Parte 1, o PSO com c1 e c2 iguais a 2 encontrou o mínimo global, com valor praticamente zero, usando " + p1.particulas + " partículas e " + p1.iteracoes + " iterações.\n\n" +
  "Na Parte 2, o que aprendemos é que o PSO depende do equilíbrio entre o individual e o coletivo. Social demais, como no [0; 1], o enxame converge cedo e às vezes no lugar errado. Social de menos, como no [1; 0] e no [1; 0,1], o enxame nunca se junta. Com equilíbrio, no [1; 1] e no [2; 2], ele explora primeiro e refina depois, e é aí que estão os melhores resultados.\n\n" +
  "E a intensidade também importa: com c1 e c2 iguais a 4, o enxame encontra a região certa, mas não consegue assentar. O fator de constrição resolve isso.\n\n" +
  "Obrigado. Estamos à disposição para perguntas."
);

pres.writeFile({ fileName: path.join(__dirname, "apresentacao.pptx") }).then((f) => {
  console.log("gerado:", f);
});
