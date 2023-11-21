from typing import List
from util.Database import Database
from models.Chat import Chat

class ChatRepo:

    @classmethod
    def createTable(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS chat (
            idCliente INTEGER,
            dataHora TEXT,
            idFuncionario INTEGER,
            mensagem TEXT,
            PRIMARY KEY (idCliente, dataHora),
            FOREIGN KEY (idCliente) REFERENCES Cliente (idCliente),
            FOREIGN KEY (idFuncionario) REFERENCES Funcionario (idFuncionario))
        """
        conn = Database.createConnection()
        cursor = conn.cursor()
        tableCreated = (cursor.execute(sql).rowcount > 0)
        conn.commit()
        conn.close()
        return tableCreated
    
    @classmethod
    def insert(cls, chat: Chat) -> Chat:
        sql = "INSERT INTO chat (idCliente, dataHora, idFuncionario, mensagem) VALUES (?, ?, ?, ?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (chat.idCliente, chat.dataHora, chat.idFuncionario, chat.mensagem))
        if (result.rowcount > 0):
            conn.commit()
            conn.close()
            return chat
        else:
            conn.close()
            return None
    
    @classmethod
    def update(cls, chat: Chat) -> Chat:
        sql = "UPDATE chat SET idFuncionario=?, mensagem=? WHERE idCliente=? AND dataHora=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (chat.idFuncionario, chat.mensagem, chat.idCliente, chat.dataHora))
        if (result.rowcount > 0):
            conn.commit()
            conn.close()
            return chat
        else:
            conn.close()
            return None
        
    @classmethod
    def delete(cls, idCliente: int, dataHora: str) -> bool:
        sql = "DELETE FROM chat WHERE idCliente=? AND dataHora=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCliente, dataHora))
        if (result.rowcount > 0):
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
        
    @classmethod
    def getAll(cls) -> List[Chat]:
        sql = "SELECT idCliente, dataHora, idFuncionario, mensagem FROM chat"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql).fetchall()
        chats = [Chat(*x) for x in result]
        return chats
    
    @classmethod
    def getOne(cls, idCliente: int, dataHora: str) -> Chat:
        sql = "SELECT idCliente, dataHora, idFuncionario, mensagem FROM chat WHERE idCliente=? AND dataHora=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCliente, dataHora)).fetchone()
        chat = Chat(*result) if result else None
        return chat
