// Orquestra a home logada (index_logado.html): modal de review, edição
// in-place (sem reload), autocomplete, e a seção "jogos para descobrir".
// O modal de criar/editar é o compartilhado com o perfil (nota decimal).

import { iniciarAutocomplete } from "./autocomplete.js";
import { configurarOverlay, abrir } from "./overlay.js";
import { ligarDeletarReviews, ligarEditarReview } from "./reviews.js";
import { ligarAdicionarDesejo } from "./wishlist.js";
import { montarEstrelas } from "./stars.js";
import { criarRatingInput } from "./rating-input.js";

const ESTRELAS_HOME = { cheia: "filled", meia: "half", vazia: "empty" };

function textoNota(elemento) {
  return (nota) => {
    if (!elemento) return;
    const n = Number(nota);
    const valor = Number.isInteger(n) ? String(n) : n.toFixed(1).replace(".", ",");
    elemento.textContent = `${valor} / 5`;
  };
}

const overlayReview = document.getElementById("overlay-review");
const overlayEdit = document.getElementById("overlay-edit-review");

const inputNome = document.getElementById("input-nome-jogo");
const inputCapa = document.getElementById("input-capa-jogo");
const modalNome = document.getElementById("modal-nome-jogo");
const modalCapa = document.getElementById("modal-capa-jogo");

const CAPA_PADRAO = modalCapa?.getAttribute("src") || "";

// Seletor de estrelas do modal de criar review.
const ratingCriar = criarRatingInput(document.getElementById("estrelas-criar"), {
  input: document.getElementById("input-nota-criar"),
  aoMudar: textoNota(document.getElementById("nota-valor-criar")),
});

function abrirModalComJogo(nome, capa) {
  if (modalNome) modalNome.textContent = nome;
  if (modalCapa) {
    modalCapa.src = capa;
    modalCapa.alt = nome;
  }
  if (inputNome) inputNome.value = nome;
  if (inputCapa) inputCapa.value = capa;
  ratingCriar.set(0);
  abrir(overlayReview);
}

function abrirModalVazio() {
  if (modalNome) modalNome.textContent = "Pesquise um jogo";
  if (modalCapa) {
    modalCapa.src = CAPA_PADRAO;
    modalCapa.alt = "Jogo";
  }
  if (inputNome) inputNome.value = "";
  if (inputCapa) inputCapa.value = "";
  ratingCriar.set(0);
  abrir(overlayReview);
}

// Abre o modal de review em branco pelo "+" do header e pelo card de CTA.
[
  document.getElementById("abrir-review"),
  document.getElementById("abrir-review-card"),
]
  .filter(Boolean)
  .forEach((botao) => botao.addEventListener("click", abrirModalVazio));

configurarOverlay(overlayReview, {
  fechadores: [document.getElementById("fechar-review")],
});

// Não deixa publicar sem escolher a nota (input hidden não valida sozinho).
const formCriar = overlayReview?.querySelector(".modal-review");
formCriar?.addEventListener("submit", (evento) => {
  if (!ratingCriar.get()) {
    evento.preventDefault();
    document.getElementById("estrelas-criar")?.classList.add("invalido");
  }
});

// Excluir reviews recentes.
ligarDeletarReviews(".btn-deletar-review", "[data-card-review]");

// Editar review: abrir modal preenchido.
const editId = document.getElementById("edit-review-id");
const editNota = document.getElementById("edit-review-nota");
const editTexto = document.getElementById("edit-review-texto");

const ratingEditar = criarRatingInput(document.getElementById("estrelas-editar"), {
  input: editNota,
  aoMudar: textoNota(document.getElementById("nota-valor-editar")),
});

document.querySelectorAll(".btn-editar-review").forEach((botao) => {
  botao.addEventListener("click", () => {
    const card = botao.closest(".review-recente-card");
    if (!card) return;

    if (editId) editId.value = botao.dataset.id;
    ratingEditar.set(card.dataset.nota);
    if (editTexto) editTexto.value = card.dataset.texto;

    abrir(overlayEdit);
  });
});

configurarOverlay(overlayEdit, {
  fechadores: [document.getElementById("fechar-edit-review")],
});

// Salvar edição com atualização in-place (antes dava window.location.reload()).
ligarEditarReview({
  form: document.getElementById("form-edit-review"),
  overlay: overlayEdit,
  lerDados: () => ({
    id: editId?.value,
    nota: editNota?.value,
    review_texto: editTexto?.value,
  }),
  aoAtualizar: ({ id, nota, review_texto }) => {
    const card = document.querySelector(`[data-card-review][data-id="${id}"]`);
    if (!card) return;

    card.dataset.nota = nota;
    card.dataset.texto = review_texto;

    const texto = card.querySelector(".review-recente-texto");
    const stars = card.querySelector(".review-recente-stars");

    if (texto) texto.textContent = review_texto;
    if (stars) stars.innerHTML = montarEstrelas(nota, ESTRELAS_HOME);
  },
});

// Autocomplete (header + busca dentro do modal).
iniciarAutocomplete({
  aoSelecionar: (jogo, input) => {
    if (input.closest(".modal-review")) {
      abrirModalComJogo(jogo.nome, jogo.capa);
    }
  },
});

// Jogos para descobrir: avaliar (abre modal) e adicionar à lista de desejo.
document.querySelectorAll(".btn-avaliar-descobrir").forEach((botao) => {
  botao.addEventListener("click", () => {
    const card = botao.closest(".jogo-descobrir-card");
    if (!card) return;

    abrirModalComJogo(card.dataset.nome, card.dataset.capa);
  });
});

ligarAdicionarDesejo(".btn-desejo-descobrir", (botao) => {
  const card = botao.closest(".jogo-descobrir-card");
  if (!card) return null;
  return { nome_jogo: card.dataset.nome, capa_jogo_url: card.dataset.capa };
});
