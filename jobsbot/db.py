from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from .models import Base

def init_db(database_url: str) -> sessionmaker[Session]:
    """Crea la base de datos con las tablas necesarias y returna la session factory"""
    if database_url.startswith("sqlite:///") and ":memory:" not in database_url:
        Path(database_url.removeprefix("sqlite:///")).parent.mkdir(parents=True,exist_ok=True)
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    return sessionmaker(engine,expire_on_commit=False)