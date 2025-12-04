from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app import crud, schemas, models

router = APIRouter()


@router.get("/", response_model=List[schemas.Warehouse])
def get_warehouses(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        city: str = Query(None, description="Фильтр по городу"),
        db: Session = Depends(get_db)
):
    """Получить список складов"""
    query = db.query(models.Warehouse)
    if city:
        query = query.filter(models.Warehouse.city.ilike(f"%{city}%"))
    return query.offset(skip).limit(limit).all()


@router.get("/{warehouse_id}", response_model=schemas.Warehouse)
def get_warehouse(warehouse_id: UUID, db: Session = Depends(get_db)):
    """Получить склад по ID"""
    warehouse = crud.get_warehouse(db, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {warehouse_id} не найден")
    return warehouse


@router.post("/", response_model=schemas.Warehouse, status_code=201)
def create_warehouse(warehouse: schemas.WarehouseCreate, db: Session = Depends(get_db)):
    """Создать новый склад"""
    existing = db.query(models.Warehouse).filter(
        models.Warehouse.warehouse_code == warehouse.warehouse_code
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Склад с кодом {warehouse.warehouse_code} уже существует")

    return crud.create_warehouse(db, warehouse)


@router.put("/{warehouse_id}", response_model=schemas.Warehouse)
def update_warehouse(
        warehouse_id: UUID,
        warehouse_update: schemas.WarehouseUpdate,
        db: Session = Depends(get_db)
):
    """Обновить склад"""
    warehouse = crud.update_warehouse(db, warehouse_id, warehouse_update)
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {warehouse_id} не найден")
    return warehouse


@router.delete("/{warehouse_id}", status_code=204)
def delete_warehouse(warehouse_id: UUID, db: Session = Depends(get_db)):
    """Удалить склад"""
    warehouse = crud.get_warehouse(db, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail=f"Склад с ID {warehouse_id} не найден")

    if warehouse.shipments:
        raise HTTPException(status_code=400, detail="Невозможно удалить склад с существующими отправлениями")

    crud.delete_warehouse(db, warehouse_id)