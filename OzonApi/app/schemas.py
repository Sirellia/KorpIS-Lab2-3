from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal
import re


# ==================== DICTIONARY SCHEMAS ====================

class OrderStatusBase(BaseModel):
    status_code: str
    status_name: str


class OrderStatusCreate(OrderStatusBase):
    pass


class OrderStatus(OrderStatusBase):
    status_id: int

    class Config:
        from_attributes = True


class ShipmentStatusBase(BaseModel):
    status_code: str
    status_name: str


class ShipmentStatusCreate(ShipmentStatusBase):
    pass


class ShipmentStatus(ShipmentStatusBase):
    status_id: int

    class Config:
        from_attributes = True


class VehicleStatusBase(BaseModel):
    status_code: str
    status_name: str


class VehicleStatusCreate(VehicleStatusBase):
    pass


class VehicleStatus(VehicleStatusBase):
    status_id: int

    class Config:
        from_attributes = True


class VehicleTypeBase(BaseModel):
    type_code: str
    type_name: str


class VehicleTypeCreate(VehicleTypeBase):
    pass


class VehicleType(VehicleTypeBase):
    type_id: int

    class Config:
        from_attributes = True


class PaymentMethodBase(BaseModel):
    method_code: str
    method_name: str


class PaymentMethodCreate(PaymentMethodBase):
    pass


class PaymentMethod(PaymentMethodBase):
    method_id: int

    class Config:
        from_attributes = True


class TicketStatusBase(BaseModel):
    status_code: str
    status_name: str


class TicketStatusCreate(TicketStatusBase):
    pass


class TicketStatus(TicketStatusBase):
    status_id: int

    class Config:
        from_attributes = True


class ProductCategoryBase(BaseModel):
    category_code: str
    category_name: str


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategory(ProductCategoryBase):
    category_id: int

    class Config:
        from_attributes = True


# ==================== CUSTOMER SCHEMAS ====================

class CustomerBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=200)
    email: EmailStr
    phone: str = Field(..., max_length=20)
    address: str = Field(..., min_length=5, max_length=500)

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        pattern = r'^\+?[0-9]{10,15}$'
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        if not re.match(pattern, cleaned):
            raise ValueError('Неверный формат телефона')
        return v


class CustomerCreate(CustomerBase):
    registration_date: Optional[date] = None


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=200)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, min_length=5, max_length=500)


class Customer(CustomerBase):
    customer_id: UUID
    registration_date: date
    created_datetime: datetime

    class Config:
        from_attributes = True


# ==================== PRODUCT SCHEMAS ====================

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    sku: str = Field(..., min_length=1, max_length=50)
    weight: Decimal = Field(..., gt=0)
    dimensions: Optional[str] = Field(None, max_length=50)
    category_id: int = Field(..., gt=0)
    price: Decimal = Field(..., ge=0)


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    sku: Optional[str] = Field(None, min_length=1, max_length=50)
    weight: Optional[Decimal] = Field(None, gt=0)
    dimensions: Optional[str] = Field(None, max_length=50)
    category_id: Optional[int] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, ge=0)


class Product(ProductBase):
    product_id: UUID
    created_datetime: datetime

    class Config:
        from_attributes = True


# ==================== WAREHOUSE SCHEMAS ====================

