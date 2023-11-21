from fastapi import (APIRouter, Depends, Form, Query, Path, Request, status)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.Endereco import Endereco
from repositories.EnderecoRepo import EnderecoRepo
from repositories.ItemRepo import ItemRepo
from util.security import validar_usuario_logado
from util.templateFilters import (formatarData)
from util.validators import *
from models.Usuario import Usuario

router = APIRouter(prefix="/endereco")
templates = Jinja2Templates(directory="templates")


@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData

@router.get("/listagemenderecos", response_class=HTMLResponse)
async def listagemEndereco(
    request: Request,
    pa: int = Query(1, description="Página atual"),
    tp: int = Query(5, description="Tamanho da página"),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    enderecos = EnderecoRepo.obterPagina(pa, tp)
    totalPaginas = EnderecoRepo.obterQtdePaginas(tp) 
    return templates.TemplateResponse(
        "Endereco/listagemEndereco.html",
        {
            "request": request,
            "enderecos": enderecos, 
            "totalPaginas": totalPaginas,
            "paginaAtual": pa,
            "tamanhoPagina": tp,
            "usuario": usuario,
            "qtdeItensCarrinho": qtdeItensCarrinho
        }
    )

@router.get("/novoendereco")
async def getNovoEndereco(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse(
        "Endereco/novoEndereco.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho}
    )

@router.post("/novoendereco")
async def postNovoEndereco(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    cep: str = Form(""),
    rua: str = Form(""),
    numero: str = Form(""),
    complemento: str = Form(""),
    bairro: str = Form(""),
    cidade: str = Form(""),
    uf: str = Form(""),
):
    # Validação de dados
    erros = {}
    # Validação do campo cep
    is_not_empty(cep, "cep", erros)
    is_cep(cep, "cep", erros)
    # Validação do campo rua
    is_not_empty(rua, "rua", erros)
    # Validação do campo numero
    is_not_empty(numero, "numero", erros)
    # Validação do campo bairro
    is_not_empty(bairro, "bairro", erros)
    # Validação do campo estado
    is_not_empty(cidade, "cidade", erros)
    # Validação do campo uf
    is_not_empty(uf, "uf", erros)

    # se tem erro, mostra o formulário novamente
    if len(erros) > 0:
        valores = {}
        valores["cep"] = cep 
        valores["rua"] = rua
        valores["numero"] = numero 
        valores["bairro"] = bairro
        valores["cidade"] = cidade
        return templates.TemplateResponse(
            "Endereco/novoEndereco.html",
            {
                "request": request,
                "usuario": usuario,
                "erros": erros,
                "valores": valores,
            },
        )

    # Se não houver erros, insira o endereco no banco de dados
    if len(erros) == 0:
        # Crie um objeto Endereco com os dados fornecidos
        novo_endereco = Endereco(
            idEndereco=0,
            idCliente=usuario.idUsuario,
            cep=cep,
            rua=rua ,
            numero=numero,
            complemento=complemento,
            bairro=bairro,
            cidade=cidade,
            uf=uf,
        )

        # Insira o cliente no banco de dados
        novo_endereco = EnderecoRepo.insert(novo_endereco) 

    return RedirectResponse("/endereco/listagemenderecos", status_code=status.HTTP_303_SEE_OTHER)

# Rota para editar um produto
@router.get("/modificarendereco/{idEndereco:int}", response_class=HTMLResponse)
async def get_editar_endereco(
    request: Request,
    idEndereco: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    endereco = EnderecoRepo.obterEnderecoPorId(idEndereco)  
    if not endereco:
        return templates.TemplateResponse("Endereco/endereconaoencontrado.html", {"request": request}, status_code=404)
    return templates.TemplateResponse(
        "Endereco/editarEndereco.html",
        {"request": request, "usuario": usuario, "endereco": endereco, "qtdeItensCarrinho": qtdeItensCarrinho}
    )

# Post Modificar Categoria
@router.post("/modificarendereco/{idEndereco:int}", response_class=HTMLResponse)
async def post_editar_endereco(
    request: Request,
    idEndereco: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado),
    cep: str = Form(""),
    rua: str = Form(""),
    numero: str = Form(""),
    complemento: str = Form(""),
    bairro: str = Form(""),
    cidade: str = Form(""),
    uf: str = Form("")
):
    # Execute a lógica de edição de endereco aqui
    endereco = Endereco(
        idEndereco=idEndereco,
        idCliente=usuario.idUsuario,
        cep=cep,
        rua=rua ,
        numero=numero,
        complemento=complemento,
        bairro=bairro,
        cidade=cidade,
        uf=uf,
    )
    EnderecoRepo.update(endereco) 

    # Redirecione de volta para a página de detalhes do endereco após a edição
    return RedirectResponse("/endereco/listagemenderecos", status_code=status.HTTP_303_SEE_OTHER) 

@router.get("/excluirendereco/{idEndereco:int}", response_class=HTMLResponse)
async def get_excluir_categoria(
    request: Request,
    idEndereco: int,
    usuario: Usuario = Depends(validar_usuario_logado),
):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    # Verifique se o endereco existe
    endereco = EnderecoRepo.obterEnderecoPorId(idEndereco) 
    if not endereco:
        return templates.TemplateResponse("Endereco/endereconaoencontrado.html", {"request": request}, status_code=404)
    return templates.TemplateResponse(
        "Endereco/excluirEndereco.html",
        {"request": request, "endereco": endereco, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho}, 
    )


@router.post("/excluirendereco", response_class=HTMLResponse)
async def post_excluir_endereco(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idEndereco: int = Form(0),
):
    if EnderecoRepo.delete(idEndereco): 
        return RedirectResponse("/endereco/listagemenderecos",status_code=status.HTTP_303_SEE_OTHER,)
    else:
        raise Exception("Não foi possível excluir a categoria.")