from dataclasses import dataclass
from datetime import datetime


@dataclass
class Chat:
  idCliente: int
  dataHora: datetime
  idFuncionario: int
  mensagem: str
