from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional


@dataclass
class Reserva:
  idReserva: int
  idCliente: int
  idMesa: int
  dataReserva: date
  horaReserva: int
  qtdPessoas: int
  dataHoraCadastro: Optional[datetime] = datetime.now()
  nomeMesa: Optional[str] = ""