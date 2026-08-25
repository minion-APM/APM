// Inicialização segura das variáveis globais
let carrinho = [];
let clienteAtual = { id: 0, associado: false };

// Captura a taxa de desconto definida no HTML através do data-attribute
const DESCONTO_PCT =
    parseFloat(document.getElementById('pdv-container')?.dataset.desconto) || 10.0;


// ==========================================================
// ADICIONAR PRODUTO AO CARRINHO
// ==========================================================

function adicionarAoCarrinho(card) {

    const id = parseInt(card.getAttribute('data-id'));
    const nome = card.getAttribute('data-nome');
    const preco = parseFloat(card.getAttribute('data-preco'));
    const estoque = parseInt(card.getAttribute('data-estoque'));

    const temTamanho =
        card.getAttribute('data-tem-tamanho') === 'true';


    // PRODUTO SEM TAMANHO
    if (!temTamanho) {

        const existente = carrinho.find(item =>
            item.produto_id === id &&
            !item.tamanho_id
        );

        if (existente) {

            if (existente.quantidade < existente.estoque_max) {

                existente.quantidade++;

            } else {

                window.showToast?.(
                    `Limite de estoque atingido (${existente.estoque_max} un.).`,
                    'error'
                );

                return;
            }

        } else {

            carrinho.push({
                produto_id: id,
                nome: nome,
                preco: preco,
                quantidade: 1,
                estoque_max: estoque,
                tem_tamanho: false,
                tamanho_id: null,
                tamanho: null,
                tamanhos: []
            });
        }

        renderizarCarrinho();
        window.showToast?.('Produto adicionado ao carrinho com sucesso!', 'success');

        return;
    }


    // PRODUTO COM TAMANHO
    const tamanhos = [];

    card.querySelectorAll('.dado-tamanho').forEach(t => {

        tamanhos.push({
            id: parseInt(t.dataset.id),
            tamanho: t.dataset.tamanho,
            estoque: parseInt(t.dataset.estoque)
        });

    });


    // Adiciona uma nova linha no carrinho para escolher o tamanho
    carrinho.push({
        produto_id: id,
        nome: nome,
        preco: preco,
        quantidade: 1,
        estoque_max: 0,
        tem_tamanho: true,
        tamanho_id: null,
        tamanho: null,
        tamanhos: tamanhos
    });


    renderizarCarrinho();
    window.showToast?.('Produto adicionado ao carrinho com sucesso!', 'success');
}


// ==========================================================
// ESCOLHER TAMANHO
// ==========================================================

function escolherTamanho(indice, select) {

    const item = carrinho[indice];

    if (!item) return;


    const tamanhoId = parseInt(select.value);


    const tamanho = item.tamanhos.find(
        t => t.id === tamanhoId
    );


    // Nenhum tamanho selecionado
    if (!tamanho) {

        item.tamanho_id = null;
        item.tamanho = null;
        item.estoque_max = 0;

        renderizarCarrinho();

        return;
    }


    // Verifica se esse mesmo produto + tamanho já existe
    const existente = carrinho.find(
        (i, pos) =>
            pos !== indice &&
            i.produto_id === item.produto_id &&
            i.tamanho_id === tamanho.id
    );


    // Se já existir o mesmo tamanho, aumenta a quantidade
    if (existente) {

        if (existente.quantidade < existente.estoque_max) {

            existente.quantidade++;

        } else {

            window.showToast?.(
                `Limite de estoque atingido (${existente.estoque_max} un.).`,
                'error'
            );
        }


        // Remove a linha nova que estava esperando tamanho
        carrinho.splice(indice, 1);

        renderizarCarrinho();

        return;
    }


    // Salva o tamanho escolhido
    item.tamanho_id = tamanho.id;
    item.tamanho = tamanho.tamanho;
    item.estoque_max = tamanho.estoque;
    item.quantidade = 1;


    renderizarCarrinho();
}


// ==========================================================
// ALTERAR QUANTIDADE
// ==========================================================

function alterarQtd(indice, delta) {

    const item = carrinho[indice];

    if (!item) return;


    // Se tiver tamanho, obriga escolher antes
    if (item.tem_tamanho && !item.tamanho_id) {

        window.showToast?.('Selecione o tamanho primeiro.', 'error');

        return;
    }


    item.quantidade += delta;


    if (item.quantidade <= 0) {

        carrinho.splice(indice, 1);
        renderizarCarrinho();

        return;
    }


    if (item.quantidade > item.estoque_max) {

        window.showToast?.(
            `Apenas ${item.estoque_max} unidades disponíveis no estoque.`,
            'error'
        );

        item.quantidade = item.estoque_max;
    }


    renderizarCarrinho();
}


// ==========================================================
// REMOVER ITEM
// ==========================================================

