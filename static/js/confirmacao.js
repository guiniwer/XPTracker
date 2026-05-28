// Modal de confirmação reaproveitável (ver _modal_confirmacao.html).
// confirmar(...) abre o modal e resolve uma Promise<boolean> conforme a escolha.

import { abrir, fechar } from "./overlay.js";

const overlay = document.getElementById("overlay-confirmacao");
const tituloEl = document.getElementById("confirmacao-titulo");
const mensagemEl = document.getElementById("confirmacao-mensagem");
const btnConfirmar = document.getElementById("btn-confirmar-confirmacao");
const btnCancelar = document.getElementById("btn-cancelar-confirmacao");

export function confirmar({
  titulo = "Tem certeza?",
  mensagem = "Essa ação não pode ser desfeita.",
  textoConfirmar = "Excluir",
} = {}) {
  return new Promise((resolve) => {
    // Sem o modal no DOM (páginas que não incluem o partial), cai no nativo.
    if (!overlay || !btnConfirmar || !btnCancelar) {
      resolve(window.confirm(mensagem));
      return;
    }

    if (tituloEl) tituloEl.textContent = titulo;
    if (mensagemEl) mensagemEl.textContent = mensagem;
    btnConfirmar.textContent = textoConfirmar;

    abrir(overlay);

    function finalizar(resultado) {
      fechar(overlay);
      btnConfirmar.removeEventListener("click", aoConfirmar);
      btnCancelar.removeEventListener("click", aoCancelar);
      overlay.removeEventListener("click", aoClicarFundo);
      document.removeEventListener("keydown", aoTeclar);
      resolve(resultado);
    }

    function aoConfirmar() {
      finalizar(true);
    }

    function aoCancelar() {
      finalizar(false);
    }

    function aoClicarFundo(evento) {
      if (evento.target === overlay) finalizar(false);
    }

    function aoTeclar(evento) {
      if (evento.key === "Escape") finalizar(false);
    }

    btnConfirmar.addEventListener("click", aoConfirmar);
    btnCancelar.addEventListener("click", aoCancelar);
    overlay.addEventListener("click", aoClicarFundo);
    document.addEventListener("keydown", aoTeclar);
  });
}
