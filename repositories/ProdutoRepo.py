import datetime
from typing import List
from util.Database import Database
from models.Produto import Produto

class ProdutoRepo:
    @classmethod
    def createTable(cls): #Cria a tabela produto no banco de dados, se ela ainda não existir. O método executa uma instrução SQL para criar a tabela com as colunas correspondentes aos atributos da classe Produto. 
        sql = """
            CREATE TABLE IF NOT EXISTS produto (
            idProduto INTEGER PRIMARY KEY AUTOINCREMENT,
            idCategoria INTEGER,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            descricao TEXT NOT NULL,
            qtdEstoque INTEGER NOT NULL,
            emPromocao BOOLEAN NOT NULL,
            dataLancamento DATE NOT NULL,
            FOREIGN KEY (idCategoria) REFERENCES Categoria (idCategoria)
            )
        """
        conn = Database.createConnection()
        cursor = conn.cursor()
        tableCreated = (cursor.execute(sql).rowcount > 0)
        conn.commit()
        conn.close()
        return tableCreated

    @classmethod
    def insert(cls, produto: Produto) -> Produto: # Insere um novo registro na tabela produto. O método recebe um objeto Produto como parâmetro e executa uma instrução SQL para inserir os valores dos atributos do objeto na tabela.
        sql = "INSERT INTO produto (idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento) VALUES (?, ?, ?, ?, ?, ?, ?)" 
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (produto.idCategoria, produto.nome, produto.preco, produto.descricao, produto.qtdEstoque, produto.emPromocao, produto.dataLancamento))
        if result.rowcount > 0:
            produto.idProduto = result.lastrowid
            conn.commit()
            conn.close()
            return produto
        else:
            conn.close()
            return None

    @classmethod
    def update(cls, produto: Produto) -> Produto: #Atualiza um registro existente na tabela produto. 
        sql = "UPDATE produto SET idCategoria=?, nome=?, preco=?, descricao=?, qtdEstoque=?, emPromocao=?, dataLancamento=? WHERE idProduto=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (produto.idCategoria, produto.nome, produto.preco, produto.descricao, produto.qtdEstoque, produto.emPromocao, produto.dataLancamento, produto.idProduto))
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return produto
        else:
            conn.close()
            return None

    @classmethod
    def delete(cls, idProduto: int) -> bool: #xclui um registro da tabela produto com base no atributo idProduto.
        sql = "DELETE FROM produto WHERE idProduto=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idProduto, ))
        if result.rowcount > 0:
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False

    @classmethod
    def getAll(cls) -> List[Produto]: #Retorna uma lista de todos os registros da tabela produto. O método executa uma instrução SQL para selecionar todos os registros e cria objetos Produto com os valores retornados
        sql = "SELECT idProduto, idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento FROM produto"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql).fetchall()
        produtos = [Produto(*row) for row in result]
        conn.close()
        return produtos
    
    
    @classmethod
    def getAllByCategoria(cls, idCategoria: int) -> List[Produto]: 
        sql = "SELECT idProduto, idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento FROM produto WHERE idCategoria=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCategoria, )).fetchall()
        produtos = [Produto(*row) for row in result]
        conn.close()
        return produtos
    

    @classmethod
    def getOne(cls, idProduto: int) -> Produto: # Retorna um objeto Produto com base no atributo idProduto.
        sql = "SELECT idProduto, idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento FROM produto WHERE idProduto=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idProduto, )).fetchone()
        produto = Produto(*result) if result else None
        conn.close()
        return produto
    
    @classmethod
    def getAllOrderedByDataLancamentoDesc(cls) -> List[Produto]: #Retorna uma lista de todos os registros da tabela produto, ordenados pela data de lançamento em ordem decrescente
        sql = "SELECT idProduto, idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento FROM produto ORDER BY dataLancamento DESC"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql).fetchall()
        produtos = [Produto(*row) for row in result]
        conn.close()
        return produtos[::-1]

    @classmethod
    def getPromocao(cls) -> List[Produto]: #Retorna uma lista de todos os registros da tabela produto que estão em promoção
        sql = "SELECT idProduto, idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento FROM produto WHERE emPromocao = 'sim'"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql).fetchall()
        produtos = [Produto(*row) for row in result]
        conn.close()
        return produtos

    @classmethod
    def getNaoPromocao(cls) -> List[Produto]: #Retorna uma lista de todos os registros da tabela produto que não estão em promoção.
        sql = "SELECT idProduto, idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento FROM produto WHERE emPromocao = 'nao'"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql).fetchall()
        produtos = [Produto(*row) for row in result]
        conn.close()
        return produtos
    
    
    @classmethod
    def getLancamento(cls) -> List[Produto]:
        today = datetime.datetime.now()
        thirty_days_ago = today - datetime.timedelta(days=30)
        sql = "SELECT idProduto, idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento FROM produto WHERE dataLancamento >= ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (thirty_days_ago,)).fetchall()
        produtos = [Produto(*row) for row in result]
        conn.close()
        return produtos 
    
    @classmethod
    def obterProduto(cls, pagina: int, tamanhoPagina: int) -> List[Produto]:
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT idProduto, idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento FROM produto ORDER BY nome LIMIT ?, ?"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [Produto(*x) for x in resultado]
        return objetos
    
    @classmethod
    def obterQtdeProdutos(cls, tamanhoPagina: int) -> int:
        sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM produto) AS FLOAT) / ?) AS qtdePaginas"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (tamanhoPagina, )).fetchone()
        return int(resultado[0])
    
    @classmethod
    def obterProdutosEmPromocao(cls, pagina: int, tamanhoPagina: int) -> List[Produto]:
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT idProduto, idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento FROM produto WHERE emPromocao = 'sim' ORDER BY nome LIMIT ?, ?"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [Produto(*x) for x in resultado] 
        return objetos
    
    @classmethod
    def obterQtdeProdutosEmPromocao(cls, tamanhoPagina: int) -> int:
        sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM produto WHERE emPromocao = 'sim') AS FLOAT) / ?) AS qtdePaginas"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (tamanhoPagina,)).fetchone()
        return int(resultado[0])
    
    @classmethod
    def obterProdutosNaoPromocao(cls, pagina: int, tamanhoPagina: int) -> List[Produto]:
        inicio = (pagina - 1) * tamanhoPagina
        sql = "SELECT idProduto, idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento FROM produto WHERE emPromocao = 'nao' ORDER BY nome LIMIT ?, ?"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (inicio, tamanhoPagina)).fetchall()
        objetos = [Produto(*x) for x in resultado] 
        return objetos

    @classmethod
    def obterQtdeProdutosNaoPromocao(cls, tamanhoPagina: int) -> int:
        sql = "SELECT CEIL(CAST((SELECT COUNT(*) FROM produto WHERE emPromocao = 'nao') AS FLOAT) / ?) AS qtdePaginas"
        conexao = Database.createConnection()
        cursor = conexao.cursor()
        resultado = cursor.execute(sql, (tamanhoPagina,)).fetchone()
        return int(resultado[0])
    
    @classmethod
    def obterPorCategoria(cls, idCategoria: int) -> List[Produto]:
        sql = "SELECT idProduto, idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento FROM produto WHERE idCategoria = ?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCategoria,)).fetchall()
        produtos = [Produto(*x) for x in result]
        conn.close()
        return produtos
    
    @classmethod
    def obterProdutoPorId(cls, idProduto: int) -> Produto | None:
        sql = "SELECT idProduto, idCategoria, nome, preco, descricao, qtdEstoque, emPromocao, dataLancamento FROM produto WHERE idProduto = ?"
        conn = Database.createConnection() 
        cursor = conn.cursor()
        resultado = cursor.execute(sql, (idProduto,)).fetchone()
        conn.close() 
        if resultado:
            objeto = Produto(
                idProduto=resultado[0],
                idCategoria=resultado[1],
                nome=resultado[2],
                preco=resultado[3],
                descricao=resultado[4],
                qtdEstoque=resultado[5],
                emPromocao=resultado[6],
                dataLancamento=resultado[7]
            )
            return objeto
        else:
            return None
        
    @classmethod
    def exists_produto_with_categoria(cls, idCategoria: int) -> bool:
        sql = "SELECT COUNT(*) FROM produto WHERE idCategoria=?"
        conn = Database.createConnection()
        cursor = conn.cursor()
        result = cursor.execute(sql, (idCategoria,)).fetchone()
        conn.close()
        # Retorna True se houver pelo menos um produto associado, False caso contrário
        return result[0] > 0