function removerItem(indice) {

    if (!carrinho[indice]) return;

    window.openConfirmation({
        title: 'Tem certeza?',
        message: 'Tem certeza que deseja remover este produto do carrinho?',
        confirmText: 'Remover produto',
        onConfirm: () => {
            carrinho.splice(indice, 1);
            renderizarCarrinho();
            window.showToast?.('Produto removido do carrinho.', 'success');
        }
    });
}

function limparCarrinho() {
    if (carrinho.length === 0) return;

    window.openConfirmation({
        title: 'Tem certeza?',
        message: 'Tem certeza que deseja limpar o carrinho? Todos os produtos adicionados serão removidos.',
        confirmText: 'Limpar carrinho',
        onConfirm: () => {
            carrinho = [];
            renderizarCarrinho();
            window.showToast?.('Carrinho limpo com sucesso!', 'success');
        }
    });
}

function cancelarVenda() {
    if (carrinho.length === 0) return;

    window.openConfirmation({
        title: 'Tem certeza?',
        message: 'Tem certeza que deseja cancelar a venda atual? Os produtos do carrinho serão removidos.',
        cancelText: 'Continuar venda',
        cancelStyle: 'primary',
        confirmText: 'Cancelar venda',
        danger: true,
        onConfirm: () => {
            carrinho = [];
            document.getElementById('obs-input').value = '';
            document.getElementById('select-cliente').value = '0';
            atualizarCliente(document.getElementById('select-cliente'));
            renderizarCarrinho();
            window.showToast?.('Venda cancelada com sucesso!', 'success');
        }
    });
}


// ==========================================================
// ATUALIZAR CLIENTE
// ==========================================================

function atualizarCliente(select) {

    const opt = select.options[select.selectedIndex];

    clienteAtual.id = parseInt(opt.value);

    clienteAtual.associado =
        opt.getAttribute('data-associado') === 'true';


    const badge =
        document.getElementById('badge-desconto');


    if (badge) {

        badge.style.display =
            clienteAtual.associado
                ? 'inline-flex'
                : 'none';
    }


    renderizarTotais();
}


// ==========================================================
// RENDERIZAR CARRINHO
// ==========================================================

function renderizarCarrinho() {

    const lista =
        document.getElementById('lista-carrinho');

    const vazio =
        document.getElementById('msg-vazio');

    const totais =
        document.getElementById('totais');

    const btnFinal =
        document.getElementById('btn-finalizar');


    if (!lista) return;


    // CARRINHO VAZIO
    if (carrinho.length === 0) {

        lista.innerHTML = '';

        if (vazio)
            vazio.style.display = 'flex';

        if (totais)
            totais.style.display = 'none';

        if (btnFinal)
            btnFinal.disabled = true;

        return;
    }


    if (vazio)
        vazio.style.display = 'none';

    if (totais)
        totais.style.display = 'block';


    lista.innerHTML = '';


    carrinho.forEach((item, indice) => {

        const subtotalItem =
            item.preco * item.quantidade;


        const div =
            document.createElement('div');


        div.className = 'item-carrinho';


        // ==================================================
        // TAMANHOS
        // ==================================================

        let tamanhoHTML = '';


        if (item.tem_tamanho) {

            let options = `
                <option value="">
                    Escolha o tam.
                </option>
            `;


            item.tamanhos.forEach(t => {

                const selecionado =
                    item.tamanho_id === t.id
                        ? 'selected'
                        : '';


                const desabilitado =
                    t.estoque <= 0
                        ? 'disabled'
                        : '';


                options += `
                    <option
                        value="${t.id}"
                        ${selecionado}
                        ${desabilitado}
                    >
                        ${t.tamanho} (${t.estoque})
                    </option>
                `;
            });


            tamanhoHTML = `
                <select
                    onchange="escolherTamanho(${indice}, this)"
                    style="
                        width: 105px;
                        height: 28px;
                        margin: 3px 0;
                        padding: 2px 5px;
                        font-size: 10px;
                        border: 1px solid #cbd5e1;
                        border-radius: 5px;
                        background: white;
                    "
                >
                    ${options}
                </select>
            `;
        }


        // ==================================================
        // HTML DO ITEM
        // ==================================================

        div.innerHTML = `

            <div style="flex:1; min-width:0;">

                <div
                    class="item-nome"
                    style="
                        white-space:nowrap;
                        overflow:hidden;
                        text-overflow:ellipsis;
                        margin-bottom:2px;
                    "
                >
                    ${item.nome}
                </div>


                ${tamanhoHTML}


                <div class="item-preco-unit">
                    R$ ${item.preco.toFixed(2).replace('.', ',')} / un.
                </div>

            </div>


            <div class="item-qty-ctrl">

                <button
                    type="button"
                    class="qty-btn"
                    onclick="alterarQtd(${indice}, -1)"
                >
                    −
                </button>


                <span class="qty-value">
                    ${item.quantidade}
                </span>


                <button
                    type="button"
                    class="qty-btn"
                    onclick="alterarQtd(${indice}, 1)"
                >
                    +
                </button>

            </div>


            <div class="item-subtotal">
                R$ ${subtotalItem.toFixed(2).replace('.', ',')}
            </div>


            <button
                type="button"
                class="item-remover"
                onclick="removerItem(${indice})"
                title="Remover item"
            >
                ×
            </button>
        `;


        lista.appendChild(div);
    });


    // Verifica se existe produto aguardando tamanho
    const tamanhoPendente =
        carrinho.some(
            item =>
                item.tem_tamanho &&
                !item.tamanho_id
        );


    if (btnFinal) {

        btnFinal.disabled =
            carrinho.length === 0 ||
            tamanhoPendente;
    }


    renderizarTotais();
}


