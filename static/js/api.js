// Cliente único para os endpoints JSON do Flask.
// Centraliza as chamadas de rede para o resto do front não repetir fetch/headers.

async function postJSON(url, corpo) {
  return fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });
}

export async function buscarSugestoes(termo) {
  const resposta = await fetch(`/sugestoes-jogos?q=${encodeURIComponent(termo)}`);

  if (!resposta.ok) {
    throw new Error("Falha ao buscar sugestões de jogos.");
  }

  return resposta.json();
}

export function deletarReview(id) {
  return fetch(`/deletar-avaliacao-json/${id}`, { method: "POST" });
}

export function editarReview(id, dados) {
  return postJSON(`/editar-avaliacao-json/${id}`, dados);
}

export function adicionarDesejo(dados) {
  return postJSON("/adicionar-desejo-json", dados);
}

export function deletarDesejo(id) {
  return fetch(`/deletar-desejo-json/${id}`, { method: "POST" });
}
