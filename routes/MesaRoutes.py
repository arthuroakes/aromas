from fastapi import (APIRouter, Depends, Query, Request, Path, Form, HTTPException, status)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.Mesa import Mesa
from repositories.MesaRepo import MesaRepo
from models.Usuario import Usuario
from repositories.ReservaRepo import ReservaRepo
from util.templateFilters import (formatarData)
from util.security import validar_usuario_logado
from util.validators import is_not_empty

router = APIRouter(prefix="/mesa")
templates = Jinja2Templates(directory="templates")


@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData

@router.get("/reservanamesa", response_class=HTMLResponse)
async def produto_em_algum_pedido(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    return templates.TemplateResponse("Reserva/reservanamesa.html", {"request": request, "usuario": usuario})

@router.get("/listagemmesas", response_class=HTMLResponse)
async def listagem_mesas(
    request: Request,
    pa: int = Query(1, description="Página atual"),
    tp: int = Query(6, description="Tamanho da página"),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    if usuario:
        if usuario.admin or usuario.funcionario:
            mesas = MesaRepo.obterMesa(pa, tp)
            totalPaginas = MesaRepo.obterQtdeMesas(tp)
            return templates.TemplateResponse(
                "Reserva/listagemMesa.html",
                {
                    "request": request,
                    "mesas": mesas,
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

@router.get("/novamesa", response_class=HTMLResponse)
async def nova_mesa(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    return templates.TemplateResponse(
        "Reserva/novaMesa.html", {"request": request, "usuario": usuario}
    )

# Post Nova Categoria
@router.post("/novamesa")
async def post_cadastrar_categoria(
    request: Request,
    numero: str = Form(...),
    assentos: str = Form(...), 
): 
    # Validação de dados
    erros = {}
    # Validação do campo numero
    is_not_empty(numero, "numero", erros)
    # Validação do campo assento
    is_not_empty(assentos, "assentos", erros) 

    mesa_existente = MesaRepo.obterPorNumero(numero) 
    if mesa_existente: 
        return RedirectResponse(
            f"/mesa/novamesa?error=A mesa com o número '{numero}' já existe.", 
            status_code=status.HTTP_303_SEE_OTHER
        ) 

    if len(erros) > 0:
        valores = {}
        valores["numero"] = numero
        valores["assentos"] = assentos
        return templates.TemplateResponse(
            "Reserva/novaMesa.html",
            {
                "request": request,
                "erros": erros,
                "valores": valores,
            },
        )
    
    # Crie a mesa com os dados fornecidos
    MesaRepo.insert(
        Mesa(
            idMesa=0, 
            numero=numero,
            assentos=assentos,
        )
    )

    response = RedirectResponse("/mesa/listagemmesas", status.HTTP_302_FOUND) 
    return response

@router.get("/modificarmesa/{idMesa:int}", response_class=HTMLResponse)
async def get_editar_mesa(
    request: Request,
    idMesa: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    mesa = MesaRepo.obterMesaPorId(idMesa)  
    if not mesa:
        return templates.TemplateResponse("Reserva/mesanaoencontrada.html", {"request": request}, status_code=404)
    return templates.TemplateResponse(
        "Reserva/editarMesa.html",
        {"request": request, "usuario": usuario, "mesa": mesa}, 
    )

# Post Modificar Mesa
@router.post("/modificarmesa/{idMesa:int}", response_class=HTMLResponse)
async def post_editar_mesa(
    request: Request,
    idMesa: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado),
    numero: str = Form(...),
    assentos: str = Form(...),
):
    # Execute a lógica de edição de mesa aqui
    mesa = Mesa(
        idMesa=idMesa,  
        numero=numero,
        assentos=assentos
    )
    MesaRepo.update(mesa)

    # Redirecione de volta para a página de detalhes da mesa após a edição
    return RedirectResponse("/mesa/listagemmesas", status_code=status.HTTP_303_SEE_OTHER)

# Rota para excluir uma mesa
@router.get("/excluirmesa/{idMesa:int}", response_class=HTMLResponse)
async def get_excluir_mesa(
    request: Request,
    idMesa: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    # Verificar se há reservas associadas a esta mesa
    if ReservaRepo.exists_reserva_with_mesa(idMesa): 
        return RedirectResponse("/mesa/reservanamesa", status_code=303)
    # Verifique se a mesa existe
    mesa = MesaRepo.obterMesaPorId(idMesa)
    if not mesa:
         return templates.TemplateResponse("mesanaoencontrada.html", {"request": request}, status_code=404)

    # Renderize a página de confirmação de exclusão
    return templates.TemplateResponse(
        "Reserva/excluirMesa.html",
        {"request": request, "mesa": mesa, "usuario": usuario},
    )


@router.post("/excluirmesa", response_class=HTMLResponse)
async def post_excluir_mesa(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idMesa: int = Form(0),
):
    if MesaRepo.delete(idMesa): 
        return RedirectResponse(
            "/mesa/listagemmesas",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    else:
        raise Exception("Não foi possível excluir a mesa.")