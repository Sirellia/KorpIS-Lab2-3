from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from decimal import Decimal

from app.database import get_db
from app import crud, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.OrderItem])
def get_order_items(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        order_id: UUID = Query(None, description="Фильтр по заказу"),
        db: Session = Depends(get_db)
):
    """Получить список позиций заказов"""
    if order_id:
        return crud.get_order_items_by_order(db, order_id)
    return crud.get_order_items(db, skip=skip, limit=limit)


@router.get("/{order_item_id}", response_model=schemas.OrderItem)
def get_order_item(order_item_id: UUID, db: Session = Depends(get_db)):
    """Получить позицию заказа по ID"""
    item = crud.get_order_item(db, order_item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Позиция заказа с ID {order_item_id} не найдена")
    return item


@router.post("/", response_model=schemas.OrderItem, status_code=201)
def create_order_item(order_item: schemas.OrderItemCreate, db: Session = Depends(get_db)):
    """Добавить позицию в заказ"""
    # Проверка существования заказа
    order = crud.get_order(db, order_item.order_id)
    if not order:
        raise HTTPException(status_code=400, detail=f"Заказ с ID {order_item.order_id} не найден")

    # Проверка существования товара
    product = crud.get_product(db, order_item.product_id)
    if not product:
        raise HTTPException(status_code=400, detail=f"Товар с ID {order_item.product_id} не найден")

    item = crud.create_order_item(db, order_item)

    # Обновляем сумму заказа
    _update_order_total(db, order)

    return item


@router.put("/{order_item_id}", response_model=schemas.OrderItem)
def update_order_item(
        order_item_id: UUID,
        order_item_update: schemas.OrderItemUpdate,
        db: Session = Depends(get_db)
):
    """Обновить позицию заказа"""
    item = crud.update_order_item(db, order_item_id, order_item_update)
    if not item:
        raise HTTPException(status_code=404, detail=f"Позиция заказа с ID {order_item_id} не найдена")

    # Обновляем сумму заказа
    _update_order_total(db, item.order)

    return item


@router.delete("/{order_item_id}", status_code=204)
def delete_order_item(order_item_id: UUID, db: Session = Depends(get_db)):
    """Удалить позицию заказа"""
    item = crud.get_order_item(db, order_item_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Позиция заказа с ID {order_item_id} не найдена")

    order = item.order
    crud.delete_order_item(db, order_item_id)

    # Обновляем сумму заказа
    _update_order_total(db, order)


def _update_order_total(db: Session, order):
    """Вспомогательная функция для обновления суммы заказа"""
    db.refresh(order)
    total = sum(item.total_price for item in order.order_items)
    order.total_amount = total
    db.commit()