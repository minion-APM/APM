# controllers/produto_controller.py
import os
import shutil
import uuid
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models.produto import Produto
from app.models.categoria import Categoria
from app.models.produto_tamanho import ProdutoTamanho
from app.auth import get_usuario_logado, get_admin
from app.pagination import paginate

router = APIRouter(prefix="/produtos", tags=["Produtos"])

templates = Jinja2Templates(directory="app/templates")

UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============================================================
# LISTAGEM
# ============================================================

@router.get("/")
def listar_produtos(
    request: Request,
    busca: str = "",
    categoria_id: int = 0,
    page: int = 1,
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado)
):
    query = db.query(Produto)

    if usuario['role'] != 'admin':
        query = query.filter(Produto.ativo == True)

    if busca:
        query = query.filter(Produto.nome.ilike(f"%{busca}%"))

    if categoria_id:
        query = query.filter(Produto.categoria_id == categoria_id)

    produtos, pagination = paginate(query.order_by(Produto.nome), page)
    categorias = db.query(Categoria).filter(Categoria.ativo == True).all()

    return templates.TemplateResponse(
        request,
        "produtos/index.html",
        {
            "request":      request,
            "usuario":      usuario,
            "produtos":     produtos,
            "categorias":   categorias,
            "pagination":   pagination,
            "busca":        busca,
            "categoria_id": categoria_id,
        }
    )


# ============================================================
# CADASTRO
# ============================================================

@router.get("/novo")
def form_novo_produto(
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    categorias = db.query(Categoria).filter(Categoria.ativo == True).all()

    return templates.TemplateResponse(
        request,
        "produtos/form.html",
        {
            "request":    request,
            "usuario":    admin,
            "editando":   None,
            "categorias": categorias
        }
    )


@router.post("/novo")
async def criar_produto(
    request: Request,
    nome: str                    = Form(...),
    preco: float                 = Form(...),
    estoque_atual: int           = Form(...),
    categoria_id: int            = Form(0),
    imagem: UploadFile           = File(None),
    tamanho_id: List[str]        = Form(default=[]),
    tamanho: List[str]           = Form(default=[]),
    tamanho_estoque: List[int]   = Form(default=[]),
    db: Session                  = Depends(get_db),
    admin                        = Depends(get_admin)
):
    categorias = db.query(Categoria).filter(Categoria.ativo == True).all()

    if db.query(Produto).filter(Produto.nome.ilike(nome)).first():
        return templates.TemplateResponse(
            request,
            "produtos/form.html",
            {
                "request":    request,
                "usuario":    admin,
                "editando":   None,
                "categorias": categorias,
                "erro":       "Já existe um produto com este nome.",
                "valores":    {"nome": nome, "preco": preco,
                               "estoque_atual": estoque_atual,
                               "categoria_id": categoria_id}
            },
            status_code=400
        )

    imagem_path = await _salvar_imagem(imagem)

    produto = Produto(
        nome          = nome,
        preco         = preco,
        estoque_atual = estoque_atual,
        categoria_id  = categoria_id or None,
        imagem_path   = imagem_path,
    )

    db.add(produto)
    db.flush()  # gera o produto.id sem commitar ainda

    # Salva os tamanhos
    for tam, est in zip(tamanho, tamanho_estoque):
        if tam:
            db.add(ProdutoTamanho(
                produto_id = produto.id,
                tamanho    = tam,
                estoque    = est
            ))

    db.commit()

    return RedirectResponse(url="/produtos?criado=ok", status_code=302)


# ============================================================
# DETALHE
# ============================================================

@router.get("/{produto_id}")
def detalhe_produto(
    produto_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_logado)
):
    produto = db.query(Produto).filter(
        Produto.id == produto_id,
        Produto.ativo == True
    ).first()

    if not produto:
        return RedirectResponse(url="/produtos", status_code=302)

    return templates.TemplateResponse(
        request,
        "produtos/index.html",
        {"request": request, "usuario": usuario, "produto": produto}
    )


# ============================================================
# EDIÇÃO
# ============================================================

