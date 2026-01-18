from sqlalchemy import create_engine, Column, INTEGER, String
from sqlalchemy.orm import declarative_base
from data.config import PG_DB, PG_HOST, PG_PASS, PG_PORT, PG_USER
engine = create_engine(f'postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}')

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'