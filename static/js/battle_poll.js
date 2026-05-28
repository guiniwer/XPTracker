const poll = document.getElementById("mk-poll");

if (poll) {
    const bar = poll.querySelector(".poll-bar");
    const segs = poll.querySelectorAll(".poll-seg");
    const STORAGE_KEY = "xpt_mk_vote";

    const pctEl = (side) => poll.querySelector(`.poll-seg.${side} .poll-pct`);

    const randInt = (min, max) =>
        Math.floor(Math.random() * (max - min + 1)) + min;

    // pct = porcentagem do lado escolhido (sempre o vencedor, 51-65)
    function render(side, pct) {
        const subzeroPct = side === "subzero" ? pct : 100 - pct;
        const scorpionPct = 100 - subzeroPct;

        bar.style.setProperty("--split", `${subzeroPct}%`);
        pctEl("subzero").textContent = `${subzeroPct}%`;
        pctEl("scorpion").textContent = `${scorpionPct}%`;

        segs.forEach((seg) => {
            const isWinner = seg.dataset.side === side;
            seg.classList.toggle("winner", isWinner);
            seg.classList.toggle("loser", !isWinner);
        });

        bar.dataset.voted = "true";
    }

    function vote(side) {
        const pct = randInt(51, 65);
        render(side, pct);
        try {
            sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ side, pct }));
        } catch (e) {
            /* sessionStorage indisponível — voto só na sessão atual */
        }
    }

    // Restaura voto salvo (sem re-randomizar)
    try {
        const saved = JSON.parse(sessionStorage.getItem(STORAGE_KEY));
        const validSide = saved?.side === "subzero" || saved?.side === "scorpion";
        if (validSide && saved.pct >= 51 && saved.pct <= 65) {
            render(saved.side, saved.pct);
        }
    } catch (e) {
        /* JSON inválido — ignora e mantém estado neutro */
    }

    segs.forEach((seg) => {
        seg.addEventListener("click", () => {
            if (bar.dataset.voted === "true") return;
            vote(seg.dataset.side);
        });
    });
}
