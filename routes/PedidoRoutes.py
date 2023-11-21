import datetime
from fastapi import (
    APIRouter,
    Depends,
    Query,
    Request,
    Form,
    HTTPException,
    status,
    Path,
)
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from models.Item import Item
from models.Pedido import Pedido
from repositories.ClienteRepo import ClienteRepo
from repositories.EnderecoRepo import EnderecoRepo
from repositories.ItemRepo import ItemRepo
from repositories.PedidoRepo import PedidoRepo
from repositories.ProdutoRepo import ProdutoRepo
from models.Usuario import Usuario
from util.templateFilters import formatarData, formatarIdParaImagem
from util.security import validar_usuario_logado

router = APIRouter(prefix="/pedido")
templates = Jinja2Templates(directory="templates")


@router.on_event("startup")
async def startup_event():
    templates.env.filters["date"] = formatarData
    templates.env.filters["id_img"] = formatarIdParaImagem


@router.get("/listagempedidos", response_class=HTMLResponse)
async def listagemPedidos(
    request: Request,
    pa: int = Query(1, description="Página atual"),
    tp: int = Query(5, description="Tamanho da página"),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    pedidos = PedidoRepo.obterPagina(pa, tp)
    totalPaginas = PedidoRepo.obterQtdePaginas(tp)
    return templates.TemplateResponse(
        "Pedido/listagemPedido.html",
        {
            "request": request,
            "pedidos": pedidos,
            "totalPaginas": totalPaginas,
            "paginaAtual": pa,
            "tamanhoPagina": tp,
            "usuario": usuario,
        },
    )


@router.get("/listagemtodospedidos", response_class=HTMLResponse)
async def listagemPedidos(
    request: Request,
    pa: int = Query(1, description="Página atual"),
    tp: int = Query(5, description="Tamanho da página"),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    pedidos = PedidoRepo.obterPedidos(pa, tp)
    totalPaginas = PedidoRepo.obterQtdePaginas(tp)
    return templates.TemplateResponse(
        "Pedido/listagemPedido.html",
        {
            "request": request,
            "pedidos": pedidos,
            "totalPaginas": totalPaginas,
            "paginaAtual": pa,
            "tamanhoPagina": tp,
            "usuario": usuario,
        },
    )


@router.get("/carrinho", response_class=HTMLResponse)
async def carrinho(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        pedido: Pedido = PedidoRepo.getPedidoByClienteByStatus(
            usuario.idUsuario, "carrinho"
        )
        itens = []
        qtdeItensCarrinho = 0
        if pedido:
            itens = ItemRepo.getAllByPedido(pedido.idPedido)
            qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
        return templates.TemplateResponse(
            "Pedido/carrinho.html",
            {
                "request": request,
                "usuario": usuario,
                "itens": itens,
                "qtdeItensCarrinho": qtdeItensCarrinho,
            },
        )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)


@router.get("/carrinho/{idProduto:int}", response_class=HTMLResponse)
async def carrinho(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idProduto: int = Path(),
):
    if usuario and usuario.cliente:
        if idProduto:
            produto = ProdutoRepo.obterProdutoPorId(idProduto)
            if produto:
                pedido: Pedido = PedidoRepo.getPedidoByClienteByStatus(
                    usuario.idUsuario, "carrinho"
                )
                if not pedido:
                    pedido: Pedido = PedidoRepo.insert(
                        Pedido(
                            idPedido=0,
                            idCliente=usuario.idUsuario,
                            idFuncionario=0,
                            idEndereco=0,
                            dataHora=datetime.date,
                            formaPagamento="",
                            status="carrinho",
                            tipoEntrega="",
                        )
                    )
                itemPedido = ItemRepo.getOne(pedido.idPedido, produto.idProduto)
                if not itemPedido:
                    itemPedido = ItemRepo.insert(
                        Item(
                            idPedido=pedido.idPedido,
                            idProduto=produto.idProduto,
                            quantidade=1,
                            valorUnitario=produto.preco,
                        )
                    )
                if itemPedido:
                    return RedirectResponse("/pedido/carrinho")
    else:
        return RedirectResponse("/login")


@router.get("/excluiritem/{idProduto:int}", response_class=HTMLResponse)
async def get_excluir_item(
    request: Request, idProduto: int, usuario: Usuario = Depends(validar_usuario_logado)
):
    qtdeItensCarrinho = 0
    # Verifique se o pedido existe
    produto = ProdutoRepo.obterProdutoPorId(idProduto)
    if not produto:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)

    # Renderize a página de confirmação de exclusão
    return templates.TemplateResponse(
        "Pedido/excluirItem.html",
        {
            "request": request,
            "produto": produto,
            "usuario": usuario,
            "qtdeItensCarrinho": qtdeItensCarrinho,
        },
    )


@router.post("/excluiritem", response_class=HTMLResponse)
async def post_excluir_item(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idProduto: int = Form(0),
):
    if usuario and usuario.cliente:
        # captura o carrinho do usuário logado e exclui o item
        pedido: Pedido = PedidoRepo.getPedidoByClienteByStatus(
            usuario.idUsuario, "carrinho"
        )
        if ItemRepo.delete(pedido.idPedido, idProduto):
            return RedirectResponse(
                "/pedido/carrinho",
                status_code=status.HTTP_303_SEE_OTHER,
            )
        else:
            raise Exception("Não foi possível excluir o produto.")


@router.get("/aquisicao", response_class=HTMLResponse)
async def entrega(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    # Como vai funcionar a atualização da coluna tipoEntrega no bd?
    # pedido = PedidoRepo.getPedidoByClienteByStatus(usuario.idUsuario, "carrinho")
    # PedidoRepo.atualizarTipoEntrega(pedido.idPedido, "Entrega")
    return templates.TemplateResponse(
        "Pedido/ped_aquisicao.html",
        {
            "request": request,
            "usuario": usuario,
            "qtdeItensCarrinho": qtdeItensCarrinho,
        },
    )


@router.get("/entrega", response_class=HTMLResponse)
async def getEntrega(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    enderecos = EnderecoRepo.obterPorCliente(usuario.idUsuario)
    return templates.TemplateResponse(
        "Pedido/entrega.html",
        {
            "request": request,
            "usuario": usuario,
            "qtdeItensCarrinho": qtdeItensCarrinho,
            "enderecos": enderecos,
        },
    )


@router.post("/entrega", response_class=RedirectResponse)
async def postEntrega(
    request: Request,
    idEndereco: int = Form(...),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    endereco = EnderecoRepo.obterEnderecoPorId(idEndereco)
    pedido = PedidoRepo.getPedidoByClienteByStatus(usuario.idUsuario, "carrinho")
    PedidoRepo.atualizarEndereco(pedido.idPedido, idEndereco)
    return RedirectResponse("/pedido/pagamento", status.HTTP_302_FOUND)


@router.get("/pagamento", response_class=HTMLResponse)
async def get_pagamento(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    pedido = PedidoRepo.getPedidoByClienteByStatus(usuario.idUsuario, "carrinho")
    cliente = ClienteRepo.obterPorId(usuario.idUsuario)
    itensPedido = ItemRepo.getAllByPedido(pedido.idPedido)
    valortotal = ItemRepo.calcular_valor_total(pedido.idPedido)
    enderecoEntrega = EnderecoRepo.obterEnderecoPorId(pedido.idEndereco)
    return templates.TemplateResponse(
        "Pedido/pagamento.html",
        {
            "request": request,
            "usuario": usuario,
            "qtdeItensCarrinho": qtdeItensCarrinho,
            "pedido": pedido,
            "cliente": cliente,
            "itens": itensPedido,
            "endereco": enderecoEntrega,
            "valortotal": valortotal,
        },
    )


@router.post("/pagamento", response_class=RedirectResponse)
async def postPagamento(
    request: Request,
    formaPagamento: str = Form(...),
    observacao: str = Form(...),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    pedido = PedidoRepo.getPedidoByClienteByStatus(usuario.idUsuario, "carrinho")
    PedidoRepo.atualizarFormaPagamento(pedido.idPedido, formaPagamento)
    PedidoRepo.atualizarObservacao(pedido.idPedido, observacao)
    PedidoRepo.atualizarStatus(pedido.idPedido, status="pedido")
    return RedirectResponse("/pedido/sucesso", status.HTTP_302_FOUND)


@router.get("/sucesso", response_class=HTMLResponse)
async def sobrenos(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse(
        "Pedido/sucessoPedido.html",
        {
            "request": request,
            "usuario": usuario,
            "qtdeItensCarrinho": qtdeItensCarrinho,
        },
    )


@router.get("/porcliente", response_class=HTMLResponse)
async def acompanhar_pedido(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    pedidos = PedidoRepo.getPedidosByCliente(usuario.idUsuario)    
    return templates.TemplateResponse(
        "Pedido/pedidosCliente.html",
        {"request": request, "usuario": usuario, "pedidos": pedidos, "totalPaginas": 1, "paginaAtual": 1},
    )
    
    
@router.get("/detalhes/{id_pedido:int}", response_class=HTMLResponse)
async def pedido_andamento(
    request: Request, id_pedido: int = Path(), usuario: Usuario = Depends(validar_usuario_logado)
):
    pedido = PedidoRepo.obterPedidoPorId(id_pedido)
    itens = ItemRepo.getAllByPedido(pedido.idPedido)
    return templates.TemplateResponse(
        "Pedido/detalhes.html",
        {"request": request, "usuario": usuario, "pedido": pedido, "itens": itens},	
    )


@router.get("/aceitarpedido", response_class=HTMLResponse)
async def get_aceitar_pedido(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    pedido = PedidoRepo.getPedidoByStatus("pedido")
    PedidoRepo.atualizarStatus(pedido.idPedido, status="aceito")
    PedidoRepo.atualizaridFuncionario(pedido.idPedido, usuario.idUsuario)
    return RedirectResponse("/pedido/listagempedidos", status.HTTP_302_FOUND)


@router.get("/entregapedido", response_class=HTMLResponse)
async def get_aceitar_pedido(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    pedido = PedidoRepo.getPedidoByStatus("aceito")
    PedidoRepo.atualizarStatus(pedido.idPedido, status="entrega")
    PedidoRepo.atualizaridFuncionario(pedido.idPedido, usuario.idUsuario)
    return RedirectResponse("/pedido/listagempedidos", status.HTTP_302_FOUND)


@router.get("/pedidoentregue", response_class=HTMLResponse)
async def get_pedido_entregue(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    pedido = PedidoRepo.getPedidoByStatus("entrega")
    PedidoRepo.atualizarStatus(pedido.idPedido, status="entregue")
    PedidoRepo.atualizaridFuncionario(pedido.idPedido, usuario.idUsuario)
    return RedirectResponse("/pedido/andamento", status.HTTP_302_FOUND)


@router.get("/motivocancelar", response_class=HTMLResponse)
async def get_motivo_cancelamento(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse(
        "Pedido/ped_cancel.html",
        {
            "request": request,
            "usuario": usuario,
            "qtdeItensCarrinho": qtdeItensCarrinho,
        },
    )


@router.get("/pedidocancelado", response_class=HTMLResponse)
async def pedidocancelado(
    request: Request, usuario: Usuario = Depends(validar_usuario_logado)
):
    qtdeItensCarrinho = 0
    if usuario and usuario.cliente:
        qtdeItensCarrinho = ItemRepo.getCountCartItemsFromUser(usuario.idUsuario)
    return templates.TemplateResponse(
        "Pedido/pedidocancelado.html",
        {
            "request": request,
            "usuario": usuario,
            "qtdeItensCarrinho": qtdeItensCarrinho,
        },
    )


@router.get("/cancelar", response_class=RedirectResponse)
async def get_(request: Request, usuario: Usuario = Depends(validar_usuario_logado)):
    pedido = PedidoRepo.getPedidosByCliente(usuario.idUsuario)
    PedidoRepo.atualizarStatus(pedido.idPedido, status="cancelado")
    return RedirectResponse("/pedido/pedidocancelado", status.HTTP_302_FOUND)


@router.get("/excluirpedido/{idPedido:int}", response_class=HTMLResponse)
async def get_excluir_pedido(
    request: Request,
    idPedido: int = Path(),
    usuario: Usuario = Depends(validar_usuario_logado),
):
    # Verifique se o cliente existe
    pedido = PedidoRepo.getOne(idPedido)
    if not pedido:
        return templates.TemplateResponse(
            "Pedido/pedidonaoencontrado.html", {"request": request}, status_code=404
        )
    return templates.TemplateResponse(
        "Pedido/excluirPedido.html",
        {"request": request, "pedido": pedido, "usuario": usuario},
    )


@router.post("/excluirpedido", response_class=HTMLResponse)
async def post_excluir_pedido(
    request: Request,
    usuario: Usuario = Depends(validar_usuario_logado),
    idPedido: int = Form(0),
):
    if PedidoRepo.delete(idPedido):
        if usuario.funcionario:
            return RedirectResponse(
                "/pedido/listagempedidos", status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            return RedirectResponse(
                "/pedido/listagemtodospedidos", status_code=status.HTTP_303_SEE_OTHER
            )
    else:
        raise Exception("Não foi possível excluir o cliente.")
