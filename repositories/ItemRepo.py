from typing import List
from util.Database import Database
from models.Item import Item


class ItemRepo:

  @classmethod
  def createTable(
    cls
  ):  #cria a tabela "item" no banco de dados, se ela ainda não existir. Ele define a estrutura da tabela, incluindo os nomes e tipos de colunas, bem como as chaves primárias e estrangeiras.
    sql = """
            CREATE TABLE IF NOT EXISTS item (
            idPedido INTEGER,
            idProduto INTEGER,
            quantidade INTEGER,
            valorUnitario REAL,
            observacao TEXT,
            valorItem REAL GENERATED ALWAYS AS (quantidade * valorUnitario),
            PRIMARY KEY (idPedido, idProduto),
            FOREIGN KEY (idPedido) REFERENCES Pedido (idPedido),
            FOREIGN KEY (idProduto) REFERENCES Produto (idProduto))
        """
    conn = Database.createConnection()
    cursor = conn.cursor()
    tableCreated = (cursor.execute(sql).rowcount > 0)
    conn.commit()
    conn.close()
    return tableCreated

  @classmethod
  def insert(
      cls,
      item: Item) -> Item:  #Este método insere um novo item na tabela "item".
    sql = "INSERT INTO item (idPedido, idProduto, quantidade, valorUnitario) VALUES (?, ?, ?, ?)"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(
      sql, (item.idPedido, item.idProduto, item.quantidade, item.valorUnitario))
    if (result.rowcount > 0):
      conn.commit()
      conn.close()
      return item
    else:
      conn.close()
      return None

  @classmethod
  def update(
    cls, item: Item
  ) -> Item:  # Este método atualiza um item existente na tabela "item". Ele recebe um objeto Item contendo os dados atualizados do item.
    sql = "UPDATE item SET quantidade=?, valorUnitario=?, observacao=?, valorItem=? WHERE idPedido=? AND idProduto=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(
      sql, (item.quantidade, item.valorUnitario,
            item.valorItem, item.idPedido, item.idProduto))
    if (result.rowcount > 0):
      conn.commit()
      conn.close()
      return item
    else:
      conn.close()
      return None

  @classmethod
  def delete(cls, idPedido: int, idProduto: int) -> bool: 
    sql = "DELETE FROM item WHERE idPedido=? AND idProduto=?"  #Este método exclui um item da tabela "item" com base nos campos idPedido e idProduto.
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (idPedido, idProduto))
    if (result.rowcount > 0):
      conn.commit()
      conn.close()
      return True
    else:
      conn.close()
      return False

  @classmethod
  def getAll(
    cls
  ) -> List[
      Item]:  #Este método recupera todos os itens da tabela "item". Ele executa uma consulta SQL que retorna todos os registros da tabela. Os resultados são transformados em objetos Item e retornados como uma lista
    sql = "SELECT idPedido, idProduto, quantidade, valorUnitario, observacao, valorItem FROM item"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql).fetchall()
    items = [Item(*x) for x in result]
    return items

  @classmethod
  def getOne(
    cls, idPedido: int, idProduto: int
  ) -> Item:  # Este método recupera um único item da tabela "item" com base nos campos idPedido e idProduto.
    sql = "SELECT idPedido, idProduto, quantidade, valorUnitario, observacao, valorItem FROM item WHERE idPedido=? AND idProduto=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (idPedido, idProduto)).fetchone()
    item = Item(*result) if result else None
    return item

  @classmethod
  def getAllByPedido(
    cls, idPedido: int
  ) -> List[
      Item]:  #Este método recupera todos os itens da tabela "item". Ele executa uma consulta SQL que retorna todos os registros da tabela. Os resultados são transformados em objetos Item e retornados como uma lista
    sql = "SELECT item.idPedido, item.idProduto, quantidade, valorUnitario, valorItem, produto.nome as nomeProduto FROM item INNER JOIN produto ON item.idProduto = produto.idProduto WHERE idPedido=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (idPedido, )).fetchall()
    items = [Item(*x) for x in result]
    return items
  
  @classmethod
  def getCountByPedido(
    cls, idPedido: int
  ) -> List[
      Item]:  #Este método recupera todos os itens da tabela "item". Ele executa uma consulta SQL que retorna todos os registros da tabela. Os resultados são transformados em objetos Item e retornados como uma lista
    sql = "SELECT COUNT(idProduto) FROM item WHERE idPedido=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (idPedido, )).fetchone()
    return int(result[0])
  
  @classmethod
  def getCountCartItemsFromUser(
    cls, idUsuario: int
  ) -> List[
      Item]:
    sql = "SELECT COUNT(*) FROM item INNER JOIN pedido ON item.idPedido = pedido.idPedido INNER JOIN cliente ON cliente.idCliente = pedido.idCliente WHERE pedido.status='carrinho' and cliente.idCliente=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (idUsuario, )).fetchone()
    return int(result[0])
  
  @classmethod
  def exists_pedido_with_produto(cls, idProduto: int) -> bool:
    sql = "SELECT COUNT(*) FROM item WHERE idProduto=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (idProduto,)).fetchone()
    conn.close()
    # Retorna True se houver pelo menos um pedido associado, False caso contrário
    return result[0] > 0
  
  @classmethod
  def calcular_valor_total(cls, idPedido: int) -> float:
    sql = "SELECT SUM(quantidade * valorUnitario) FROM item WHERE idPedido = ?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (idPedido,)).fetchone()
    valor_total = result[0] if result and result[0] else 0.0
    return round(valor_total, 4)