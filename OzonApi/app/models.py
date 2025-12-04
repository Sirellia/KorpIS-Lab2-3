from sqlalchemy import Column, String, Integer, DateTime, Date, Numeric, SmallInteger, ForeignKey, CheckConstraint
from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# ==================== DICTIONARIES ====================

class Dictionary_OrderStatus(Base):
    __tablename__ = 'Dictionary_OrderStatus'

    status_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    status_code = Column(String(30), nullable=False, unique=True)
    status_name = Column(String(100), nullable=False)

    orders = relationship("Order", back_populates="order_status")


class Dictionary_ShipmentStatus(Base):
    __tablename__ = 'Dictionary_ShipmentStatus'

    status_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    status_code = Column(String(30), nullable=False, unique=True)
    status_name = Column(String(100), nullable=False)

    shipments = relationship("Shipment", back_populates="shipment_status")


class Dictionary_VehicleStatus(Base):
    __tablename__ = 'Dictionary_VehicleStatus'

    status_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    status_code = Column(String(30), nullable=False, unique=True)
    status_name = Column(String(100), nullable=False)

    vehicles = relationship("Delivery_Vehicle", back_populates="vehicle_status")


class Dictionary_VehicleType(Base):
    __tablename__ = 'Dictionary_VehicleType'

    type_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    type_code = Column(String(30), nullable=False, unique=True)
    type_name = Column(String(100), nullable=False)

    vehicles = relationship("Delivery_Vehicle", back_populates="vehicle_type")


class Dictionary_PaymentMethod(Base):
    __tablename__ = 'Dictionary_PaymentMethod'

    method_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    method_code = Column(String(30), nullable=False, unique=True)
    method_name = Column(String(100), nullable=False)

    orders = relationship("Order", back_populates="payment_method")


class Dictionary_TicketStatus(Base):
    __tablename__ = 'Dictionary_TicketStatus'

    status_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    status_code = Column(String(30), nullable=False, unique=True)
    status_name = Column(String(100), nullable=False)

    tickets = relationship("Support_Ticket", back_populates="ticket_status")


class Dictionary_ProductCategory(Base):
    __tablename__ = 'Dictionary_ProductCategory'

    category_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    category_code = Column(String(30), nullable=False, unique=True)
    category_name = Column(String(100), nullable=False)

    products = relationship("Product", back_populates="category")


# ==================== MAIN ENTITIES ====================

class Customer(Base):
    __tablename__ = 'Customer'

    customer_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=func.newid())
    full_name = Column(String(200), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    phone = Column(String(20), nullable=False, unique=True)
    address = Column(String(500), nullable=False)
    registration_date = Column(Date, nullable=False, server_default=func.cast(func.getutcdate(), Date))
    created_datetime = Column(DateTime, nullable=False, server_default=func.getutcdate())

    orders = relationship("Order", back_populates="customer")
    support_tickets = relationship("Support_Ticket", back_populates="customer")


class Product(Base):
    __tablename__ = 'Product'

    product_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=func.newid())
    name = Column(String(200), nullable=False)
    description = Column(String(1000))
    sku = Column(String(50), nullable=False, unique=True)
    weight = Column(Numeric(10, 3), nullable=False)
    dimensions = Column(String(50))
    category_id = Column(SmallInteger, ForeignKey('Dictionary_ProductCategory.category_id'), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    created_datetime = Column(DateTime, nullable=False, server_default=func.getutcdate())

    category = relationship("Dictionary_ProductCategory", back_populates="products")
    order_items = relationship("Order_Item", back_populates="product")

    __table_args__ = (
        CheckConstraint('weight > 0', name='CHK_Product_Weight'),
        CheckConstraint('price >= 0', name='CHK_Product_Price'),
    )


class Warehouse(Base):
    __tablename__ = 'Warehouse'

    warehouse_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=func.newid())
    warehouse_code = Column(String(20), nullable=False, unique=True)
    warehouse_name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=False)
    city = Column(String(100), nullable=False)
    created_datetime = Column(DateTime, nullable=False, server_default=func.getutcdate())

    shipments = relationship("Shipment", back_populates="warehouse")


