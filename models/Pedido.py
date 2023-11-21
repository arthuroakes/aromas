from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Pedido:
  idPedido: int
  idCliente: int
  idFuncionario: int
  idEndereco: int
  formaPagamento: str
  dataHora: datetime
  status: str 
  tipoEntrega: str
  observacao: Optional[str] = ""