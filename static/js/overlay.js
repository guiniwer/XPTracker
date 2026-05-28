// Controle genérico de overlays/modais (classe "ativo").
// Reaproveitado por todos os modais (review, edição, galeria).

export function abrir(overlay) {
  if (overlay) overlay.classList.add("ativo");
}

export function fechar(overlay) {
  if (overlay) overlay.classList.remove("ativo");
}

// Liga abertura/fechamento padrão: botões de abrir, botões de fechar,
// clique no fundo e tecla Esc.
export function configurarOverlay(overlay, { abridores = [], fechadores = [] } = {}) {
  if (!overlay) return;

  abridores
    .filter(Boolean)
    .forEach((el) => el.addEventListener("click", () => abrir(overlay)));

  fechadores
    .filter(Boolean)
    .forEach((el) => el.addEventListener("click", () => fechar(overlay)));

  overlay.addEventListener("click", (evento) => {
    if (evento.target === overlay) fechar(overlay);
  });

  document.addEventListener("keydown", (evento) => {
    if (evento.key === "Escape" && overlay.classList.contains("ativo")) {
      fechar(overlay);
    }
  });
}
