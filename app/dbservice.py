from sqlalchemy import create_engine, Column, Integer, String, DateTime, func, ForeignKey
from sqlalchemy.orm import declarative_base,sessionmaker,relationship, validates
from datetime import datetime
# bind database to the engine

SQLALCHEMY_DATABASE_URL = "sqlite:///.user_auth.db"
engine= create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
db = SessionLocal()

# create the relevant tables needed for user profile and storing other important details.
# user table, user-details table, payment details table

# create a basemodel which carries the d column and use it to extend other tables.. 
# This pevents repetition since all tables require id
class BaseModel(Base):
    __abstract__ = True ## means the class won't create a table of its own
    id= Column(Integer, primary_key=True, index=True, autoincrement=True)

class User(BaseModel):
    __tablename__ = "users"

    first_name=Column(String(80))
    last_name=Column(String(80))
    email=Column(String, unique=True, nullable=False)
    hashed_password=Column(String, nullable=False)
    role = Column(String)
    phone_number = Column(String(15), nullable=False)
    created_at = Column(DateTime, default= func.now(), nullable=False)
    firebase_id= Column(String)

    user_detail = relationship('UserDetail', back_populates='user')
class UserDetail(BaseModel):
    __tablename__= "user_details"

    uid= Column(Integer,ForeignKey('users.id'), nullable=False)
    last_login= Column(String, nullable=False)
    account_status= Column(String, default="Active")
    
    user = relationship('User', back_populates='user_detail')

    @validates('last_login')
    def validate_last_login(self, key, value):
        # Ensure 'last_login' is always a datetime string in a consistent format
        try:
            datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError("Invalid datetime format for 'last_login'. Expected format: %Y-%m-%d %H:%M:%S")
        return value

Base.metadata.create_all(bind=engine)