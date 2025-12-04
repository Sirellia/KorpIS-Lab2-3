from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app import crud, schemas, models

router = APIRouter()


@router.get("/", response_model=List[schemas.Order])
def get_orders(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        customer_id: UUID = Query(None, description="Фильтр по клиенту"),
        status_id: int = Query(None, description="Фильтр по статусу"),
        db: Session = Depends(get_db)
):
    """Получить список заказов"""
    query = db.query(models.Order)
    if customer_id:
        query = query.filter(models.Order.customer_id == customer_id)
    if status_id:
        query = query.filter(models.Order.order_status_id == status_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{order_id}", response_model=schemas.Order)
def get_order(order_id: UUID, db: Session = Depends(get_db)):
    """Получить заказ по ID"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Заказ с ID {order_id} не найден")
    return order


@router.get("/{order_id}/items", response_model=List[schemas.OrderItem])
def get_order_items(order_id: UUID, db: Session = Depends(get_db)):
    """Получить позиции заказа"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Заказ с ID {order_id} не найден")
    return crud.get_order_items_by_order(db, order_id)


@router.get("/{order_id}/shipments", response_model=List[schemas.Shipment])
def get_order_shipments(order_id: UUID, db: Session = Depends(get_db)):
    """Получить отправления заказа"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Заказ с ID {order_id} не найден")
    return crud.get_shipments_by_order(db, order_id)


@router.post("/", response_model=schemas.Order, status_code=201)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db)):
    """Создать новый заказ"""
    # Проверка существования клиента
    customer = crud.get_customer(db, order.customer_id)
    if not customer:
        raise HTTPException(status_code=400, detail=f"Клиент с ID {order.customer_id} не найден")

    # Проверка статуса
    status = db.query(models.Dictionary_OrderStatus).filter(
        models.Dictionary_OrderStatus.status_id == order.order_status_id
    ).first()
    if not status:
        raise HTTPException(status_code=400, detail=f"Статус заказа с ID {order.order_status_id} не найден")

    # Проверка способа оплаты
    payment = db.query(models.Dictionary_PaymentMethod).filter(
        models.Dictionary_PaymentMethod.method_id == order.payment_method_id
    ).first()
    if not payment:
        raise HTTPException(status_code=400, detail=f"Способ оплаты с ID {order.payment_method_id} не найден")

    return crud.create_order(db, order)


@router.put("/{order_id}", response_model=schemas.Order)
def update_order(
        order_id: UUID,
        order_update: schemas.OrderUpdate,
        db: Session = Depends(get_db)
):
    """Обновить заказ"""
    order = crud.update_order(db, order_id, order_update)
    if not order:
        raise HTTPException(status_code=404, detail=f"Заказ с ID {order_id} не найден")
    return order


@router.put("/{order_id}/status/{status_id}", response_model=schemas.Order)
def update_order_status(order_id: UUID, status_id: int, db: Session = Depends(get_db)):
    """Обновить статус заказа"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Заказ с ID {order_id} не найден")

    status = db.query(models.Dictionary_OrderStatus).filter(
        models.Dictionary_OrderStatus.status_id == status_id
    ).first()
    if not status:
        raise HTTPException(status_code=400, detail=f"Статус с ID {status_id} не найден")

    order.order_status_id = status_id
    db.commit()
    db.refresh(order)
    return order


@router.post("/{order_id}/recalculate", response_model=schemas.Order)
def recalculate_order_total(order_id: UUID, db: Session = Depends(get_db)):
    """Пересчитать сумму заказа по позициям"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Заказ с ID {order_id} не найден")

    total = sum(item.total_price for item in order.order_items)
    order.total_amount = total
    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=204)
def delete_order(order_id: UUID, db: Session = Depends(get_db)):
    """Удалить заказ"""
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Заказ с ID {order_id} не найден")
    crud.delete_order(db, order_id)