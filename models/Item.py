from dataclasses import dataclass
from typing import Optional


@dataclass
class Item:
  idPedido: int
  idProduto: int  
  quantidade: int
  valorUnitario: float
  valorItem: Optional[float] = ""
  nomeProduto: Optional[str] = ""