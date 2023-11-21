from dataclasses import dataclass


@dataclass
class Endereco:
  idEndereco: int
  idCliente: int
  cep: str
  rua: str
  numero: int
  complemento: str
  bairro: str
  cidade: str
  uf: str