# Importe os módulos necessários
from datetime import date
from io import BytesIO
from PIL import Image
from fastapi import APIRouter, Depends, FastAPI, File, Form, Path, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.Funcionario import Funcionario
from models.Usuario import Usuario
from repositories.FuncionarioRepo import FuncionarioRepo
from util.security import validar_usuario_logado
from util.templateFilters import formatarData, formatarIdParaImagem
from util.validators import add_error, is_email, is_not_empty

# Crie uma instância do roteador
router = APIRouter(prefix="/funcionario")
templates = Jinja2Templates(directory="templates")

@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData
    templates.env.filters["id_img"] = formatarIdParaImagem 

# Rota para listar todos os funcionários
@router.get("/listagemfuncionarios", response_class=HTMLResponse)
async def listagem_funcionarios(
    request: Request,
    pa: int = Query(1, description="Página atual"),
    tp: int = Query(5, description="Tamanho da página"),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    funcionarios = FuncionarioRepo.obterPagina(pa, tp)
    totalPaginas = FuncionarioRepo.obterQtdePaginas(tp) 
    return templates.TemplateResponse(
        "Funcionario/listagemFuncionario.html",
        {
            "request": request,
            "funcionarios": funcionarios,
            "totalPaginas": totalPaginas,
            "paginaAtual": pa,
            "tamanhoPagina": tp,
            "usuario": usuario,
        },
    )

@router.get("/minhaconta", response_class=HTMLResponse)
async def getminhaconta(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    if usuario:
        funcionario = FuncionarioRepo.obterPorId(usuario.idUsuario) 
        if funcionario:
            return templates.TemplateResponse(
                "Funcionario/minhaConta.html",
                {"request": request, "usuario": usuario, "funcionario": funcionario},
            )
        else:
            return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

@router.get("/trocarfoto/{idUsuario:int}")
async def get_trocar_foto(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado), idUsuario: int = Path() 
):
    funcionario = FuncionarioRepo.obterPorId(idUsuario)
    return templates.TemplateResponse(
        "Funcionario/trocarFoto.html", {"request": request, "usuario": usuario, "funcionario": funcionario} 
    )

@router.post("/trocarfoto/{idUsuario:int}")
async def post_trocar_foto(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idUsuario: int = Path(),
    arquivoImagem: UploadFile = File(...),
):
    funcionario = FuncionarioRepo.obterPorId(idUsuario)

    # Normalização de dados
    conteudo_arquivo = await arquivoImagem.read()

    # Salvar a imagem no diretório de imagens de clientes
    with open(f"static/img/funcionarios/{funcionario.idUsuario:04d}.jpg", "wb") as img: 
        img.write(conteudo_arquivo)

    return RedirectResponse("/funcionario/minhaconta", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/modificarfuncionario/{idUsuario:int}")
async def get_editar_funcionario(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado), idUsuario: int = Path() 
):
    funcionario = FuncionarioRepo.obterPorId(idUsuario)
    if not funcionario:
        return templates.TemplateResponse("Funcionario/funcionarionaoencontrado.html", {"request": request}, status_code=404)
    return templates.TemplateResponse(
        "Admin/editarFuncionario.html", {"request": request, "usuario": usuario, "funcionario": funcionario} 
    )

@router.post("/modificarfuncionario/{idUsuario:int}")
async def postEditarFuncionario(
    request: Request,
    idUsuario: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado), 
    nome: str = Form(""),
    dataNascimento: date = Form(""),
    dataAdmissao: date = Form(""),
    salario: float = Form(0),
    cpf: str = Form(""),
    telefone: str = Form(""),
    email: str = Form("") 
):
    if usuario:
        # Verifique se o ID do funcionario é igual ao ID do usuário logado
            funcionario = FuncionarioRepo.obterPorId(idUsuario)
            if funcionario:
                # Atualize os detalhes do funcionario com os novos dados do formulário
                funcionario.nome = nome
                funcionario.email = email
                funcionario.cpf = cpf
                funcionario.telefone = telefone
                funcionario.dataNascimento = dataNascimento
                funcionario.dataAdmissao = dataAdmissao
                funcionario.salario = salario 
                FuncionarioRepo.update(funcionario)
                if usuario.funcionario and usuario.idUsuario == idUsuario: 
                    return RedirectResponse("/funcionario/minhaconta", status_code=status.HTTP_303_SEE_OTHER)
                else:
                    return RedirectResponse("/funcionario/listagemfuncionarios", status_code=status.HTTP_303_SEE_OTHER)
            else:
                raise HTTPException(status_code=404, detail="Funcionario não encontrado")
        # else:
        #     raise HTTPException(status_code=401, detail="Não autorizado")
    else:
        raise HTTPException(status_code=401, detail="Não autorizado")

# Rota para excluir um produto
@router.get("/excluirfuncionario/{idUsuario:int}", response_class=HTMLResponse) 
async def get_excluir_funcionario(
    request: Request,
    idUsuario: int = Path,
    usuario: Usuario = Depends(validar_usuario_logado)
):
    # Verifique se o funcionario existe
    funcionario = FuncionarioRepo.obterPorId(idUsuario) 
    if not funcionario:
        return templates.TemplateResponse("Funcionario/funcionarionaoencontrado.html", {"request": request}, status_code=404)

    # Renderize a página de confirmação de exclusão
    return templates.TemplateResponse(
        "Admin/excluirFuncionario.html",
        {"request": request, "funcionario": funcionario, "usuario": usuario}, 
    )


@router.post("/excluirfuncionario", response_class=HTMLResponse)
async def post_excluir_funcionario(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idUsuario: int = Form(0),
):
    if FuncionarioRepo.delete(idUsuario):
        return RedirectResponse(
            "/funcionario/listagemfuncionarios",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    else:
        raise Exception("Não foi possível excluir o funcionário.")