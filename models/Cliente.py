from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from models.Usuario import Usuario


@dataclass
class Cliente(Usuario):
  pontuacao: Optional[int] = 0
  dataCadastro: Optional[datetime] = datetime.now()
  dataNascimento: Optional[datetime] = None 