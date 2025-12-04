from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import crud, schemas

router = APIRouter()


@router.get("/order-statuses", response_model=List[schemas.OrderStatus])
def get_order_statuses(db: Session = Depends(get_db)):
    """Получить список статусов заказов"""
    return crud.get_order_statuses(db)


@router.get("/shipment-statuses", response_model=List[schemas.ShipmentStatus])
def get_shipment_statuses(db: Session = Depends(get_db)):
    """Получить список статусов отправлений"""
    return crud.get_shipment_statuses(db)


@router.get("/vehicle-statuses", response_model=List[schemas.VehicleStatus])
def get_vehicle_statuses(db: Session = Depends(get_db)):
    """Получить список статусов ТС"""
    return crud.get_vehicle_statuses(db)


@router.get("/vehicle-types", response_model=List[schemas.VehicleType])
def get_vehicle_types(db: Session = Depends(get_db)):
    """Получить список типов ТС"""
    return crud.get_vehicle_types(db)


@router.get("/payment-methods", response_model=List[schemas.PaymentMethod])
def get_payment_methods(db: Session = Depends(get_db)):
    """Получить список способов оплаты"""
    return crud.get_payment_methods(db)


@router.get("/ticket-statuses", response_model=List[schemas.TicketStatus])
def get_ticket_statuses(db: Session = Depends(get_db)):
    """Получить список статусов обращений"""
    return crud.get_ticket_statuses(db)


@router.get("/product-categories", response_model=List[schemas.ProductCategory])
def get_product_categories(db: Session = Depends(get_db)):
    """Получить список категорий товаров"""
    return crud.get_product_categories(db)