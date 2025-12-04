from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import date

from app.database import get_db
from app import crud, schemas, models

router = APIRouter()


@router.get("/", response_model=List[schemas.Shipment])
def get_shipments(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        status_id: int = Query(None, description="Фильтр по статусу"),
        vehicle_id: UUID = Query(None, description="Фильтр по ТС"),
        db: Session = Depends(get_db)
):
    """Получить список отправлений"""
    query = db.query(models.Shipment)
    if status_id:
        query = query.filter(models.Shipment.shipment_status_id == status_id)
    if vehicle_id:
        query = query.filter(models.Shipment.vehicle_id == vehicle_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{shipment_id}", response_model=schemas.Shipment)
def get_shipment(shipment_id: UUID, db: Session = Depends(get_db)):
    """Получить отправление по ID"""
    shipment = crud.get_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail=f"Отправление с ID {shipment_id} не найдено")
    return shipment


@router.post("/", response_model=schemas.Shipment, status_code=201)
def create_shipment(shipment: schemas.ShipmentCreate, db: Session = Depends(get_db)):
    """Создать новое отправление"""
    # Проверка заказа
    order = crud.get_order(db, shipment.order_id)
    if not order:
        raise HTTPException(status_code=400, detail=f"Заказ с ID {shipment.order_id} не найден")

    # Проверка статуса
    status = db.query(models.Dictionary_ShipmentStatus).filter(
        models.Dictionary_ShipmentStatus.status_id == shipment.shipment_status_id
    ).first()
    if not status:
        raise HTTPException(status_code=400, detail=f"Статус отправления с ID {shipment.shipment_status_id} не найден")

    # Проверка ТС
    vehicle = crud.get_vehicle(db, shipment.vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=400, detail=f"ТС с ID {shipment.vehicle_id} не найдено")

    # Проверка склада
    warehouse = crud.get_warehouse(db, shipment.warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=400, detail=f"Склад с ID {shipment.warehouse_id} не найден")

    return crud.create_shipment(db, shipment)


@router.put("/{shipment_id}", response_model=schemas.Shipment)
def update_shipment(
        shipment_id: UUID,
        shipment_update: schemas.ShipmentUpdate,
        db: Session = Depends(get_db)
):
    """Обновить отправление"""
    shipment = crud.update_shipment(db, shipment_id, shipment_update)
    if not shipment:
        raise HTTPException(status_code=404, detail=f"Отправление с ID {shipment_id} не найдено")
    return shipment


@router.put("/{shipment_id}/deliver", response_model=schemas.Shipment)
def mark_as_delivered(shipment_id: UUID, db: Session = Depends(get_db)):
    """Отметить отправление как доставленное"""
    shipment = crud.get_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail=f"Отправление с ID {shipment_id} не найдено")

    # Находим статус "Доставлен"
    delivered_status = db.query(models.Dictionary_ShipmentStatus).filter(
        models.Dictionary_ShipmentStatus.status_code == 'DELIVERED'
    ).first()

    if delivered_status:
        shipment.shipment_status_id = delivered_status.status_id
    shipment.actual_arrival = date.today()

    db.commit()
    db.refresh(shipment)
    return shipment


@router.delete("/{shipment_id}", status_code=204)
def delete_shipment(shipment_id: UUID, db: Session = Depends(get_db)):
    """Удалить отправление"""
    shipment = crud.get_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail=f"Отправление с ID {shipment_id} не найдено")
    crud.delete_shipment(db, shipment_id)