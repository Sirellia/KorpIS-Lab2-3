from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging
import uvicorn
import os
import uuid

from app.database import engine, get_db, SessionLocal
from app import models
from app.routers import (
    customers, products, orders, order_items,
    shipments, vehicles, warehouses, support_tickets,
    dictionaries
)
from app.etl import ETLOrchestrator

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="OzonLogistics API",
    description="REST API для управления логистикой и доставкой OZON с ETL функциональностью",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(order_items.router, prefix="/api/order-items", tags=["order-items"])
app.include_router(shipments.router, prefix="/api/shipments", tags=["shipments"])
app.include_router(vehicles.router, prefix="/api/vehicles", tags=["vehicles"])
app.include_router(warehouses.router, prefix="/api/warehouses", tags=["warehouses"])
app.include_router(support_tickets.router, prefix="/api/support-tickets", tags=["support-tickets"])
app.include_router(dictionaries.router, prefix="/api/dictionaries", tags=["dictionaries"])


@app.get("/")
async def root():
    return {
        "message": "OzonLogistics API",
        "version": "2.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Database connection failed")


# ETL endpoints
@app.post("/api/etl/upload-file")
async def upload_file(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        file_type: str = "auto"
):
    """Эндпоинт для загрузки файла и запуска ETL"""
    try:
        allowed_extensions = ['.csv', '.xlsx', '.xls']
        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Неподдерживаемый формат файла. Разрешены: {', '.join(allowed_extensions)}"
            )

        os.makedirs("data/input", exist_ok=True)

        file_id = str(uuid.uuid4())
        file_path = os.path.join("data/input", f"{file_id}_{file.filename}")

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        background_tasks.add_task(process_uploaded_file, file_path, file_type)

        return {
            "message": "Файл загружен и находится в обработке",
            "file_id": file_id,
            "filename": file.filename
        }

    except Exception as e:
        logger.error(f"Ошибка загрузки файла: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки файла: {str(e)}")


@app.get("/api/etl/status")
async def get_etl_status():
    """Получить статус ETL-процессов"""
    return {"status": "running", "message": "ETL system is operational"}


def process_uploaded_file(file_path: str, file_type: str):
    """Фоновая задача обработки файла"""
    db = SessionLocal()
    try:
        orchestrator = ETLOrchestrator(db)

        if file_type == "customers" or "customer" in file_path.lower():
            orchestrator.process_customers_file(file_path)
        elif file_type == "products" or "product" in file_path.lower():
            orchestrator.process_products_file(file_path)
        elif file_type == "orders" or "order" in file_path.lower():
            orchestrator.process_orders_file(file_path)
        else:
            # Автоопределение
            if "customer" in file_path.lower():
                orchestrator.process_customers_file(file_path)
            elif "product" in file_path.lower():
                orchestrator.process_products_file(file_path)
            elif "order" in file_path.lower():
                orchestrator.process_orders_file(file_path)

    except Exception as e:
        logger.error(f"Ошибка обработки файла {file_path}: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )