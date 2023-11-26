# routes/MainRoutes.py
from datetime import date
from PIL import Image
from io import BytesIO
from fastapi import APIRouter, Depends, Form, File, Path, HTTPException, Request, UploadFile, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.Categoria import Categoria
from models.Cliente import Cliente
from models.Produto import Produto
from fastapi import HTTPException 
from repositories.CategoriaRepo import CategoriaRepo
from repositories.ClienteRepo import ClienteRepo
from util.imageUtil import transformar_em_quadrada
from util.security import gerar_token, obter_hash_senha, validar_usuario_logado, verificar_senha
from util.templateFilters import formatarData, formatarIdParaImagem
from models.Usuario import Usuario
from repositories.ProdutoRepo import ProdutoRepo
from repositories.UsuarioRepo import UsuarioRepo
from repositories.ItemRepo import ItemRepo
from util.validators import *

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData
    templates.env.filters["id_img"] = formatarIdParaImagem


# Deve gerar uma lista de produtos em promação e produtos em lançamento para mostrar na pag inicial
@router.get("/")
async def getIndex(
    request: Request, 
    usuario: Usuario = Depends(validar_usuario_logado),
    pa: int = Query(1, description="Página atual"),
    tp: int = Query(4, description="Tamanho da página"),
    pagatual: int = Query(1, description="Página atual"),
    tamanhopag: int = Query(4, description="Tamanho da página"),
):
    produtos = ProdutoRepo.obterProdutosEmPromocao(pa, tp) 
    totalPaginas = ProdutoRepo.obterQtdeProdutosEmPromocao(tp)
    produto = ProdutoRepo.obterProdutosNaoPromocao(pagatual, tamanhopag)
    totalPagina = ProdutoRepo.obterQtdeProdutosNaoPromocao(tamanhopag)
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse(
        "Main/index.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho, "produtos": produtos, "totalPaginas": totalPaginas, "produto": produto, "totalPagina": totalPagina, "paginaAtual": pa, "tamanhoPagina": tp, "paginaAtual": pagatual, "tamanhoPagina": tamanhopag}
    )

