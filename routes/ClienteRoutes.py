from datetime import date
from io import BytesIO
from PIL import Image
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Path,
    File,
    Query,
    Request,
    UploadFile,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from repositories.EnderecoRepo import EnderecoRepo
from repositories.ItemRepo import ItemRepo
from repositories.MesaRepo import MesaRepo
from repositories.ProdutoRepo import ProdutoRepo
from repositories.ReservaRepo import ReservaRepo
from repositories.UsuarioRepo import UsuarioRepo
from util.imageUtil import transformar_em_quadrada
from util.security import gerar_token, obter_hash_senha, validar_usuario_logado
from util.templateFilters import (
    capitalizar_nome_proprio,
    formatarData,
    formatarIdParaImagem,
)
from util.validators import *
from repositories.ClienteRepo import ClienteRepo
from models.Usuario import Usuario
from models.Cliente import Cliente

router = APIRouter(prefix="/cliente")
templates = Jinja2Templates(directory="templates")


@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData
    templates.env.filters["id_img"] = formatarIdParaImagem

@router.get("/aniversario/{idCliente:int}", response_class=HTMLResponse)
async def aniversario_cliente(request: Request, usuario: Usuario = Depends(validar_usuario_logado), idCliente: int = Path()):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    aniversario = ClienteRepo.AniversarioClienteHoje(idCliente) 
    return templates.TemplateResponse("Avulso/minhaconta.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho, "aniversario": aniversario})

@router.get("/carrinho", response_class=HTMLResponse)
async def carrinho(request: Request, usuario: Usuario = Depends(validar_usuario_logado), produto_idProduto: int = None):
    produto = None
    if produto_idProduto:
        # Lógica para obter as informações do produto com base no produto_id
        produto = ProdutoRepo.obterProdutoPorId(produto_idProduto)
    return templates.TemplateResponse("Avulso/carrinho.html", {"request": request, "usuario": usuario, "produto": produto}) 

@router.get("/listagemclientes", response_class=HTMLResponse)
async def listagemCliente(
    request: Request,
    pa: int = Query(1, description="Página atual"),
    tp: int = Query(5, description="Tamanho da página"),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    # if usuario:
    #     if usuario.admin:
                clientes = ClienteRepo.obterPagina(pa, tp)
                totalPaginas = ClienteRepo.obterQtdePaginas(tp)
                return templates.TemplateResponse(
                    "Cliente/listagemCliente.html",
                    {
                        "request": request,
                        "clientes": clientes,
                        "totalPaginas": totalPaginas,
                        "paginaAtual": pa,
                        "tamanhoPagina": tp,
                        "usuario": usuario,
                    },
                )
    #     else:
    #         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    # else:
    #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

# Apenas Adimin pode acesar essa área ---- GET ----
@router.get("/modificarcliente/{idUsuario:int}") 
async def getEditarCliente(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado), idUsuario: int = Path()
): 
    cliente = ClienteRepo.obterPorId(idUsuario) 
    if not cliente:
        return templates.TemplateResponse("Cliente/clientenaoencontrado.html", {"request": request}, status_code=404)
    return templates.TemplateResponse(
        "Cliente/editarCliente.html", {"request": request, "usuario": usuario, "cliente": cliente} 
    )

@router.post("/modificarcliente/{idUsuario:int}")
async def postEditarCliente(
    request: Request,
    idUsuario: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado), 
    nome: str = Form(""),
    dataNascimento: date = Form(""),
    pontuacao: int = Form(""),
    cpf: str = Form(""),
    telefone: str = Form(""),
    email: str = Form("") 
):
    if usuario:
        # Verifique se o ID do cliente é igual ao ID do usuário logado
            cliente = ClienteRepo.obterPorId(idUsuario)
            if cliente:
                # Atualize os detalhes do cliente com os novos dados do formulário
                cliente.nome = nome
                cliente.email = email
                cliente.cpf = cpf
                cliente.telefone = telefone
                cliente.pontuacao = pontuacao
                cliente.dataNascimento = dataNascimento
                ClienteRepo.update(cliente)
                if usuario.cliente and usuario.idUsuario == idUsuario:
                    return RedirectResponse("/cliente/minhaconta", status_code=status.HTTP_303_SEE_OTHER)
                else:
                    return RedirectResponse("/cliente/listagemclientes", status_code=status.HTTP_303_SEE_OTHER)
            else:
                raise HTTPException(status_code=404, detail="Cliente não encontrado")
    else:
        raise HTTPException(status_code=401, detail="Não autorizado")
    
