// Inicialização segura das variáveis globais
let carrinho = [];
let clienteAtual = { id: 0, associado: false };

// Captura a taxa de desconto definida no HTML através do data-attribute
const DESCONTO_PCT = parseFloat(document.getElementById('pdv-container')?.dataset.desconto) || 10.0;

// FUNÇÃO: Adicionar Item ao Carrinho (Multi-itens corrigidos)
function adicionarAoCarrinho(card) {
    const id = parseInt(card.getAttribute('data-id'));
    const nome = card.getAttribute('data-nome');
    const preco = parseFloat(card.getAttribute('data-preco'));
    const estoque = parseInt(card.getAttribute('data-estoque'));

    const existente = carrinho.find(item => item.produto_id === id);

    if (existente) {
        if (existente.quantidade < existente.estoque_max) {
            existente.quantidade++;
        } else {
            alert(`Limite de estoque atingido (${existente.estoque_max} un.).`);
            return;
        }
    } else {
        carrinho.push({
            produto_id: id,
            nome: nome,
            preco: preco,
            quantidade: 1,
            estoque_max: estoque
        });
    }

    renderizarCarrinho();
}

// FUNÇÃO: Alterar a quantidade usando os botões de + e -
function alterarQtd(produtoId, delta) {
    const item = carrinho.find(i => i.produto_id === parseInt(produtoId));
    if (!item) return;

    item.quantidade += delta;

    if (item.quantidade <= 0) {
        removerItem(produtoId);
        return;
    }

    if (item.quantidade > item.estoque_max) {
        alert(`Apenas ${item.estoque_max} unidades disponíveis no estoque.`);
        item.quantidade = item.estoque_max;
    }

    renderizarCarrinho();
}

// FUNÇÃO: Remover item completamente (Botão X)
function removerItem(produtoId) {
    carrinho = carrinho.filter(item => item.produto_id !== parseInt(produtoId));
    renderizarCarrinho();
}

// FUNÇÃO: Atualiza o status do desconto baseado no cliente escolhido
function atualizarCliente(select) {
    const opt = select.options[select.selectedIndex];
    clienteAtual.id = parseInt(opt.value);
    clienteAtual.associado = (opt.getAttribute('data-associado') === 'true');

    const badge = document.getElementById('badge-desconto');
    if (badge) {
        badge.style.display = clienteAtual.associado ? 'inline-flex' : 'none';
    }

    renderizarTotais();
}

// FUNÇÃO: Renderização Visual do Carrinho
function renderizarCarrinho() {
    const lista = document.getElementById('lista-carrinho');
    const vazio = document.getElementById('msg-vazio');
    const totais = document.getElementById('totais');
    const btnFinal = document.getElementById('btn-finalizar');

    if (!lista) return;

    if (carrinho.length === 0) {
        lista.innerHTML = '';
        if (vazio) vazio.style.display = 'flex';
        if (totais) totais.style.display = 'none';
        if (btnFinal) btnFinal.disabled = true;
        return;
    }

    if (vazio) vazio.style.display = 'none';
    if (totais) totais.style.display = 'block';
    if (btnFinal) btnFinal.disabled = false;

    lista.innerHTML = '';

    carrinho.forEach(item => {
        const subtotalItem = item.preco * item.quantidade;
        
        const div = document.createElement('div');
        div.className = 'item-carrinho';
        div.innerHTML = `
            <div style="flex:1; min-width:0;">
                <div class="item-nome" style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${item.nome}</div>
                <div class="item-preco-unit">R$ ${item.preco.toFixed(2).replace('.', ',')} / un.</div>
            </div>
            <div class="item-qty-ctrl">
                <button type="button" class="qty-btn" onclick="alterarQtd(${item.produto_id}, -1)">−</button>
                <span class="qty-value">${item.quantidade}</span>
                <button type="button" class="qty-btn" onclick="alterarQtd(${item.produto_id}, 1)">+</button>
            </div>
            <div class="item-subtotal">R$ ${subtotalItem.toFixed(2).replace('.', ',')}</div>
            <button type="button" class="item-remover" onclick="removerItem(${item.produto_id})" title="Remover item">×</button>
        `;
        lista.appendChild(div);
    });

    renderizarTotais();
}

// FUNÇÃO: Recalcula Valores Gerais do Rodapé Financeiro
function renderizarTotais() {
    const subtotal = carrinho.reduce((acc, item) => acc + (item.preco * item.quantidade), 0);
    const descontoValor = clienteAtual.associado ? (subtotal * (DESCONTO_PCT / 100)) : 0;
    const total = subtotal - descontoValor;

    const formatarMoeda = valor => 'R$ ' + valor.toFixed(2).replace('.', ',');

    const elemSubtotal = document.getElementById('val-subtotal');
    const elemTotal = document.getElementById('val-total');
    
    if (elemSubtotal) elemSubtotal.textContent = formatarMoeda(subtotal);
    if (elemTotal) elemTotal.textContent = formatarMoeda(total);

    const linhaDesc = document.getElementById('linha-desconto');
    const labelDesc = document.getElementById('label-desconto');
    const valDesc = document.getElementById('val-desconto');

    if (linhaDesc && clienteAtual.associado && descontoValor > 0) {
        linhaDesc.style.display = 'flex';
        if (labelDesc) labelDesc.textContent = `Desconto (${DESCONTO_PCT}%)`;
        if (valDesc) valDesc.textContent = `− ${formatarMoeda(descontoValor)}`;
    } else if (linhaDesc) {
        linhaDesc.style.display = 'none';
    }
}

// FUNÇÃO: Dispara a submissão final da venda
function finalizarVenda() {
    if (carrinho.length === 0) return;

    document.getElementById('input-carrinho').value = JSON.stringify(carrinho.map(i => ({
        produto_id: parseInt(i.produto_id),
        nome:       i.nome,
        preco:      parseFloat(i.preco),
        quantidade: parseInt(i.quantidade),
    })));

    document.getElementById('input-cliente-id').value = clienteAtual.id;
    document.getElementById('input-obs').value = document.getElementById('obs-input').value;

    document.getElementById('form-venda').submit();
}

// Filtro de Busca da Grade
document.getElementById('busca-produto')?.addEventListener('input', function () {
    const termo = this.value.toLowerCase().trim();
    document.querySelectorAll('.produto-card').forEach(card => {
        const nome = card.getAttribute('data-nome-lower') || '';
        card.style.display = nome.includes(termo) ? '' : 'none';
    });
});

// Atalhos Globais de Caixa (F2 e F8)
window.addEventListener('keydown', function(e) {
    if (e.key === 'F2') {
        e.preventDefault();
        document.getElementById('busca-produto')?.focus();
    }
    if (e.key === 'F8') {
        e.preventDefault();
        const btn = document.getElementById('btn-finalizar');
        if (btn && !btn.disabled) {
            finalizarVenda();
        }
    }
});

// FUNÇÃO: Redireciona o Administrador para a tela de cadastro
function abrirModalCadastro() {
    window.location.href = "/usuarios"; 
}