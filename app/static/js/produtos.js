function abrirTamanhos(id) {
    const area = document.getElementById("tamanhos-" + id);

    if (!area) {
        return;
    }

    area.style.display =
        area.style.display === "none" ? "block" : "none";
}