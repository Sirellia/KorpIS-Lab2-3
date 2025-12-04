#!/usr/bin/env python3
"""
Главный скрипт для запуска ETL-процессов
"""

import os
import sys
import logging

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.etl import ETLOrchestrator

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/etl.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Главная функция"""
    logger.info("Запуск ETL-процесса")

    db = SessionLocal()
    try:
        orchestrator = ETLOrchestrator(db)
        orchestrator.run_etl_pipeline()

        # Вывод сводки в консоль
        summary = orchestrator._generate_summary()
        print("\n" + "="*50)
        print("ETL PROCESS SUMMARY")
        print("="*50)
        print(f"Total processed: {summary['total_processed']}")
        print(f"Valid records: {summary['total_valid']}")
        print(f"Errors: {summary['total_errors']}")
        print(f"Success rate: {summary['success_rate']}%")
        print("="*50)

    except Exception as e:
        logger.error(f"Критическая ошибка ETL-процесса: {str(e)}")
        return 1
    finally:
        db.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())