# Rota para mostrar a página de visualizar produtos 
@router.get("/produtos", response_class=HTMLResponse)
async def produtos(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    produtos = ProdutoRepo.getAll()
    categorias = CategoriaRepo.getAll()
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse("Produto/produtosMain.html", {"request": request, "usuario": usuario, "produtos": produtos, "categorias": categorias, "qtdeItensCarrinho": qtdeItensCarrinho})

@router.get("/sobrenos", response_class=HTMLResponse)
async def sobrenos(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse("Avulso/sobrenos.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho}) 


@router.get("/localizacao", response_class=HTMLResponse)
async def localizacao(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse("Avulso/localizacao.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho})


@router.get("/contato", response_class=HTMLResponse)
async def suporte(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse("Avulso/contato.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho})

# @router.post("/contato", response_class=RedirectResponse)
# async def postContato(
#     request: Request,
#     nome: str = Form(...),
#     email: str = Form(...),
#     mensagem: str = Form(...),
#     usuario: Usuario = Depends(validar_usuario_logado),
# ):
#     qtdeItensCarrinho = 0
#     if usuario and usuario.cliente:
#         qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
#     return RedirectResponse("/pedido/sucesso", status.HTTP_302_FOUND) 

@router.get("/reserva", response_class=HTMLResponse)
async def reserva(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse(
        "Reserva/listagemReserva.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho}
    )


@router.get("/minhaconta", response_class=HTMLResponse)
async def minhaconta(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse("Avulso/minhaconta.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho})


@router.get("/meuspedidos", response_class=HTMLResponse)
async def meuspedidos(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse("Avulso/meuspedidos.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho})


@router.get("/chat", response_class=HTMLResponse)
async def chat(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    return templates.TemplateResponse("Avulso/chat.html", {"request": request, "usuario": usuario}) 

@router.get("/notfound", response_class=HTMLResponse)
async def notfound(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    return templates.TemplateResponse("Main/notfound.html", {"request": request, "usuario": usuario}) 


# Login

@router.get("/login")
async def getLogin(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    return templates.TemplateResponse(
        "Main/login.html", {"request": request, "usuario": usuario}
    )


@router.post("/login")
async def postLogin(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    email: str = Form(""),
    senha: str = Form(""),
    returnUrl: str = Query("/"), 
):
    # Normalização de dados
    email = email.strip().lower()
    senha = senha.strip()

    # Validação de dados
    erros = {}
    erro_login = None  # Inicialize a variável de erro_login como None

    # Validação do campo email
    is_not_empty(email, "email", erros) 
    if is_email(email, "email", erros):
        if UsuarioRepo.emailNaoExiste(email):
                add_error("email", "E-mail não cadastrado.", erros)

    # Validação do campo senha
    is_not_empty(senha, "senha", erros)
    # if UsuarioRepo.senhaExiste(senha):
    #         add_error("senha", "E-mail ou senha incorretos.", erros)

    # Só verifica a senha no BD se os dados forem válidos
    if len(erros) == 0:
        hash_senha_bd = UsuarioRepo.obterSenhaDeEmail(email)
        if hash_senha_bd:
            if verificar_senha(senha, hash_senha_bd):
                token = gerar_token()
                if UsuarioRepo.alterarToken(email, token):
                    response = RedirectResponse(returnUrl, status.HTTP_302_FOUND)
                    response.set_cookie(
                        key="auth_token", value=token, max_age=5400, httponly=True
                    )
                    return response
                else:
                    raise Exception(
                        "Não foi possível alterar o token do usuário no banco de dados."
                    )
            else:
                add_error("senha", "E-mail ou senha incorretos.", erros)
        else:
            erro_login = "Usuário não cadastrado."  # Defina a mensagem de erro_login

    # Se há algum erro, mostra o formulário novamente
    if len(erros) > 0 or erro_login:
        valores = {}
        valores["email"] = email 
        valores["senha"] = senha 
        return templates.TemplateResponse(
            "Main/login.html",
            {
                "request": request,
                "usuario": usuario,
                "erros": erros,
                "valores": valores,
                "erro_login": erro_login,  # Passe a mensagem de erro_login para o template
            },
        )


@router.get("/logout")
async def getLogout(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    if usuario:
        UsuarioRepo.alterarToken(usuario.email, "")
    response = RedirectResponse("/", status.HTTP_302_FOUND)
    response.set_cookie(
        key="auth_token", value="", httponly=True, expires="1970-01-01T00:00:00Z"
    )
    return response

@router.get("/novocliente")
async def getNovoCliente(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    return templates.TemplateResponse(
        "Cliente/novoCliente.html", {"request": request, "usuario": usuario}
    )


@router.post("/novocliente")
async def postNovoCliente(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    nome: str = Form(""),
    dataNascimento: date = Form(""),
    cpf: str = Form(""),
    telefone: str = Form(""),
    email: str = Form(""),
    senha: str = Form(""),
    confSenha: str = Form(""),
    arquivoImagem: UploadFile = File(...),
):
    # Normalização de dados
    nome = nome.strip()
    cpf = cpf.strip()
    telefone = telefone.strip()
    email = email.strip().lower()
    senha = senha.strip()
    confSenha = confSenha.strip()

    # Validação de dados
    erros = {}
    # Validação do campo nome
    is_not_empty(nome, "nome", erros)
    # Validação do campo dataNascimento
    # is_not_empty(dataNascimento, "dataNascimento", erros)
    if not dataNascimento:
        add_error("dataNascimento", "Data de nascimento é obrigatória.", erros)
    # Validação do campo CPF
    is_not_empty(cpf, "cpf", erros)
    if is_cpf(cpf, "cpf", erros):
        if UsuarioRepo.cpfExiste(cpf):
            add_error("cpf", "CPF já cadastrado.", erros)
    # Validação do campo telefone
    is_not_empty(telefone, "telefone", erros)
    if is_phone_number(telefone, "telefone", erros):
        if UsuarioRepo.telefoneExiste(telefone):
            add_error("telefone", "Telefone já cadastrado.", erros)
    # Validação do campo email
    is_not_empty(email, "email", erros)
    if is_email(email, "email", erros):
        if UsuarioRepo.emailExiste(email):
            add_error("email", "E-mail já cadastrado.", erros)
    # Validação do campo senha
    is_not_empty(senha, "senha", erros)
    is_password(senha, "senha", erros)
    # Validação do campo confSenha
    is_not_empty(confSenha, "confSenha", erros)
    if senha != confSenha:
        add_error("confSenha", "As senhas não coincidem.", erros) 
    # validação da imagem
    conteudo_arquivo = await arquivoImagem.read()
    if not conteudo_arquivo:
        # Define o caminho para a imagem padrão
        path_imagem_padrao = "static/img/cliente.jpg"
        with open(path_imagem_padrao, "rb") as img:
            conteudo_arquivo = img.read()
    imagem = Image.open(BytesIO(conteudo_arquivo))
    if not imagem:
        add_error("arquivoImagem", "Nenhuma imagem foi enviada.", erros)

    # Se não houver erros, insira o cliente no banco de dados
    if len(erros) == 0:
        # Crie um objeto Cliente com os dados fornecidos
        novo_cliente = Cliente(
            idUsuario=0,
            nome=nome,
            email=email,
            cpf=cpf,
            telefone=telefone,
            senha=obter_hash_senha(senha),
            token=None,
            dataNascimento=dataNascimento,
            pontuacao=0,
        )

        # Insira o cliente no banco de dados
        novo_cliente = ClienteRepo.insert(novo_cliente)

        if novo_cliente:
            imagem_quadrada = transformar_em_quadrada(imagem)
            imagem_quadrada.save(f"static/img/clientes/{novo_cliente.idUsuario:04d}.jpg", "JPEG") 
        
        # Gera um token para o cliente recém-cadastrado
        token = gerar_token()

        # Atualiza o token no banco de dados
        if not UsuarioRepo.alterarToken(email, token):
            raise HTTPException(
                status_code=500,
                detail="Não foi possível atualizar o token no banco de dados.",
            )

        # Redireciona o cliente para a página inicial ou outra página
        if usuario == "admin": 
            response = RedirectResponse(
                "/cliente/listagemclientes", status_code=status.HTTP_302_FOUND
            )
        else:
            response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)

        # Define o token como cookie
        response.set_cookie(
            key="auth_token", value=token, httponly=True, expires="1970-01-01T00:00:00Z"
        )
        return response 

    # se tem erro, mostra o formulário novamente
    if len(erros) > 0:
        valores = {}
        valores["nome"] = nome
        valores["dataNascimento"] = str(dataNascimento)
        valores["cpf"] = cpf
        valores["telefone"] = telefone
        valores["email"] = email.lower()
        return templates.TemplateResponse(
            "Cliente/novoCliente.html",
            {
                "request": request,
                "usuario": usuario,
                "erros": erros,
                "valores": valores,
            },
        )

@router.get("/alterarsenha", response_class=HTMLResponse)
async def getAlterarSenha(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    if usuario:
        qtdeItensCarrinho = 0
        if usuario and usuario.cliente:
            qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
        return templates.TemplateResponse(
            "Main/alterarSenha.html", {"request": request, "usuario": usuario, "qtdeItensCarrinho": qtdeItensCarrinho}
        )
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@router.post("/alterarsenha", response_class=HTMLResponse)
async def postAlterarSenha(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    senhaAtual: str = Form(""),
    novaSenha: str = Form(""),
    confNovaSenha: str = Form(""),    
):
    # normalização dos dados
    senhaAtual = senhaAtual.strip()
    novaSenha = novaSenha.strip()
    confNovaSenha = confNovaSenha.strip()    

    # verificação de erros
    erros = {}
    # validação do campo senhaAtual
    is_not_empty(senhaAtual, "senhaAtual", erros)    
    # validação do campo novaSenha
    is_not_empty(novaSenha, "novaSenha", erros)
    is_password(novaSenha, "novaSenha", erros)
    # validação do campo confNovaSenha
    is_not_empty(confNovaSenha, "confNovaSenha", erros)
    is_matching_fields(confNovaSenha, "confNovaSenha", novaSenha, "Nova Senha", erros)
    
    # só verifica a senha no banco de dados se não houverem erros de validação
    if len(erros) == 0:    
        hash_senha_bd = UsuarioRepo.obterSenhaDeEmail(usuario.email)
        if hash_senha_bd:
            if not verificar_senha(senhaAtual, hash_senha_bd):            
                add_error("senhaAtual", "Senha atual está incorreta.", erros)
    
    # se tem erro, mostra o formulário novamente
    if len(erros) > 0:
        valores = {}        
        return templates.TemplateResponse(
            "Main/alterarSenha.html",
            {
                "request": request,
                "usuario": usuario,                
                "erros": erros,
                "valores": valores,
            },
        )

    # se passou pelas validações, altera a senha no banco de dados
    hash_nova_senha = obter_hash_senha(novaSenha)
    UsuarioRepo.alterarSenha(usuario.idUsuario, hash_nova_senha)
    
    return RedirectResponse("/", status_code=303) 