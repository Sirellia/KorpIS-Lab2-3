import pandas as pd
import os
import json
from typing import Dict, Any, Tuple
import logging
from datetime import datetime
import matplotlib

matplotlib.use('Agg')  # Используем backend без GUI
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
        """Сохранение отчета об ошибках"""
        if errors_df.empty:
            logger.info("Нет ошибок для сохранения")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Создаём директорию если её нет
        os.makedirs(etl_config.ERRORS_DIR, exist_ok=True)

        # Сохраняем ошибки в CSV
        error_file = f"{process_type}_errors_{timestamp}.csv"
        error_path = os.path.join(etl_config.ERRORS_DIR, error_file)
        errors_df.to_csv(error_path, index=False, encoding='utf-8-sig')
        logger.info(f"Отчет об ошибках сохранен: {error_path}")

        # Сохраняем сводку в JSON
        summary = {
            'source_file': source_file,
            'process_type': process_type,
            'timestamp': timestamp,
            'total_errors': len(errors_df),
            'error_details': []
        }

        # Добавляем детали ошибок
        if '_errors' in errors_df.columns:
            for idx, row in errors_df.iterrows():
                error_info = {
                    'row_index': row.get('_original_index', idx),
                    'errors': row.get('_errors', [])
                }
                # Добавляем данные строки (без служебных полей)
                row_data = {k: str(v) for k, v in row.items() if not k.startswith('_')}
                error_info['data'] = row_data
                summary['error_details'].append(error_info)

        summary_file = f"{process_type}_errors_summary_{timestamp}.json"
        summary_path = os.path.join(etl_config.ERRORS_DIR, summary_file)

        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"Сводка об ошибках сохранена: {summary_path}")


class CustomerDataLoader(DataLoader):
    """Загрузчик данных клиентов"""

    def load_customer_data(self, valid_df: pd.DataFrame, source_file: str) -> Tuple[Dict[str, Any], Dict[str, str]]:
        """Загрузка данных клиентов в БД"""
        stats = {
            'total_processed': len(valid_df),
            'customers_created': 0,
            'customers_skipped': 0,
            'errors': []
        }

        customer_mapping = {}  # email -> customer_id

        for idx, row in valid_df.iterrows():
            try:
                email = row.get('email', '').strip().lower()

                # Проверка существования клиента по email
                existing = crud.get_customer_by_email(self.db, email)
                if existing:
                    customer_mapping[email] = str(existing.customer_id)
                    stats['customers_skipped'] += 1
                    logger.info(f"Клиент с email {email} уже существует, пропускаем")
                    continue

                customer_data = schemas.CustomerCreate(
                    full_name=row['full_name'],
                    email=email,
                    phone=row['phone'],
                    address=row['address'],
                    registration_date=row.get('registration_date')
                )

                customer = crud.create_customer(self.db, customer_data)
                customer_mapping[email] = str(customer.customer_id)
                stats['customers_created'] += 1
                logger.info(f"Создан клиент: {row['full_name']} ({email})")

            except Exception as e:
                error_msg = f"Ошибка при создании клиента {row.get('full_name', 'N/A')}: {str(e)}"
                stats['errors'].append(error_msg)
                logger.error(error_msg)

        self.db.commit()
        logger.info(
            f"Загрузка клиентов завершена: создано {stats['customers_created']}, пропущено {stats['customers_skipped']}")
        return stats, customer_mapping


class ProductDataLoader(DataLoader):
    """Загрузчик данных товаров"""

    def load_product_data(self, valid_df: pd.DataFrame, source_file: str) -> Dict[str, Any]:
        """Загрузка данных товаров в БД"""
        stats = {
            'total_processed': len(valid_df),
            'products_created': 0,
            'products_skipped': 0,
            'errors': []
        }

        # Получаем маппинг категорий
        categories = self.db.query(models.Dictionary_ProductCategory).all()
        category_mapping = {c.category_code: c.category_id for c in categories}

        for idx, row in valid_df.iterrows():
            try:
                sku = row.get('sku', '').strip().upper()

                # Проверка существования товара по SKU
                existing = crud.get_product_by_sku(self.db, sku)
                if existing:
                    stats['products_skipped'] += 1
                    logger.info(f"Товар с SKU {sku} уже существует, пропускаем")
                    continue

                category_id = category_mapping.get(row.get('category_code'))
                if not category_id:
                    stats['errors'].append(f"Категория не найдена: {row.get('category_code')}")
                    continue

                product_data = schemas.ProductCreate(
                    name=row['name'],
                    description=row.get('description'),
                    sku=sku,
                    weight=float(row['weight']),
                    dimensions=row.get('dimensions'),
                    category_id=category_id,
                    price=float(row['price'])
                )

                crud.create_product(self.db, product_data)
                stats['products_created'] += 1
                logger.info(f"Создан товар: {row['name']} ({sku})")

            except Exception as e:
                error_msg = f"Ошибка при создании товара {row.get('name', 'N/A')}: {str(e)}"
                stats['errors'].append(error_msg)
                logger.error(error_msg)

        self.db.commit()
        logger.info(
            f"Загрузка товаров завершена: создано {stats['products_created']}, пропущено {stats['products_skipped']}")
        return stats


