# ============================================================
# controllers/movimentacao_controller.py
# ============================================================

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.movimentacao import Movimentacao, Tipo_de_movimentacao
from app.models.produto import Produto
from app.models.produto_tamanho import ProdutoTamanho
from app.auth import get_usuario_logado, get_admin
from app.pagination import paginate


router = APIRouter(
    prefix="/movimentacoes",
    tags=["Movimentações"]
)

templates = Jinja2Templates(directory="app/templates")


# ============================================================
# HISTÓRICO GERAL
# ============================================================

@router.get("/")
def listar_movimentacoes(
    request: Request,
    produto_id: int = 0,
    tipo: str = "",
    page: int = 1,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    query = db.query(Movimentacao).order_by(
        Movimentacao.criado_em.desc()
    )

    if produto_id:
        query = query.filter(
            Movimentacao.produto_id == produto_id
        )

    if tipo in ("entrada", "saida", "cancelamento", "ajuste"):
        query = query.filter(
            Movimentacao.tipo == tipo
        )

    movimentacoes, pagination = paginate(query, page)

    produtos = db.query(Produto).filter(
        Produto.ativo == True
    ).all()

    return templates.TemplateResponse(
        request,
        "movimentacoes/index.html",
        {
            "request": request,
            "usuario": admin,
            "movimentacoes": movimentacoes,
            "produtos": produtos,
            "produto_id": produto_id,
            "tipo": tipo,
            "pagination": pagination,
        }
    )


# ============================================================
# FORMULÁRIO
# ============================================================

@router.get("/nova")
def form_nova_movimentacao(
    request: Request,
    produto_id: int = 0,
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado)
):
    produtos = db.query(Produto).filter(
        Produto.ativo == True
    ).all()

    return templates.TemplateResponse(
        request,
        "movimentacoes/form.html",
        {
            "request": request,
            "usuario": usuario,
            "produtos": produtos,
            "produto_id": produto_id,
            "tipos": Tipo_de_movimentacao,
        }
    )


# ============================================================
# REGISTRAR MOVIMENTAÇÃO
# ============================================================

