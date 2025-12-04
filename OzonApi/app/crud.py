from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging
from decimal import Decimal
from app import models, schemas

logger = logging.getLogger(__name__)


# ==================== CUSTOMER CRUD ====================

def get_customer(db: Session, customer_id: UUID) -> Optional[models.Customer]:
    logger.info(f"Fetching customer with ID: {customer_id}")
    return db.query(models.Customer).filter(models.Customer.customer_id == customer_id).first()


def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Customer]:
    logger.info(f"Fetching customers with skip: {skip}, limit: {limit}")
    return db.query(models.Customer).offset(skip).limit(limit).all()


def get_customer_by_email(db: Session, email: str) -> Optional[models.Customer]:
    return db.query(models.Customer).filter(models.Customer.email == email).first()


def create_customer(db: Session, customer: schemas.CustomerCreate) -> models.Customer:
    logger.info(f"Creating customer: {customer.full_name}")
    db_customer = models.Customer(**customer.model_dump(exclude_unset=True))
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    logger.info(f"Customer created with ID: {db_customer.customer_id}")
    return db_customer


def update_customer(db: Session, customer_id: UUID, customer_update: schemas.CustomerUpdate) -> Optional[models.Customer]:
    logger.info(f"Updating customer with ID: {customer_id}")
    db_customer = get_customer(db, customer_id)
    if db_customer:
        update_data = customer_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)
        db.commit()
        db.refresh(db_customer)
        logger.info(f"Customer with ID {customer_id} updated successfully")
    return db_customer


def delete_customer(db: Session, customer_id: UUID) -> bool:
    logger.info(f"Deleting customer with ID: {customer_id}")
    db_customer = get_customer(db, customer_id)
    if db_customer:
        db.delete(db_customer)
        db.commit()
        logger.info(f"Customer with ID {customer_id} deleted successfully")
        return True
    return False


# ==================== PRODUCT CRUD ====================

def get_product(db: Session, product_id: UUID) -> Optional[models.Product]:
    logger.info(f"Fetching product with ID: {product_id}")
    return db.query(models.Product).filter(models.Product.product_id == product_id).first()


def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[models.Product]:
    logger.info(f"Fetching products with skip: {skip}, limit: {limit}")
    return db.query(models.Product).offset(skip).limit(limit).all()


def get_product_by_sku(db: Session, sku: str) -> Optional[models.Product]:
    return db.query(models.Product).filter(models.Product.sku == sku).first()


def create_product(db: Session, product: schemas.ProductCreate) -> models.Product:
    logger.info(f"Creating product: {product.name}")
    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    logger.info(f"Product created with ID: {db_product.product_id}")
    return db_product


def update_product(db: Session, product_id: UUID, product_update: schemas.ProductUpdate) -> Optional[models.Product]:
    logger.info(f"Updating product with ID: {product_id}")
    db_product = get_product(db, product_id)
    if db_product:
        update_data = product_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_product, field, value)
        db.commit()
        db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: UUID) -> bool:
    logger.info(f"Deleting product with ID: {product_id}")
    db_product = get_product(db, product_id)
    if db_product:
        db.delete(db_product)
        db.commit()
        return True
    return False


# ==================== WAREHOUSE CRUD ====================

def get_warehouse(db: Session, warehouse_id: UUID) -> Optional[models.Warehouse]:
    return db.query(models.Warehouse).filter(models.Warehouse.warehouse_id == warehouse_id).first()


def get_warehouses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Warehouse]:
    return db.query(models.Warehouse).offset(skip).limit(limit).all()


def create_warehouse(db: Session, warehouse: schemas.WarehouseCreate) -> models.Warehouse:
    db_warehouse = models.Warehouse(**warehouse.model_dump())
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def update_warehouse(db: Session, warehouse_id: UUID, warehouse_update: schemas.WarehouseUpdate) -> Optional[models.Warehouse]:
    db_warehouse = get_warehouse(db, warehouse_id)
    if db_warehouse:
        update_data = warehouse_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_warehouse, field, value)
        db.commit()
        db.refresh(db_warehouse)
    return db_warehouse