class OrderDataLoader(DataLoader):
    """Загрузчик данных заказов"""

    def load_order_data(self, valid_df: pd.DataFrame, source_file: str) -> Dict[str, Any]:
        """Загрузка данных заказов в БД"""
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

        for idx, row in valid_df.iterrows():
            try:
                status_id = status_mapping.get(row.get('order_status_code', 'NEW'), status_mapping.get('NEW'))
                payment_id = payment_mapping.get(row.get('payment_method_code'))

                if not payment_id:
                    stats['errors'].append(f"Способ оплаты не найден: {row.get('payment_method_code')}")
                    continue

                order_data = schemas.OrderCreate(
                    customer_id=row['customer_id'],
                    order_status_id=status_id,
                    total_amount=float(row.get('total_amount', 0)),
                    delivery_address=row['delivery_address'],
                    payment_method_id=payment_id,
                    order_date=row.get('order_date')
                )

                crud.create_order(self.db, order_data)
                stats['orders_created'] += 1

            except Exception as e:
                error_msg = f"Ошибка при создании заказа: {str(e)}"
                stats['errors'].append(error_msg)
                logger.error(error_msg)

        self.db.commit()
        logger.info(f"Загрузка заказов завершена: создано {stats['orders_created']}")
        return stats


class VisualizationEngine:
    """Движок для визуализации результатов ETL"""

    @staticmethod
    def create_etl_dashboard(stats: Dict[str, Any], output_path: str):
        """Создание дашборда с результатами ETL"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))
            fig.suptitle('OzonLogistics ETL Dashboard', fontsize=16)

            # Фильтруем только валидные статистики
            valid_stats = {k: v for k, v in stats.items() if isinstance(v, dict) and 'total_processed' in v}

            if not valid_stats:
                logger.warning("Нет данных для визуализации")
                plt.close()
                return

            labels = list(valid_stats.keys())
            processed = [s.get('total_processed', 0) for s in valid_stats.values()]

            # Считаем созданные записи
            created = []
            for s in valid_stats.values():
                count = s.get('customers_created', 0) + s.get('products_created', 0) + s.get('orders_created', 0)
                created.append(count)

            # 1. Статистика по процессам
            x = range(len(labels))
            width = 0.35
            axes[0, 0].bar([i - width / 2 for i in x], processed, width, label='Обработано', color='blue')
            axes[0, 0].bar([i + width / 2 for i in x], created, width, label='Создано', color='green')
            axes[0, 0].set_xticks(x)
            axes[0, 0].set_xticklabels(labels)
            axes[0, 0].legend()
            axes[0, 0].set_title('Статистика по процессам')
            axes[0, 0].set_ylabel('Количество записей')

            # 2. Распределение записей
            if sum(processed) > 0:
                axes[0, 1].pie(processed, labels=labels, autopct='%1.1f%%', startangle=90)
            axes[0, 1].set_title('Распределение обработанных записей')

            # 3. Ошибки
            error_counts = [len(s.get('errors', [])) for s in valid_stats.values()]
            colors = ['red' if e > 0 else 'green' for e in error_counts]
            axes[1, 0].bar(labels, error_counts, color=colors)
            axes[1, 0].set_title('Количество ошибок по процессам')
            axes[1, 0].set_ylabel('Количество ошибок')

            # 4. Сводка
            total_processed = sum(processed)
            total_created = sum(created)
            total_errors = sum(error_counts)
            success_rate = (total_created / total_processed * 100) if total_processed > 0 else 0

            summary_text = f"""
            СВОДКА ETL-ПРОЦЕССА

            Всего обработано: {total_processed}
            Всего создано: {total_created}
            Всего ошибок: {total_errors}

            Успешность: {success_rate:.1f}%
            """
            axes[1, 1].text(0.5, 0.5, summary_text, ha='center', va='center',
                            transform=axes[1, 1].transAxes, fontsize=14,
                            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            axes[1, 1].set_title('Итоговая сводка')
            axes[1, 1].axis('off')

            plt.tight_layout()

            # Создаём директорию если её нет
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"Дашборд сохранен: {output_path}")

        except Exception as e:
            logger.error(f"Ошибка при создании дашборда: {str(e)}")
            plt.close()