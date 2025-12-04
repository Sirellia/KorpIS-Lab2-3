from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime

from app.database import get_db
from app import crud, schemas, models

router = APIRouter()


@router.get("/", response_model=List[schemas.SupportTicket])
def get_support_tickets(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
        customer_id: UUID = Query(None, description="Фильтр по клиенту"),
        status_id: int = Query(None, description="Фильтр по статусу"),
        db: Session = Depends(get_db)
):
    """Получить список обращений в поддержку"""
    query = db.query(models.Support_Ticket)
    if customer_id:
        query = query.filter(models.Support_Ticket.customer_id == customer_id)
    if status_id:
        query = query.filter(models.Support_Ticket.ticket_status_id == status_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{ticket_id}", response_model=schemas.SupportTicket)
def get_support_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    """Получить обращение по ID"""
    ticket = crud.get_support_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Обращение с ID {ticket_id} не найдено")
    return ticket


@router.post("/", response_model=schemas.SupportTicket, status_code=201)
def create_support_ticket(ticket: schemas.SupportTicketCreate, db: Session = Depends(get_db)):
    """Создать новое обращение"""
    # Проверка клиента
    customer = crud.get_customer(db, ticket.customer_id)
    if not customer:
        raise HTTPException(status_code=400, detail=f"Клиент с ID {ticket.customer_id} не найден")

    # Проверка заказа (если указан)
    if ticket.order_id:
        order = crud.get_order(db, ticket.order_id)
        if not order:
            raise HTTPException(status_code=400, detail=f"Заказ с ID {ticket.order_id} не найден")

    # Проверка статуса
    status = db.query(models.Dictionary_TicketStatus).filter(
        models.Dictionary_TicketStatus.status_id == ticket.ticket_status_id
    ).first()
    if not status:
        raise HTTPException(status_code=400, detail=f"Статус обращения с ID {ticket.ticket_status_id} не найден")

    return crud.create_support_ticket(db, ticket)


@router.put("/{ticket_id}", response_model=schemas.SupportTicket)
def update_support_ticket(
        ticket_id: UUID,
        ticket_update: schemas.SupportTicketUpdate,
        db: Session = Depends(get_db)
):
    """Обновить обращение"""
    ticket = crud.update_support_ticket(db, ticket_id, ticket_update)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Обращение с ID {ticket_id} не найдено")
    return ticket


@router.put("/{ticket_id}/resolve", response_model=schemas.SupportTicket)
def resolve_ticket(
        ticket_id: UUID,
        resolution: str,
        db: Session = Depends(get_db)
):
    """Закрыть обращение с решением"""
    ticket = crud.get_support_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Обращение с ID {ticket_id} не найдено")

    # Находим статус "Закрыт"
    closed_status = db.query(models.Dictionary_TicketStatus).filter(
        models.Dictionary_TicketStatus.status_code == 'CLOSED'
    ).first()

    if closed_status:
        ticket.ticket_status_id = closed_status.status_id
    ticket.resolution = resolution
    ticket.closed_at = datetime.utcnow()

    db.commit()
    db.refresh(ticket)
    return ticket


@router.delete("/{ticket_id}", status_code=204)
def delete_support_ticket(ticket_id: UUID, db: Session = Depends(get_db)):
    """Удалить обращение"""
    ticket = crud.get_support_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Обращение с ID {ticket_id} не найдено")
    crud.delete_support_ticket(db, ticket_id)