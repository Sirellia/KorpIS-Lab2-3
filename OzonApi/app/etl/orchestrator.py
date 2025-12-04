import os
import logging
from datetime import datetime
import json
from typing import Dict, Any

from sqlalchemy.orm import Session

from app.etl.extractors import CustomerDataExtractor, ProductDataExtractor, OrderDataExtractor
from app.etl.transformers import CustomerDataTransformer, ProductDataTransformer, OrderDataTransformer
from app.etl.loaders import CustomerDataLoader, ProductDataLoader, OrderDataLoader, VisualizationEngine
from config.etl_config import etl_config

logger = logging.getLogger(__name__)


class ETLOrchestrator:
    """Оркестратор ETL-процессов для OzonLogistics"""

    def __init__(self, db: Session):
        self.db = db
        self.stats = {}

        # Инициализация компонентов
        self.extractors = {
            'customers': CustomerDataExtractor(),
            'products': ProductDataExtractor(),
            'orders': OrderDataExtractor()
        }

        self.transformers = {
            'customers': CustomerDataTransformer(),
            'products': ProductDataTransformer(),
            'orders': OrderDataTransformer()
        }

        self.loaders = {
            'customers': CustomerDataLoader(db),
            'products': ProductDataLoader(db),
            'orders': OrderDataLoader(db)
        }

        self.customer_mapping = {}

    def process_customers_file(self, file_path: str):
        """Обработка файла с данными клиентов"""
        logger.info(f"Начало обработки файла клиентов: {file_path}")

        try:
            # Нормализуем путь
            normalized_path = os.path.normpath(file_path)

            # Extract
            extractor = self.extractors['customers']
            raw_data = extractor.extract_customers_data(normalized_path)
            logger.info(f"Извлечено записей: {len(raw_data)}")

            # Transform
            transformer = self.transformers['customers']
            valid_data, errors_data = transformer.transform_customer_data(raw_data)
            logger.info(f"Валидных: {len(valid_data)}, С ошибками: {len(errors_data)}")

            # Load
            loader = self.loaders['customers']
            load_stats, self.customer_mapping = loader.load_customer_data(valid_data, file_path)

            # Сохранение ошибок
            if not errors_data.empty:
                loader.save_errors_report(errors_data, file_path, 'customers')
                logger.info(f"Сохранен отчет об ошибках: {len(errors_data)} записей")

            # Статистика
            self.stats['customers'] = {
                'total_processed': len(raw_data),
                'valid_records': len(valid_data),
                'error_records': len(errors_data),
                **load_stats
            }

            logger.info(f"Обработка клиентов завершена: {len(valid_data)} успешно, {len(errors_data)} с ошибками")

            # Сохраняем итоговый отчёт
            self._save_final_report()

        except Exception as e:
            logger.error(f"Ошибка при обработке файла клиентов {file_path}: {str(e)}")
            self.stats['customers'] = {'error': str(e), 'total_processed': 0}

    def process_products_file(self, file_path: str):
        """Обработка файла с данными товаров"""
        logger.info(f"Начало обработки файла товаров: {file_path}")

        try:
            normalized_path = os.path.normpath(file_path)

            extractor = self.extractors['products']
            raw_data = extractor.extract_products_data(normalized_path)

            transformer = self.transformers['products']
            valid_data, errors_data = transformer.transform_product_data(raw_data)

            loader = self.loaders['products']
            load_stats = loader.load_product_data(valid_data, file_path)

            if not errors_data.empty:
                loader.save_errors_report(errors_data, file_path, 'products')

            self.stats['products'] = {
                'total_processed': len(raw_data),
                'valid_records': len(valid_data),
                'error_records': len(errors_data),
                **load_stats
            }

            logger.info(f"Обработка товаров завершена: {len(valid_data)} успешно")
            self._save_final_report()

        except Exception as e:
            logger.error(f"Ошибка при обработке файла товаров {file_path}: {str(e)}")
            self.stats['products'] = {'error': str(e), 'total_processed': 0}

    def process_orders_file(self, file_path: str):
        """Обработка файла с данными заказов"""
        logger.info(f"Начало обработки файла заказов: {file_path}")

        try:
            normalized_path = os.path.normpath(file_path)

            extractor = self.extractors['orders']
            raw_data = extractor.extract_orders_data(normalized_path)

            transformer = self.transformers['orders']
            valid_data, errors_data = transformer.transform_order_data(raw_data, self.customer_mapping)

            loader = self.loaders['orders']
            load_stats = loader.load_order_data(valid_data, file_path)

            if not errors_data.empty:
                loader.save_errors_report(errors_data, file_path, 'orders')

            self.stats['orders'] = {
                'total_processed': len(raw_data),
                'valid_records': len(valid_data),
                'error_records': len(errors_data),
                **load_stats
            }

            logger.info(f"Обработка заказов завершена: {len(valid_data)} успешно")
            self._save_final_report()

        except Exception as e:
            logger.error(f"Ошибка при обработке файла заказов {file_path}: {str(e)}")
            self.stats['orders'] = {'error': str(e), 'total_processed': 0}

    def run_etl_pipeline(self):
        """Запуск полного ETL-конвейера"""
        logger.info("=" * 50)
        logger.info("Запуск ETL-конвейера OzonLogistics")
        logger.info("=" * 50)

        extractor = self.extractors['customers']
        files = extractor.list_available_files()

        if not files:
            logger.warning("Нет файлов для обработки в директории input")
            return self.stats

        for file in files:
            logger.info(f"Обработка файла: {file}")
            file_lower = file.lower()

            if 'customer' in file_lower or 'клиент' in file_lower:
                self.process_customers_file(file)
            elif 'product' in file_lower or 'товар' in file_lower:
                self.process_products_file(file)
            elif 'order' in file_lower or 'заказ' in file_lower:
                self.process_orders_file(file)
            else:
                logger.warning(f"Неизвестный тип файла: {file}")

        self._create_visualizations()
        self._save_final_report()

        logger.info("=" * 50)
        logger.info("ETL-конвейер завершен")
        logger.info("=" * 50)

        return self.stats

    def _create_visualizations(self):
        """Создание визуализаций"""
        try:
            if not self.stats:
                logger.warning("Нет данных для визуализации")
                return

            # Создаём директорию
            os.makedirs(etl_config.OUTPUT_DIR, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            dashboard_path = os.path.join(etl_config.OUTPUT_DIR, f"etl_dashboard_{timestamp}.png")

            VisualizationEngine.create_etl_dashboard(self.stats, dashboard_path)

        except Exception as e:
            logger.error(f"Ошибка при создании визуализаций: {str(e)}")

    def _save_final_report(self):
        """Сохранение итогового отчета"""
        try:
            # Создаём директорию
            os.makedirs(etl_config.OUTPUT_DIR, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(etl_config.OUTPUT_DIR, f"etl_report_{timestamp}.json")

            report = {
                'timestamp': timestamp,
                'generated_at': datetime.now().isoformat(),
                'statistics': self.stats,
                'summary': self._generate_summary()
            }

            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"Итоговый отчет сохранен: {report_path}")

        except Exception as e:
            logger.error(f"Ошибка при сохранении отчета: {str(e)}")

    def _generate_summary(self) -> Dict[str, Any]:
        """Генерация сводки по процессу"""
        total_processed = 0
        total_valid = 0
        total_errors = 0
        total_created = 0

        for process_name, process_stats in self.stats.items():
            if isinstance(process_stats, dict):
                total_processed += process_stats.get('total_processed', 0)
                total_valid += process_stats.get('valid_records', 0)
                total_errors += process_stats.get('error_records', 0)
                total_created += process_stats.get('customers_created', 0)
                total_created += process_stats.get('products_created', 0)
                total_created += process_stats.get('orders_created', 0)

        success_rate = (total_valid / total_processed * 100) if total_processed > 0 else 0

        return {
            'total_processed': total_processed,
            'total_valid': total_valid,
            'total_errors': total_errors,
            'total_created': total_created,
            'success_rate': round(success_rate, 2)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Получить текущую статистику"""
        return {
            'stats': self.stats,
            'summary': self._generate_summary()
        }