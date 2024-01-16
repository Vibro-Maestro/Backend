import os

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import bcrypt

db_url = os.getenv('VIBRO_MAESTRO_DB_URL')
engine = create_engine(db_url, echo=True)

Session = sessionmaker(bind=engine)
Base = declarative_base()

class Music(Base):
    __tablename__ = 'musics'

Base.metadata.create_all(engine)