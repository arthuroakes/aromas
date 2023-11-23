# /util/security.py
import bcrypt
import secrets
#import bcrypt
from fastapi import Request
from models.Usuario import Usuario
from repositories.ClienteRepo import ClienteRepo
from repositories.FuncionarioRepo import FuncionarioRepo
from repositories.UsuarioRepo import UsuarioRepo

def validar_usuario_logado(request: Request) -> Usuario | None:
    try:
        token = request.cookies["auth_token"]
        if token.strip() == "":
            return None
        usuario = UsuarioRepo.obterUsuarioPorToken(token)
        if usuario:
            usuario.funcionario = FuncionarioRepo.existeId(usuario.idUsuario)
            usuario.cliente = ClienteRepo.existeId(usuario.idUsuario) 
        return usuario
    except KeyError:
        return None    

def obter_hash_senha(senha: str) -> str:
    # A função bcrypt.hashpw espera que a senha seja em bytes, por isso usamos .encode()
    hashed = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()) 
    return hashed.decode()  # Decodificar para obter a string do hash

def verificar_senha(senha: str, hash_senha: str) -> bool:
    try:
        # A função bcrypt.checkpw espera que ambos sejam bytes
        return bcrypt.checkpw(senha.encode(), hash_senha.encode())
    except ValueError:
        return False
    
def gerar_token(length: int = 32) -> str:
    return secrets.token_hex(length)