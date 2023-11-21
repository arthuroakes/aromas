from typing import List
from util.Database import Database
from models.Endereco import Endereco

class EnderecoRepo:

    @classmethod
    def createTable(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS endereco (
            idEndereco INTEGER PRIMARY KEY AUTOINCREMENT,
            idCliente INTEGER,
            cep TEXT NOT NULL,
            rua TEXT NOT NULL,
            numero TEXT NOT NULL,
            complemento TEXT,
            bairro TEXT NOT NULL,
            cidade TEXT NOT NULL,
            uf TEXT NOT NULL,
            FOREIGN KEY (idCliente) REFERENCES Cliente (idCliente))
        """
        conn = Database.createConnection()
        cursor = conn.cursor()
        tableCreated = (cursor.execute(sql).rowcount > 0)
        conn.commit()
        conn.close()
        return tableCreated
    
    @classmethod
    def insert(cls, endereco: Endereco) -> Endereco:
        sql = "INSERT INTO endereco (idCliente, cep, rua, numero, complemento, bairro, cidade, uf) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (endereco.idCliente, endereco.cep, endereco.rua, endereco.numero, endereco.complemento, endereco.bairro, endereco.cidade, endereco.uf))
        if (result.rowcount > 0):
            conn.commit()
            conn.close()
            return endereco
        else:
            conn.close()
            return None
    
    @classmethod
    def update(cls, endereco: Endereco) -> Endereco:
        sql = "UPDATE endereco SET idCliente=?, cep=?, rua=?, numero=?, complemento=?, bairro=?, cidade=?, uf=? WHERE idEndereco=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (endereco.idCliente, endereco.cep, endereco.rua, endereco.numero, endereco.complemento, endereco.bairro, endereco.cidade, endereco.uf, endereco.idEndereco))
        if (result.rowcount > 0):
            conn.commit()
            conn.close()
            return endereco
        else:
            conn.close()
            return None
        
    @classmethod
    def delete(cls, idEndereco: int) -> bool:
        sql = "DELETE FROM endereco WHERE idEndereco=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idEndereco,))
        if (result.rowcount > 0):
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
        
    @classmethod
    def getAll(cls) -> List[Endereco]:
        sql = "SELECT idEndereco, idCliente, cep, rua, numero, complemento, bairro, cidade, uf FROM endereco"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql).fetchall()
        enderecos = [Endereco(*x) for x in result]
        return enderecos
    
    @classmethod
    def getOne(cls, idEndereco: int) -> Endereco:
        sql = "SELECT idEndereco, idCliente, cep, rua, numero, complemento, bairro, cidade, uf FROM endereco WHERE idEndereco=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idEndereco,)).fetchone()
        endereco = Endereco
        endereco = Endereco(*result) if result else None
        return endereco
    
    @classmethod
    def obterEnderecoPorId(cls, idEndereco: int) -> Endereco | None:
        sql = "SELECT idEndereco, idCliente, cep, rua, numero, complemento, bairro, cidade, uf FROM endereco WHERE idEndereco=?"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (idEndereco,)).fetchone()
        if resultado:
            objeto = Endereco(
                idEndereco=resultado[0],
                idCliente=resultado[1],
                cep=resultado[2],
                rua=resultado[3],
                numero=resultado[4],
                complemento=resultado[5],
                bairro=resultado[6],
                cidade=resultado[7],
                uf=resultado[8],
            )
            return objeto
        else:
            return None
    
    @classmethod
    def obterPagina(cls, pagina: int, tamanhoPagina: int) -> List[Endereco]: 
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT idEndereco, idCliente, cep, rua, numero, complemento, bairro, cidade, uf FROM endereco LIMIT ?, ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [Endereco(*x) for x in result] 
        return objetos
    
    @classmethod
    def obterQtdePaginas(cls, tamanhoPagina: int) -> int:
        sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM endereco) AS FLOAT) / ?) AS qtdePaginas"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (tamanhoPagina, )).fetchone()
        return int(result[0])

    @classmethod
    def obterPorCliente(cls, idCliente: int) -> List[Endereco]:
        sql = "SELECT idEndereco, idCliente, cep, rua, numero, complemento, bairro, cidade, uf FROM endereco WHERE idCliente=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCliente,)).fetchall()
        objetos = [Endereco(*x) for x in result]
        return objetos
    
    @classmethod
    def obterEnderecoPorIdCliente(cls, idUsuario: int, pagina: int, tamanhoPagina: int) -> List[Endereco]: 
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT idEndereco, idUsuario, cep, rua, numero, complemento, bairro, cidade, uf FROM endereco INNER JOIN usuario ON endereco.idCliente = usuario.idUsuario WHERE idCliente=? LIMIT ?, ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idUsuario, inicio, tamanhoPagina)).fetchall()
        objetos = [Endereco(*x) for x in result] 
        return objetos