// Monta o HTML das estrelas de uma nota (0 a 5, com meia estrela).
// As classes são parametrizáveis porque cada página usa nomes diferentes
// (perfil: pink/half/white | home: filled/half/empty).

const CLASSES_PADRAO = { cheia: "pink", meia: "half", vazia: "white" };

export function montarEstrelas(nota, classes = CLASSES_PADRAO) {
  const valor = Number(nota);
  let html = "";

  for (let i = 1; i <= 5; i++) {
    if (i <= valor) {
      html += `<span class="${classes.cheia}">★</span>`;
    } else if (i - 0.5 <= valor) {
      html += `<span class="${classes.meia}">★</span>`;
    } else {
      html += `<span class="${classes.vazia}">★</span>`;
    }
  }

  return html;
}
