// Autocomplete da home pública: mostra sugestões reais de jogos, mas qualquer
// seleção leva o visitante para a tela de login (a busca em si exige conta).

import { iniciarAutocomplete } from "./autocomplete.js";

iniciarAutocomplete({
  aoSelecionar: (jogo, input) => {
    const wrapper = input.closest(".autocomplete-wrapper");
    window.location.href = wrapper?.dataset.loginUrl ?? "/login";
  },
});
