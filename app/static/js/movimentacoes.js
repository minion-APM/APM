const produto = document.getElementById("select-produto");
const tamanho = document.getElementById("select-tamanho");

const areaTamanho = document.getElementById("area-tamanho");

const infoEstoque = document.getElementById("info-estoque");
const valorEstoque = document.getElementById("valor-estoque");

const quantidade = document.getElementById("input-quantidade");
const preco = document.getElementById("input-preco");

const infoSubtotal = document.getElementById("info-subtotal");
const valorSubtotal = document.getElementById("valor-subtotal");


function carregarProduto() {

    const option = produto.options[produto.selectedIndex];

    if (!option || !option.value) {
        areaTamanho.style.display = "none";
        infoEstoque.style.display = "none";
        return;
    }

    const temTamanho = option.dataset.temTamanho === "1";

    preco.value = Number(option.dataset.preco || 0).toFixed(2);


    if (temTamanho) {

        areaTamanho.style.display = "block";

        tamanho.innerHTML =
            '<option value="0">Selecione...</option>';

        document.querySelectorAll(".dado-tamanho")
            .forEach(item => {

                if (item.dataset.produto === option.value) {

                    const novaOption =
                        document.createElement("option");

                    novaOption.value = item.dataset.id;

                    novaOption.dataset.estoque =
                        item.dataset.estoque;

                    novaOption.textContent =
                        item.dataset.tamanho;

                    tamanho.appendChild(novaOption);
                }

            });

        valorEstoque.textContent = "Selecione um tamanho";
        infoEstoque.style.display = "block";

    } else {

        areaTamanho.style.display = "none";

        tamanho.value = "0";

        valorEstoque.textContent =
            option.dataset.estoque;

        infoEstoque.style.display = "block";
    }

    atualizarSubtotal();
}


function carregarTamanho() {

    const option =
        tamanho.options[tamanho.selectedIndex];

    if (
        option &&
        option.value !== "0"
    ) {
        valorEstoque.textContent =
            option.dataset.estoque;
    }
}


function atualizarSubtotal() {

    const qtd =
        Number(quantidade.value) || 0;

    const valor =
        Number(preco.value) || 0;

    const total = qtd * valor;


    if (qtd > 0) {

        valorSubtotal.textContent =
            total.toLocaleString("pt-BR", {
                style: "currency",
                currency: "BRL"
            });

        infoSubtotal.style.display = "block";

    } else {

        infoSubtotal.style.display = "none";
    }
}


produto.addEventListener(
    "change",
    carregarProduto
);

tamanho.addEventListener(
    "change",
    carregarTamanho
);

quantidade.addEventListener(
    "input",
    atualizarSubtotal
);

preco.addEventListener(
    "input",
    atualizarSubtotal
);


if (produto.value) {
    carregarProduto();
}