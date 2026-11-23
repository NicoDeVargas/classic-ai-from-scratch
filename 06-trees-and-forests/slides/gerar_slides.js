const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");

const RAIZ = path.dirname(__dirname);
const IMG = path.join(__dirname, "img");
const SAIDA = path.join(RAIZ, "saida");

const tr = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_trabalho.json"), "utf-8"));
const ext = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_extras.json"), "utf-8"));
const vid = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_videos.json"), "utf-8"));
const conf = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_confere.json"), "utf-8"));
const fech = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_fechamento.json"), "utf-8"));
const folga = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_folga.json"), "utf-8"));
const torto = JSON.parse(fs.readFileSync(path.join(SAIDA, "resumo_alvo_torto.json"), "utf-8"));

const ESCURO = "152C43";
const DESTAQUE = "75BFB4";
const VERDE = "3F9E92";
const VERMELHO = "152C43";
const AZUL = "4F7396";
const TINTA = "152C43";
const CINZA = "5C6E80";
const CARTAO = "F1F5F7";
const BRANCO = "FFFFFF";
const CLARO = "D3DEE6";

const TITULO_FONTE = "Segoe UI Semibold";
const CORPO_FONTE = "Calibri";

const ALUNOS = [
  "David Lanza Melo Matos",
  "Lucca Molinari Barbosa",
  "Nicolas Rodrigues de Vargas",
];

function v(x, casas) {
  return x.toFixed(casas === undefined ? 1 : casas).replace(".", ",");
}

const p1 = tr.parte1;
const p2 = tr.parte2;
const pa = tr.parte3_arvore;
const pf = tr.parte3_floresta;
const p4 = tr.parte4;
const ma = tr.melhor_arvore;
const mf = tr.melhor_floresta;
const raiz = ext.raiz;
const cortes = raiz.cortes.slice().sort((a, b) => b.reducao - a.reducao);
const mod = ext.modelos;
const modelo = (trecho) => mod.find((m) => m.nome.includes(trecho)).media;
const imp = ext.importancia_ordem;
const va = vid.arvore;
const vf = vid.floresta;
const minF = Math.min(...pf.slice(4).map((s) => s.media_teste));
const maxF = Math.max(...pf.slice(4).map((s) => s.media_teste));

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.author = "Trabalho prático - Árvore de decisão";
pres.title = "Árvores de regressão e floresta aleatória no dataset Diabetes";

const L = 0.7;
const LARG = 11.9;