@router.post("/nova")
def registrar_movimentacao(
    request: Request,
    produto_id: int = Form(...),
    tamanho_id: int = Form(0),
    tipo: str = Form(...),
    quantidade: int = Form(...),
    preco_unitario: float = Form(...),
    observacao: str = Form(""),
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado)
):

    produtos = db.query(Produto).filter(
        Produto.ativo == True
    ).all()


    # ========================================================
    # VALIDA TIPO
    # ========================================================

    if tipo not in (
        Tipo_de_movimentacao.ENTRADA,
        Tipo_de_movimentacao.SAIDA
    ):
        return templates.TemplateResponse(
            request,
            "movimentacoes/form.html",
            {
                "request": request,
                "usuario": usuario,
                "produtos": produtos,
                "produto_id": produto_id,
                "tipos": Tipo_de_movimentacao,
                "erro": "Tipo de movimentação inválido.",
            },
            status_code=400
        )


    # ========================================================
    # VALIDA QUANTIDADE
    # ========================================================

    if quantidade <= 0:
        return templates.TemplateResponse(
            request,
            "movimentacoes/form.html",
            {
                "request": request,
                "usuario": usuario,
                "produtos": produtos,
                "produto_id": produto_id,
                "tipos": Tipo_de_movimentacao,
                "erro": "A quantidade deve ser maior que zero.",
            },
            status_code=400
        )


    # ========================================================
    # BUSCA PRODUTO
    # ========================================================

    produto = db.query(Produto).filter(
        Produto.id == produto_id
    ).with_for_update().first()

    if not produto:
        return RedirectResponse(
            url="/movimentacoes/nova",
            status_code=302
        )


    tamanho_movimentado = None


    # ========================================================
    # PRODUTO COM TAMANHO
    # ========================================================

    if produto.tamanhos:

        tamanho_movimentado = db.query(
            ProdutoTamanho
        ).filter(
            ProdutoTamanho.id == tamanho_id,
            ProdutoTamanho.produto_id == produto.id
        ).with_for_update().first()


        if not tamanho_movimentado:
            return templates.TemplateResponse(
                request,
                "movimentacoes/form.html",
                {
                    "request": request,
                    "usuario": usuario,
                    "produtos": produtos,
                    "produto_id": produto_id,
                    "tipos": Tipo_de_movimentacao,
                    "erro": "Selecione um tamanho.",
                },
                status_code=400
            )


        # SAÍDA
        if tipo == Tipo_de_movimentacao.SAIDA:

            if quantidade > tamanho_movimentado.estoque:

                return templates.TemplateResponse(
                    request,
                    "movimentacoes/form.html",
                    {
                        "request": request,
                        "usuario": usuario,
                        "produtos": produtos,
                        "produto_id": produto_id,
                        "tipos": Tipo_de_movimentacao,
                        "erro": (
                            f"Estoque insuficiente no tamanho "
                            f"{tamanho_movimentado.tamanho}. "
                            f"Disponível: "
                            f"{tamanho_movimentado.estoque}."
                        ),
                    },
                    status_code=400
                )

            tamanho_movimentado.estoque -= quantidade


        # ENTRADA
        else:
            tamanho_movimentado.estoque += quantidade


        # Atualiza o estoque total do produto
        produto.estoque_atual = sum(
            t.estoque
            for t in produto.tamanhos
        )


    # ========================================================
    # PRODUTO SEM TAMANHO
    # ========================================================

    else:

        # SAÍDA
        if tipo == Tipo_de_movimentacao.SAIDA:

            if quantidade > produto.estoque_atual:

                return templates.TemplateResponse(
                    request,
                    "movimentacoes/form.html",
                    {
                        "request": request,
                        "usuario": usuario,
                        "produtos": produtos,
                        "produto_id": produto_id,
                        "tipos": Tipo_de_movimentacao,
                        "erro": (
                            f"Estoque insuficiente. "
                            f"Disponível: "
                            f"{produto.estoque_atual}."
                        ),
                    },
                    status_code=400
                )

            produto.estoque_atual -= quantidade


        # ENTRADA
        else:
            produto.estoque_atual += quantidade


    # ========================================================
    # SALVA MOVIMENTAÇÃO
    # ========================================================

    movimentacao = Movimentacao(
        tipo=tipo,
        quantidade=quantidade,
        preco_unitario=preco_unitario,
        observacao=observacao or None,
        produto_id=produto_id,

        tamanho_id=(
            tamanho_movimentado.id
            if tamanho_movimentado
            else None
        ),

        usuario_id=usuario.get("id"),
    )

    db.add(movimentacao)
    db.commit()


    return RedirectResponse(
        url="/movimentacoes?movimentacao=ok",
        status_code=302
    )


# ============================================================
# HISTÓRICO POR PRODUTO
# ============================================================

@router.get("/produto/{produto_id}")
def historico_produto(
    produto_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado)
):

    produto = db.query(Produto).filter(
        Produto.id == produto_id
    ).first()

    if not produto:
        return RedirectResponse(
            url="/produtos",
            status_code=302
        )


    movimentacoes = (
        db.query(Movimentacao)
        .filter(
            Movimentacao.produto_id == produto_id
        )
        .order_by(
            Movimentacao.criado_em.desc()
        )
        .all()
    )


    total_entradas = sum(
        m.quantidade
        for m in movimentacoes
        if m.tipo == Tipo_de_movimentacao.ENTRADA
    )


    total_saidas = sum(
        m.quantidade
        for m in movimentacoes
        if m.tipo == Tipo_de_movimentacao.SAIDA
    )


    return templates.TemplateResponse(
        request,
        "movimentacoes/historico.html",
        {
            "request": request,
            "usuario": usuario,
            "produto": produto,
            "movimentacoes": movimentacoes,
            "total_entradas": total_entradas,
            "total_saidas": total_saidas,
        }
    )