@router.get("/{produto_id}/editar")
def form_editar_produto(
    produto_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    editando   = db.query(Produto).filter(Produto.id == produto_id).first()
    categorias = db.query(Categoria).filter(Categoria.ativo == True).all()

    if not editando:
        return RedirectResponse(url="/produtos", status_code=302)

    return templates.TemplateResponse(
        request,
        "produtos/form.html",
        {
            "request":    request,
            "usuario":    admin,
            "editando":   editando,
            "categorias": categorias
        }
    )


@router.post("/{produto_id}/editar")
async def editar_produto(
    produto_id: int,
    request: Request,
    nome: str                    = Form(...),
    preco: float                 = Form(...),
    estoque_atual: int           = Form(...),
    categoria_id: int            = Form(0),
    imagem: UploadFile           = File(None),
    tamanho_id: List[str]        = Form(default=[]),
    tamanho: List[str]           = Form(default=[]),
    tamanho_estoque: List[int]   = Form(default=[]),
    db: Session                  = Depends(get_db),
    admin                        = Depends(get_admin)
):
    editando   = db.query(Produto).filter(Produto.id == produto_id).first()
    categorias = db.query(Categoria).filter(Categoria.ativo == True).all()

    if not editando:
        return RedirectResponse(url="/produtos", status_code=302)

    conflito = db.query(Produto).filter(
        Produto.nome.ilike(nome),
        Produto.id != produto_id
    ).first()

    if conflito:
        return templates.TemplateResponse(
            request,
            "produtos/form.html",
            {
                "request":    request,
                "usuario":    admin,
                "editando":   editando,
                "categorias": categorias,
                "erro":       "Já existe outro produto com este nome.",
            },
            status_code=400
        )

    nova_imagem_path = await _salvar_imagem(imagem)

    if nova_imagem_path:
        _remover_imagem(editando.imagem_path)
        editando.imagem_path = nova_imagem_path

    editando.nome          = nome
    editando.preco         = preco
    editando.estoque_atual = estoque_atual
    editando.categoria_id  = categoria_id or None

    # Atualiza tamanhos
    ids_existentes = [tid for tid in tamanho_id if tid]  # ids que vieram do form

    # Remove os que não vieram mais no form
    for t in editando.tamanhos:
        if str(t.id) not in ids_existentes:
            db.delete(t)

    # Atualiza ou cria
    for tid, tam, est in zip(tamanho_id, tamanho, tamanho_estoque):
        if not tam:
            continue
        if tid:  # já existe no banco, atualiza
            registro = db.query(ProdutoTamanho).filter(ProdutoTamanho.id == int(tid)).first()
            if registro:
                registro.tamanho = tam
                registro.estoque = est
        else:  # novo tamanho, cria
            db.add(ProdutoTamanho(
                produto_id = produto_id,
                tamanho    = tam,
                estoque    = est
            ))

    db.commit()

    return RedirectResponse(url="/produtos?editado=ok", status_code=302)


# ============================================================
# DESATIVAR
# ============================================================

@router.post("/{produto_id}/desativar")
def desativar_produto(
    produto_id: int,
    db: Session = Depends(get_db),
    admin = Depends(get_admin)
):
    produto = db.query(Produto).filter(Produto.id == produto_id).first()

    if not produto:
        return RedirectResponse(url="/produtos", status_code=302)

    produto.ativo = not produto.ativo
    db.commit()

    status = "ativado" if produto.ativo else "desativado"
    return RedirectResponse(url=f"/produtos?{status}=ok", status_code=302)


# ============================================================
# FUNÇÕES AUXILIARES DE IMAGEM
# ============================================================

async def _salvar_imagem(imagem: UploadFile | None):
    if not imagem or not imagem.filename:
        return None

    extensoes_permitidas = {".jpg", ".jpeg", ".png", ".webp"}
    _, ext = os.path.splitext(imagem.filename.lower())

    if ext not in extensoes_permitidas:
        return None

    nome_arquivo     = f"{uuid.uuid4()}{ext}"
    caminho_completo = os.path.join(UPLOAD_DIR, nome_arquivo)

    with open(caminho_completo, "wb") as buffer:
        shutil.copyfileobj(imagem.file, buffer)

    return f"uploads/{nome_arquivo}"


def _remover_imagem(imagem_path: str | None) -> None:
    if not imagem_path:
        return

    caminho = os.path.join("app/static", imagem_path)

    if os.path.exists(caminho):
        os.remove(caminho)
