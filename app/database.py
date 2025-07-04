# 🛠️ Importa os módulos fundamentais do SQLModel
# 🛠️ Import core modules from SQLModel
from sqlmodel import create_engine, SQLModel, Session

# 📦 Importa Generator para tipar corretamente a função get_session
# 📦 Import Generator to properly type the get_session function
from typing import Generator

# ---------------------------------------------------------------------
# 🗂️ Define o caminho do banco de dados SQLite local
# 🗂️ Set the path for the local SQLite database
DATABASE_URL = "sqlite:///./soda_machine.db"

# ⚙️ Cria a engine de conexão com o banco de dados
# ⚙️ Create the database connection engine
engine = create_engine(
    DATABASE_URL,
    echo=True  # Mostra todas as queries SQL no console (modo debug)
    # Shows all SQL queries in console (debug mode)
)

# ---------------------------------------------------------------------
# 🧱 Função para criar todas as tabelas no banco usando os modelos
# 🧱 Function to create all database tables based on model definitions
def create_db_and_tables():
    """Cria todas as tabelas definidas nos modelos SQLModel.
    Create all tables defined in SQLModel schemas."""
    SQLModel.metadata.create_all(engine)

# ---------------------------------------------------------------------
# 🔁 Gera uma sessão de banco para ser usada nos endpoints do FastAPI
# 🔁 Generate a database session to be used in FastAPI endpoints
def get_session() -> Generator[Session, None, None]:
    """Dependência para o FastAPI fornecer uma sessão de banco de dados.
    Dependency for FastAPI to provide a database session."""
    with Session(engine) as session:
        yield session