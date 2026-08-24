import json

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.venda import Venda, ItemVenda
from app.models.produto import Produto
from app.models.produto_tamanho import ProdutoTamanho
from app.models.cliente import Cliente
from app.auth import get_usuario_logado
from app.pagination import paginate


router = APIRouter(prefix="/pdv", tags=["PDV"])
templates = Jinja2Templates(directory="app/templates")

DESCONTO_ASSOCIADO = 10.0


@router.get("/")
def tela_pdv(
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    produtos = (
        db.query(Produto)
        .filter(
            Produto.ativo == True,
            Produto.estoque_atual > 0
        )
        .order_by(Produto.nome)
        .all()
    )

    clientes = (
        db.query(Cliente)
        .filter(Cliente.ativo == True)
        .order_by(Cliente.nome)
        .all()
    )

    return templates.TemplateResponse(
        request,
        "pdv/index.html",
        {
            "request": request,
            "usuario": usuario,
            "produtos": produtos,
            "clientes": clientes,
            "desconto_associado": DESCONTO_ASSOCIADO,
        }
    )


@router.post("/finalizar")
def finalizar_venda(
    request: Request,
    carrinho_json: str = Form(...),
    cliente_id: int = Form(0),
    observacao: str = Form(""),
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    try:
        itens = json.loads(carrinho_json)
    except (json.JSONDecodeError, ValueError):
        return RedirectResponse("/pdv?erro=json", 302)

    if not itens:
        return RedirectResponse("/pdv?erro=vazio", 302)

    cliente = None
    desconto_percentual = 0.0

    if cliente_id:
        cliente = db.query(Cliente).filter(
            Cliente.id == cliente_id,
            Cliente.ativo == True
        ).first()

        if cliente and cliente.is_associado:
            desconto_percentual = DESCONTO_ASSOCIADO

    total_bruto = 0.0
    itens_validados = []

    for item in itens:
        produto = db.query(Produto).filter(
            Produto.id == int(item["produto_id"]),
            Produto.ativo == True
        ).with_for_update().first()

        if not produto:
            return RedirectResponse("/pdv?erro=produto", 302)

        quantidade = int(item.get("quantidade", 0))

        if quantidade <= 0:
            return RedirectResponse("/pdv?erro=quantidade", 302)

        tamanho = None

        if produto.tamanhos:
            tamanho_id = item.get("tamanho_id")

            if not tamanho_id:
                return RedirectResponse("/pdv?erro=tamanho", 302)

            tamanho = db.query(ProdutoTamanho).filter(
                ProdutoTamanho.id == int(tamanho_id),
                ProdutoTamanho.produto_id == produto.id
            ).with_for_update().first()

            if not tamanho:
                return RedirectResponse("/pdv?erro=tamanho", 302)

            if tamanho.estoque < quantidade:
                return RedirectResponse("/pdv?erro=estoque", 302)

        else:
            if produto.estoque_atual < quantidade:
                return RedirectResponse("/pdv?erro=estoque", 302)

        total_bruto += produto.preco * quantidade

        itens_validados.append({
            "produto": produto,
            "tamanho": tamanho,
            "quantidade": quantidade,
            "preco": produto.preco,
        })

    desconto_valor = total_bruto * (desconto_percentual / 100)
    total_liquido = total_bruto - desconto_valor

    venda = Venda(
        cliente_id=cliente.id if cliente else None,
        usuario_id=usuario.get("id"),
        desconto_percentual=desconto_percentual,
        total_bruto=round(total_bruto, 2),
        total_liquido=round(total_liquido, 2),
        observacao=observacao or None,
    )

    db.add(venda)
    db.flush()

    for item in itens_validados:
        produto = item["produto"]
        tamanho = item["tamanho"]
        quantidade = item["quantidade"]

        nome_item = produto.nome

        if tamanho:
            nome_item += f" ({tamanho.tamanho})"

        db.add(
            ItemVenda(
                venda_id=venda.id,
                produto_id=produto.id,
                produto_nome=nome_item,
                quantidade=quantidade,
                preco_unitario=item["preco"],
            )
        )

        if tamanho:
            tamanho.estoque -= quantidade

            produto.estoque_atual = sum(
                t.estoque for t in produto.tamanhos
            )
        else:
            produto.estoque_atual -= quantidade

    db.commit()

    return RedirectResponse(
        f"/pdv/venda/{venda.id}?sucesso=ok",
        302
    )


@router.get("/venda/{venda_id}")
def detalhe_venda(
    venda_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    venda = db.query(Venda).filter(
        Venda.id == venda_id
    ).first()

    if not venda:
        return RedirectResponse("/pdv", 302)

    return templates.TemplateResponse(
        request,
        "pdv/comprovante.html",
        {
            "request": request,
            "usuario": usuario,
            "venda": venda,
        }
    )


@router.get("/historico")
def historico_vendas(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado)
):
    vendas, pagination = paginate(
        db.query(Venda).order_by(Venda.criado_em.desc()), page
    )

    return templates.TemplateResponse(
        request,
        "pdv/historico.html",
        {
            "request": request,
            "usuario": usuario,
            "vendas": vendas,
            "pagination": pagination,
        }
    )
