from sqlalchemy import create_engine, Column, INTEGER, String, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker
from data.config import PG_DB, PG_HOST, PG_PASS, PG_PORT, PG_USER
engine = create_engine(f'postgresql+psycopg2://{PG_USER}:{PG_PASS}@{PG_HOST}:{PG_PORT}/{PG_DB}')

Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

class User(Base):
    __tablename__ = 'users'
    id = Column(INTEGER, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True)
    full_name = Column(String(50), nullable=False)
    phone =  Column(String(13))

    def save(self, session):
        session.add(self)
        session.commit()

    @classmethod
    def check_register(cls, session, id_):
        obj = session.query(cls).filter(id_ == cls.chat_id).first()
        if not obj:
            return False
        return True