from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from app.database import get_db
from sqlalchemy.orm import Session

from app.controllers import auth_controller
from app.controllers import admin_controller
from app.controllers import categoria_controller
from app.controllers import produto_controller
from app.controllers import movimentacao_controller
from app.controllers import cliente_controller
from app.controllers import pdv_controller

from app.models.produto import Produto
from app.models.categoria import Categoria
from app.models.usuario import Usuario
from app.models.movimentacao import Movimentacao

from app.auth import get_usuario_opcional

app = FastAPI(title="Sistema MVC")

#Configurar o fastapi para servir os arquivos CSS, JS, IMG
app.mount("/static", StaticFiles(directory="app/static"), name="static")

#Configura para renderizar os templates HTML
templates = Jinja2Templates(directory="app/templates")

# Inclui os routeres do controller
app.include_router(auth_controller.router)
app.include_router(admin_controller.router)
app.include_router(categoria_controller.router)
app.include_router(produto_controller.router)
app.include_router(movimentacao_controller.router)
app.include_router(cliente_controller.router)
app.include_router(pdv_controller.router)

@app.get("/")
def tela_home(
    request: Request,
    usuario = Depends(get_usuario_opcional),
    db = Depends(get_db)
):
    if usuario is None:
        return templates.TemplateResponse(request, "index.html", {"request": request})
        
    # Contagens (o que já estava funcionando)
    total_produtos = db.query(Produto).count()
    total_categorias = db.query(Categoria).count()
    total_usuarios = db.query(Usuario).count()
    total_movimentacoes = db.query(Movimentacao).count()

    # NOVO: Busca as 4 últimas movimentações/vendas e os 3 últimos produtos cadastrados
    ultimas_movimentacoes = db.query(Movimentacao).order_by(Movimentacao.id.desc()).limit(4).all()
    ultimos_produtos = db.query(Produto).order_by(Produto.id.desc()).limit(3).all()

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "request": request, 
            "usuario": usuario,
            "total_produtos": total_produtos,
            "total_categorias": total_categorias,
            "total_usuarios": total_usuarios,
            "total_movimentacoes": total_movimentacoes,
            "ultimas_movimentacoes": ultimas_movimentacoes, # Enviando pro HTML
            "ultimos_produtos": ultimos_produtos           # Enviando pro HTML
        }
    )