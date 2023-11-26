from datetime import date
from fastapi import (APIRouter, Depends, Query, Path, Request, Form, HTTPException, status)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.Reserva import Reserva
from repositories.ItemRepo import ItemRepo
from repositories.MesaRepo import MesaRepo
from models.Usuario import Usuario
from repositories.ReservaRepo import ReservaRepo
from util.templateFilters import (formatarData)
from util.security import validar_usuario_logado

router = APIRouter(prefix="/reserva")
templates = Jinja2Templates(directory="templates")


@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData

@router.get("/listagemreservas", response_class=HTMLResponse)
async def listagem_reservas(
    request: Request,
    pa: int = Query(1, description="Página atual"),
    tp: int = Query(10, description="Tamanho da página"),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    if usuario:
        if usuario.admin or usuario.funcionario:
            reservas = ReservaRepo.obterReserva(pa, tp)
            totalPaginas = ReservaRepo.obterQtdeReservas(tp)
            return templates.TemplateResponse(
                "Reserva/listagemReserva.html",
                {
                    "request": request,
                    "reservas": reservas,
                    "totalPaginas": totalPaginas,
                    "paginaAtual": pa,
                    "tamanhoPagina": tp,
                    "usuario": usuario,
                },
            )
        else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@router.get("/modificarreserva/{idReserva:int}") 
async def getEditarReserva(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado), idReserva: int = Path()
): 
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    reserva = ReservaRepo.obterReservaPorId(idReserva)
    mesas = MesaRepo.getAll()
    return templates.TemplateResponse(
        "Reserva/editarReserva.html", {"request": request, "usuario": usuario, "reserva": reserva, "mesas": mesas, "qtdeItensCarrinho": qtdeItensCarrinho} 
    )

@router.post("/modificarreserva/{idReserva:int}", response_class=HTMLResponse)
async def post_editar_reserva(
    request: Request,
    idReserva: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado),
    idMesa: int = Form(0),
    dataReserva: date = Form(...),
    horaReserva: str = Form(...), 
    qtdPessoas: int = Form(...),
):
    # Execute a lógica de edição de reserva aqui
    reserva = Reserva(
        idReserva=idReserva,
        idMesa=idMesa,
        dataReserva=dataReserva,
        horaReserva=horaReserva,
        qtdPessoas=qtdPessoas
    )
    ReservaRepo.update(reserva)

    # Redirecione de volta para a página de detalhes da reserva após a edição
    return RedirectResponse("/reserva/listagemreservas", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/novareserva", response_class=HTMLResponse)
async def get_nova_reserva(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    qtdeItensCarrinho = 0 
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    mesas = MesaRepo.getAll() 
    return templates.TemplateResponse(
        "Reserva/novaReserva.html", {"request": request, "usuario": usuario, "mesas": mesas, "qtdeItensCarrinho": qtdeItensCarrinho} 
    )

@router.post("/novareserva", response_class=HTMLResponse)
async def post_nova_reserva(
    request: Request, 
    usuario: Usuario = Depends(validar_usuario_logado),
    idMesa: int = Form(0),
    dataReserva: date = Form(...),
    horaReserva: str = Form(...), 
    qtdPessoas: int = Form(...), 
):
    # tratamento de erros
    erros = {}

    if len(erros) > 0:
        valores = {}
        valores["idMesa"] = idMesa 
        valores["dataReserva"] = dataReserva
        valores["horaReserva"] = horaReserva
        valores["qtdPessoas"] = qtdPessoas
        return templates.TemplateResponse(
            "Reserva/novoReserva.html",
            {
                "request": request,
                "usuario": usuario,
                "erros": erros,
                "valores": valores,
            },
        )
    
    ReservaRepo.insert(
        Reserva(
            idReserva=0,
            idCliente=usuario.idUsuario,
            idMesa=idMesa,
            dataReserva=dataReserva,
            horaReserva=horaReserva,
            qtdPessoas=qtdPessoas,
        )
    )

    return RedirectResponse("/cliente/minhasreservas", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/excluirreserva/{idReserva:int}", response_class=HTMLResponse)
async def get_excluir_reserva(
    request: Request,
    idReserva: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    # Verifique se a reserva existe
    reserva = ReservaRepo.obterReservaPorId(idReserva)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")

    # Renderize a página de confirmação de exclusão
    return templates.TemplateResponse(
        "Reserva/excluirReserva.html",
        {"request": request, "reserva": reserva, "usuario": usuario}, 
    )


@router.post("/excluirreserva", response_class=HTMLResponse)
async def post_excluir_reserva(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idReserva: int = Form(0),
):
    if ReservaRepo.delete(idReserva): 
        if usuario.funcionario: 
            return RedirectResponse("/reserva/listagemreservas", status_code=status.HTTP_303_SEE_OTHER)
        else:
            return RedirectResponse("/cliente/minhasreservas", status_code=status.HTTP_303_SEE_OTHER)
    else:
        raise Exception("Não foi possível excluir a reserva.")
