from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app import crud, schemas, models

router = APIRouter()


@router.get("/", response_model=List[schemas.Vehicle])
def get_vehicles(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        status_id: int = Query(None, description="Фильтр по статусу"),
        type_id: int = Query(None, description="Фильтр по типу"),
        db: Session = Depends(get_db)
):
    """Получить список транспортных средств"""
    query = db.query(models.Delivery_Vehicle)
    if status_id:
        query = query.filter(models.Delivery_Vehicle.vehicle_status_id == status_id)
    if type_id:
        query = query.filter(models.Delivery_Vehicle.vehicle_type_id == type_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{vehicle_id}", response_model=schemas.Vehicle)
def get_vehicle(vehicle_id: UUID, db: Session = Depends(get_db)):
    """Получить ТС по ID"""
    vehicle = crud.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"ТС с ID {vehicle_id} не найдено")
    return vehicle


@router.post("/", response_model=schemas.Vehicle, status_code=201)
def create_vehicle(vehicle: schemas.VehicleCreate, db: Session = Depends(get_db)):
    """Создать новое ТС"""
    # Проверка уникальности госномера
    existing = db.query(models.Delivery_Vehicle).filter(
        models.Delivery_Vehicle.license_plate == vehicle.license_plate
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"ТС с номером {vehicle.license_plate} уже существует")

    # Проверка типа ТС
    vehicle_type = db.query(models.Dictionary_VehicleType).filter(
        models.Dictionary_VehicleType.type_id == vehicle.vehicle_type_id
    ).first()
    if not vehicle_type:
        raise HTTPException(status_code=400, detail=f"Тип ТС с ID {vehicle.vehicle_type_id} не найден")

    # Проверка статуса ТС
    vehicle_status = db.query(models.Dictionary_VehicleStatus).filter(
        models.Dictionary_VehicleStatus.status_id == vehicle.vehicle_status_id
    ).first()
    if not vehicle_status:
        raise HTTPException(status_code=400, detail=f"Статус ТС с ID {vehicle.vehicle_status_id} не найден")

    return crud.create_vehicle(db, vehicle)


@router.put("/{vehicle_id}", response_model=schemas.Vehicle)
def update_vehicle(
        vehicle_id: UUID,
        vehicle_update: schemas.VehicleUpdate,
        db: Session = Depends(get_db)
):
    """Обновить ТС"""
    vehicle = crud.update_vehicle(db, vehicle_id, vehicle_update)
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"ТС с ID {vehicle_id} не найдено")
    return vehicle


@router.put("/{vehicle_id}/status/{status_id}", response_model=schemas.Vehicle)
def update_vehicle_status(vehicle_id: UUID, status_id: int, db: Session = Depends(get_db)):
    """Обновить статус ТС"""
    vehicle = crud.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"ТС с ID {vehicle_id} не найдено")

    status = db.query(models.Dictionary_VehicleStatus).filter(
        models.Dictionary_VehicleStatus.status_id == status_id
    ).first()
    if not status:
        raise HTTPException(status_code=400, detail=f"Статус с ID {status_id} не найден")

    vehicle.vehicle_status_id = status_id
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: UUID, db: Session = Depends(get_db)):
    """Удалить ТС"""
    vehicle = crud.get_vehicle(db, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail=f"ТС с ID {vehicle_id} не найдено")

    if vehicle.shipments:
        raise HTTPException(status_code=400, detail="Невозможно удалить ТС с существующими отправлениями")

    crud.delete_vehicle(db, vehicle_id)