from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Dict

# Import SQLAlchemy dependencies
from sqlalchemy import create_engine, Column, Integer, Float, String, Date, Base
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL is taken from environment variables
import os

DATABASE_URL = os.getenv('DATABASE_URL')

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Create a simple model for demonstration
class DepositRecord(Base):
    __tablename__ = "deposits"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    amount = Column(Float)
    rate = Column(Float)
    periods = Column(Integer)


# Create the database tables
Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()


class DepositParams(BaseModel):
    date: str = Query(..., description="Дата начала в формате dd.mm.yyyy")
    periods: int = Field(ge=1, le=60)
    amount: float = Field(ge=10000, le=3000000)
    rate: float = Field(ge=1, le=8)


def parse_date(date_str: str) -> datetime.date:
    try:
        return datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Дата должна быть в формате dd.mm.yyyy")


def get_last_day_of_month(date: datetime.date) -> datetime.date:
    next_month = date.replace(day=28) + timedelta(days=4)
    return next_month - timedelta(days=next_month.day)


@app.get('/calculation', response_model=List[Dict[str, float]])
def get_calculation(params: DepositParams = Depends(), db: SessionLocal = Depends(get_db)):
    start_date = parse_date(params.date)

    result = []
    current_date = start_date

    for _ in range(params.periods):
        params.amount *= (1 + (params.rate / 100) / 12)

        last_day_of_current_month = get_last_day_of_month(current_date)

        formatted_date = last_day_of_current_month.strftime("%d.%m.%Y")

        # Save the calculation result to the database
        deposit_record = DepositRecord(
            date=last_day_of_current_month,
            amount=params.amount,
            rate=params.rate,
            periods=params.periods
        )
        db.add(deposit_record)
        db.commit()

        result.append({
            formatted_date: round(params.amount, 2)
        })

        current_date = last_day_of_current_month + timedelta(days=1)
    return result
