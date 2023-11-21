from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Produto:
  idProduto: int
  idCategoria: int
  nome: str
  preco: float
  descricao: Optional[str] 
  qtdEstoque: int
  emPromocao: bool
  dataLancamento: date