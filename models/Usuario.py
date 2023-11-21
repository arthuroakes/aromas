from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Usuario:
    idUsuario: int
    nome: str
    email: str
    telefone: str
    cpf: Optional[str] = ""    
    senha: Optional[str] = ""
    token: Optional[str] = ""
    admin: Optional[bool] = False
    funcionario: Optional[bool] = False
    cliente: Optional[bool] = False
