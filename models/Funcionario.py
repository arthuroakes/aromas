from dataclasses import dataclass
from datetime import date
from typing import Optional
from models.Usuario import Usuario


@dataclass
class Funcionario(Usuario):
    dataAdmissao: date = None
    dataDemissao: Optional[date] = None
    salario: float = 0.0
    dataNascimento: date = None