def delete_warehouse(db: Session, warehouse_id: UUID) -> bool:
    db_warehouse = get_warehouse(db, warehouse_id)
    if db_warehouse:
        db.delete(db_warehouse)
        db.commit()
        return True
    return False


# ==================== VEHICLE CRUD ====================

def get_vehicle(db: Session, vehicle_id: UUID) -> Optional[models.Delivery_Vehicle]:
    return db.query(models.Delivery_Vehicle).filter(models.Delivery_Vehicle.vehicle_id == vehicle_id).first()


def get_vehicles(db: Session, skip: int = 0, limit: int = 100) -> List[models.Delivery_Vehicle]:
    return db.query(models.Delivery_Vehicle).offset(skip).limit(limit).all()


def create_vehicle(db: Session, vehicle: schemas.VehicleCreate) -> models.Delivery_Vehicle:
    db_vehicle = models.Delivery_Vehicle(**vehicle.model_dump())
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle


def update_vehicle(db: Session, vehicle_id: UUID, vehicle_update: schemas.VehicleUpdate) -> Optional[models.Delivery_Vehicle]:
    db_vehicle = get_vehicle(db, vehicle_id)
    if db_vehicle:
        update_data = vehicle_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_vehicle, field, value)
        db.commit()
        db.refresh(db_vehicle)
    return db_vehicle


def delete_vehicle(db: Session, vehicle_id: UUID) -> bool:
    db_vehicle = get_vehicle(db, vehicle_id)
    if db_vehicle:
        db.delete(db_vehicle)
        db.commit()
        return True
    return False


# ==================== ORDER CRUD ====================

def get_order(db: Session, order_id: UUID) -> Optional[models.Order]:
    return db.query(models.Order).filter(models.Order.order_id == order_id).first()


def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[models.Order]:
    return db.query(models.Order).offset(skip).limit(limit).all()


def get_orders_by_customer(db: Session, customer_id: UUID) -> List[models.Order]:
    return db.query(models.Order).filter(models.Order.customer_id == customer_id).all()


def create_order(db: Session, order: schemas.OrderCreate) -> models.Order:
    logger.info(f"Creating order for customer: {order.customer_id}")
    db_order = models.Order(**order.model_dump(exclude_unset=True))
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    logger.info(f"Order created with ID: {db_order.order_id}")
    return db_order


def update_order(db: Session, order_id: UUID, order_update: schemas.OrderUpdate) -> Optional[models.Order]:
    db_order = get_order(db, order_id)
    if db_order:
        update_data = order_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_order, field, value)
        db.commit()
        db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: UUID) -> bool:
    db_order = get_order(db, order_id)
    if db_order:
        db.delete(db_order)
        db.commit()
        return True
    return False


# ==================== ORDER ITEM CRUD ====================

def get_order_item(db: Session, order_item_id: UUID) -> Optional[models.Order_Item]:
    return db.query(models.Order_Item).filter(models.Order_Item.order_item_id == order_item_id).first()


def get_order_items(db: Session, skip: int = 0, limit: int = 100) -> List[models.Order_Item]:
    return db.query(models.Order_Item).offset(skip).limit(limit).all()


def get_order_items_by_order(db: Session, order_id: UUID) -> List[models.Order_Item]:
    return db.query(models.Order_Item).filter(models.Order_Item.order_id == order_id).all()


def create_order_item(db: Session, order_item: schemas.OrderItemCreate) -> models.Order_Item:
    # Calculate total_price
    total_price = Decimal(str(order_item.quantity)) * order_item.price_per_unit
    db_order_item = models.Order_Item(
        **order_item.model_dump(),
        total_price=total_price
    )
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    return db_order_item


def update_order_item(db: Session, order_item_id: UUID, order_item_update: schemas.OrderItemUpdate) -> Optional[models.Order_Item]:
    db_order_item = get_order_item(db, order_item_id)
    if db_order_item:
        update_data = order_item_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_order_item, field, value)
        # Recalculate total_price
        db_order_item.total_price = Decimal(str(db_order_item.quantity)) * db_order_item.price_per_unit
        db.commit()
        db.refresh(db_order_item)
    return db_order_item


