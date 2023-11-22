from datetime import date
from io import BytesIO
from PIL import Image
from fastapi import (
    APIRouter,
    Depends,
    File,
    Query,
    Path,
    Request,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.Produto import Produto
from repositories.CategoriaRepo import CategoriaRepo
from repositories.ItemRepo import ItemRepo
from repositories.PedidoRepo import PedidoRepo
from repositories.ProdutoRepo import ProdutoRepo
from models.Usuario import Usuario
from util.imageUtil import transformar_em_quadrada
from util.templateFilters import (
    capitalizar_nome_proprio,
    formatarData,
    formatarIdParaImagem,
)
from util.security import validar_usuario_logado
from util.validators import add_error, is_not_empty, is_project_name, is_size_between

router = APIRouter(prefix="/produto")
templates = Jinja2Templates(directory="templates")


@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData
    templates.env.filters["id_img"] = formatarIdParaImagem

@router.get("/produtonopedido", response_class=HTMLResponse)
async def produto_em_algum_pedido(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    return templates.TemplateResponse("Produto/produtonopedido.html", {"request": request, "usuario": usuario})

# Rota para listar produtos
@router.get("/listagemprodutos", response_class=HTMLResponse)
async def listagem_produtos(
    request: Request,
    pa: int = Query(1, description="Página atual"),
    tp: int = Query(10, description="Tamanho da página"),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    if usuario:
        if usuario.admin or usuario.funcionario:
            produtos = ProdutoRepo.obterProduto(pa, tp)
            totalPaginas = ProdutoRepo.obterQtdeProdutos(tp)
            return templates.TemplateResponse(
                "Produto/listagemProduto.html",
                {
                    "request": request,
                    "produtos": produtos,
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



@router.get("/categoria/{idCategoria:int}", response_class=HTMLResponse)
async def getPorCategoria(request: Request, usuario: Usuario = Depends(validar_usuario_logado), idCategoria: int = Path()):
    produtos = ProdutoRepo.getAllByCategoria(idCategoria)
    categorias = CategoriaRepo.getAll()
    categoria = CategoriaRepo.obterCategoriaPorId(idCategoria)
    return templates.TemplateResponse("Produto/produtosMain.html", {"request": request, "usuario": usuario, "produtos": produtos, "categorias": categorias, "categoria": categoria})

@router.get("/modificarproduto", response_class=HTMLResponse)
async def modificar_produto(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    if usuario:
        if usuario.admin or usuario.funcionario:
            return templates.TemplateResponse(
                "Produto/editarProduto.html", {"request": request}
            )
        else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/modificarproduto")
async def modificar_produto(produto: Produto):
    ProdutoRepo.update(produto)  # Chama o método de atualização do ProdutoRepo
    return {"message": "Produto atualizado com sucesso."}


# Rota para criar um novo produto
@router.get("/novoproduto", response_class=HTMLResponse)
async def novo_produto(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    if usuario:
        if usuario.admin or usuario.funcionario:
            categorias = CategoriaRepo.getAll()
            return templates.TemplateResponse("Produto/novoProduto.html", {"request": request, "usuario": usuario, "categorias": categorias	}) 
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@router.post("/novoproduto")
async def cadastrar_produto(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idCategoria: int = Form(0),
    nome: str = Form(...),
    preco: float = Form(...),
    descricao: str = Form(...),
    qtdEstoque: str = Form(...), 
    emPromocao: str = Form(...),  # Modificamos para string
    dataLancamento: date = Form(...),
    arquivoImagem: UploadFile = File(...),
):
    
    if usuario:
        if usuario.admin or usuario.funcionario:
            # normalização de dados
            nome = capitalizar_nome_proprio(nome).strip()
            descricao = descricao.strip()

            # tratamento de erros
            erros = {}

            # Validação do campo idCategoria
            # is_not_empty(idCategoria, "idCategoria", erros)
            # if CategoriaRepo.categoriaExiste(idCategoria):
            #         add_error("idCategoria", "ID da categoria não encontrado.", erros)
            # validação da imagem
            conteudo_arquivo = await arquivoImagem.read()
            imagem = Image.open(BytesIO(conteudo_arquivo))
            if not imagem:
                add_error("arquivoImagem", "Nenhuma imagem foi enviada.", erros)
            # Converte o valor do campo emPromocao para um booleano
            em_promocao = True if emPromocao.lower() == "sim" else False

            if len(erros) > 0:
                valores = {}
                valores["idCategoria"] = idCategoria
                valores["nome"] = nome
                valores["preco"] = preco
                valores["descricao"] = descricao
                valores["qtdEstoque"] = qtdEstoque
                valores["emPromocao"] = emPromocao
                valores["dataLancamento"] = dataLancamento
                return templates.TemplateResponse(
                    "Produto/novoProduto.html",
                    {
                        "request": request,
                        "usuario": usuario,
                        "erros": erros,
                        "valores": valores,
                    },
                )

            # Cria o produto com os dados fornecidos
            novo_produto = ProdutoRepo.insert(
                Produto(
                    idProduto=0,
                    idCategoria=idCategoria,
                    nome=nome,
                    preco=preco,
                    descricao=descricao,
                    qtdEstoque=qtdEstoque,
                    emPromocao=emPromocao,
                    dataLancamento=dataLancamento,
                )
            )
            if novo_produto:
                imagem_quadrada = transformar_em_quadrada(imagem)
                imagem_quadrada.save(f"static/img/{novo_produto.idProduto:04d}.jpg", "JPEG")
            return RedirectResponse(
                "/produto/listagemprodutos", status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


# Rota para editar um produto
@router.get("/modificarproduto/{idProduto:int}", response_class=HTMLResponse)
async def get_editar_produto(
    request: Request,
    idProduto: int = Path(), 
    usuario: Usuario = Depends(validar_usuario_logado),
):
    categorias = CategoriaRepo.getAll()
    produto = ProdutoRepo.obterProdutoPorId(idProduto)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return templates.TemplateResponse(
        "Produto/editarProduto.html",
        {"request": request, "usuario": usuario, "produto": produto, "categorias": categorias}
    )


@router.post("/modificarproduto/{idProduto:int}", response_class=HTMLResponse)
async def post_editar_produto(
    request: Request,
    idProduto: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado),
    idCategoria: int = Form(...),
    nome: str = Form(...),
    preco: float = Form(...),
    descricao: str = Form(...),
    qtdEstoque: str = Form(...),
    emPromocao: str = Form(...),
    dataLancamento: str = Form(...),
):
    # Execute a lógica de edição de produto aqui
    produto = Produto(
        idProduto=idProduto,
        idCategoria=idCategoria,
        nome=nome,
        preco=preco,
        descricao=descricao,  # Adicione a descrição se necessário
        qtdEstoque=qtdEstoque,
        emPromocao=emPromocao,
        dataLancamento=dataLancamento,
    )
    ProdutoRepo.update(produto)

    # Redirecione de volta para a página de detalhes do produto após a edição
    return RedirectResponse("/produto/listagemprodutos", status_code=status.HTTP_303_SEE_OTHER)


# Rota para excluir um produto
@router.get("/excluirproduto/{idProduto:int}", response_class=HTMLResponse)
async def get_excluir_produto(
    request: Request,
    idProduto: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    # Verificar se há pedidos associados a este produto
    if ItemRepo.exists_pedido_with_produto(idProduto): 
        return RedirectResponse("/produto/produtonopedido", status_code=303)
    # Verifique se o produto existe
    produto = ProdutoRepo.obterProdutoPorId(idProduto)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Renderize a página de confirmação de exclusão
    return templates.TemplateResponse(
        "Produto/excluirProduto.html",
        {"request": request, "produto": produto, "usuario": usuario}
    )


@router.post("/excluirproduto", response_class=HTMLResponse)
async def post_excluir_produto(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idProduto: int = Form(0),
):
    if ProdutoRepo.delete(idProduto):
        return RedirectResponse(
            "/produto/listagemprodutos",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    else:
        raise Exception("Não foi possível excluir o produto.")
