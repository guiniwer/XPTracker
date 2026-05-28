
/* para editar o perfil */
const perfil = document.querySelector(".perfil");
const btnEditar = document.querySelector("#btn-editar");
const btnCancelar = document.querySelector(".btn-cancelar");
const inputFotoPerfil = document.querySelector("#foto_perfil_url");
const previewAvatarPerfil = document.querySelector("#preview-avatar-perfil");
const inputBio = document.querySelector("#input-bio");
const bioCount = document.querySelector("#bio-count");

if (perfil && btnEditar) {
    btnEditar.addEventListener("click", () => {
        perfil.classList.add("editando");
    });
}

if (perfil && btnCancelar) {
    btnCancelar.addEventListener("click", () => {
        perfil.classList.remove("editando");
    });
}

if (inputBio && bioCount) {
    const atualizarContadorBio = () => {
        bioCount.textContent = inputBio.value.length;
    };

    atualizarContadorBio();
    inputBio.addEventListener("input", atualizarContadorBio);
}

/* galeria de avatares (personagens de jogos) */
const overlayGaleria = document.querySelector("#overlay-galeria");
const abrirGaleria = document.querySelector("#abrir-galeria-avatar");
const fecharGaleria = document.querySelector("#fechar-galeria");
const avatarTopo = document.querySelector("#avatar-topo");
const opcoesAvatar = document.querySelectorAll(".avatar-opcao");

function abrirGaleriaAvatar() {
    if (overlayGaleria) overlayGaleria.classList.add("ativo");
}

function fecharGaleriaAvatar() {
    if (overlayGaleria) overlayGaleria.classList.remove("ativo");
}

if (abrirGaleria) {
    abrirGaleria.addEventListener("click", abrirGaleriaAvatar);
}

if (fecharGaleria) {
    fecharGaleria.addEventListener("click", fecharGaleriaAvatar);
}

if (overlayGaleria) {
    overlayGaleria.addEventListener("click", (evento) => {
        if (evento.target === overlayGaleria) {
            fecharGaleriaAvatar();
        }
    });
}

opcoesAvatar.forEach((opcao) => {
    opcao.addEventListener("click", () => {
        const novaUrl = opcao.dataset.avatar;

        if (inputFotoPerfil) inputFotoPerfil.value = novaUrl;
        if (previewAvatarPerfil) previewAvatarPerfil.src = novaUrl;
        if (avatarTopo) avatarTopo.src = novaUrl;

        opcoesAvatar.forEach((item) => item.classList.remove("selecionado"));
        opcao.classList.add("selecionado");

        fecharGaleriaAvatar();
    });
});
