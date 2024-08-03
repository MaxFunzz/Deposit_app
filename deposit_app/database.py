from sqlalchemy import create_engine, Column, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:mysecretpassword@db/deposit_database"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Deposit(Base):
    __tablename__ = "deposits"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    amount = Column(Float)


def create_tables():
    Base.metadata.create_all(bind=engine)
