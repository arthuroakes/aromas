from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from repositories.UsuarioRepo import UsuarioRepo
from repositories.CategoriaRepo import CategoriaRepo
from repositories.ChatRepo import ChatRepo
from repositories.ClienteRepo import ClienteRepo
from repositories.EnderecoRepo import EnderecoRepo
from repositories.FuncionarioRepo import FuncionarioRepo
from repositories.ItemRepo import ItemRepo
from repositories.MesaRepo import MesaRepo
from repositories.PedidoRepo import PedidoRepo
from repositories.ProdutoRepo import ProdutoRepo
from repositories.ReservaRepo import ReservaRepo
from routes.MainRoutes import router as MainRoutes
from routes.AdminRoutes import router as AdminRoutes
from routes.ClienteRoutes import router as ClienteRoutes
from routes.FuncionarioRoutes import router as FuncionarioRoutes 
from routes.ProdutoRoutes import router as ProdutoRoutes
from routes.CategoriaRoutes import router as CategoriaRoutes
from routes.PedidoRoutes import router as PedidoRoutes 
from routes.ReservaRoutes import router as ReservaRoutes
from routes.MesaRoutes import router as MesaRoutes
from routes.EnderecoRoutes import router as EnderecoRoutes
from routes.ChatRoutes import router as ChatRoutes

CategoriaRepo.createTable()
ChatRepo.createTable()
ClienteRepo.createTable()
EnderecoRepo.createTable()
FuncionarioRepo.createTable()
ItemRepo.createTable()
MesaRepo.createTable()
PedidoRepo.createTable()
ProdutoRepo.createTable()
ReservaRepo.createTable()
UsuarioRepo.createTable()
UsuarioRepo.criarUsuarioAdmin()


app = FastAPI()

app.mount(path="/static", app=StaticFiles(directory="static"), name="static")

app.include_router(MainRoutes)
app.include_router(ClienteRoutes)
app.include_router(AdminRoutes)
app.include_router(FuncionarioRoutes)
app.include_router(ProdutoRoutes)
app.include_router(CategoriaRoutes)
app.include_router(PedidoRoutes)
app.include_router(ReservaRoutes)
app.include_router(MesaRoutes)
app.include_router(EnderecoRoutes)
app.include_router(ChatRoutes) 

if CategoriaRepo.obterQtde() == 0:
  CategoriaRepo.inserirCategoriasBase()


# if __name__ == "__main__":
#   uvicorn.run(app="main:app", reload=True) 

### esquecer senha precisa de enviar email, o que foge do escopo do técnico.