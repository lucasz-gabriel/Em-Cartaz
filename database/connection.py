from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Caminho do banco de dados
DATABASE_URL = "sqlite:///cinema.db"

# Cria a conexão com o banco
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Fábrica de sessões para realizar operações no banco
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para os modelos das tabelas
Base = declarative_base()
