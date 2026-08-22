from database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    amount = Column(Float)
    # type can be either "income" or "expense"
    type = Column(String)
    category = Column(String)
    date = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))
