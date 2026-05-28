// Ações de review (excluir e editar) reaproveitadas pela home e pelo perfil.
// A atualização visual do card fica a cargo de cada página (markup diferente),
// por isso a edição recebe um callback "aoAtualizar".

import { deletarReview, editarReview } from "./api.js";
import { confirmar } from "./confirmacao.js";

export function ligarDeletarReviews(botaoSelector, cardSelector) {
  document.querySelectorAll(botaoSelector).forEach((botao) => {
    botao.addEventListener("click", async (evento) => {
      evento.stopPropagation();

      const id = botao.dataset.id;
      const card = botao.closest(cardSelector);
      if (!id) return;

      const ok = await confirmar({
        titulo: "Excluir avaliação?",
        textoConfirmar: "Excluir",
      });
      if (!ok) return;

      botao.disabled = true;
      try {
        const resposta = await deletarReview(id);
        if (resposta.ok && card) {
          card.remove();
        } else {
          botao.disabled = false;
        }
      } catch (erro) {
        console.error("Erro ao excluir review:", erro);
        botao.disabled = false;
      }
    });
  });
}

export function ligarEditarReview({ form, overlay, lerDados, aoAtualizar }) {
  if (!form) return;

  form.addEventListener("submit", async (evento) => {
    evento.preventDefault();

    const dados = lerDados();
    if (!dados || !dados.id || dados.nota === undefined || dados.nota === null || dados.nota === "" || !dados.review_texto) {
      return;
    }

    const botao = form.querySelector('button[type="submit"]');
    if (botao) botao.disabled = true;

    try {
      const resposta = await editarReview(dados.id, {
        nota: dados.nota,
        review_texto: dados.review_texto,
      });

      if (resposta.ok) {
        if (typeof aoAtualizar === "function") aoAtualizar(dados);
        if (overlay) overlay.classList.remove("ativo");
      }
    } catch (erro) {
      console.error("Erro ao editar review:", erro);
    } finally {
      if (botao) botao.disabled = false;
    }
  });
}
