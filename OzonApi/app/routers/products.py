from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app import crud, schemas, models

router = APIRouter()


@router.get("/", response_model=List[schemas.Product])
def get_products(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        category_id: int = Query(None, description="Фильтр по категории"),
        db: Session = Depends(get_db)
):
    """Получить список всех товаров"""
    if category_id:
        return db.query(models.Product).filter(
            models.Product.category_id == category_id
        ).offset(skip).limit(limit).all()
    return crud.get_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """Получить товар по ID"""
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Товар с ID {product_id} не найден")
    return product


@router.post("/", response_model=schemas.Product, status_code=201)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Создать новый товар"""
    # Проверка уникальности SKU
    existing = crud.get_product_by_sku(db, product.sku)
    if existing:
        raise HTTPException(status_code=400, detail=f"Товар с SKU {product.sku} уже существует")

    # Проверка существования категории
    category = db.query(models.Dictionary_ProductCategory).filter(
        models.Dictionary_ProductCategory.category_id == product.category_id
    ).first()
    if not category:
        raise HTTPException(status_code=400, detail=f"Категория с ID {product.category_id} не найдена")

    return crud.create_product(db, product)


@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
        product_id: UUID,
        product_update: schemas.ProductUpdate,
        db: Session = Depends(get_db)
):
    """Обновить товар"""
    product = crud.update_product(db, product_id, product_update)
    if not product:
        raise HTTPException(status_code=404, detail=f"Товар с ID {product_id} не найден")
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: UUID, db: Session = Depends(get_db)):
    """Удалить товар"""
    product = crud.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Товар с ID {product_id} не найден")

    # Проверка на наличие в заказах
    if product.order_items:
        raise HTTPException(status_code=400, detail="Невозможно удалить товар, который есть в заказах")

    crud.delete_product(db, product_id)