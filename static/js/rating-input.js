// Seletor de nota por estrelas (0 a 5, com meia estrela).
// Hover faz preview; clicar na metade esquerda da estrela vale .5 e na
// direita vale a estrela inteira. O valor escolhido é escrito num input
// hidden para o form enviar normalmente. Retorna { get, set } para a página
// resetar (criar) ou preencher (editar) a nota.

export function criarRatingInput(container, { input, valorInicial = 0, aoMudar } = {}) {
  if (!container) return { get: () => 0, set: () => {} };

  let valor = Number(valorInicial) || 0;

  const estrelas = [];
  container.innerHTML = "";
  for (let i = 1; i <= 5; i++) {
    const estrela = document.createElement("span");
    estrela.className = "estrela";
    estrela.dataset.indice = String(i);
    estrela.textContent = "★";
    container.appendChild(estrela);
    estrelas.push(estrela);
  }

  function pintar(nota) {
    estrelas.forEach((estrela, idx) => {
      const posicao = idx + 1;
      estrela.classList.remove("cheia", "meia", "vazia");
      if (posicao <= nota) estrela.classList.add("cheia");
      else if (posicao - 0.5 <= nota) estrela.classList.add("meia");
      else estrela.classList.add("vazia");
    });
  }

  function notaNaPosicao(evento) {
    const estrela = evento.target.closest(".estrela");
    if (!estrela || !container.contains(estrela)) return null;
    const rect = estrela.getBoundingClientRect();
    const indice = Number(estrela.dataset.indice);
    const metadeEsquerda = evento.clientX - rect.left < rect.width / 2;
    return metadeEsquerda ? indice - 0.5 : indice;
  }

  function definir(nota) {
    valor = Number(nota) || 0;
    if (input) input.value = valor ? String(valor) : "";
    pintar(valor);
    container.classList.remove("invalido");
    if (typeof aoMudar === "function") aoMudar(valor);
  }

  container.addEventListener("mousemove", (evento) => {
    const nota = notaNaPosicao(evento);
    if (nota !== null) pintar(nota);
  });
  container.addEventListener("mouseleave", () => pintar(valor));
  container.addEventListener("click", (evento) => {
    const nota = notaNaPosicao(evento);
    if (nota !== null) definir(nota);
  });

  definir(valor);

  return {
    get: () => valor,
    set: (nota) => definir(nota),
  };
}
