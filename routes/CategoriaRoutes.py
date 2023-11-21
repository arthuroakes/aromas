from fastapi import APIRouter, Depends, HTTPException, Path, Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.Categoria import Categoria
from repositories.CategoriaRepo import CategoriaRepo
from repositories.ProdutoRepo import ProdutoRepo
from util.security import validar_usuario_logado
from util.templateFilters import formatarData
from models.Usuario import Usuario
from util.validators import *

router = APIRouter(prefix="/categoria")
templates = Jinja2Templates(directory="templates")


@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData

@router.get("/produtonacategoria", response_class=HTMLResponse)
async def produto_em_algum_pedido(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    return templates.TemplateResponse("Produto/produtonacategoria.html", {"request": request, "usuario": usuario})

# Listagem Categoria
@router.get("/listagemcategoria", response_class=HTMLResponse)
async def get_listagem_categorias(
    request: Request,
    pa: int= Query(1, description="Página atual"),
    tp: int = Query(8, description="Tamanho da página"),  
    usuario: Usuario = Depends(validar_usuario_logado),
):
    categorias = CategoriaRepo.obterPagina(pa, tp)  
    totalPaginas = CategoriaRepo.obterQtdePaginas(tp)  

    return templates.TemplateResponse(
        "Produto/listagemCategoria.html",
        {
            "request": request,
            "categorias": categorias,
            "totalPaginas": totalPaginas,
            "paginaAtual": pa,
            "tamanhoPagina": tp,
            "usuario": usuario,
        },
    )

# Get Nova Categoria
@router.get("/novacategoria", response_class=HTMLResponse)
async def get_nova_categoria(request: Request, usuario: Usuario = Depends(validar_usuario_logado),):
    return templates.TemplateResponse(
        "Produto/novaCategoria.html", {"request": request, "usuario": usuario} 
    )

# Post Nova Categoria
@router.post("/novacategoria")
async def post_cadastrar_categoria(
    request: Request,
    nome: str = Form(...),
): 
    # Validação de dados
    erros = {}
    # Validação do campo nome
    is_not_empty(nome, "nome", erros)
    # if is_categoria_existe(nome, "nome", erros): 
    # # Verifique se a categoria já existe no banco de dados
    #     if CategoriaRepo.nomeExiste(nome):
    #             add_error("nome", "Categoria já cadastrada.", erros)

    categoria_existente = CategoriaRepo.obterPorNome(nome)
    if categoria_existente:
        return RedirectResponse(
            f"/categoria/novacategoria?error=A categoria com o nome '{nome}' já existe.",
            status_code=status.HTTP_303_SEE_OTHER
        ) 

    # Crie a categoria com os dados fornecidos
    CategoriaRepo.insert(
        Categoria(
            idCategoria=0,
            nome=nome,
        )
    )

    if len(erros) > 0:
        valores = {}
        valores["nome"] = nome
        return templates.TemplateResponse(
            "Produto/novaCategoria.html",
            {
                "request": request,
                "erros": erros,
                "valores": valores,
            },
        )

    response = RedirectResponse("/categoria/listagemcategoria", status.HTTP_302_FOUND) 
    return response

# Rota para editar um produto
@router.get("/modificarcategoria/{idCategoria:int}", response_class=HTMLResponse)
async def get_editar_categoria(
    request: Request,
    idCategoria: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    categoria = CategoriaRepo.obterCategoriaPorId(idCategoria)  
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")
    return templates.TemplateResponse(
        "Produto/editarCategoria.html",
        {"request": request, "usuario": usuario, "categoria": categoria},
    )

# Post Modificar Categoria
@router.post("/modificarcategoria/{idCategoria:int}", response_class=HTMLResponse)
async def post_editar_categoria(
    request: Request,
    idCategoria: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado),
    nome: str = Form(...),
):
    # Execute a lógica de edição de categoria aqui
    categoria = Categoria(
        idCategoria=idCategoria,
        nome=nome,
    )
    CategoriaRepo.update(categoria)

    # Redirecione de volta para a página de detalhes da categoria após a edição
    return RedirectResponse("/categoria/listagemcategoria", status_code=status.HTTP_303_SEE_OTHER) 

# Rota para excluir uma categoria
@router.get("/excluircategoria/{idCategoria:int}", response_class=HTMLResponse)
async def get_excluir_categoria(
    request: Request,
    idCategoria: int,
    usuario: Usuario = Depends(validar_usuario_logado),
):
    # Verificar se há produtos associados a esta categoria
    if ProdutoRepo.exists_produto_with_categoria(idCategoria): 
        return RedirectResponse("/categoria/produtonacategoria", status_code=303)
    # Verifique se a categoria existe
    categoria = CategoriaRepo.obterCategoriaPorId(idCategoria)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoria não encontrada")

    # Renderize a página de confirmação de exclusão
    return templates.TemplateResponse(
        "Produto/excluirCategoria.html",
        {"request": request, "categoria": categoria, "usuario": usuario},  
    )


@router.post("/excluircategoria", response_class=HTMLResponse)
async def post_excluir_categoria(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idCategoria: int = Form(0),
):
            if CategoriaRepo.delete(idCategoria):
                return RedirectResponse(
                    "/categoria/listagemcategoria",
                    status_code=status.HTTP_303_SEE_OTHER,
                )
            else:
                raise Exception("Não foi possível excluir a categoria.")
