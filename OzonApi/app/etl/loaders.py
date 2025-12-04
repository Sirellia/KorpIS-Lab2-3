import pandas as pd
import os
import json
from typing import Dict, Any
import logging
from datetime import datetime
import matplotlib.pyplot as plt

from sqlalchemy.orm import Session
from app import crud, schemas, models
from config.etl_config import etl_config

logger = logging.getLogger(__name__)


class DataLoader:
    """Базовый класс для загрузки данных"""

    def __init__(self, db: Session):
        self.db = db

    def save_errors_report(self, errors_df: pd.DataFrame, source_file: str, process_type: str):
        if errors_df.empty:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        error_file = f"{process_type}_errors_{timestamp}.csv"
        error_path = os.path.join(etl_config.ERRORS_DIR, error_file)

        errors_df.to_csv(error_path, index=False, encoding='utf-8')
        logger.info(f"Отчет об ошибках сохранен: {error_path}")


class CustomerDataLoader(DataLoader):
    """Загрузчик данных клиентов"""

    def load_customer_data(self, valid_df: pd.DataFrame, source_file: str) -> Dict[str, Any]:
        stats = {
            'total_processed': len(valid_df),
            'customers_created': 0,
            'errors': []
        }

        customer_mapping = {}  # email -> customer_id

        for _, row in valid_df.iterrows():
            try:
                # Проверка существования клиента по email
                existing = crud.get_customer_by_email(self.db, row['email'])
                if existing:
                    customer_mapping[row['email']] = str(existing.customer_id)
                    continue

                customer_data = schemas.CustomerCreate(
                    full_name=row['full_name'],
                    email=row['email'],
                    phone=row['phone'],
                    address=row['address'],
                    registration_date=row.get('registration_date')
                )

                customer = crud.create_customer(self.db, customer_data)
                customer_mapping[row['email']] = str(customer.customer_id)
                stats['customers_created'] += 1

            except Exception as e:
                stats['errors'].append(f"Ошибка при создании клиента {row.get('full_name', '')}: {str(e)}")

        self.db.commit()
        logger.info(f"Загрузка клиентов завершена: {stats}")
        return stats, customer_mapping


class ProductDataLoader(DataLoader):
    """Загрузчик данных товаров"""

    def load_product_data(self, valid_df: pd.DataFrame, source_file: str) -> Dict[str, Any]:
        stats = {
            'total_processed': len(valid_df),
            'products_created': 0,
            'errors': []
        }

        # Получаем маппинг категорий
        categories = self.db.query(models.Dictionary_ProductCategory).all()
        category_mapping = {c.category_code: c.category_id for c in categories}

        for _, row in valid_df.iterrows():
            try:
                # Проверка существования товара по SKU
                existing = crud.get_product_by_sku(self.db, row['sku'])
                if existing:
                    continue

                category_id = category_mapping.get(row['category_code'])
                if not category_id:
                    stats['errors'].append(f"Категория не найдена: {row['category_code']}")
                    continue

                product_data = schemas.ProductCreate(
                    name=row['name'],
                    description=row.get('description'),
                    sku=row['sku'],
                    weight=row['weight'],
                    dimensions=row.get('dimensions'),
                    category_id=category_id,
                    price=row['price']
                )

                crud.create_product(self.db, product_data)
                stats['products_created'] += 1

            except Exception as e:
                stats['errors'].append(f"Ошибка при создании товара {row.get('name', '')}: {str(e)}")

        self.db.commit()
        logger.info(f"Загрузка товаров завершена: {stats}")
        return stats


class OrderDataLoader(DataLoader):
    """Загрузчик данных заказов"""

    def load_order_data(self, valid_df: pd.DataFrame, source_file: str) -> Dict[str, Any]:
        stats = {
            'total_processed': len(valid_df),
            'orders_created': 0,
            'errors': []
        }

        # Получаем маппинги справочников
        statuses = self.db.query(models.Dictionary_OrderStatus).all()
        status_mapping = {s.status_code: s.status_id for s in statuses}

        payment_methods = self.db.query(models.Dictionary_PaymentMethod).all()
        payment_mapping = {p.method_code: p.method_id for p in payment_methods}

        for _, row in valid_df.iterrows():
            try:
                status_id = status_mapping.get(row.get('order_status_code', 'NEW'), status_mapping.get('NEW'))
                payment_id = payment_mapping.get(row['payment_method_code'])

                if not payment_id:
                    stats['errors'].append(f"Способ оплаты не найден: {row['payment_method_code']}")
                    continue

                order_data = schemas.OrderCreate(
                    customer_id=row['customer_id'],
                    order_status_id=status_id,
                    total_amount=row['total_amount'],
                    delivery_address=row['delivery_address'],
                    payment_method_id=payment_id,
                    order_date=row.get('order_date')
                )

                crud.create_order(self.db, order_data)
                stats['orders_created'] += 1

            except Exception as e:
                stats['errors'].append(f"Ошибка при создании заказа: {str(e)}")

        self.db.commit()
        logger.info(f"Загрузка заказов завершена: {stats}")
        return stats


class VisualizationEngine:
    """Движок для визуализации результатов ETL"""

    @staticmethod
    def create_etl_dashboard(stats: Dict[str, Any], output_path: str):
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('OzonLogistics ETL Dashboard', fontsize=16)

            # 1. Общая статистика
            labels = list(stats.keys())
            processed = [s.get('total_processed', 0) for s in stats.values()]
            created = [s.get('customers_created', 0) + s.get('products_created', 0) + s.get('orders_created', 0)
                       for s in stats.values()]

            x = range(len(labels))
            axes[0, 0].bar([i - 0.2 for i in x], processed, 0.4, label='Обработано', color='blue')
            axes[0, 0].bar([i + 0.2 for i in x], created, 0.4, label='Создано', color='green')
            axes[0, 0].set_xticks(x)
            axes[0, 0].set_xticklabels(labels)
            axes[0, 0].legend()
            axes[0, 0].set_title('Статистика по процессам')

            # 2. Распределение записей
            if sum(processed) > 0:
                axes[0, 1].pie(processed, labels=labels, autopct='%1.1f%%')
            axes[0, 1].set_title('Распределение записей')

            # 3. Ошибки
            error_counts = [len(s.get('errors', [])) for s in stats.values()]
            axes[1, 0].bar(labels, error_counts, color='red')
            axes[1, 0].set_title('Количество ошибок')

            # 4. Сводка
            total_processed = sum(processed)
            total_created = sum(created)
            total_errors = sum(error_counts)
            success_rate = (total_created / total_processed * 100) if total_processed > 0 else 0

            summary_text = f"""
            Всего обработано: {total_processed}
            Всего создано: {total_created}
            Всего ошибок: {total_errors}
            Успешность: {success_rate:.1f}%
            """
            axes[1, 1].text(0.5, 0.5, summary_text, ha='center', va='center',
                            transform=axes[1, 1].transAxes, fontsize=14)
            axes[1, 1].set_title('Сводка')
            axes[1, 1].axis('off')

            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"Дашборд сохранен: {output_path}")

        except Exception as e:
            logger.error(f"Ошибка при создании дашборда: {str(e)}")