class Delivery_Vehicle(Base):
    __tablename__ = 'Delivery_Vehicle'

    vehicle_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=func.newid())
    license_plate = Column(String(20), nullable=False, unique=True)
    vehicle_type_id = Column(SmallInteger, ForeignKey('Dictionary_VehicleType.type_id'), nullable=False)
    capacity = Column(Integer, nullable=False)
    driver_name = Column(String(200), nullable=False)
    vehicle_status_id = Column(SmallInteger, ForeignKey('Dictionary_VehicleStatus.status_id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, server_default=func.getutcdate())

    vehicle_type = relationship("Dictionary_VehicleType", back_populates="vehicles")
    vehicle_status = relationship("Dictionary_VehicleStatus", back_populates="vehicles")
    shipments = relationship("Shipment", back_populates="vehicle")

    __table_args__ = (
        CheckConstraint('capacity > 0', name='CHK_Vehicle_Capacity'),
    )


class Order(Base):
    __tablename__ = 'Order'

    order_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=func.newid())
    customer_id = Column(UNIQUEIDENTIFIER, ForeignKey('Customer.customer_id'), nullable=False)
    order_date = Column(Date, nullable=False, server_default=func.cast(func.getutcdate(), Date))
    order_status_id = Column(SmallInteger, ForeignKey('Dictionary_OrderStatus.status_id'), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    delivery_address = Column(String(500), nullable=False)
    payment_method_id = Column(SmallInteger, ForeignKey('Dictionary_PaymentMethod.method_id'), nullable=False)
    created_datetime = Column(DateTime, nullable=False, server_default=func.getutcdate())

    customer = relationship("Customer", back_populates="orders")
    order_status = relationship("Dictionary_OrderStatus", back_populates="orders")
    payment_method = relationship("Dictionary_PaymentMethod", back_populates="orders")
    order_items = relationship("Order_Item", back_populates="order", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="order")
    support_tickets = relationship("Support_Ticket", back_populates="order")

    __table_args__ = (
        CheckConstraint('total_amount >= 0', name='CHK_Order_TotalAmount'),
    )


class Order_Item(Base):
    __tablename__ = 'Order_Item'

    order_item_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=func.newid())
    order_id = Column(UNIQUEIDENTIFIER, ForeignKey('Order.order_id'), nullable=False)
    product_id = Column(UNIQUEIDENTIFIER, ForeignKey('Product.product_id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    price_per_unit = Column(Numeric(10, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)
    created_datetime = Column(DateTime, nullable=False, server_default=func.getutcdate())

    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

    __table_args__ = (
        CheckConstraint('quantity > 0', name='CHK_OrderItem_Quantity'),
        CheckConstraint('price_per_unit >= 0', name='CHK_OrderItem_Price'),
        CheckConstraint('total_price >= 0', name='CHK_OrderItem_TotalPrice'),
    )


class Shipment(Base):
    __tablename__ = 'Shipment'

    shipment_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=func.newid())
    order_id = Column(UNIQUEIDENTIFIER, ForeignKey('Order.order_id'), nullable=False)
    shipment_date = Column(Date, nullable=False, server_default=func.cast(func.getutcdate(), Date))
    shipment_status_id = Column(SmallInteger, ForeignKey('Dictionary_ShipmentStatus.status_id'), nullable=False)
    vehicle_id = Column(UNIQUEIDENTIFIER, ForeignKey('Delivery_Vehicle.vehicle_id'), nullable=False)
    warehouse_id = Column(UNIQUEIDENTIFIER, ForeignKey('Warehouse.warehouse_id'), nullable=False)
    estimated_arrival = Column(Date, nullable=False)
    actual_arrival = Column(Date)
    created_datetime = Column(DateTime, nullable=False, server_default=func.getutcdate())

    order = relationship("Order", back_populates="shipments")
    shipment_status = relationship("Dictionary_ShipmentStatus", back_populates="shipments")
    vehicle = relationship("Delivery_Vehicle", back_populates="shipments")
    warehouse = relationship("Warehouse", back_populates="shipments")

    __table_args__ = (
        CheckConstraint('estimated_arrival >= shipment_date', name='CHK_Shipment_Dates'),
    )


class Support_Ticket(Base):
    __tablename__ = 'Support_Ticket'

    ticket_id = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=func.newid())
    customer_id = Column(UNIQUEIDENTIFIER, ForeignKey('Customer.customer_id'), nullable=False)
    order_id = Column(UNIQUEIDENTIFIER, ForeignKey('Order.order_id'))
    created_at = Column(DateTime, nullable=False, server_default=func.getutcdate())
    ticket_status_id = Column(SmallInteger, ForeignKey('Dictionary_TicketStatus.status_id'), nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(String(2000), nullable=False)
    resolution = Column(String(2000))
    closed_at = Column(DateTime)
    created_datetime = Column(DateTime, nullable=False, server_default=func.getutcdate())

    customer = relationship("Customer", back_populates="support_tickets")
    order = relationship("Order", back_populates="support_tickets")
    ticket_status = relationship("Dictionary_TicketStatus", back_populates="tickets")