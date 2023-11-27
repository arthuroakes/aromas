import datetime
from fastapi import (APIRouter, Depends, Query, Request, Form, HTTPException, status, Path)
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.Usuario import Usuario
from repositories.ItemRepo import ItemRepo
from util.templateFilters import formatarData, formatarIdParaImagem
from util.security import validar_usuario_logado

router = APIRouter(prefix="/chat")
templates = Jinja2Templates(directory="templates")


@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData
    templates.env.filters["id_img"] = formatarIdParaImagem

@router.get("/chatcliente", response_class=HTMLResponse)
async def chat(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse("Cliente/chat.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho}) 

@router.get("/chatfuncionario", response_class=HTMLResponse)
async def sobrenos(request: Request, usuario: Usuario = Depends(validar_usuario_logado)): 
    return templates.TemplateResponse("Funcionario/chat.html", {"request": request, "usuario": usuario}) 