function tituloSlide(slide, texto) {
  slide.addText(texto, {
    x: L, y: 0.38, w: LARG, h: 0.85,
    isTextBox: true, margin: 0,
    fontFace: TITULO_FONTE, fontSize: 28, color: TINTA, valign: "middle",
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

function topicos(slide, itens, x, y, w, passo) {
  itens.forEach((l, i) => {
    const yy = y + i * passo;
    faixa(slide, x, yy, passo - 0.2, l[0]);
    texto(slide, l[1], { x: x + 0.28, y: yy, w: w - 0.28, h: 0.38, fontSize: 15.5, bold: true });
    texto(slide, l[2], { x: x + 0.28, y: yy + 0.4, w: w - 0.28, h: passo - 0.65, fontSize: 13.5, color: CINZA });
  });
}

function rodape(slide, t, y) {
  cartao(slide, { x: L, y: y, w: LARG, h: 7.2 - y, fundo: ESCURO });
  texto(slide, t, { x: L + 0.3, y: y, w: LARG - 0.6, h: 7.2 - y, fontSize: 14.5, color: CLARO, valign: "middle" });
}

function numeroGrande(slide, x, y, w, rotulo, valor, sub, corRotulo) {
  cartao(slide, { x: x, y: y, w: w, h: 1.9, fundo: ESCURO });
  texto(slide, rotulo, { x: x, y: y + 0.15, w: w, h: 0.3, fontSize: 11.5, bold: true, charSpacing: 1.5, color: corRotulo || DESTAQUE, align: "center" });
  texto(slide, valor, { x: x, y: y + 0.5, w: w, h: 0.75, fontSize: 30, color: BRANCO, align: "center", fontFace: TITULO_FONTE });
  texto(slide, sub, { x: x, y: y + 1.3, w: w, h: 0.4, fontSize: 13, color: CLARO, align: "center" });
}

function tabelaExemplos(slide, x, y, w, comFloresta) {
  const colunas = comFloresta ? ["paciente", "real", "árvore", "floresta"] : ["paciente", "real", "previsto"];
  const lc = w / colunas.length;
  slide.addShape(pres.ShapeType.rect, { x: x, y: y, w: w, h: 0.4, fill: { color: ESCURO }, line: { color: ESCURO, width: 0.5 } });
  colunas.forEach((c, i) => texto(slide, c, { x: x + i * lc, y: y, w: lc, h: 0.4, fontSize: 13, bold: true, color: BRANCO, align: "center", valign: "middle" }));
  tr.exemplos1.forEach((e, k) => {
    const yy = y + 0.4 + k * 0.38;
    if (k % 2 === 0) {
      slide.addShape(pres.ShapeType.rect, { x: x, y: yy, w: w, h: 0.38, fill: { color: CARTAO }, line: { color: CARTAO, width: 0.5 } });
    }
    const linha = ["nº " + e.indice, v(e.real, 0), v(e.previsto, 0)].concat(comFloresta ? [v(tr.exemplos2[k].previsto, 0)] : []);
    linha.forEach((c, i) => texto(slide, c, { x: x + i * lc, y: yy, w: lc, h: 0.38, fontSize: 13.5, align: "center", valign: "middle",
      bold: i === 1, color: i === 0 ? CINZA : TINTA }));
  });
}

/* ------------------------------------------------------------- 1 capa */
const s1 = pres.addSlide();
s1.addImage({ path: path.join(IMG, "logo.png"), x: L, y: 0.55, w: 2.75, h: 2.75 * 83 / 221 });
s1.addImage({ path: path.join(IMG, "capa.png"), x: 7.95, y: 1.0, w: 4.65, h: 4.65 });
s1.addShape(pres.ShapeType.rect, { x: L, y: 2.2, w: 0.9, h: 0.07, fill: { color: DESTAQUE }, line: { color: DESTAQUE, width: 0.5 } });
texto(s1, "Árvores de regressão\ne floresta aleatória", {
  x: L, y: 2.45, w: 7.0, h: 1.75, fontFace: TITULO_FONTE, fontSize: 40, color: TINTA, lineSpacingMultiple: 1.02,
});
texto(s1, "Prevendo a progressão do diabetes: de uma árvore que decora os dados a uma floresta que generaliza", {
  x: L, y: 4.25, w: 6.4, h: 0.8, fontSize: 17, color: CINZA,
});
texto(s1, "Inteligência Artificial, trabalho prático de árvore de decisão", {
  x: L, y: 5.3, w: 7.0, h: 0.3, fontSize: 13, bold: true, color: VERDE, valign: "middle",
});
texto(s1, ALUNOS.join("\n"), {
  x: L, y: 5.65, w: 7.0, h: 1.0, fontSize: 15, color: TINTA, lineSpacingMultiple: 1.2,
});
s1.addNotes(
  "INTEGRANTE 1 (abertura)\n\n" +
  "Bom dia. Este é o nosso último trabalho, sobre árvores de decisão. Usamos árvores de regressão e floresta aleatória para prever a progressão do diabetes, no mesmo dataset do trabalho passado.\n\n" +
  "Eu apresento o problema, como uma árvore decide, como ela aprende e o resultado da Parte 1. Depois vêm a floresta aleatória, com dois vídeos, e o efeito da profundidade. Por fim, o número de árvores, três extras e as conclusões.\n\n" +
  "A imagem da capa é o que uma floresta aprende: um mapa suave feito da média de cem árvores."
);

/* --------------------------------------------------------- 2 problema */
const s2 = pres.addSlide();
tituloSlide(s2, "O problema: prever um número");
topicos(s2, [
  [CINZA, "O mesmo dataset", tr.n + " pacientes e 10 medidas: idade, sexo, IMC, pressão e 6 exames de sangue."],
  [AZUL, "Agora é regressão", "No trabalho passado, a pergunta era acima ou abaixo da média. Agora o modelo prevê o próprio valor da progressão, de " + v(tr.min_target, 0) + " a " + v(tr.max_target, 0) + "."],
  [DESTAQUE, "A métrica: MAE", "O erro médio absoluto: em média, por quantos pontos a previsão erra. Quanto menor, melhor."],
  [VERDE, "O teste", "80% dos pacientes treinam (" + tr.n_treino + ") e 20% testam (" + tr.n_teste + "), em 10 divisões diferentes."],
], L, 1.4, 6.6, 1.2);
cartao(s2, { x: 7.7, y: 1.4, w: 4.9, h: 4.6, fundo: ESCURO });
texto(s2, "UMA RÉGUA PARA COMPARAR", { x: 7.95, y: 1.6, w: 4.4, h: 0.3, fontSize: 12, bold: true, charSpacing: 2, color: DESTAQUE });
texto(s2, v(modelo("sempre a média")), { x: 7.95, y: 2.0, w: 4.4, h: 1.0, fontSize: 50, color: BRANCO, fontFace: TITULO_FONTE });
texto(s2, "é o MAE de quem não usa nenhum exame e prevê sempre a média do treino, que fica perto de " + v(tr.media_target, 0) + ".", {
  x: 7.95, y: 3.15, w: 4.4, h: 1.2, fontSize: 15, color: CLARO,
});
texto(s2, "Um modelo só vale a pena se errar menos do que isso.", {
  x: 7.95, y: 4.6, w: 4.4, h: 0.9, fontSize: 15, bold: true, color: BRANCO,
});
rodape(s2, "O enunciado não proíbe bibliotecas, mas escrevemos a árvore e a floresta do zero, só com numpy, e conferimos com o scikit-learn.", 6.25);
s2.addNotes(
  "INTEGRANTE 1\n\n" +
  "O dataset é o mesmo do trabalho de Naive Bayes: " + tr.n + " pacientes, com dez medidas de cada um.\n\n" +
  "A diferença é a pergunta. No trabalho passado a gente só dizia se a doença ia progredir acima ou abaixo da média. Agora é regressão: o modelo tem que prever o próprio número, que vai de " + v(tr.min_target, 0) + " a " + v(tr.max_target, 0) + ".\n\n" +
  "A métrica é o MAE, o erro médio absoluto: em média, por quantos pontos a previsão erra. Quanto menor, melhor. Como sempre, 80% dos pacientes treinam o modelo e 20% ficam para o teste, em dez divisões diferentes.\n\n" +
  "Para ter uma régua: quem não usa exame nenhum e prevê sempre a média erra " + v(modelo("sempre a média")) + " pontos. Guardem esse número, ele vai ser útil daqui a pouco.\n\n" +
  "O enunciado não proíbe bibliotecas, mas nós escrevemos a árvore e a floresta do zero, para entender cada passo, e conferimos com o scikit-learn."
);

/* ------------------------------------------------------ 3 como decide */
const s3 = pres.addSlide();
tituloSlide(s3, "Como uma árvore decide");
imagem(s3, "arvore_desenho.png", L, 1.2, 11.9, 6.6 / 15);
rodape(s3, [
  { text: "Cada caixa branca é uma pergunta de sim ou não sobre uma medida. ", options: { bold: true, color: BRANCO } },
  { text: "O paciente desce até uma folha, e a previsão é a média dos pacientes de treino que caíram ali. Esta árvore tem profundidade 3: três perguntas, " + ext.arvore3.folhas + " respostas possíveis.", options: { color: CLARO } },
], 6.45);
s3.addNotes(
  "INTEGRANTE 1\n\n" +
  "Uma árvore de regressão é uma sequência de perguntas de sim ou não. Esta é uma árvore de verdade, treinada nos nossos dados, com profundidade 3.\n\n" +
  "Para prever um paciente, a gente começa no topo. A primeira pergunta é: o s5, que é o logaritmo dos triglicerídeos, é menor ou igual a " + v(ext.arvore3.limiar, 2) + "? Se sim, vai para a esquerda; se não, para a direita. Depois vem outra pergunta, sobre o IMC, e assim por diante.\n\n" +
  "Quando o paciente chega numa caixa verde, que é uma folha, a previsão é a média dos pacientes de treino que caíram naquela mesma folha.\n\n" +
  "Reparem que cada caixa mostra a média do grupo. No topo estão todos, com média 153. Só a primeira pergunta já separa um grupo de média 113 de outro de média 197. Cada pergunta deixa os grupos mais parecidos por dentro.\n\n" +
  "Com profundidade 3, são três perguntas e no máximo " + ext.arvore3.folhas + " respostas diferentes."
);

/* ------------------------------------------------------ 4 como aprende */
const s4 = pres.addSlide();
tituloSlide(s4, "Como ela escolhe a primeira pergunta");
imagem(s4, "corte_raiz.png", L, 1.2, 11.9, 6.8 / 16);
rodape(s4, [
  { text: "A árvore testa todos os cortes possíveis de todas as medidas. ", options: { bold: true, color: BRANCO } },
  { text: "Cada curva mostra quanto a variância cai em cada corte. Ganha o ponto mais alto de todos: " + raiz.vencedor + " ≤ " + v(cortes[0].limiar, 2) + ", que reduz a variância de " + v(raiz.variancia_inicial, 0) + " em " + v(cortes[0].reducao, 0) + ". O " + cortes[1].feature + " fica logo atrás.", options: { color: CLARO } },
], 6.4);
s4.addNotes(
  "INTEGRANTE 1\n\n" +
  "E como a árvore escolhe qual pergunta fazer? Ela testa todas.\n\n" +
  "Cada quadro é uma medida. O eixo horizontal são os valores onde dá para cortar, e a curva mostra quanto a variância cai se a gente dividir os pacientes naquele ponto. Variância alta quer dizer um grupo misturado; a árvore quer grupos parecidos por dentro, então procura a maior queda. É o equivalente, na regressão, ao ganho de informação que vimos em aula.\n\n" +
  "A bolinha escura é o melhor corte de cada medida. O vencedor geral, com a borda verde, é o " + raiz.vencedor + ", cortando em " + v(cortes[0].limiar, 2) + ": a variância cai " + v(cortes[0].reducao, 0) + " pontos, de um total de " + v(raiz.variancia_inicial, 0) + ". O " + cortes[1].feature + " fica logo atrás, com " + v(cortes[1].reducao, 0) + ". Já o sexo quase não reduz nada.\n\n" +
  "Escolhida a primeira pergunta, os pacientes são divididos em dois grupos, e o mesmo processo se repete dentro de cada grupo. É assim que a árvore cresce.\n\n" +
  "Um detalhe: s5 e bmi também foram as duas melhores medidas no nosso trabalho de Naive Bayes. Dois métodos bem diferentes chegaram na mesma resposta."
);

/* --------------------------------------------------------- 5 parte 1 */
const s5 = pres.addSlide();
tituloSlide(s5, "Parte 1: uma árvore sozinha");
imagem(s5, "parte1.png", L, 1.25, 7.9, 4.8 / 11);
numeroGrande(s5, 8.85, 1.3, 1.8, "MAE NO TREINO", v(p1.media_treino), "erro zero", CLARO);
numeroGrande(s5, 10.8, 1.3, 1.8, "MAE NO TESTE", v(p1.media_teste), "desvio " + v(p1.desvio_teste), "D3DEE6");
texto(s5, "5 exemplos do último modelo", { x: 8.85, y: 3.4, w: 3.75, h: 0.35, fontSize: 13.5, bold: true });
tabelaExemplos(s5, 8.85, 3.8, 3.75, false);
rodape(s5, [
  { text: "Sem limite de profundidade, a árvore decora o treino e erra " + v(p1.media_teste, 0) + " no teste. ", options: { bold: true, color: BRANCO } },
  { text: "Prever sempre a média, sem olhar exame nenhum, erra " + v(modelo("sempre a média"), 0) + ". Ela quase não ganha do chute.", options: { color: CLARO } },
], 6.2);
s5.addNotes(
  "INTEGRANTE 1\n\n" +
  "Este é o resultado da Parte 1. Treinamos uma árvore em cada uma das dez divisões, sem limite de profundidade, que é o padrão. As barras claras são o erro no treino e as escuras, no teste.\n\n" +
  "No treino o erro é zero em todas as divisões. A árvore cresce até cada paciente ficar sozinho numa folha, então ela acerta todo mundo que já viu.\n\n" +
  "No teste, o MAE médio é " + v(p1.media_teste) + ", com desvio padrão de " + v(p1.desvio_teste) + ". Os cinco exemplos mostram como ela erra: um paciente com valor real " + v(tr.exemplos1[1].real, 0) + " recebeu a previsão " + v(tr.exemplos1[1].previsto, 0) + ".\n\n" +
  "Agora lembrem da régua: prever sempre a média erra " + v(modelo("sempre a média"), 0) + ". A nossa árvore, com dez exames na mão, erra " + v(p1.media_teste, 0) + ". Quase não ganha do chute.\n\n" +
  "O motivo é que ela não aprendeu um padrão, ela decorou os pacientes. O próximo slide mostra isso acontecendo."
);

/* ------------------------------------------------- 6 video arvore */
const s6 = pres.addSlide();
tituloSlide(s6, "A árvore decorando os dados, em vídeo");
s6.addMedia({
  type: "video",
  path: path.join(SAIDA, "arvore_crescendo.mp4"),
  cover: "data:image/png;base64," + fs.readFileSync(path.join(IMG, "capa_arvore_crescendo.png")).toString("base64"),
  x: L, y: 1.25, w: 8.4, h: 8.4 * 9 / 16,
});
texto(s6, "clique para reproduzir · " + va.duracao_s + " s · árvore só com bmi e s5, para dar para desenhar", {
  x: L, y: 6.05, w: 8.4, h: 0.3, fontSize: 12.5, italic: true, color: CINZA, align: "center",
});
cartao(s6, { x: 9.35, y: 1.25, w: 3.25, h: 5.1, fundo: ESCURO });
texto(s6, "O que observar", { x: 9.6, y: 1.4, w: 2.8, h: 0.4, fontSize: 17, bold: true, color: DESTAQUE });
texto(s6, [
  "cada pergunta corta o mapa em retângulos",
  "até a profundidade " + va.melhor + ", treino e teste melhoram juntos",
  "depois o treino continua caindo e o teste sobe",
  "no fim são " + va.folhas_final + " retângulos, alguns com um paciente só",
].map((t) => "• " + t).join("\n\n"), {
  x: 9.6, y: 1.9, w: 2.85, h: 4.3, fontSize: 13.5, color: CLARO,
});
s6.addNotes(
  "INTEGRANTE 2\n\n" +
  "[DAR PLAY NO VÍDEO — ele está embutido no slide, é só clicar. Dura " + va.duracao_s + " segundos.]\n\n" +
  "Para enxergar o que a árvore faz, treinamos uma só com duas medidas, o IMC e o s5, porque assim dá para desenhar. Cada ponto é um paciente do treino, e a cor é a progressão da doença: quanto mais escura, maior a progressão. O fundo é o que a árvore prevê em cada região.\n\n" +
  "Cada pergunta da árvore é um corte reto no mapa. Com profundidade 1 são dois retângulos, com 2 são quatro, e assim vai.\n\n" +
  "Olhem o gráfico da direita. No começo, o erro de treino e o de teste caem juntos: a árvore está aprendendo o padrão geral, que é claro embaixo à esquerda e escuro em cima à direita. Mas a partir da profundidade " + va.melhor + ", o erro de treino continua caindo e o de teste começa a subir.\n\n" +
  "No fim são " + va.folhas_final + " retângulos, alguns desenhados em volta de um único paciente. A árvore parou de aprender o padrão e passou a decorar os pontos. Isso é o sobreajuste, e é por isso que ela vai mal no teste."
);

/* --------------------------------------------------- 7 ideia floresta */
const s7 = pres.addSlide();
tituloSlide(s7, "A saída: uma floresta de árvores diferentes");
const passos7 = [
  [AZUL, "1", "Sorteio dos pacientes", "Cada árvore treina com " + tr.n_treino + " pacientes sorteados com reposição: alguns se repetem e cerca de " + v(ext.fracao_fora * 100, 0) + "% ficam de fora."],
  [DESTAQUE, "2", "Sorteio das medidas", "Em cada pergunta, a árvore só pode escolher entre " + tr.k + " das 10 medidas, sorteadas na hora."],
  [VERMELHO, "3", "Árvores diferentes", "Com dados e medidas diferentes, cada árvore decora coisas diferentes e erra para um lado diferente."],
  [VERDE, "4", "A média", "A previsão da floresta é a média das " + tr.arvores + " árvores. Os erros de cada uma se cancelam."],
];
passos7.forEach((p, i) => {
  const x = L + i * 3.0;
  cartao(s7, { x: x, y: 1.5, w: 2.8, h: 3.6 });
  s7.addShape(pres.ShapeType.ellipse, { x: x + 0.25, y: 1.75, w: 0.62, h: 0.62, fill: { color: p[0] }, line: { color: p[0], width: 0.5 } });
  texto(s7, p[1], { x: x + 0.25, y: 1.75, w: 0.62, h: 0.62, fontSize: 20, bold: true, color: p[0] === DESTAQUE ? TINTA : BRANCO, align: "center", valign: "middle" });
  texto(s7, p[2], { x: x + 0.25, y: 2.55, w: 2.35, h: 0.4, fontSize: 17, bold: true });
  texto(s7, p[3], { x: x + 0.25, y: 3.0, w: 2.35, h: 2.0, fontSize: 14, color: CINZA });
});
rodape(s7, "É como consultar vários especialistas com experiências diferentes, em vez de um só: cada um erra de um jeito, e a opinião média é mais confiável.", 5.5);
s7.addNotes(
  "INTEGRANTE 2\n\n" +
  "A saída para esse problema é a floresta aleatória. A ideia é: em vez de confiar em uma árvore, treinar muitas, todas diferentes, e tirar a média.\n\n" +
  "Para as árvores saírem diferentes, a floresta usa dois sorteios. O primeiro é o dos pacientes: cada árvore treina com " + tr.n_treino + " pacientes sorteados com reposição. Alguns aparecem repetidos, e cerca de " + v(ext.fracao_fora * 100, 0) + "% ficam de fora de cada árvore.\n\n" +
  "O segundo é o das medidas: em cada pergunta, a árvore não pode olhar as dez medidas. Ela sorteia " + tr.k + " e escolhe o melhor corte só entre essas. Usamos " + tr.k + " porque é aproximadamente a raiz de 10, a regra que vimos em aula. Esse sorteio se repete a cada pergunta.\n\n" +
  "O resultado é que cada árvore decora coisas diferentes e erra para um lado diferente. Quando a gente tira a média das cem previsões, os erros se cancelam e sobra o padrão que todas enxergaram.\n\n" +
  "É a comparação do material: consultar vários especialistas com experiências diferentes em vez de um só."
);

/* --------------------------------------------------------- 8 parte 2 */
const s8 = pres.addSlide();
tituloSlide(s8, "Parte 2: a floresta aleatória");
imagem(s8, "parte2.png", L, 1.25, 7.9, 4.8 / 11);
numeroGrande(s8, 8.85, 1.3, 1.8, "UMA ÁRVORE", v(p1.media_teste), "desvio " + v(p1.desvio_teste), "D3DEE6");
numeroGrande(s8, 10.8, 1.3, 1.8, "A FLORESTA", v(p2.media_teste), "desvio " + v(p2.desvio_teste), "9FD9D0");
texto(s8, "os mesmos 5 pacientes", { x: 8.85, y: 3.4, w: 3.75, h: 0.35, fontSize: 13.5, bold: true });
tabelaExemplos(s8, 8.85, 3.8, 3.75, true);
rodape(s8, [
  { text: "O MAE de teste cai de " + v(p1.media_teste) + " para " + v(p2.media_teste) + ", " + v(100 * (1 - p2.media_teste / p1.media_teste), 0) + "% a menos, e a floresta ganha nas 10 divisões. ", options: { bold: true, color: BRANCO } },
  { text: "O erro de treino sobe de 0 para " + v(p2.media_treino) + ": ela parou de decorar.", options: { color: CLARO } },
], 6.2);
s8.addNotes(
  "INTEGRANTE 2\n\n" +
  "Este é o resultado da Parte 2: o mesmo procedimento, com uma floresta de " + tr.arvores + " árvores, nas mesmas dez divisões.\n\n" +
  "O MAE médio de teste caiu de " + v(p1.media_teste) + " para " + v(p2.media_teste) + ", com desvio padrão de " + v(p2.desvio_teste) + ". É uma redução de " + v(100 * (1 - p2.media_teste / p1.media_teste), 0) + "%, e a floresta ganhou da árvore em todas as dez divisões.\n\n" +
  "Reparem também no treino. A árvore tinha erro zero; a floresta tem " + v(p2.media_treino) + ". Parece pior, mas é um bom sinal: ela parou de decorar os pacientes.\n\n" +
  "A tabela mostra os mesmos cinco pacientes do slide da árvore. O paciente de valor real " + v(tr.exemplos1[1].real, 0) + ", para quem a árvore previu " + v(tr.exemplos1[1].previsto, 0) + ", agora recebe " + v(tr.exemplos2[1].previsto, 0) + ". A floresta não acerta todos, mas evita os erros absurdos."
);

/* ------------------------------------------------- 9 video floresta */
const s9 = pres.addSlide();
tituloSlide(s9, "A média das árvores, em vídeo");
s9.addMedia({
  type: "video",
  path: path.join(SAIDA, "floresta_media.mp4"),
  cover: "data:image/png;base64," + fs.readFileSync(path.join(IMG, "capa_floresta_media.png")).toString("base64"),
  x: L, y: 1.25, w: 8.4, h: 8.4 * 9 / 16,
});
texto(s9, "clique para reproduzir · " + vf.duracao_s + " s · floresta só com bmi e s5, para dar para desenhar", {
  x: L, y: 6.05, w: 8.4, h: 0.3, fontSize: 12.5, italic: true, color: CINZA, align: "center",
});
cartao(s9, { x: 9.35, y: 1.25, w: 3.25, h: 5.1, fundo: ESCURO });
texto(s9, "O que observar", { x: 9.6, y: 1.4, w: 2.8, h: 0.4, fontSize: 17, bold: true, color: DESTAQUE });
texto(s9, [
  "à esquerda, cada árvore sozinha: um mapa todo recortado",
  "à direita, a média das árvores: o mapa vai ficando suave",
  "sozinhas, as árvores erram " + v(vf.erro_uma, 0) + " em média",
  "juntas, erram " + v(vf.erro_100, 0) + ", e quase todo o ganho vem nas primeiras 20",
].map((t) => "• " + t).join("\n\n"), {
  x: 9.6, y: 1.9, w: 2.85, h: 4.3, fontSize: 13.5, color: CLARO,
});
s9.addNotes(
  "INTEGRANTE 2\n\n" +
  "[DAR PLAY NO VÍDEO — ele está embutido no slide, é só clicar. Dura " + vf.duracao_s + " segundos.]\n\n" +
  "Este vídeo mostra por que a média funciona, de novo com só duas medidas para dar para desenhar.\n\n" +
  "À esquerda aparece uma árvore de cada vez, sozinha. Cada uma é um mapa todo recortado, cheio de retângulos pequenos, e cada uma é recortada de um jeito diferente. À direita está a média de todas as árvores até aquele momento.\n\n" +
  "Com uma árvore, os dois mapas são iguais. Conforme as árvores entram, o mapa da direita vai ficando suave: os recortes de cada árvore, que eram manias de cada uma, somem na média, e sobra o padrão geral, que vai do claro ao escuro.\n\n" +
  "No gráfico de baixo, os pontos cinzas são o erro de cada árvore sozinha, em torno de " + v(vf.erro_uma, 0) + ". A linha verde é o erro da média, que cai para " + v(vf.erro_100, 0) + ". Nenhuma árvore sozinha é tão boa quanto o conjunto. E reparem que quase toda a queda acontece nas primeiras vinte árvores. Isso volta na Parte 4."
);

/* -------------------------------------------------------- 10 parte 3 */
const s10 = pres.addSlide();
tituloSlide(s10, "Parte 3: o efeito da profundidade");
imagem(s10, "parte3.png", L, 1.25, 8.2, 5.2 / 14);
topicos(s10, [
  [VERMELHO, "Árvore: melhor em " + ma, "MAE de " + v(pa[ma - 1].media_teste) + ". Mais funda que isso, o treino cai e o teste sobe até " + v(pa[9].media_teste) + "."],
  [VERDE, "Floresta: melhor em " + mf, "MAE de " + v(pf[mf - 1].media_teste) + ". De 5 a 10 fica entre " + v(minF) + " e " + v(maxF) + ": não piora."],
], 9.2, 1.35, 3.45, 1.55);
cartao(s10, { x: 9.2, y: 4.55, w: 3.4, h: 1.5 });
texto(s10, "A faixa colorida é o desvio padrão das 10 divisões.", { x: 9.4, y: 4.55, w: 3.0, h: 1.5, fontSize: 13.5, color: CINZA, valign: "middle" });
rodape(s10, [
  { text: "A árvore sozinha precisa ser freada. A floresta, não: ", options: { bold: true, color: BRANCO } },
  { text: "árvores fundas decoram, mas cada uma decora uma coisa, e a média cancela. A diferença entre as profundidades 5 a 10 da floresta é menor que o desvio padrão.", options: { color: CLARO } },
], 6.3);
s10.addNotes(
  "INTEGRANTE 2\n\n" +
  "Na Parte 3 variamos a profundidade máxima de 1 a 10, com dez divisões para cada valor. O enunciado pede isso para a árvore; nós fizemos também para a floresta, para comparar. A linha clara é o treino, a escura é o teste, e a faixa em volta é o desvio padrão.\n\n" +
  "À esquerda, uma árvore sozinha. O erro de treino só cai, até chegar perto de zero. O erro de teste cai até a profundidade " + ma + ", onde chega a " + v(pa[ma - 1].media_teste) + ", e depois sobe sem parar, até " + v(pa[9].media_teste) + ". É o mesmo formato do vídeo: a partir de certo ponto, mais profundidade é só decoreba. Com apenas " + ma + " perguntas, a árvore erra bem menos do que a árvore sem limite da Parte 1.\n\n" +
  "À direita, a floresta. O comportamento é outro: o erro de teste cai e depois fica parado. O melhor valor é na profundidade " + mf + ", com " + v(pf[mf - 1].media_teste) + ", mas de 5 a 10 ele fica entre " + v(minF) + " e " + v(maxF) + ". Essa diferença é bem menor que o desvio padrão, então não dá para dizer que 6 é melhor que 10.\n\n" +
  "A conclusão é que a árvore sozinha precisa ser freada, e a floresta não. As árvores fundas da floresta decoram, mas cada uma decora uma coisa diferente, e a média cancela."
);

/* -------------------------------------------------------- 11 parte 4 */
const s11 = pres.addSlide();
tituloSlide(s11, "Parte 4: quantas árvores?");
imagem(s11, "parte4.png", L, 1.25, 7.9, 5 / 11);
topicos(s11, [
  [VERMELHO, "De 5 para 20 árvores", "O MAE de teste cai de " + v(p4[0].media_teste) + " para " + v(p4[2].media_teste) + "."],
  [DESTAQUE, "De 20 para 80 árvores", "Cai só de " + v(p4[2].media_teste) + " para " + v(p4[4].media_teste) + ": quatro vezes mais árvores, " + v(p4[2].media_teste - p4[4].media_teste) + " ponto de ganho."],
  [VERDE, "O desvio também cai", "De " + v(p4[0].desvio_teste) + " para " + v(p4[4].desvio_teste) + ": com mais árvores o resultado depende menos da sorte."],
], 8.9, 1.35, 3.75, 1.4);
rodape(s11, "Profundidade fixada em " + mf + ", a melhor da floresta na Parte 3. Mais árvores nunca pioram, mas o ganho vai acabando, e o custo de treinar cresce na mesma proporção.", 5.9);
s11.addNotes(
  "INTEGRANTE 2\n\n" +
  "Na Parte 4 fixamos a profundidade em " + mf + ", que foi a melhor da floresta na Parte 3, e variamos o número de árvores: 5, 10, 20, 40 e 80. De novo, dez divisões para cada valor.\n\n" +
  "O erro de teste cai rápido no começo: de " + v(p4[0].media_teste) + " com 5 árvores para " + v(p4[2].media_teste) + " com 20. Depois quase para: com 80 árvores, chega a " + v(p4[4].media_teste) + ". Quatro vezes mais árvores para ganhar " + v(p4[2].media_teste - p4[4].media_teste) + " ponto.\n\n" +
  "É o que o vídeo da floresta já mostrava: a maior parte do ganho vem nas primeiras árvores. Depois, cada árvore nova muda pouco a média.\n\n" +
  "O desvio padrão também cai, de " + v(p4[0].desvio_teste) + " para " + v(p4[4].desvio_teste) + ". Com poucas árvores, o resultado depende da sorte de quais árvores saíram; com muitas, fica estável.\n\n" +
  "Então mais árvores nunca pioram, mas o custo de treinar cresce na mesma proporção. Aqui, algo entre 20 e 40 já seria suficiente."
);

/* ------------------------------------------------ 12 extra: sacola */
const s12 = pres.addSlide();
tituloSlide(s12, "Extra: um teste que vem de graça");
imagem(s12, "extra_fora_da_sacola.png", L, 1.25, 7.2, 5 / 8.6);
topicos(s12, [
  [DESTAQUE, "Quem ficou fora da sacola", "Cada árvore deixa de fora uns " + v(ext.fracao_fora * 100, 0) + "% dos pacientes do treino. Para essa árvore, eles são pacientes novos."],
  [VERDE, "A estimativa", "Cada paciente é previsto só pelas árvores que nunca o viram. Isso dá um MAE de " + v(ext.fora_media) + "."],
  [AZUL, "Confere com o teste", "O MAE medido no conjunto de teste foi " + v(ext.fora_teste) + ". Diferença de " + v(Math.abs(ext.fora_media - ext.fora_teste)) + " ponto."],
], 8.2, 1.35, 4.45, 1.5);
rodape(s12, "A floresta consegue estimar o próprio erro sem separar nenhum paciente para o teste. Com poucos dados, isso deixa treinar com todo mundo.", 5.95);
s12.addNotes(
  "INTEGRANTE 3\n\n" +
  "Agora os extras, que vão além do enunciado. O primeiro é uma propriedade curiosa da floresta.\n\n" +
  "Lembram que cada árvore treina com pacientes sorteados com reposição? Por causa disso, cada árvore deixa de fora mais ou menos " + v(ext.fracao_fora * 100, 0) + "% dos pacientes do treino. Em inglês isso se chama out-of-bag, fora da sacola. Para aquela árvore, esses pacientes são novos, ela nunca viu.\n\n" +
  "Então dá para fazer um teste sem conjunto de teste: cada paciente do treino é previsto só pelas árvores que não o viram. Calculamos o MAE dessas previsões nas dez divisões: a média foi " + v(ext.fora_media) + ".\n\n" +
  "E o MAE medido de verdade, no conjunto de teste, foi " + v(ext.fora_teste) + ". A diferença é de " + v(Math.abs(ext.fora_media - ext.fora_teste)) + " ponto. Divisão por divisão os valores variam, mas na média a estimativa bate.\n\n" +
  "Ou seja, a floresta consegue estimar o próprio erro de graça. Num dataset pequeno como este, isso permitiria treinar com todos os pacientes, sem separar 20% para o teste."
);

/* --------------------------------------------- 13 extra: por dentro */
const s13 = pres.addSlide();
tituloSlide(s13, "Extra: por dentro da floresta");
imagem(s13, "extra_importancia.png", L, 1.25, 5.85, 5 / 8.6);
imagem(s13, "extra_k.png", 6.75, 1.25, 5.85, 5 / 8.6);
texto(s13, "Quais medidas a floresta mais usa", { x: L, y: 4.7, w: 5.85, h: 0.35, fontSize: 14.5, bold: true, align: "center" });
texto(s13, "Quantas medidas sortear em cada pergunta", { x: 6.75, y: 4.7, w: 5.85, h: 0.35, fontSize: 14.5, bold: true, align: "center" });
rodape(s13, [
  { text: imp[0] + ", " + imp[1] + " e " + imp[2] + " respondem por " + v((ext.importancia[imp[0]] + ext.importancia[imp[1]] + ext.importancia[imp[2]]) * 100, 0) + "% do trabalho da floresta: ", options: { bold: true, color: BRANCO } },
  { text: "as mesmas três melhores do Naive Bayes. Já o sorteio de medidas rende pouco aqui: sortear 3, 5 ou as 10 dá entre " + v(Math.min(ext.ks[1].media, ext.ks[2].media, ext.ks[3].media)) + " e " + v(Math.max(ext.ks[1].media, ext.ks[2].media, ext.ks[3].media)) + ". Com só 10 medidas, o sorteio dos pacientes já basta.", options: { color: CLARO } },
], 5.3);
s13.addNotes(
  "INTEGRANTE 3\n\n" +
  "O segundo extra olha a floresta por dentro, com duas perguntas.\n\n" +
  "À esquerda: quais medidas a floresta mais usa? Somamos, em todas as árvores, quanto cada medida reduziu a variância. O " + imp[0] + " e o " + imp[1] + " respondem por " + v(ext.importancia[imp[0]] * 100, 0) + "% e " + v(ext.importancia[imp[1]] * 100, 0) + "%, e o " + imp[2] + " vem em terceiro. São exatamente as três melhores features do nosso trabalho de Naive Bayes, na mesma ordem. Dois métodos completamente diferentes concordam sobre o que importa nesses dados.\n\n" +
  "À direita: o sorteio de medidas faz diferença? Testamos sortear 1, 3, 5 ou as 10 medidas em cada pergunta, em " + ext.divisoes + " divisões. Sortear as 10 é o mesmo que não sortear: é só o bagging, sem a parte aleatória das features.\n\n" +
  "O resultado é que sortear 3, 5 ou 10 dá praticamente o mesmo erro, entre " + v(Math.min(ext.ks[1].media, ext.ks[2].media, ext.ks[3].media)) + " e " + v(Math.max(ext.ks[1].media, ext.ks[2].media, ext.ks[3].media)) + ". Só sortear uma medida piora, para " + v(ext.ks[0].media) + ", porque aí a árvore não escolhe nada.\n\n" +
  "Então, sendo honestos: neste dataset, o ganho da floresta vem quase todo do sorteio dos pacientes e da média. O sorteio de medidas ajuda mais quando há muitas features, e aqui são só dez."
);

/* ----------------------------------------------- 14 extra: modelos */
const s14 = pres.addSlide();
tituloSlide(s14, "Extra: a floresta é o melhor modelo?");
imagem(s14, "extra_modelos.png", L, 1.25, 7.9, 5 / 10.5);
topicos(s14, [
  [DESTAQUE, "Boosting", "Árvores pequenas em fila, cada uma corrigindo o erro das anteriores: " + v(modelo("boosting")) + ", um pouco melhor que a floresta."],
  [AZUL, "Regressão linear", "O modelo mais simples de todos ganha: " + v(modelo("linear")) + "."],
  [CINZA, "Por quê?", "Nesses dados o efeito das medidas é quase uma reta, e árvores só sabem fazer degraus. E são poucos pacientes para tantos degraus."],
], 8.9, 1.35, 3.75, 1.5);
rodape(s14, "A floresta resolve o problema da árvore, mas não é automaticamente o melhor modelo. Vale sempre comparar com o mais simples.", 5.95);
s14.addNotes(
  "INTEGRANTE 3\n\n" +
  "O terceiro extra é uma pergunta que a gente achou que precisava fazer: a floresta é o melhor modelo para esses dados? Comparamos sete modelos em " + ext.divisoes + " divisões.\n\n" +
  "De cima para baixo: prever sempre a média erra " + v(modelo("sempre a média")) + ". Uma árvore sem limite, " + v(modelo("sem limite")) + ". Uma árvore de profundidade 3, " + v(modelo("profundidade 3")) + ". O bagging e a floresta ficam em " + v(modelo("bagging")) + " e " + v(modelo("floresta aleatória")) + ".\n\n" +
  "Também implementamos o boosting, que o material apresenta no final: " + ext.boosting.arvores + " árvores pequenas, de profundidade " + ext.boosting.profundidade + ", treinadas em fila, cada uma tentando corrigir o erro das anteriores. Deu " + v(modelo("boosting")) + ", um pouco melhor que a floresta.\n\n" +
  "E a surpresa: a regressão linear, o modelo mais simples que existe, ganha de todos, com " + v(modelo("linear")) + ".\n\n" +
  "A explicação que encontramos é que, nesses dados, o efeito das medidas é quase uma reta: quanto maior o IMC, maior a progressão. Uma reta descreve isso com um número só. A árvore só sabe fazer degraus, e precisa de muitos degraus para imitar uma rampa, com poucos pacientes em cada um.\n\n" +
  "Então a floresta resolve o problema da árvore, mas não é automaticamente o melhor modelo. Vale sempre comparar com o mais simples."
);

/* ------------------------------------------- 15 extra: alvo torto */
const sT = pres.addSlide();
tituloSlide(sT, "Extra: e se os dados não fossem uma reta?");
const t0 = torto.linhas[0];
const t1 = torto.linhas[torto.linhas.length - 1];
imagem(sT, "alvo_torto.png", L, 1.25, 7.9, 5.6 / 11);
topicos(sT, [
  [DESTAQUE, "O teste", "Mesmos pacientes e mesmas divisões. Só o alvo é inventado, e vai de uma reta pura até degraus e curvas, com o mesmo ruído dos dados reais."],
  [AZUL, "Só reta", "A regressão linear ganha: " + v(t0.linear) + " contra " + v(t0.floresta) + ". A floresta não ganha em nenhuma das " + t0.divisoes + " divisões."],
  [VERDE, "Só degraus e curvas", "A floresta ganha: " + v(t1.floresta) + " contra " + v(t1.linear) + ", em " + t1.floresta_ganha + " das " + t1.divisoes + " divisões."],
], 8.9, 1.35, 3.75, 1.5);
rodape(sT, [
  { text: "A floresta não perdeu por ser pior: perdeu porque estes dados são quase uma reta. ", options: { bold: true, color: BRANCO } },
  { text: "Quando a relação entorta, a regressão linear piora " + v(t1.linear - t0.linear) + " e a floresta só " + v(t1.floresta - t0.floresta) + ".", options: { color: CLARO } },
], 5.95);
sT.addNotes(
  "INTEGRANTE 3\n\n" +
  "Essa derrota para a regressão linear nos incomodou, então fizemos um teste para saber se a culpa é da floresta ou dos dados.\n\n" +
  "Mantivemos os mesmos pacientes e as mesmas dez divisões, e trocamos só o alvo por um alvo inventado por nós, com o mesmo ruído dos dados reais. No lado esquerdo do gráfico o alvo é uma reta pura. No lado direito ele é feito só de degraus e curvas: por exemplo, a progressão só sobe quando o IMC e o s5 são altos ao mesmo tempo. No meio, misturas dos dois.\n\n" +
  "Quando o alvo é uma reta, a regressão linear ganha: " + v(t0.linear) + " contra " + v(t0.floresta) + ". É quase a mesma diferença que vimos nos dados reais. A floresta não ganhou em nenhuma das " + t0.divisoes + " divisões.\n\n" +
  "Conforme o alvo entorta, a linha escura da regressão linear sobe rápido, e a linha verde da floresta quase não se mexe. No final, a floresta ganha: " + v(t1.floresta) + " contra " + v(t1.linear) + ", em " + t1.floresta_ganha + " das " + t1.divisoes + " divisões.\n\n" +
  "As faixas claras são o desvio entre as divisões, e elas se sobrepõem, então o que sustenta a conclusão é a contagem de vitórias.\n\n" +
  "Então a floresta não perdeu por ser um modelo pior. Ela perdeu porque o dataset Diabetes é quase uma reta com ruído. Ela não supõe formato nenhum, e por isso funciona razoavelmente em qualquer caso. A regressão linear é ótima quando o mundo é reto, e quebra quando não é."
);

/* ------------------------------------------- 16 fechamento do semestre */
const sF = pres.addSlide();
tituloSlide(sF, "Fechamento: os trabalhos do semestre se encontram");
const mediaCurva = (chave, k) => fech.rodadas.reduce((a, r) => a + r[chave][k < 0 ? r[chave].length - 1 : k], 0) / fech.rodadas.length;
const ft = fech.teste;
imagem(sF, "fechamento.png", L, 1.2, 11.9, 5.4 / 17);
const fp = folga.principal;
const fe = folga.extra;
const mediana = (v) => v.slice().sort((a, b) => a - b)[Math.floor(v.length / 2)];
const fortes = Object.keys(fe.vezes_escolhida).filter((f) => fe.vezes_escolhida[f] >= 90);
const cartoesF = [
  [VERDE, "PSO na árvore (trabalho 3)", "Procurando sozinho a profundidade, o erro cai de " + v(fp.arvore_livre.media) + " para " + v(fp.arvore_pso.media) + ". Ganhou nas " + fp.pso_ganhou + " divisões."],
  [VERMELHO, "AG e PSO na floresta", "A padrão erra " + v(ft.padrao.media) + ". Ajustada, de " + v(ft.pso.media) + " a " + v(ft.ag.media) + ": melhorou no treino, mas não no teste."],
  [DESTAQUE, "AG no Naive Bayes (trabalhos 1 e 5)", "Com " + v(fe.n_medidas, 0) + " medidas em vez de 10, a acurácia vai de " + v(fe.bayes_todas.media * 100) + "% para " + v(fe.bayes_ag.media * 100) + "% (" + folga.divisoes_extra + " divisões)."],
];
cartoesF.forEach((c, i) => {
  const x = L + i * 4.0;
  cartao(sF, { x: x, y: 5.05, w: 3.9, h: 1.3 });
  faixa(sF, x, 5.05, 1.3, c[0]);
  texto(sF, c[1], { x: x + 0.25, y: 5.1, w: 3.55, h: 0.35, fontSize: 14, bold: true });
  texto(sF, c[2], { x: x + 0.25, y: 5.45, w: 3.55, h: 0.85, fontSize: 12, color: CINZA });
});
rodape(sF, [
  { text: "A busca ajuda onde o modelo está mal ajustado, e não onde ele já está no limite. ", options: { bold: true, color: BRANCO } },
  { text: "Em todos os casos ela só enxergou o treino; o teste ficou guardado até o fim. E o AG manteve " + fortes.join(", ") + " em pelo menos 90% das vezes: as mesmas três medidas de sempre.", options: { color: CLARO } },
], 6.45);
sF.addNotes(
  "INTEGRANTE 3\n\n" +
  "Como este é o último trabalho, quisemos juntar o semestre inteiro num slide. Pegamos o algoritmo genético do primeiro trabalho e o enxame de partículas do terceiro, com a mesma receita daqueles trabalhos, e colocamos para ajustar os modelos deste. Um cuidado importante: em todos os casos a busca só enxerga os dados de treino. O conjunto de teste fica guardado até o fim.\n\n" +
  "Primeiro gráfico, à esquerda: o PSO ajustando a árvore sozinha. Cada partícula é uma configuração, com a profundidade máxima e o tamanho mínimo de um grupo para ser dividido. Lembram que a árvore sem limite errava " + v(fp.arvore_livre.media) + "? Com a configuração que o PSO encontrou, o erro cai para " + v(fp.arvore_pso.media) + ", e a árvore ajustada ganhou em todas as " + fp.pso_ganhou + " divisões. O PSO não sabia a resposta da Parte 3, e chegou sozinho em árvores rasas: a profundidade típica que ele escolheu foi " + mediana(fp.profundidades) + ".\n\n" +
  "Segundo gráfico, no meio: a mesma ideia na floresta, com o AG escolhendo as medidas e o PSO a configuração. Aqui não funcionou. A floresta padrão erra " + v(ft.padrao.media) + "; com o PSO, " + v(ft.pso.media) + "; com o AG, " + v(ft.ag.media) + ". Durante a busca o erro estimado caiu, mas no teste nenhuma versão ajustada ganhou. A floresta já estava no limite desses dados, e a busca acabou escolhendo a configuração que teve mais sorte no treino. Ou seja, até a busca decora.\n\n" +
  "Terceiro gráfico, à direita: voltamos ao trabalho de Naive Bayes, onde tínhamos visto que usar menos medidas ajudava. Agora deixamos o AG escolher as medidas, cada cromossomo com dez bits, um por medida. Em " + folga.divisoes_extra + " divisões, ele ficou em média com " + v(fe.n_medidas, 0) + " das 10 medidas, e a acurácia foi de " + v(fe.bayes_todas.media * 100) + "% para " + v(fe.bayes_ag.media * 100) + "%. O ganho é pequeno, mas o modelo usa quase metade das medidas. E o gráfico mostra quais sobrevivem: " + fortes.join(", ") + " foram mantidas em pelo menos 90% das vezes. São as mesmas três que apareceram no ranking do Naive Bayes e na importância da floresta.\n\n" +
  "A lição que fica: a busca ajuda muito quando o modelo está mal ajustado, como a árvore sem limite, e não ajuda quando ele já está no limite, como a floresta."
);

/* ---------------------------------------------------- 17 demonstracao */
const sD = pres.addSlide();
tituloSlide(sD, "Ao vivo: escolha um paciente");
sD.addImage({ path: path.join(IMG, "demo.png"), x: L, y: 1.25, w: 8.3, h: 8.3 * 0.6 });
cartao(sD, { x: 9.3, y: 1.25, w: 3.3, h: 4.98, fundo: ESCURO });
texto(sD, "Ao vivo", { x: 9.55, y: 1.4, w: 2.8, h: 0.4, fontSize: 17, bold: true, color: DESTAQUE });
texto(sD, [
  "a página tem a nossa árvore e a nossa floresta treinadas dentro",
  "cada controle é uma medida do paciente",
  "o caminho na árvore acende, e as 100 árvores votam",
  "o gráfico mostra a árvore dando saltos e a floresta mudando suave",
].map((t) => "• " + t).join("\n\n"), {
  x: 9.55, y: 1.9, w: 2.85, h: 4.2, fontSize: 13.5, color: CLARO,
});
rodape(sD, "Arquivo demo/floresta_ao_vivo.html: abre com dois cliques em qualquer navegador, sem internet e sem instalar nada.", 6.45);
sD.addNotes(
  "INTEGRANTE 3\n\n" +
  "[ABRIR O ARQUIVO demo/floresta_ao_vivo.html NO NAVEGADOR — deixar aberto numa aba antes da apresentação. Se não der para abrir, usar a imagem do slide.]\n\n" +
  "Antes de concluir, em vez de mais um gráfico, queremos mostrar a floresta funcionando.\n\n" +
  "Esta página tem dentro dela a árvore e a floresta que nós treinamos. Cada controle à esquerda é uma medida do paciente.\n\n" +
  "[CLICAR EM \"Sortear um paciente real do teste\".] Este é um paciente de verdade, que os modelos nunca viram. Em cima aparecem as três previsões e o quanto cada uma errou. No meio, o caminho que ele fez na árvore de três perguntas. Embaixo à esquerda, o voto de cada uma das cem árvores: elas discordam bastante, e a floresta responde a média.\n\n" +
  "[ARRASTAR DEVAGAR O CONTROLE DO bmi.] Reparem no gráfico da direita. A linha fina e escura é a árvore sem limite: ela dá saltos para cima e para baixo, porque decorou os pacientes. A linha grossa e verde é a floresta: sobe de forma suave. É a diferença entre decorar e generalizar, que foi o assunto do trabalho inteiro.\n\n" +
  "[PEDIR PARA O PROFESSOR ESCOLHER OS VALORES DE UM PACIENTE.] Professor, quer inventar um paciente?\n\n" +
  "[VOLTAR PARA OS SLIDES.] Com isso, vamos às conclusões."
);

/* ------------------------------------------------------ 18 conclusoes */
const s15 = pres.addSlide();
s15.background = { color: ESCURO };
texto(s15, "Conclusões", { x: L, y: 0.45, w: LARG, h: 0.85, fontFace: TITULO_FONTE, fontSize: 28, color: BRANCO, valign: "middle" });
const concl = [
  ["Uma árvore", "Sem limite, decora o treino: MAE 0 no treino e " + v(p1.media_teste) + " no teste, quase igual a prever a média."],
  ["A profundidade", "Limitada a " + ma + " perguntas, a mesma árvore erra " + v(pa[ma - 1].media_teste) + ". Mais funda que isso é decoreba."],
  ["A floresta", "A média de " + tr.arvores + " árvores diferentes erra " + v(p2.media_teste) + ", não precisa de freio na profundidade e estabiliza com 20 a 40 árvores."],
  ["O que aprendemos", "A floresta estima o próprio erro de graça, aponta as mesmas medidas do Naive Bayes e só perde para uma reta porque estes dados são quase uma reta. O PSO conserta a árvore sozinho, mas não melhora a floresta."],
];
concl.forEach((c, i) => {
  const y = 1.6 + i * 1.15;
  texto(s15, c[0], { x: L, y: y, w: 2.8, h: 0.9, fontSize: 17, bold: true, color: DESTAQUE, valign: "middle" });
  texto(s15, c[1], { x: L + 2.9, y: y, w: 9.0, h: 0.9, fontSize: 16, color: BRANCO, valign: "middle" });
});
s15.addNotes(
  "INTEGRANTE 3\n\n" +
  "Para fechar.\n\n" +
  "Uma árvore de regressão sem limite decora o treino: erro zero no treino e " + v(p1.media_teste) + " no teste, quase o mesmo que prever sempre a média.\n\n" +
  "Limitando a profundidade a " + ma + " perguntas, a mesma árvore erra " + v(pa[ma - 1].media_teste) + ". A profundidade é o freio da decoreba.\n\n" +
  "A floresta aleatória resolve de outro jeito: deixa cada árvore decorar à vontade, mas faz cada uma decorar uma coisa diferente e tira a média. O erro cai para " + v(p2.media_teste) + ", ela não precisa de freio na profundidade, e de 20 a 40 árvores já bastam.\n\n" +
  "Nos extras, vimos que a floresta estima o próprio erro com os pacientes que ficaram fora de cada árvore, que ela aponta as mesmas medidas importantes do Naive Bayes, e que, nesses dados, uma regressão linear simples ainda ganha, porque eles são quase uma reta: com um alvo torto, a floresta passa na frente. E quando colocamos o AG e o PSO dos outros trabalhos para ajustar os modelos, eles consertaram a árvore, mas não conseguiram melhorar a floresta.\n\n" +
  "Com isso encerramos. Obrigado pelo semestre. Estamos à disposição para perguntas."
);

pres.writeFile({ fileName: path.join(__dirname, "apresentacao.pptx") }).then((f) => {
  console.log("gerado:", f);
});