class WarehouseBase(BaseModel):
    warehouse_code: str = Field(..., min_length=1, max_length=20)
    warehouse_name: str = Field(..., min_length=1, max_length=200)
    address: str = Field(..., min_length=5, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    warehouse_code: Optional[str] = Field(None, min_length=1, max_length=20)
    warehouse_name: Optional[str] = Field(None, min_length=1, max_length=200)
    address: Optional[str] = Field(None, min_length=5, max_length=500)
    city: Optional[str] = Field(None, min_length=1, max_length=100)


class Warehouse(WarehouseBase):
    warehouse_id: UUID
    created_datetime: datetime

    class Config:
        from_attributes = True


# ==================== VEHICLE SCHEMAS ====================

class VehicleBase(BaseModel):
    license_plate: str = Field(..., min_length=1, max_length=20)
    vehicle_type_id: int = Field(..., gt=0)
    capacity: int = Field(..., gt=0)
    driver_name: str = Field(..., min_length=2, max_length=200)
    vehicle_status_id: int = Field(..., gt=0)


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    license_plate: Optional[str] = Field(None, min_length=1, max_length=20)
    vehicle_type_id: Optional[int] = Field(None, gt=0)
    capacity: Optional[int] = Field(None, gt=0)
    driver_name: Optional[str] = Field(None, min_length=2, max_length=200)
    vehicle_status_id: Optional[int] = Field(None, gt=0)


class Vehicle(VehicleBase):
    vehicle_id: UUID
    created_datetime: datetime

    class Config:
        from_attributes = True


# ==================== ORDER SCHEMAS ====================

class OrderBase(BaseModel):
    customer_id: UUID
    order_status_id: int = Field(..., gt=0)
    total_amount: Decimal = Field(..., ge=0)
    delivery_address: str = Field(..., min_length=5, max_length=500)
    payment_method_id: int = Field(..., gt=0)


class OrderCreate(OrderBase):
    order_date: Optional[date] = None


class OrderUpdate(BaseModel):
    customer_id: Optional[UUID] = None
    order_status_id: Optional[int] = Field(None, gt=0)
    total_amount: Optional[Decimal] = Field(None, ge=0)
    delivery_address: Optional[str] = Field(None, min_length=5, max_length=500)
    payment_method_id: Optional[int] = Field(None, gt=0)


class Order(OrderBase):
    order_id: UUID
    order_date: date
    created_datetime: datetime

    class Config:
        from_attributes = True


# ==================== ORDER ITEM SCHEMAS ====================

class OrderItemBase(BaseModel):
    order_id: UUID
    product_id: UUID
    quantity: int = Field(..., gt=0)
    price_per_unit: Decimal = Field(..., ge=0)


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0)
    price_per_unit: Optional[Decimal] = Field(None, ge=0)


class OrderItem(OrderItemBase):
    order_item_id: UUID
    total_price: Decimal
    created_datetime: datetime

    class Config:
        from_attributes = True


# ==================== SHIPMENT SCHEMAS ====================

class ShipmentBase(BaseModel):
    order_id: UUID
    shipment_status_id: int = Field(..., gt=0)
    vehicle_id: UUID
    warehouse_id: UUID
    estimated_arrival: date
    actual_arrival: Optional[date] = None


class ShipmentCreate(ShipmentBase):
    shipment_date: Optional[date] = None


class ShipmentUpdate(BaseModel):
    shipment_status_id: Optional[int] = Field(None, gt=0)
    vehicle_id: Optional[UUID] = None
    warehouse_id: Optional[UUID] = None
    estimated_arrival: Optional[date] = None
    actual_arrival: Optional[date] = None


class Shipment(ShipmentBase):
    shipment_id: UUID
    shipment_date: date
    created_datetime: datetime

    class Config:
        from_attributes = True


# ==================== SUPPORT TICKET SCHEMAS ====================

class SupportTicketBase(BaseModel):
    customer_id: UUID
    order_id: Optional[UUID] = None
    ticket_status_id: int = Field(..., gt=0)
    subject: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    resolution: Optional[str] = Field(None, max_length=2000)


class SupportTicketCreate(SupportTicketBase):
    pass


class SupportTicketUpdate(BaseModel):
    ticket_status_id: Optional[int] = Field(None, gt=0)
    subject: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    resolution: Optional[str] = Field(None, max_length=2000)
    closed_at: Optional[datetime] = None


class SupportTicket(SupportTicketBase):
    ticket_id: UUID
    created_at: datetime
    closed_at: Optional[datetime]
    created_datetime: datetime

    class Config:
        from_attributes = True


# ==================== RESPONSE SCHEMAS WITH RELATIONSHIPS ====================

class CustomerWithOrders(Customer):
    orders: List[Order] = []


class ProductWithCategory(Product):
    category: Optional[ProductCategory] = None


class OrderWithDetails(Order):
    customer: Optional[Customer] = None
    order_status: Optional[OrderStatus] = None
    payment_method: Optional[PaymentMethod] = None
    order_items: List[OrderItem] = []


class ShipmentWithDetails(Shipment):
    order: Optional[Order] = None
    shipment_status: Optional[ShipmentStatus] = None
    vehicle: Optional[Vehicle] = None
    warehouse: Optional[Warehouse] = None


class VehicleWithDetails(Vehicle):
    vehicle_type: Optional[VehicleType] = None
    vehicle_status: Optional[VehicleStatus] = None


class SupportTicketWithDetails(SupportTicket):
    customer: Optional[Customer] = None
    order: Optional[Order] = None
    ticket_status: Optional[TicketStatus] = None