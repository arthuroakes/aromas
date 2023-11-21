from typing import List
from util.Database import Database
from models.Reserva import Reserva


class ReservaRepo:

  @classmethod
  def createTable(cls):
    sql = """
            CREATE TABLE IF NOT EXISTS reserva (
            idReserva INTEGER PRIMARY KEY AUTOINCREMENT,
            idCliente INTEGER NOT NULL,
            idMesa INTEGER NOT NULL,
            dataHoraCadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
            dataReserva DATE NOT NULL,
            horaReserva INTEGER NOT NULL, 
            qtdPessoas INTEGER NOT NULL,
            FOREIGN KEY (idCliente) REFERENCES Cliente (idCliente),
            FOREIGN KEY (idMesa) REFERENCES Mesa (idMesa))
        """
    conn = Database.createConnection()
    cursor = conn.cursor()
    tableCreated = (cursor.execute(sql).rowcount > 0)
    conn.commit()
    conn.close()
    return tableCreated

  @classmethod
  def insert(cls, reserva: Reserva) -> Reserva:
    sql = "INSERT INTO reserva (idCliente, idMesa, dataHoraCadastro, dataReserva, horaReserva, qtdPessoas) VALUES (?, ?, ?, ?, ?, ?)"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (reserva.idCliente, reserva.idMesa,reserva.dataHoraCadastro, reserva.dataReserva, reserva.horaReserva, reserva.qtdPessoas))
    if (result.rowcount > 0):
      conn.commit()
      conn.close()
      return reserva
    else:
      conn.close()
      return None

  @classmethod
  def update(cls, reserva: Reserva) -> Reserva:
    sql = "UPDATE reserva SET idCliente=?, idMesa=?, dataHoraCadastro=?, dataReserva=?, horaReserva=?, qtdPessoas=? WHERE idReserva=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(
      sql, (reserva.idCliente, reserva.idMesa, reserva.dataHoraCadastro,
            reserva.dataReserva, reserva.horaReserva, reserva.qtdPessoas, reserva.idReserva))
    if (result.rowcount > 0):
      conn.commit()
      conn.close()
      return reserva
    else:
      conn.close()
      return None

  @classmethod
  def delete(cls, idReserva: int) -> bool:
    sql = "DELETE FROM reserva WHERE idReserva=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (idReserva, ))
    if (result.rowcount > 0):
      conn.commit()
      conn.close()
      return True
    else:
      conn.close()
      return False

  @classmethod
  def getAll(cls) -> List[Reserva]:
    sql = "SELECT idReserva, idCliente, idMesa, dataHoraCadastro, dataReserva, horaReserva, qtdPessoas FROM reserva"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql).fetchall()
    reservas = [Reserva(*x) for x in result]
    return reservas

  @classmethod
  def getOne(cls, idReserva: int) -> Reserva:
    sql = "SELECT idReserva, idCliente, idMesa, dataHoraCadastro, dataReserva, horaReserva, qtdPessoas FROM reserva WHERE idReserva=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (idReserva, )).fetchone()
    reserva = Reserva(*result) if result else None
    return reserva

  @classmethod
  def obterReserva(cls, pagina: int, tamanhoPagina: int) -> List[Reserva]:
      inicio = (pagina - 1) * tamanhoPagina
      sql = "SELECT idReserva, usuario.nome, mesa.numero, dataHoraCadastro, dataReserva, horaReserva, qtdPessoas FROM reserva INNER JOIN mesa ON reserva.idMesa = mesa.idMesa INNER JOIN usuario ON reserva.idCliente = usuario.idUsuario ORDER BY idReserva LIMIT ?, ?"
      conn = Database.createConnection()
      cursor = conn.cursor()
      result = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
      objetos = [
          Reserva(
              idReserva=x[0],
              idCliente=x[1],
              idMesa=x[2],
              dataHoraCadastro=x[3],
              dataReserva=x[4],
              horaReserva=x[5],
              qtdPessoas=x[6],
          )
          for x in result
      ]
      return objetos

  @classmethod
  def obterQtdeReservas(cls, tamanhoPagina: int) -> int:
      sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM reserva) AS FLOAT) / ?) AS qtdePaginas"
      conexao = Database.createConnection()
      cursor = conexao.cursor()
      resultado = cursor.execute(sql, (tamanhoPagina, )).fetchone()
      return int(resultado[0])

  
  @classmethod
  def obterReservaPorId(cls, idReserva: int) -> Reserva | None:
      sql = "SELECT idReserva, idCliente, idMesa, dataHoraCadastro, dataReserva, horaReserva, qtdPessoas FROM reserva WHERE idReserva = ?"
      conn = Database.createConnection() 
      cursor = conn.cursor()
      resultado = cursor.execute(sql, (idReserva,)).fetchone()
      conn.close() 
      if resultado:
          objeto = Reserva(
              idReserva=resultado[0],
              idCliente=resultado[1],
              idMesa=resultado[2],
              dataHoraCadastro=resultado[3],
              dataReserva=resultado[4],
              horaReserva=resultado[5],
              qtdPessoas=resultado[6]
          )
          return objeto
      else:
          return None
      
  @classmethod
  def exists_reserva_with_mesa(cls, idMesa: int) -> bool:
    sql = "SELECT COUNT(*) FROM reserva WHERE idMesa=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (idMesa,)).fetchone()
    conn.close()
    # Retorna True se houver pelo menos uma reserva associada, False caso contrário
    return result[0] > 0
  
  @classmethod
  def obterReservaPorIdCliente(cls, idUsuario: int, pagina: int, tamanhoPagina: int) -> List[Reserva]:
    inicio = (pagina - 1) * tamanhoPagina
    sql = "SELECT idReserva, idUsuario, mesa.numero, dataHoraCadastro, dataReserva, horaReserva, qtdPessoas FROM reserva INNER JOIN mesa ON reserva.idMesa = mesa.idMesa INNER JOIN usuario ON reserva.idCliente = usuario.idUsuario WHERE idCliente = ? ORDER BY dataReserva LIMIT ?, ?"
    conexao = Database.createConnection()
    cursor = conexao.cursor()
    resultado = cursor.execute(sql, (idUsuario, inicio, tamanhoPagina)).fetchall()
    reservas = [
       Reserva(
          idReserva=x[0],
          idCliente=x[1],
          idMesa=x[2],
          dataHoraCadastro=x[3],
          dataReserva=x[4],
          horaReserva=x[5],
          qtdPessoas=x[6],
        ) 
        for x in resultado
    ]
    conexao.close()
    return reservas