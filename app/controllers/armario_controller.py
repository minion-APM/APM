from datetime import date, datetime, time

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.auth import get_admin, get_usuario_logado
from app.database import get_db
from app.models.armario import AluguelArmario, Armario
from app.models.cliente import Cliente
from app.pagination import paginate


router = APIRouter(prefix="/armarios", tags=["Armários"])
templates = Jinja2Templates(directory="app/templates")

STATUS_VALIDOS = {"disponivel", "bloqueado", "manutencao"}


@router.get("/")
def listar_armarios(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado),
):
    armarios, pagination = paginate(
        db.query(Armario).order_by(Armario.numero), page
    )
    return templates.TemplateResponse(
        request,
        "armarios/index.html",
        {
            "request": request,
            "usuario": usuario,
            "armarios": armarios,
            "pagination": pagination,
        },
    )


@router.get("/novo")
def form_novo_armario(request: Request, admin=Depends(get_admin)):
    return templates.TemplateResponse(
        request,
        "armarios/form.html",
        {"request": request, "usuario": admin, "editando": None},
    )


@router.get("/historico")
def historico_alugueis(
    request: Request,
    page: int = 1,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado),
):
    alugueis, pagination = paginate(
        db.query(AluguelArmario).order_by(AluguelArmario.inicio_em.desc()),
        page,
    )
    return templates.TemplateResponse(
        request,
        "armarios/historico.html",
        {
            "request": request,
            "usuario": usuario,
            "alugueis": alugueis,
            "pagination": pagination,
        },
    )


@router.get("/{armario_id}/alugar")
def escolher_cliente(
    armario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado),
):
    armario = db.query(Armario).filter(Armario.id == armario_id).first()
    if not armario or armario.status != "disponivel":
        return RedirectResponse("/armarios?erro=aluguel", status_code=302)

    return templates.TemplateResponse(
        request,
        "armarios/alugar.html",
        {
            "request": request,
            "usuario": usuario,
            "armario": armario,
            "modo": "alugar",
            "data_padrao": date.today().isoformat(),
            "hora_padrao": datetime.now().strftime("%H:%M"),
        },
    )


@router.post("/novo")
def criar_armario(
    request: Request,
    numero: str = Form(...),
    descricao: str = Form(""),
    status_armario: str = Form("disponivel"),
    db: Session = Depends(get_db),
    admin=Depends(get_admin),
):
    numero = numero.strip()
    if not numero or status_armario not in STATUS_VALIDOS:
        return _render_form(request, admin, None, numero, descricao, "Dados inválidos.")

    if db.query(Armario).filter(Armario.numero.ilike(numero)).first():
        return _render_form(
            request, admin, None, numero, descricao,
            "Já existe um armário com este número ou nome.",
        )

    db.add(Armario(numero=numero, descricao=descricao.strip() or None, status=status_armario))
    db.commit()
    return RedirectResponse("/armarios?criado=ok", status_code=302)


@router.get("/{armario_id}/editar")
def form_editar_armario(
    armario_id: int,
    request: Request,
    db: Session = Depends(get_db),
    admin=Depends(get_admin),
):
    armario = db.query(Armario).filter(Armario.id == armario_id).first()
    if not armario:
        return RedirectResponse("/armarios", status_code=302)
    return templates.TemplateResponse(
        request,
        "armarios/alugar.html",
        {
            "request": request,
            "usuario": admin,
            "armario": armario,
            "modo": "editar",
        },
    )


@router.post("/{armario_id}/editar")
def editar_armario(
    armario_id: int,
    request: Request,
    descricao: str = Form(""),
    status_armario: str = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(get_admin),
):
    armario = db.query(Armario).filter(Armario.id == armario_id).first()
    if not armario:
        return RedirectResponse("/armarios", status_code=302)

    if status_armario not in STATUS_VALIDOS or armario.status == "alugado":
        return RedirectResponse(f"/armarios/{armario_id}/editar?erro=status", 302)
    armario.descricao = descricao.strip() or None
    armario.status = status_armario
    db.commit()
    return RedirectResponse("/armarios?editado=ok", status_code=302)


@router.post("/{armario_id}/status")
def alterar_status(
    armario_id: int,
    status_armario: str = Form(...),
    db: Session = Depends(get_db),
    admin=Depends(get_admin),
):
    armario = db.query(Armario).filter(Armario.id == armario_id).first()
    if not armario or status_armario not in STATUS_VALIDOS:
        return RedirectResponse("/armarios?erro=status", status_code=302)
    if armario.status == "alugado":
        return RedirectResponse("/armarios?erro=alugado", status_code=302)

    armario.status = status_armario
    db.commit()
    return RedirectResponse("/armarios?status=ok", status_code=302)


@router.post("/{armario_id}/alugar")
def alugar_armario(
    armario_id: int,
    cliente: str = Form(...),
    dia: date = Form(...),
    hora: time = Form(...),
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado),
):
    armario = db.query(Armario).filter(Armario.id == armario_id).with_for_update().first()
    identificacao = cliente.strip()
    cliente_encontrado = db.query(Cliente).filter(
        Cliente.ativo == True,
        or_(
            func.lower(Cliente.nome) == identificacao.lower(),
            func.lower(Cliente.matricula) == identificacao.lower(),
        ),
    ).first()
    if not armario or armario.status != "disponivel" or not cliente_encontrado:
        return RedirectResponse(f"/armarios/{armario_id}/alugar?erro=cliente", status_code=302)

    armario.status = "alugado"
    armario.cliente_id = cliente_encontrado.id
    inicio_em = datetime.combine(dia, hora)
    armario.alugado_em = inicio_em
    db.add(AluguelArmario(
        armario_id=armario.id,
        cliente_id=cliente_encontrado.id,
        usuario_id=usuario.get("id"),
        inicio_em=inicio_em,
    ))
    db.commit()
    return RedirectResponse("/armarios?alugado=ok", status_code=302)


@router.post("/{armario_id}/devolver")
def devolver_armario(
    armario_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_logado),
):
    armario = db.query(Armario).filter(Armario.id == armario_id).with_for_update().first()
    if not armario or armario.status != "alugado":
        return RedirectResponse("/armarios?erro=devolucao", status_code=302)

    armario.status = "disponivel"
    armario.cliente_id = None
    armario.alugado_em = None
    aluguel = db.query(AluguelArmario).filter(
        AluguelArmario.armario_id == armario.id,
        AluguelArmario.devolvido_em.is_(None),
    ).order_by(AluguelArmario.id.desc()).first()
    if aluguel:
        aluguel.devolvido_em = datetime.now()
    db.commit()
    return RedirectResponse("/armarios?devolvido=ok", status_code=302)


def _render_form(request, usuario, editando, numero, descricao, erro):
    return templates.TemplateResponse(
        request,
        "armarios/form.html",
        {
            "request": request,
            "usuario": usuario,
            "editando": editando,
            "valores": {"numero": numero, "descricao": descricao},
            "erro": erro,
        },
        status_code=400,
    )