@router.get("/trocarfoto/{idUsuario:int}")
async def get_trocar_foto(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado), idUsuario: int = Path() 
):
    cliente = ClienteRepo.obterPorId(idUsuario)
    return templates.TemplateResponse(
        "Cliente/trocarFoto.html", {"request": request, "usuario": usuario, "cliente": cliente} 
    )

@router.post("/trocarfoto/{idUsuario:int}")
async def post_trocar_foto(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idUsuario: int = Path(),
    arquivoImagem: UploadFile = File(...),
):
    cliente = ClienteRepo.obterPorId(idUsuario)

    # Normalização de dados
    conteudo_arquivo = await arquivoImagem.read()

    # Salvar a imagem no diretório de imagens de clientes
    with open(f"static/img/clientes/{cliente.idUsuario:04d}.jpg", "wb") as img:
        img.write(conteudo_arquivo)

    return RedirectResponse("/cliente/minhaconta", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/minhaconta", response_class=HTMLResponse)
async def getminhaconta(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    qtdeItensCarrinho = 0
    if usuario:
        cliente = ClienteRepo.obterPorId(usuario.idUsuario) 
        if cliente:
            qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
            return templates.TemplateResponse(
                "Cliente/minhaConta.html",
                {"request": request, "usuario": usuario, "cliente": cliente, "qtdeItensCarrinho": qtdeItensCarrinho}
            )
        else:
            return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@router.get("/meuspedidos", response_class=HTMLResponse)
async def meuspedidos(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse("Avulso/meuspedidos.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho})

@router.get("/meusenderecos", response_class=HTMLResponse)
async def endereco(
    request: Request, 
    pa: int = Query(1, description="Página atual"),
    tp: int = Query(5, description="Tamanho da página"),
    usuario: Usuario = Depends(validar_usuario_logado)
):
    enderecos = EnderecoRepo.obterEnderecoPorIdCliente(usuario.idUsuario, pa, tp) 
    totalPaginas = EnderecoRepo.obterQtdePaginas(tp)
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse("Endereco/listagemEndereco.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho, "enderecos": enderecos, "totalPaginas": totalPaginas})

@router.get("/minhasreservas", response_class=HTMLResponse)
async def minhasreservas(
    request: Request, 
    usuario: Usuario = Depends(validar_usuario_logado),
    pa: int = Query(1, description="Página atual"),
    tp: int = Query(10, description="Tamanho da página")
):
    reservas = ReservaRepo.obterReservaPorIdCliente(usuario.idUsuario, pa, tp)
    totalPaginas = ReservaRepo.obterQtdeReservas(tp)
    mesas = MesaRepo.getAll()
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse(
        "Reserva/listagemReserva.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho, "reservas": reservas, "totalPaginas": totalPaginas, "paginaAtual": pa, "tamanhoPagina": tp, "mesas": mesas}) 


@router.get("/excluircliente/{idUsuario:int}", response_class=HTMLResponse)
async def get_excluir_cliente(
    request: Request,
    idUsuario: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado)
):
    # Verifique se o cliente existe
    cliente = ClienteRepo.obterPorId(idUsuario)
    if not cliente:
        return templates.TemplateResponse("Cliente/clientenaoencontrado.html", {"request": request}, status_code=404)
    return templates.TemplateResponse(
        "Cliente/excluirCliente.html",
        {"request": request, "cliente": cliente, "usuario": usuario},
    )


@router.post("/excluircliente", response_class=HTMLResponse)
async def post_excluir_cliente(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idUsuario: int = Form(0),
):
    if ClienteRepo.delete(idUsuario): 
        return RedirectResponse(
            "/cliente/listagemclientes",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    else:
        raise Exception("Não foi possível excluir o cliente.")