def delete_order_item(db: Session, order_item_id: UUID) -> bool:
    db_order_item = get_order_item(db, order_item_id)
    if db_order_item:
        db.delete(db_order_item)
        db.commit()
        return True
    return False


# ==================== SHIPMENT CRUD ====================

def get_shipment(db: Session, shipment_id: UUID) -> Optional[models.Shipment]:
    return db.query(models.Shipment).filter(models.Shipment.shipment_id == shipment_id).first()


def get_shipments(db: Session, skip: int = 0, limit: int = 100) -> List[models.Shipment]:
    return db.query(models.Shipment).offset(skip).limit(limit).all()


def get_shipments_by_order(db: Session, order_id: UUID) -> List[models.Shipment]:
    return db.query(models.Shipment).filter(models.Shipment.order_id == order_id).all()


def create_shipment(db: Session, shipment: schemas.ShipmentCreate) -> models.Shipment:
    db_shipment = models.Shipment(**shipment.model_dump(exclude_unset=True))
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)
    return db_shipment


def update_shipment(db: Session, shipment_id: UUID, shipment_update: schemas.ShipmentUpdate) -> Optional[models.Shipment]:
    db_shipment = get_shipment(db, shipment_id)
    if db_shipment:
        update_data = shipment_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_shipment, field, value)
        db.commit()
        db.refresh(db_shipment)
    return db_shipment


def delete_shipment(db: Session, shipment_id: UUID) -> bool:
    db_shipment = get_shipment(db, shipment_id)
    if db_shipment:
        db.delete(db_shipment)
        db.commit()
        return True
    return False


# ==================== SUPPORT TICKET CRUD ====================

def get_support_ticket(db: Session, ticket_id: UUID) -> Optional[models.Support_Ticket]:
    return db.query(models.Support_Ticket).filter(models.Support_Ticket.ticket_id == ticket_id).first()


def get_support_tickets(db: Session, skip: int = 0, limit: int = 100) -> List[models.Support_Ticket]:
    return db.query(models.Support_Ticket).offset(skip).limit(limit).all()


def get_support_tickets_by_customer(db: Session, customer_id: UUID) -> List[models.Support_Ticket]:
    return db.query(models.Support_Ticket).filter(models.Support_Ticket.customer_id == customer_id).all()


def create_support_ticket(db: Session, ticket: schemas.SupportTicketCreate) -> models.Support_Ticket:
    db_ticket = models.Support_Ticket(**ticket.model_dump(exclude_unset=True))
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


def update_support_ticket(db: Session, ticket_id: UUID, ticket_update: schemas.SupportTicketUpdate) -> Optional[models.Support_Ticket]:
    db_ticket = get_support_ticket(db, ticket_id)
    if db_ticket:
        update_data = ticket_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_ticket, field, value)
        db.commit()
        db.refresh(db_ticket)
    return db_ticket


def delete_support_ticket(db: Session, ticket_id: UUID) -> bool:
    db_ticket = get_support_ticket(db, ticket_id)
    if db_ticket:
        db.delete(db_ticket)
        db.commit()
        return True
    return False


# ==================== DICTIONARY CRUD ====================

def get_order_statuses(db: Session) -> List[models.Dictionary_OrderStatus]:
    return db.query(models.Dictionary_OrderStatus).all()


def get_shipment_statuses(db: Session) -> List[models.Dictionary_ShipmentStatus]:
    return db.query(models.Dictionary_ShipmentStatus).all()


def get_vehicle_statuses(db: Session) -> List[models.Dictionary_VehicleStatus]:
    return db.query(models.Dictionary_VehicleStatus).all()


def get_vehicle_types(db: Session) -> List[models.Dictionary_VehicleType]:
    return db.query(models.Dictionary_VehicleType).all()


def get_payment_methods(db: Session) -> List[models.Dictionary_PaymentMethod]:
    return db.query(models.Dictionary_PaymentMethod).all()


def get_ticket_statuses(db: Session) -> List[models.Dictionary_TicketStatus]:
    return db.query(models.Dictionary_TicketStatus).all()


def get_product_categories(db: Session) -> List[models.Dictionary_ProductCategory]:
    return db.query(models.Dictionary_ProductCategory).all()