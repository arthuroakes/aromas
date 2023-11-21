from typing import List
from models.Usuario import Usuario
from util.Database import Database


class UsuarioRepo:
    @classmethod
    def createTable(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS usuario (
            idUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            telefone TEXT NOT NULL,
            senha TEXT NOT NULL,
            token TEXT,
            cpf TEXT NOT NULL,
            admin BOOLEAN NOT NULL DEFAULT 0,
            UNIQUE (email))
        """
        conn = Database.createConnection()
        cursor = conn.cursor()
        tableCreated = cursor.execute(sql).rowcount > 0
        conn.commit()
        conn.close()
        return tableCreated

    @classmethod
    def criarUsuarioAdmin(cls) -> bool:
        sql = "INSERT OR IGNORE INTO usuario (nome, email, telefone, senha, cpf, admin) VALUES (?, ?, ?, ?, ?, ?)"
        # hash da senha 123456
        hash_senha = "$2b$12$WU9pnIyBUZOJHN7hgkhWtew8hI0Keiobr8idjIxYDwCyiSb5zh0iq"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(
            sql,
            (
                "Administrador do Sistema",
                "admin@email.com",
                "0000-0000",
                hash_senha,
                "000.000.000-00",
                True,
            ),
        )
        if resultado.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    @classmethod
    def insert(cls, usuario: Usuario) -> Usuario:
        sql = "INSERT INTO usuario (nome, email, telefone, senha, cpf) VALUES (?, ?, ?, ?, ?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(
            sql,
            (usuario.nome, usuario.email, usuario.telefone, usuario.senha, usuario.cpf),
        )
        if result.rowcount > 0:
            usuario.idUsuario = result.lastrowid
            conn.commit()
            conn.close()
            return usuario
        else:
            conn.close()
            return None

    @classmethod
    def alterarSenha(cls, idUsuario: int, senha: str) -> bool:
        sql = "UPDATE usuario SET senha=? WHERE idUsuario=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (senha, idUsuario))
        if resultado.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    @classmethod
    def alterarToken(cls, email: str, token: str) -> bool:
        sql = "UPDATE usuario SET token=? WHERE email=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (token, email))
        if resultado.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    @classmethod
    def alterarAdmin(cls, id: int, admin: bool) -> bool:
        sql = "UPDATE usuario SET admin=? WHERE id=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (admin, id))
        if resultado.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()

            return False

    @classmethod
    def emailExiste(cls, email: str) -> bool:
        sql = "SELECT EXISTS (SELECT 1 FROM usuario WHERE email=?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (email,)).fetchone()
        return bool(resultado[0])
    
    @classmethod
    def emailNaoExiste(cls, email: str) -> bool:
        sql = "SELECT EXISTS (SELECT 1 FROM usuario WHERE email=?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (email,)).fetchone()
        return not bool(resultado[0]) if resultado is not None else True
    
    @classmethod
    def telefoneExiste(cls, telefone: str) -> bool:
        sql = "SELECT EXISTS (SELECT 1 FROM usuario WHERE telefone=?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (telefone,)).fetchone()
        return bool(resultado[0])
    
    @classmethod
    def cpfExiste(cls, cpf: str) -> bool:
        sql = "SELECT EXISTS (SELECT 1 FROM usuario WHERE cpf=?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (cpf,)).fetchone() 
        return bool(resultado[0])
    
    @classmethod
    def senhaExiste(cls, senha: str) -> bool:
        sql = "SELECT EXISTS (SELECT 1 FROM usuario WHERE senha=?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (senha,)).fetchone()
        return bool(resultado[0])

    @classmethod
    def obterSenhaDeEmail(cls, email: str) -> str | None:
        sql = "SELECT senha FROM usuario WHERE email=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (email,)).fetchone()
        if resultado:
            return str(resultado[0])
        else:
            return None

    @classmethod
    def update(cls, usuario: Usuario) -> Usuario:
        sql = "UPDATE usuario SET nome=?, email=?, cpf=?, telefone=? WHERE idUsuario=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(
            sql,
            (
                usuario.nome,
                usuario.email,
                usuario.cpf,
                usuario.telefone,
                usuario.idUsuario,
            ),
        )
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return usuario
        else:
            conn.close()
            return None

    @classmethod
    def delete(cls, idUsuario: int) -> bool:
        sql = "DELETE FROM usuario WHERE idUsuario=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idUsuario,))
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    @classmethod
    def obterUsuarioPorToken(cls, token: str) -> Usuario:
        sql = "SELECT idUsuario, nome, email, telefone, admin FROM usuario WHERE token=?"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        # quando se executa fechone em um cursor sem resultado, ele retorna None
        resultado = cursor.execute(sql, (token,)).fetchone()
        if resultado:
            objeto = Usuario(
                idUsuario=resultado[0],
                nome=resultado[1],
                email=resultado[2],
                telefone=resultado[3],
                admin=bool(resultado[4]))
            return objeto
        else:
            return None
        
    @classmethod
    def obterUsuario(cls, pagina: int, tamanhoPagina: int) -> List[Usuario]:
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT idUsuario, nome, email, telefone, senha, token, cpf, admin FROM usuario ORDER BY nome LIMIT ?, ?"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [Usuario(*x) for x in resultado]
        return objetos
    
    @classmethod
    def obterQtdeUsuarios(cls, tamanhoPagina: int) -> int:
        sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM usuario) AS FLOAT) / ?) AS qtdePaginas"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (tamanhoPagina, )).fetchone()
        return int(resultado[0])  
