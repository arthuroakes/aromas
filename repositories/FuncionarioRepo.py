import shutil
from typing import List

from fastapi import UploadFile
from repositories.UsuarioRepo import UsuarioRepo
from util.Database import Database
from models.Funcionario import Funcionario
from models.Usuario import Usuario


class FuncionarioRepo:

  @classmethod
  def createTable(cls):
    sql = """
            CREATE TABLE IF NOT EXISTS funcionario (
            idFuncionario INTEGER PRIMARY KEY,
            dataAdmissao TEXT NOT NULL,
            dataDemissao TEXT,
            salario REAL NOT NULL,
            dataNascimento DATE NOT NULL,
            FOREIGN KEY (idFuncionario) REFERENCES Usuario (idUsuario))
        """
    conn = Database.createConnection()
    cursor = conn.cursor()
    tableCreated = (cursor.execute(sql).rowcount > 0)
    conn.commit()
    conn.close()
    return tableCreated

  @classmethod
  def insert(cls, funcionario: Funcionario) -> Funcionario:
    usuario = UsuarioRepo.insert(
      Usuario(0, funcionario.nome, funcionario.email, funcionario.telefone, 
              funcionario.cpf, funcionario.senha))
    sql = "INSERT INTO funcionario (idFuncionario, dataAdmissao, dataDemissao, salario, dataNascimento) VALUES (?, ?, ?, ?, ?)"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql,
                            (usuario.idUsuario, funcionario.dataAdmissao,
                             funcionario.dataDemissao, funcionario.salario, funcionario.dataNascimento))
    if (result.rowcount > 0):
      conn.commit()
      conn.close()
      funcionario.idUsuario = usuario.idUsuario
      return funcionario
    else:
      conn.close()
      return None

  @classmethod ## alterar update
  def update(cls, funcionario: Funcionario) -> Funcionario:
    usuario = Usuario(
        idUsuario=funcionario.idUsuario,
        nome=funcionario.nome, 
        email=funcionario.email, 
        cpf=funcionario.cpf,
        telefone=funcionario.telefone
    )
    UsuarioRepo.update(usuario)
    sql = "UPDATE funcionario SET dataAdmissao=?, dataDemissao=?, salario=?, dataNascimento=? WHERE idFuncionario=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(
      sql, 
      (
          funcionario.dataAdmissao, 
          funcionario.dataDemissao, 
          funcionario.salario, 
          funcionario.dataNascimento, 
          funcionario.idUsuario
      ))
    if (result.rowcount > 0):
      conn.commit()
      conn.close()
      funcionario.idUsuario = usuario.idUsuario 
      return funcionario
    else:
      conn.close()
      return None

  @classmethod
  def delete(cls, idUsuario: int) -> bool:
      sql = "DELETE FROM funcionario WHERE idFuncionario=?"
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
  def getAll(cls) -> List[Funcionario]:
    sql = "SELECT usuario.idUsuario, usuario.nome, usuario.email, usuario.telefone, usuario.cpf, funcionario.dataAdmissao, funcionario.dataDemissao, funcionario.salario, funcionario.dataNascimento FROM funcionario INNER JOIN usuario ON funcionario.idFuncionario = usuario.idUsuario ORDER BY usuario.nome"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql).fetchall()
    funcionarios = [Funcionario(*x) for x in result]
    return funcionarios

  @classmethod
  def getOne(cls, idFuncionario: int) -> Funcionario:
    sql = "SELECT idUsuario, nome, email, telefone, cpf, senha, dataAdmissao, dataDemissao, salario, dataNascimento FROM funcionario INNER JOIN usuario ON funcionario.idFuncionario = usuario.idUsuario ORDER BY funcionario.nome WHERE idFuncionario=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (idFuncionario, )).fetchone()
    funcionario = Funcionario(*result)
    return funcionario

  @classmethod
  def getAllOrderedByAdmissionDateAsc(cls) -> List[Funcionario]:
    sql = "SELECT idUsuario, nome, email, senha, telefone, cpf, pontuacao, dataCadastro, dataNascimento, dataAdmissao, dataDemissao, salario FROM funcionario INNER JOIN usuario ON funcionario.idFuncionario = usuario.idUsuario ORDER BY dataAdmissao ASC"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql).fetchall()
    funcionarios = [Funcionario(*x) for x in result]
    return funcionarios
  
  @classmethod
  def existeId(cls, idFuncionario: int) -> bool:
    sql = "SELECT idFuncionario FROM funcionario WHERE idFuncionario=?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (idFuncionario, )).fetchone()    
    return result != None 

  @classmethod
  def obterPagina(cls, pagina: int, tamanhoPagina: int) -> List[Funcionario]:
    inicio = (pagina - 1) * tamanhoPagina
    sql = "SELECT usuario.idUsuario, usuario.nome, usuario.email, usuario.telefone, usuario.cpf, funcionario.dataAdmissao, funcionario.dataDemissao, funcionario.salario, funcionario.dataNascimento FROM funcionario INNER JOIN usuario ON funcionario.idFuncionario = usuario.idUsuario ORDER BY usuario.nome LIMIT ?, ?"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
    objetos = [
      Funcionario(
          idUsuario=x[0],
          nome=x[1],
          email=x[2],
          telefone=x[3],
          cpf=x[4],
          dataAdmissao=x[5],
          dataDemissao=x[6],
          salario=x[7],
          dataNascimento=x[8],
      )
      for x in result
    ]
    return objetos
  
  @classmethod
  def obterQtdePaginas(cls, tamanhoPagina: int) -> int:
    sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM funcionario) AS FLOAT) / ?) AS qtdePaginas"
    conn = Database.createConnection()
    cursor = conn.cursor()
    result = cursor.execute(sql, (tamanhoPagina, )).fetchone()
    return int(result[0])
  
  @classmethod
  def obterPorId(cls, idFuncionario: int) -> Funcionario | None:
      sql = "SELECT usuario.idUsuario, usuario.nome, usuario.email, usuario.telefone, usuario.cpf, funcionario.dataAdmissao, funcionario.dataDemissao, funcionario.salario, funcionario.dataNascimento FROM funcionario INNER JOIN usuario ON funcionario.idFuncionario = usuario.idUsuario WHERE funcionario.idFuncionario = ?"
      conn = Database.createConnection()
      cursor = conn.cursor()
      resultado = cursor.execute(sql, (idFuncionario,)).fetchone()
      conn.close()
      if resultado:
          objeto = Funcionario(
              idUsuario=resultado[0],
              nome=resultado[1],
              email=resultado[2],
              telefone=resultado[3],
              cpf=resultado[4],
              dataAdmissao=resultado[5],
              dataDemissao=resultado[6],
              salario=resultado[7],
              dataNascimento=resultado[8]
          )
          return objeto
      else:
          return None
        
  @classmethod
  def atualizardataDemissao(cls, idFuncionario: int, dataDemissao: str) -> bool: 
      sql = "UPDATE funcionario SET dataDemissao=? WHERE idFuncionario=?"
      conn = Database.createConnection()
      cursor = conn.cursor()
      result = cursor.execute(sql, (idFuncionario, dataDemissao))
      if result.rowcount > 0:
          conn.commit()
          conn.close()
          return True
      else:
          conn.close()
          return False