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
    __tablename__ = 'music'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    music_name = Column(String)
    composer = Column(String)

    file_name = Column(String, unique=True)

Base.metadata.create_all(engine)

def create_music(music_name, composer, file_name):
    session = Session()

    music = Music(music_name=music_name, composer=composer, file_name=file_name)

    session.add(music)
    session.commit()

    session.close()

def read_music(music_name, composer):
    session = Session()

    music = session.query(Music).where(Music.music_name == music_name).where(Music.composer == composer).first()
    session.close()

    return music.file_name

def update_music(music_name, composer, updated_file_name):
    session = Session()

    music = session.query(Music).where(Music.music_name == music_name).where(Music.composer == composer).first()

    if music:
        music.file_name = updated_file_name

    session.commit()
    session.close()

def delete_music(music_name, composer):
    session = Session()

    music = session.query(Music).where(Music.music_name == music_name).where(Music.composer == composer).first()

    if music:
        session.delete(music)
        session.commit()

    session.close()