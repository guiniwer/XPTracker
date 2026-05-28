// Autocomplete de busca de jogos — implementação única para todas as buscas
// (header e modais). Substitui as 3 cópias que existiam nos templates.

import { buscarSugestoes } from "./api.js";

const MIN_CARACTERES = 2;

function criarItem(jogo) {
  const item = document.createElement("button");
  item.type = "button";
  item.className = "sugestao-item";

  const img = document.createElement("img");
  img.src = jogo.capa;
  img.alt = jogo.nome;

  const span = document.createElement("span");
  span.textContent = jogo.nome;

  item.append(img, span);
  return item;
}

export function iniciarAutocomplete({ aoSelecionar } = {}) {
  document.querySelectorAll(".input-autocomplete").forEach((input) => {
    const wrapper = input.closest(".autocomplete-wrapper");
    if (!wrapper) return;

    const box = wrapper.querySelector(".sugestoes-box");
    if (!box) return;

    const botaoLimpar = wrapper.querySelector(".btn-limpar-busca");

    const atualizarEstado = () => {
      wrapper.classList.toggle("tem-texto", input.value.trim().length > 0);
    };

    const limparBox = () => {
      box.replaceChildren();
      box.classList.remove("ativo");
    };

    input.addEventListener("input", async () => {
      atualizarEstado();

      const termo = input.value.trim();
      if (termo.length < MIN_CARACTERES) {
        limparBox();
        return;
      }

      try {
        const sugestoes = await buscarSugestoes(termo);
        const fragmento = document.createDocumentFragment();

        sugestoes.forEach((jogo) => {
          if (!jogo.nome || !jogo.capa) return;

          const item = criarItem(jogo);
          item.addEventListener("click", () => {
            input.value = jogo.nome;
            atualizarEstado();

            if (typeof aoSelecionar === "function") {
              aoSelecionar(jogo, input);
            }

            limparBox();
          });

          fragmento.appendChild(item);
        });

        // Troca o conteúdo de uma vez só (evita o "pisca" de limpar e repintar).
        box.replaceChildren(fragmento);
        box.classList.toggle("ativo", box.children.length > 0);
      } catch (erro) {
        console.error("Erro ao buscar sugestões:", erro);
        limparBox();
      }
    });

    if (botaoLimpar) {
      botaoLimpar.addEventListener("click", () => {
        input.value = "";
        atualizarEstado();
        limparBox();
        input.focus();
      });
    }

    document.addEventListener("click", (evento) => {
      if (!wrapper.contains(evento.target)) limparBox();
    });

    atualizarEstado();
  });
}