// ==========================================================
// RECALCULAR TOTAIS
// ==========================================================

function renderizarTotais() {

    const subtotal = carrinho.reduce(
        (acc, item) =>
            acc +
            (item.preco * item.quantidade),
        0
    );


    const descontoValor =
        clienteAtual.associado
            ? subtotal * (DESCONTO_PCT / 100)
            : 0;


    const total =
        subtotal - descontoValor;


    const formatarMoeda = valor =>
        'R$ ' +
        valor
            .toFixed(2)
            .replace('.', ',');


    const elemSubtotal =
        document.getElementById('val-subtotal');

    const elemTotal =
        document.getElementById('val-total');


    if (elemSubtotal)
        elemSubtotal.textContent =
            formatarMoeda(subtotal);


    if (elemTotal)
        elemTotal.textContent =
            formatarMoeda(total);


    const linhaDesc =
        document.getElementById('linha-desconto');

    const labelDesc =
        document.getElementById('label-desconto');

    const valDesc =
        document.getElementById('val-desconto');


    if (
        linhaDesc &&
        clienteAtual.associado &&
        descontoValor > 0
    ) {

        linhaDesc.style.display = 'flex';


        if (labelDesc)
            labelDesc.textContent =
                `Desconto (${DESCONTO_PCT}%)`;


        if (valDesc)
            valDesc.textContent =
                `− ${formatarMoeda(descontoValor)}`;

    } else if (linhaDesc) {

        linhaDesc.style.display = 'none';
    }
}


// ==========================================================
// FINALIZAR VENDA
// ==========================================================

function finalizarVenda() {

    if (carrinho.length === 0)
        return;


    // Não deixa finalizar sem escolher o tamanho
    const tamanhoPendente =
        carrinho.some(
            item =>
                item.tem_tamanho &&
                !item.tamanho_id
        );


    if (tamanhoPendente) {

        window.showToast?.('Selecione o tamanho de todos os produtos.', 'error');

        return;
    }


    const confirmarFinalizacao = () => {
    document.getElementById(
        'input-carrinho'
    ).value = JSON.stringify(

        carrinho.map(i => ({

            produto_id:
                parseInt(i.produto_id),

            tamanho_id:
                i.tamanho_id
                    ? parseInt(i.tamanho_id)
                    : null,

            tamanho:
                i.tamanho || null,

            nome:
                i.nome,

            preco:
                parseFloat(i.preco),

            quantidade:
                parseInt(i.quantidade)

        }))

    );


    document.getElementById(
        'input-cliente-id'
    ).value = clienteAtual.id;


    document.getElementById(
        'input-obs'
    ).value =
        document.getElementById(
            'obs-input'
        ).value;


    document.getElementById(
        'form-venda'
    ).submit();
    };

    window.openConfirmation({
        title: 'Finalizar venda?',
        message: 'Tem certeza que deseja finalizar esta venda?',
        cancelText: 'Voltar',
        confirmText: 'Finalizar venda',
        onConfirm: confirmarFinalizacao
    });
}


// ==========================================================
// FILTRO DE BUSCA
// ==========================================================

document
    .getElementById('busca-produto')
    ?.addEventListener(
        'input',
        function () {

            const termo =
                this.value
                    .toLowerCase()
                    .trim();


            document
                .querySelectorAll('.produto-card')
                .forEach(card => {

                    const nome =
                        card.getAttribute(
                            'data-nome-lower'
                        ) || '';


                    card.style.display =
                        nome.includes(termo)
                            ? ''
                            : 'none';
                });
        }
    );


// ==========================================================
// ATALHOS F2 E F8
// ==========================================================

window.addEventListener(
    'keydown',
    function (e) {

        if (e.key === 'F2') {

            e.preventDefault();

            document
                .getElementById(
                    'busca-produto'
                )
                ?.focus();
        }


        if (e.key === 'F8') {

            e.preventDefault();


            const btn =
                document.getElementById(
                    'btn-finalizar'
                );


            if (
                btn &&
                !btn.disabled
            ) {

                finalizarVenda();
            }
        }
    }
);


// ==========================================================
// CADASTRO DE USUÁRIO
// ==========================================================

function abrirModalCadastro() {

    window.location.href = "/usuarios";
}
