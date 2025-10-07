import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import Engine

# Import all models from the consolidated file
from data_models.database_models import *

class DatabaseConfig:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cardiac_health.db")
    
    engine: Engine = create_engine(
        DATABASE_URL, 
        echo=True,
        connect_args={"check_same_thread": False}
    )

def get_session():
    with Session(DatabaseConfig.engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(DatabaseConfig.engine)

db_config = DatabaseConfig()