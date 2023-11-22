from typing import List
from util.Database import Database
from models.Mesa import Mesa

class MesaRepo:

    @classmethod
    def createTable(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS mesa (
            idMesa INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            assentos INTEGER)
        """
        conn = Database.createConnection()
        cursor = conn.cursor()
        tableCreated = (cursor.execute(sql).rowcount > 0)
        conn.commit()
        conn.close()
        return tableCreated
    
    @classmethod
    def insert(cls, mesa: Mesa) -> Mesa:
        sql = "INSERT INTO mesa (nome, assentos) VALUES (?, ?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (mesa.nome, mesa.assentos))
        if (result.rowcount > 0):
            mesa.idMesa = result.lastrowid
            conn.commit()
            conn.close()
            return mesa
        else:
            conn.close()
            return None
    
    @classmethod
    def update(cls, mesa: Mesa) -> Mesa:
        sql = "UPDATE mesa SET nome=?, assentos=? WHERE idMesa=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (mesa.nome, mesa.assentos, mesa.idMesa))
        if (result.rowcount > 0):
            conn.commit()
            conn.close()
            return mesa
        else:
            conn.close()
            return None
        
    @classmethod
    def delete(cls, idMesa: int) -> bool:
        sql = "DELETE FROM mesa WHERE idMesa=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idMesa,))
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
        
    @classmethod
    def getAll(cls) -> List[Mesa]:
        sql = "SELECT idMesa, nome, assentos FROM mesa"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql).fetchall()
        mesas = [Mesa(*x) for x in result]
        return mesas
    
    @classmethod
    def getOne(cls, idMesa: int) -> Mesa:
        sql = "SELECT idMesa, nome, assentos FROM mesa WHERE idMesa=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idMesa,)).fetchone()
        mesa = Mesa(*result) if result else None
        return mesa
    
    @classmethod
    def obterMesa(cls, pagina: int, tamanhoPagina: int) -> List[Mesa]:
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT idMesa, nome, assentos FROM mesa ORDER BY idMesa LIMIT ?, ?"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [Mesa(*x) for x in resultado]
        return objetos
    
    @classmethod
    def obterQtdeMesas(cls, tamanhoPagina: int) -> int:
        sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM mesa) AS FLOAT) / ?) AS qtdePaginas"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (tamanhoPagina, )).fetchone()
        return int(resultado[0])
    
    @classmethod
    def obterPorNome(cls, nome: str) -> Mesa:
        sql = "SELECT * FROM mesa WHERE nome = ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (nome,)).fetchone()
        conn.close()
        if resultado:
            return Mesa(idMesa=resultado[0], nome=resultado[1], assentos=resultado[2]) 
        else:
            return None
        
    @classmethod
    def obterMesaPorId(cls, idMesa: int) -> Mesa | None:
        sql = "SELECT idMesa, nome, assentos FROM mesa WHERE idMesa = ?"
        conn = Database.createConnection() 
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (idMesa,)).fetchone()
        conn.close() 
        if resultado:
            objeto = Mesa(
                idMesa=resultado[0],
                nome=resultado[1],
                assentos=resultado[2]
            )
            return objeto
        else:
            return None
