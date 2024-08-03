from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from .database import engine, SessionLocal, Deposit, Base, create_tables

app = FastAPI()

@app.on_event("startup")
async def startup():
    create_tables()

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get('/calculation', response_model=List[Dict[str, float]])
def get_calculation(params: DepositParams = Depends(), db: Session = Depends(get_db)):
    start_date = parse_date(params.date)

    result = []
    current_date = start_date

    for _ in range(params.periods):
        params.amount *= (1 + (params.rate / 100) / 12)

        last_day_of_current_month = get_last_day_of_month(current_date)

        formatted_date = last_day_of_current_month.strftime("%d.%m.%Y")

        result.append({
            formatted_date: round(params.amount, 2)
        })

        deposit = Deposit(date=last_day_of_current_month, amount=params.amount)
        db.add(deposit)
        db.commit()

        current_date = last_day_of_current_month + timedelta(days=1)
    return result
