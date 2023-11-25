import random
from typing import List
from util.Database import Database
from models.Pedido import Pedido


class PedidoRepo:
    @classmethod
    def createTable(cls):
        # status: [ carrinho, pedido, aceito, entregue, cancelado ]
        # idFuncionario: funcionário que aceitou o pedido
        sql = """
            CREATE TABLE IF NOT EXISTS pedido (
            idPedido INTEGER PRIMARY KEY AUTOINCREMENT,
            idCliente INTEGER,
            idFuncionario INTEGER,
            idEndereco INTEGER,
            formaPagamento TEXT,
            dataHora DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            observacao TEXT,
            tipoEntrega TEXT, 
            FOREIGN KEY (idCliente) REFERENCES Cliente (idCliente),
            FOREIGN KEY (idFuncionario) REFERENCES Funcionario (idFuncionario),
            FOREIGN KEY (idEndereco) REFERENCES Endereco (idEndereco))
        """
        conn = Database.createConnection()
        cursor = conn.cursor()
        tableCreated = cursor.execute(sql).rowcount > 0
        conn.commit()
        conn.close()
        return tableCreated

    @classmethod
    def insert(cls, pedido: Pedido) -> Pedido:
        sql = "INSERT INTO pedido (idCliente, status) VALUES (?, ?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (pedido.idCliente, pedido.status))
        if result.rowcount > 0:
            pedido.idPedido = result.lastrowid
            conn.commit()
            conn.close()
            return pedido
        else:
            conn.close()
            return None

    @classmethod
    def update(cls, pedido: Pedido) -> Pedido:
        sql = "UPDATE pedido SET idCliente=?, idFuncionario=?, idEndereco=?, formaPagamento=?, dataHora=?, status=?, tipoEntrega=? WHERE idPedido=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(
            sql,
            (
                pedido.idCliente,
                pedido.idFuncionario,
                pedido.idEndereco,
                pedido.formaPagamento,
                pedido.dataHora,
                pedido.status,
                pedido.tipoEntrega,
                pedido.idPedido,
            ),
        )
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return pedido
        else:
            conn.close()
            return None

    @classmethod
    def delete(cls, idPedido: int) -> bool:
        sql = "DELETE FROM pedido WHERE idPedido=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idPedido,))
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    @classmethod
    def getAll(cls) -> List[Pedido]:
        sql = "SELECT idPedido, idCliente, idFuncionario, idEndereco, formaPagamento, dataHora, status, tipoEntrega FROM pedido"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql).fetchall()
        pedidos = [Pedido(*x) for x in result]
        return pedidos

    @classmethod
    def getOne(cls, idPedido: int) -> Pedido:
        sql = "SELECT idPedido, idCliente, idFuncionario, idEndereco, formaPagamento, dataHora, status, tipoEntrega FROM pedido WHERE idPedido=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idPedido,)).fetchone()
        pedido = Pedido(*result) if result else None
        return pedido

    @classmethod
    def getPedidoByClienteByStatus(cls, idCliente: int, status: str) -> Pedido | None:
        sql = "SELECT idPedido, idCliente, idFuncionario, idEndereco, formaPagamento, dataHora, status, observacao, tipoEntrega FROM pedido WHERE idCliente=? AND status=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCliente, status)).fetchone()
        if result:
            pedido = Pedido(*result)
            return pedido
        return None
    
    @classmethod
    def getAcompanharPedidoByClienteByStatus(cls, idCliente: int) -> Pedido | None: 
        sql = "SELECT idPedido, idCliente, idFuncionario, idEndereco, formaPagamento, dataHora, status, observacao, tipoEntrega FROM pedido WHERE idCliente=? AND status IN ('pedido', 'aceito', 'entrega')"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCliente,)).fetchone()
        if result:
            pedido = Pedido(*result)
            return pedido
        return None
    
    @classmethod
    def getPedidosByCliente(cls, idCliente: int) -> Pedido:
        sql = "SELECT idPedido, idCliente, idFuncionario, idEndereco, formaPagamento, dataHora, status, observacao, tipoEntrega FROM pedido WHERE idCliente=? AND status IN ('Aguardando Aceitação', 'Pedido Aceito', 'Seu Pedido Saiu Para Entrega')" 
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCliente,)).fetchall()        
        pedidos = [Pedido(*x) for x in result]
        return pedidos
    
    @classmethod
    def obterPaginaPedidosporCliente(cls, idCliente: int, pagina: int, tamanhoPagina: int) -> List[Pedido]:
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT idPedido, idCliente, idFuncionario, idEndereco, formaPagamento, dataHora, status, observacao, tipoEntrega FROM pedido WHERE idCliente=? AND status IN ('Aguardando Aceitação', 'Pedido Aceito', 'Pedido Negado', 'Seu Pedido Saiu Para Entrega') LIMIT ?, ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCliente, inicio, tamanhoPagina)).fetchall()
        objetos = [
            Pedido(
                idPedido=x[0],
                idCliente=x[1],
                idFuncionario=x[2],
                idEndereco=x[3],
                formaPagamento=x[4],
                dataHora=x[5],
                status=x[6],
                observacao=x[7],
                tipoEntrega=x[8],
            )
            for x in result
        ]
        return objetos
    
    @classmethod
    def getPedidoByStatus(cls, status: str) -> Pedido | None:
        sql = "SELECT idPedido, idCliente, idFuncionario, idEndereco, formaPagamento, dataHora, status, observacao, tipoEntrega FROM pedido WHERE status=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (status,)).fetchone()
        if result:
            pedido = Pedido(*result)
            return pedido
        return None
    
    @classmethod
    def getStatusByPedido(cls, idPedido: int) -> Pedido | None: 
        sql = "SELECT idPedido, idCliente, idFuncionario, idEndereco, formaPagamento, dataHora, status, observacao, tipoEntrega FROM pedido WHERE idPedido=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idPedido,)).fetchone()
        if result:
            pedido = Pedido(*result)
            return pedido
        return None

    @classmethod
    def obterPedidoPorId(cls, idPedido: int) -> Pedido | None:
        sql = "SELECT idPedido, idCliente, idFuncionario, idEndereco, formaPagamento, status, tipoEntrega, dataHora FROM pedido WHERE idPedido = ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (idPedido,)).fetchone()
        conn.close()
        if resultado:
            objeto = Pedido(
                idPedido=resultado[0],
                idCliente=resultado[1],
                idFuncionario=resultado[2],
                idEndereco=resultado[3],                
                formaPagamento=resultado[4],
                status=resultado[5],
                tipoEntrega=resultado[6],
                dataHora=resultado[7],
            )
            return objeto
        else:
            return None

    @classmethod
    def atualizarEndereco(cls, idPedido: int, idEndereco: int) -> bool:
        sql = "UPDATE pedido SET idEndereco=? WHERE idPedido=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idEndereco, idPedido))
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    @classmethod
    def atualizarFormaPagamento(cls, idPedido: int, formaPagamento: str) -> bool:
        sql = "UPDATE pedido SET formaPagamento=? WHERE idPedido=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (formaPagamento, idPedido))
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
        
    @classmethod
    def atualizarObservacao(cls, idPedido: int, observacao: str) -> bool:
        sql = "UPDATE pedido SET observacao=? WHERE idPedido=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (observacao, idPedido))
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
        
    @classmethod
    def atualizarStatus(cls, idPedido: int, status: str) -> bool:
        sql = "UPDATE pedido SET status=? WHERE idPedido=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (status, idPedido))
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
        
    @classmethod
    def atualizaridFuncionario(cls, idPedido: int, idFuncionario: int) -> bool:
        sql = "UPDATE pedido SET idFuncionario=? WHERE idPedido=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idFuncionario, idPedido))
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
        
    @classmethod
    def atualizarTipoEntrega(cls, idPedido: int, tipoEntrega: int) -> bool:
        sql = "UPDATE pedido SET tipoEntrega=? WHERE idPedido=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (tipoEntrega, idPedido))
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
        
    @classmethod
    def obterPagina(cls, pagina: int, tamanhoPagina: int) -> List[Pedido]: 
        inicio = (pagina - 1) * tamanhoPagina 
        sql = "SELECT idPedido, usuario.nome, idFuncionario, idEndereco, formaPagamento, dataHora, observacao, status, tipoEntrega FROM pedido INNER JOIN usuario ON pedido.idCliente = usuario.idUsuario WHERE status IN ('Aguardando Aceitação', 'Pedido Aceito') ORDER BY dataHora LIMIT ?, ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [
            Pedido(
                idPedido=x[0],
                idCliente=x[1], 
                idFuncionario=x[2],
                idEndereco=x[3],
                formaPagamento=x[4],
                dataHora=x[5],
                observacao=x[6],
                status=x[7],
                tipoEntrega=x[8],
            )
            for x in result
        ]
        return objetos

    @classmethod
    def obterQtdePaginas(cls, tamanhoPagina: int) -> int:
        sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM pedido) AS FLOAT) / ?) AS qtdePaginas"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (tamanhoPagina, )).fetchone()
        return int(result[0])
    
    @classmethod
    def obterPedidos(cls, pagina: int, tamanhoPagina: int) -> List[Pedido]: 
        inicio = (pagina - 1) * tamanhoPagina 
        sql = "SELECT idPedido, usuario.nome, idFuncionario, idEndereco, formaPagamento, dataHora, observacao, status, tipoEntrega FROM pedido INNER JOIN usuario ON pedido.idCliente = usuario.idUsuario ORDER BY dataHora LIMIT ?, ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [
            Pedido(
                idPedido=x[0],
                idCliente=x[1], 
                idFuncionario=x[2],
                idEndereco=x[3],
                formaPagamento=x[4],
                dataHora=x[5],
                observacao=x[6],
                status=x[7],
                tipoEntrega=x[8],
            )
            for x in result
        ]
        return objetos
    
    # def gerar_sequencia_numeros() -> str:
    #     # Gera uma sequência de 4 números aleatórios
    #     sequencia = ''.join(str(random.randint(0, 9)) for _ in range(4))
    #     return sequencia 