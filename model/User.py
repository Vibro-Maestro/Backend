import os

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import bcrypt

db_url = os.getenv('VIBRO_MAESTRO_DB_URL')
engine = create_engine(db_url, echo=True)

Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    email = Column(String, unique=True)
    name = Column(String)
    password_hash = Column(String)

    @property
    def password(self):
        raise AttributeError("password is write-only")

    @password.setter
    def password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.checkpw(bytes(password, 'utf-8'), self.password_hash)

Base.metadata.create_all(engine)

def create_user(email, name, password):
    session = Session()

    user = User(email=email, name=name, password=password)

    session.add(user)
    session.commit()

    session.close()

def read_user(email):
    session = Session()

    user = session.query(User).where(User.email == email).first()
    session.close()

    return user

def update_user(email=None, name=None, password=None):
    session = Session()

    user = session.query(User).where(User.email == email).first()

    if email:
        if name:
            user.name = name
        
        if password:
            user.password = password

        session.commit()

    session.close()

def delete_user(email, password):
    session = Session()

    user = session.query(User).get(email)

    if user:
        if user.password == password:
            session.delete(user)
            session.commit()

    session.close()
