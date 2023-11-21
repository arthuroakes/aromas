from typing import List
from util.Database import Database
from models.Categoria import Categoria

class CategoriaRepo:

    @classmethod
    def createTable(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS categoria (
            idCategoria INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT)
        """
        conn = Database.createConnection()
        cursor = conn.cursor()
        tableCreated = (cursor.execute(sql).rowcount > 0)
        conn.commit()
        conn.close()
        return tableCreated
    
    @classmethod
    def insert(cls, categoria: Categoria) -> Categoria:
                sql = "INSERT INTO Categoria (nome) VALUES (?)"
                conn = Database.createConnection()
                cursor = conn.cursor()
                result = cursor.execute(sql, (categoria.nome,))
                if (result.rowcount > 0):
                    categoria.idCategoria = result.lastrowid
                    conn.commit()
                    conn.close()
                    return categoria
                else:
                    conn.close()
                    return None
                
    @classmethod
    def inserirCategoriasBase(cls):
        categorias = ["Cafés", "Doces", "Bebidas", "Croissants", "Executivos", "Pães", "Panquecas", "Salgados", "Tortas", "Bolos"]
        for c in categorias:
            categoria = Categoria(0, c)
            cls.insert(categoria)
    
    @classmethod
    def update(cls, categoria: Categoria) -> Categoria:
        sql = "UPDATE categoria SET nome=? WHERE idCategoria=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (categoria.nome, categoria.idCategoria))
        if (result.rowcount > 0):
            conn.commit()
            conn.close()
            return categoria
        else:
            conn.close()
            return None
        
    @classmethod
    def delete(cls, idCategoria: int) -> bool:
        sql = "DELETE FROM categoria WHERE idCategoria=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCategoria,))
        if (result.rowcount > 0):
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
        
    @classmethod
    def getAll(cls) -> List[Categoria]:
        sql = "SELECT idCategoria, nome FROM categoria ORDER BY nome"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql).fetchall()
        categorias = [Categoria(*x) for x in result]
        return categorias
    
    @classmethod
    def getOne(cls, idCategoria: int) -> Categoria:
        sql = "SELECT idCategoria, nome FROM categoria WHERE idCategoria=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCategoria,)).fetchone()
        categoria = Categoria(*result) if result else None
        return categoria
    
    @classmethod
    def nomeExiste(cls, nome: str) -> bool:
        sql = "SELECT EXISTS (SELECT 1 FROM categoria WHERE nome=?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (nome,)).fetchone()
        return bool(resultado[0])
    
    @classmethod
    def obterPagina(cls, pagina: int, tamanhoPagina: int) -> List[Categoria]:
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT idCategoria, nome FROM categoria ORDER BY nome LIMIT ?, ?"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [Categoria(*x) for x in resultado]
        return objetos
    
    @classmethod
    def obterQtdePaginas(cls, tamanhoPagina: int) -> int:
        sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM categoria) AS FLOAT) / ?) AS qtdePaginas"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (tamanhoPagina, )).fetchone()
        return int(resultado[0])
    
    @classmethod
    def obterCategoriaPorId(cls, idCategoria: int) -> Categoria | None:
        sql = "SELECT idCategoria, nome FROM categoria WHERE idCategoria=?"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (idCategoria,)).fetchone()
        if resultado:
            objeto = Categoria(
                idCategoria=resultado[0],
                nome=resultado[1],
            )
            return objeto
        else:
            return None
        
    @classmethod
    def obterPorNome(cls, nome: str) -> Categoria:
        sql = "SELECT * FROM categoria WHERE nome = ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (nome,)).fetchone()
        conn.close()
        if resultado:
            return Categoria(idCategoria=resultado[0], nome=resultado[1])
        else:
            return None

    @classmethod
    def deleteAll():
        conn = Database.createConnection()
        cursor = conn.cursor()
        sql = "DELETE FROM Categoria"
        cursor.execute(sql)
        conn.commit()
        return True
    
    @classmethod
    def categoriaExiste(cls, idCategoria: int) -> bool:
        sql = "SELECT EXISTS (SELECT 1 FROM categoria WHERE idCategoria=?)"
        conn = Database.createConnection()
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (idCategoria,)).fetchone()
        return bool(resultado[0])

    @classmethod
    def obterQtde(cls) -> int:
        sql = "SELECT COUNT(*) FROM categoria"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql).fetchone()
        return int(result[0])