from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base,sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///.rent_a_shelf.db"
engine= create_engine(SQLALCHEMY_DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

db = SessionLocal()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    fullName=Column(String)
    email=Column(String)
    hashed_password=Column(String)
    role = Column(String)
    phone = Column(String)

Base.metadata.create_all(bind=engine)