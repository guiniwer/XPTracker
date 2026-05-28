// Orquestra a página de perfil (perfil.html): modal de review, edição in-place,
// autocomplete, lista de desejo e marcação local de jogos já avaliados.

import { iniciarAutocomplete } from "./autocomplete.js";
import { configurarOverlay, abrir } from "./overlay.js";
import { ligarDeletarReviews, ligarEditarReview } from "./reviews.js";
import { ligarExcluirDesejo, ligarExcluirDesejoLocal } from "./wishlist.js";
import { montarEstrelas } from "./stars.js";
import { criarRatingInput } from "./rating-input.js";

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

// Cards da lista de desejo abrem o modal já com o jogo.
document.querySelectorAll(".abrir-modal-jogo").forEach((card) => {
  card.addEventListener("click", () => {
    abrirModalComJogo(card.dataset.nome, card.dataset.capa);
  });
});

// Botões que abrem o modal em branco.
[
  document.getElementById("abrir-modal-perfil"),
  document.getElementById("btn-criar-review"),
]
  .filter(Boolean)
  .forEach((botao) => botao.addEventListener("click", abrirModalVazio));

configurarOverlay(overlayReview, {
  fechadores: [document.getElementById("fechar-review")],
});

// Marca localmente (localStorage) os jogos já avaliados.
const formReview = document.querySelector(".modal-review");
if (formReview) {
  formReview.addEventListener("submit", (evento) => {
    // Input hidden não valida sozinho: bloqueia publicar sem nota.
    if (!ratingCriar.get()) {
      evento.preventDefault();
      document.getElementById("estrelas-criar")?.classList.add("invalido");
      return;
    }
    const nome = inputNome?.value;
    if (nome) localStorage.setItem(`avaliado-${nome}`, "true");
  });
}

document.querySelectorAll(".card-desejo").forEach((card) => {
  const nome = card.dataset.nome;
  if (nome && localStorage.getItem(`avaliado-${nome}`) === "true") {
    card.classList.add("avaliado");
  }
});

// Excluir reviews (in-place).
ligarDeletarReviews(".btn-deletar-review-perfil", "[data-card-review]");

// Editar review: abrir modal preenchido.
const editId = document.getElementById("edit-review-id");
const editNota = document.getElementById("edit-review-nota");
const editTexto = document.getElementById("edit-review-texto");

const ratingEditar = criarRatingInput(document.getElementById("estrelas-editar"), {
  input: editNota,
  aoMudar: textoNota(document.getElementById("nota-valor-editar")),
});

document.querySelectorAll(".btn-editar-review-perfil").forEach((botao) => {
  botao.addEventListener("click", (evento) => {
    evento.stopPropagation();

    const card = botao.closest("[data-card-review]");
    if (editId) editId.value = botao.dataset.id;
    if (card) ratingEditar.set(card.dataset.nota);
    if (editTexto && card) editTexto.value = card.dataset.texto;

    abrir(overlayEdit);
  });
});

configurarOverlay(overlayEdit, {
  fechadores: [document.getElementById("fechar-edit-review")],
});

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

    const numeroNota = card.querySelector(".numero-nota");
    const textoReview = card.querySelector(".review-overlay p");
    const estrelas = card.querySelector(".stars");

    if (numeroNota) numeroNota.textContent = Number(nota).toFixed(1).replace(".", ",");
    if (textoReview) textoReview.textContent = review_texto;
    if (estrelas) estrelas.innerHTML = montarEstrelas(nota);
  },
});

// Lista de desejo: excluir (no banco) e excluir local (cards de exemplo).
ligarExcluirDesejo(".btn-excluir-desejo", "[data-card-desejo]");
ligarExcluirDesejoLocal(".btn-excluir-desejo-local", ".card-desejo");

// Autocomplete: selecionar uma sugestão abre o modal com o jogo.
iniciarAutocomplete({
  aoSelecionar: (jogo) => abrirModalComJogo(jogo.nome, jogo.capa),
});
