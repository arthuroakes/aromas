from datetime import datetime
import math
from typing import List
from util.Database import Database
from models.Cliente import Cliente
from models.Usuario import Usuario
from repositories.UsuarioRepo import UsuarioRepo


class ClienteRepo:
    @classmethod
    def createTable(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS cliente (
            idCliente INTEGER PRIMARY KEY,
            pontuacao INTEGER,
            dataCadastro DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            dataNascimento DATETIME NOT NULL,
            FOREIGN KEY (idCliente) REFERENCES Usuario (idUsuario))
        """
        conn = Database.createConnection()
        cursor = conn.cursor()
        tableCreated = cursor.execute(sql).rowcount > 0
        conn.commit()
        conn.close()
        return tableCreated

    @classmethod
    def insert(cls, cliente: Cliente) -> Cliente:
        usuario = UsuarioRepo.insert(
            Usuario(
                cliente.idUsuario,
                cliente.nome,
                cliente.email,
                cliente.telefone,
                cliente.cpf,
                cliente.senha,
            )
        )
        sql = "INSERT INTO cliente (idCliente, pontuacao, dataNascimento) VALUES (?, ?, ?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(
            sql, (usuario.idUsuario, cliente.pontuacao, cliente.dataNascimento)
        )
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            cliente.idUsuario = usuario.idUsuario
            return cliente
        else:
            conn.close()
            return None

    @classmethod
    def update(cls, cliente: Cliente) -> Cliente:
        usuario = Usuario(
            idUsuario=cliente.idUsuario,
            nome=cliente.nome,
            email=cliente.email,
            cpf=cliente.cpf,
            telefone=cliente.telefone
        )
        UsuarioRepo.update(usuario)
        sql = "UPDATE cliente SET pontuacao=?, dataCadastro=?, dataNascimento=? WHERE idCliente=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(
            sql,
            (
                cliente.pontuacao,
                cliente.dataCadastro,
                cliente.dataNascimento,
                cliente.idUsuario,
            ))
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            cliente.idUsuario = usuario.idUsuario
            return cliente
        else:
            conn.close()
            return None

    @classmethod
    def delete(cls, idUsuario: int) -> bool:
        sql = "DELETE FROM cliente WHERE idCliente=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idUsuario, ))
        if (result.rowcount > 0):
            conn.commit()
            UsuarioRepo.delete(idUsuario)
            conn.close()
            return True
        else:
            conn.close()
            return False

    @classmethod
    def getAll(cls) -> List[Cliente]:
        sql = "SELECT idCliente, usuario.nome, usuario.email, usuario.telefone, usuario.cpf, cliente.pontuacao, cliente.dataCadastro, cliente.dataNascimento FROM cliente INNER JOIN usuario ON cliente.idCliente = usuario.idUsuario ORDER BY usuario.nome"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql).fetchall()
        clientes = [Cliente(*x) for x in result]
        return clientes

    @classmethod
    def getOne(cls, idCliente: int) -> Cliente | None:
        sql = "SELECT idCliente, nome, email, telefone, cpf, pontuacao, dataCadastro, dataNascimento FROM cliente INNER JOIN usuario ON cliente.idCliente = usuario.idUsuario WHERE idCliente = ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCliente,)).fetchone()
        conn.close()
        if result:
            cliente = Cliente(
                idCliente=result[0],
                nome=result[1],
                email=result[2],
                telefone=result[3],
                cpf=result[4],
                pontuacao=result[5],
                dataCadastro=result[6],
                dataNascimento=result[7]
            )
            return cliente
        else:
            return None

    @classmethod
    def getAllOrderedByRegistrationDateAsc(cls) -> List[Cliente]:
        sql = "SELECT idCliente, nome, email, senha, telefone, cpf, pontuacao, dataCadastro, dataNascimento FROM cliente INNER JOIN usuario ON cliente.idCliente = usuario.idUsuario ORDER BY dataCadastro ASC"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql).fetchall()
        clientes = [Cliente(*x) for x in result]
        return clientes

    @classmethod
    def searchByBirthday(cls, month: int, day: int) -> List[Cliente]:
        sql = "SELECT idCliente, nome, email, senha, telefone, cpf, pontuacao, dataCadastro, dataNascimento FROM cliente INNER JOIN usuario ON cliente.idCliente = usuario.idUsuario WHERE strftime('%m', dataNascimento) = ? AND strftime('%d', dataNascimento) = ? ORDER BY nome"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(
            sql, (str(month).zfill(2), str(day).zfill(2))
        ).fetchall()
        clientes = [Cliente(*x) for x in result]
        return clientes

    @classmethod
    def AniversarioClienteHoje(cls, idCliente: int) -> bool:
        # Obtenha a data de nascimento do cliente
        cliente = cls.obterPorId(idCliente)
        if cliente:
            data_nascimento_cliente = cliente.dataNascimento

            # Obtenha a data atual
            today = datetime.now() 

            # Verifique se a data de nascimento coincide com a data atual (ignorando o ano)
            return (today.month, today.day) == (data_nascimento_cliente.month, data_nascimento_cliente.day)

        # Cliente não encontrado
        return False
    
    @classmethod
    def obterQtdeClientes(cls, tamanhoPagina: int) -> int:
        sql = "SELECT COUNT(*) FROM cliente"
        conn = Database.createConnection()
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()[0]
        conn.close()
        return math.ceil(result / tamanhoPagina)
    
    @classmethod
    def obterPorId(cls, idUsuario: int) -> Cliente | None:
        sql = "SELECT idUsuario, usuario.nome, usuario.email, usuario.telefone, usuario.cpf, cliente.pontuacao, cliente.dataCadastro, cliente.dataNascimento FROM cliente INNER JOIN usuario ON cliente.idCliente = usuario.idUsuario WHERE cliente.idCliente = ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (idUsuario,)).fetchone()
        conn.close()
        if resultado:
            objeto = Cliente(
                idUsuario=resultado[0],
                nome=resultado[1],
                email=resultado[2],
                telefone=resultado[3],
                cpf=resultado[4],
                pontuacao=resultado[5],
                dataCadastro=resultado[6],
                dataNascimento=resultado[7]
            )
            return objeto
        else:
            return None

    @classmethod
    def existeId(cls, idCliente: int) -> bool:
        sql = "SELECT idCliente FROM cliente WHERE idCliente=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCliente, )).fetchone()    
        return result != None

    @classmethod
    def obterPagina(cls, pagina: int, tamanhoPagina: int) -> List[Cliente]:
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT idCliente, usuario.nome, usuario.email, usuario.telefone, usuario.cpf, cliente.pontuacao, cliente.dataCadastro, cliente.dataNascimento FROM cliente INNER JOIN usuario ON cliente.idCliente = usuario.idUsuario ORDER BY usuario.nome LIMIT ?, ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [
            Cliente(
                idUsuario=x[0],
                nome=x[1],
                email=x[2],
                telefone=x[3],
                cpf=x[4],
                pontuacao=x[5],
                dataCadastro=x[6],
                dataNascimento=x[7],
            )
            for x in result
        ]
        return objetos
  
    @classmethod
    def obterQtdePaginas(cls, tamanhoPagina: int) -> int:
        sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM cliente) AS FLOAT) / ?) AS qtdePaginas"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (tamanhoPagina, )).fetchone()
        return int(result[0])