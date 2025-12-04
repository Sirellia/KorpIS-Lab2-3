from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app import crud, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Customer])
def get_customers(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db)
):
    """Получить список всех клиентов"""
    return crud.get_customers(db, skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=schemas.Customer)
def get_customer(customer_id: UUID, db: Session = Depends(get_db)):
    """Получить клиента по ID"""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Клиент с ID {customer_id} не найден")
    return customer


@router.get("/{customer_id}/orders", response_model=List[schemas.Order])
def get_customer_orders(customer_id: UUID, db: Session = Depends(get_db)):
    """Получить все заказы клиента"""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Клиент с ID {customer_id} не найден")
    return crud.get_orders_by_customer(db, customer_id)


@router.get("/{customer_id}/tickets", response_model=List[schemas.SupportTicket])
def get_customer_tickets(customer_id: UUID, db: Session = Depends(get_db)):
    """Получить все обращения клиента"""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Клиент с ID {customer_id} не найден")
    return crud.get_support_tickets_by_customer(db, customer_id)


@router.post("/", response_model=schemas.Customer, status_code=201)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """Создать нового клиента"""
    # Проверка уникальности email
    existing = crud.get_customer_by_email(db, customer.email)
    if existing:
        raise HTTPException(status_code=400, detail=f"Клиент с email {customer.email} уже существует")
    return crud.create_customer(db, customer)


@router.put("/{customer_id}", response_model=schemas.Customer)
def update_customer(
        customer_id: UUID,
        customer_update: schemas.CustomerUpdate,
        db: Session = Depends(get_db)
):
    """Обновить данные клиента"""
    customer = crud.update_customer(db, customer_id, customer_update)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Клиент с ID {customer_id} не найден")
    return customer


@router.delete("/{customer_id}", status_code=204)
def delete_customer(customer_id: UUID, db: Session = Depends(get_db)):
    """Удалить клиента"""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Клиент с ID {customer_id} не найден")

    # Проверка на наличие заказов
    orders = crud.get_orders_by_customer(db, customer_id)
    if orders:
        raise HTTPException(status_code=400, detail="Невозможно удалить клиента с существующими заказами")

    crud.delete_customer(db, customer_id)