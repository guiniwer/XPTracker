const email = document.getElementById("email");

if (email) {
    email.addEventListener("invalid", function () {
        if (email.value === "") {
            email.setCustomValidity("Digite seu e-mail.");
        } else {
            email.setCustomValidity("Esse e-mail nao e valido.");
        }
    });

    email.addEventListener("input", function () {
        email.setCustomValidity("");
    });
}
