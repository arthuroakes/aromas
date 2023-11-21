from datetime import date
from io import BytesIO
from PIL import Image
from fastapi import APIRouter, Depends, Form, File, HTTPException, Request, UploadFile, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from repositories.UsuarioRepo import UsuarioRepo
from util.imageUtil import transformar_em_quadrada
from util.security import obter_hash_senha, validar_usuario_logado, verificar_senha
from util.templateFilters import capitalizar_nome_proprio, formatarData, formatarIdParaImagem
from util.validators import *
from repositories.ClienteRepo import ClienteRepo
from repositories.FuncionarioRepo import FuncionarioRepo
from models.Funcionario import Funcionario
from models.Usuario import Usuario

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")

@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData
    templates.env.filters["id_img"] = formatarIdParaImagem

# Rota para mostrar a página de visualizar clientes
@router.get("/cliente", response_class=HTMLResponse)
async def visu_cliente(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    clientes = ClienteRepo.getAll()
    return templates.TemplateResponse(
        "Cliente/visuClientes.html", {"request": request, "clientes": clientes, "usuario": usuario} 
    )

@router.get("/novofuncionario")
async def getNovoFuncionario(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    if usuario:
        if usuario.admin:
            return templates.TemplateResponse(
                "Admin/novoFuncionario.html", {"request": request, "usuario": usuario}
            )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@router.post("/novofuncionario")
async def postNovoFuncionario(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    nome: str = Form(""),
    email: str = Form(""),
    cpf: str = Form(""),
    telefone: str = Form(""),
    dataAdmissao: date = Form(""),    
    salario: float = Form(0),
    dataNascimento: date = Form(""),
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
    # Validação do campo email
    is_not_empty(email, "email", erros)
    if is_email(email, "email", erros):
        if UsuarioRepo.emailExiste(email):
            add_error("email", "E-mail já cadastrado.", erros)
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
    # Validação do campo dataAdmissao
    # is_not_empty(dataAdmissao, "data_admissao", erros)
    # Validação do campo dataAdmissao
    is_greater_than(salario, "salario", 1320, erros)
    # Validação do campo dataNascimento
    if not dataNascimento:
        add_error("dataNascimento", "Data de nascimento é obrigatória.", erros)
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
        path_imagem_padrao = "static/img/funcionario.jpg"
        with open(path_imagem_padrao, "rb") as img:
            conteudo_arquivo = img.read()
    imagem = Image.open(BytesIO(conteudo_arquivo))
    if not imagem:
        add_error("arquivoImagem", "Nenhuma imagem foi enviada.", erros)

    # Se não houver erros, insira o funcionário no banco de dados
    if len(erros) == 0:
        # Crie um objeto Funcionario com os dados fornecidos
        novo_funcionario = Funcionario(
            idUsuario=0,
            nome=nome,
            email=email,
            cpf=cpf,
            telefone=telefone,
            dataAdmissao=dataAdmissao,
            salario=salario,
            dataNascimento=dataNascimento,
            senha=obter_hash_senha(senha),
            token=None,
        )

        # Insira o cliente no banco de dados
        novo_funcionario = FuncionarioRepo.insert(novo_funcionario)

        if novo_funcionario: 
            imagem_quadrada = transformar_em_quadrada(imagem)
            imagem_quadrada.save(f"static/img/funcionarios/{novo_funcionario.idUsuario:04}.jpg", "JPEG") 
        return RedirectResponse(
                "/funcionario/listagemfuncionarios", status_code=status.HTTP_303_SEE_OTHER 
            )

    # se tem erro, mostra o formulário novamente
    if len(erros) > 0:
        valores = {}
        valores["nome"] = nome
        valores["email"] = email.lower()
        valores["cpf"] = cpf
        valores["telefone"] = telefone
        valores["dataAdmissao"] = str(dataAdmissao)
        valores["salario"] = salario
        valores["dataNascimento"] = str(dataNascimento)
        return templates.TemplateResponse(
            "Admin/novoFuncionario.html",
            {
                "request": request,
                "usuario": usuario,
                "erros": erros,
                "valores": valores,
            },
        )