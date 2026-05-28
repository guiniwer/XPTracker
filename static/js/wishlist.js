// Ações da lista de desejo (adicionar/excluir).

import { adicionarDesejo, deletarDesejo } from "./api.js";
import { confirmar } from "./confirmacao.js";

const CONFIRMA_REMOVER_DESEJO = {
  titulo: "Remover da lista?",
  mensagem: "O jogo será removido da sua lista de desejo.",
  textoConfirmar: "Remover",
};

export function ligarExcluirDesejo(botaoSelector, cardSelector) {
  document.querySelectorAll(botaoSelector).forEach((botao) => {
    botao.addEventListener("click", async (evento) => {
      evento.stopPropagation();

      const id = botao.dataset.id;
      const card = botao.closest(cardSelector);

      const ok = await confirmar(CONFIRMA_REMOVER_DESEJO);
      if (!ok) return;

      botao.disabled = true;
      try {
        const resposta = await deletarDesejo(id);
        if (resposta.ok && card) {
          card.remove();
        } else {
          botao.disabled = false;
        }
      } catch (erro) {
        console.error("Erro ao excluir desejo:", erro);
        botao.disabled = false;
      }
    });
  });
}

// Remove apenas no front (cards de exemplo que não existem no banco).
export function ligarExcluirDesejoLocal(botaoSelector, cardSelector) {
  document.querySelectorAll(botaoSelector).forEach((botao) => {
    botao.addEventListener("click", async (evento) => {
      evento.stopPropagation();
      const card = botao.closest(cardSelector);
      if (!card) return;

      const ok = await confirmar(CONFIRMA_REMOVER_DESEJO);
      if (!ok) return;

      card.remove();
    });
  });
}

export function ligarAdicionarDesejo(botaoSelector, lerDados) {
  document.querySelectorAll(botaoSelector).forEach((botao) => {
    botao.addEventListener("click", async () => {
      const dados = lerDados(botao);
      if (!dados) return;

      botao.disabled = true;
      try {
        const resposta = await adicionarDesejo(dados);
        if (resposta.ok) {
          botao.classList.add("adicionado");
          botao.innerHTML = '<i class="fa-solid fa-check"></i> Adicionado';
        } else {
          botao.disabled = false;
        }
      } catch (erro) {
        console.error("Erro ao adicionar desejo:", erro);
        botao.disabled = false;
      }
    });
  });
}
