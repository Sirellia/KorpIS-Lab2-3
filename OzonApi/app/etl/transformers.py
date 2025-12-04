import pandas as pd
import numpy as np
from typing import Dict, Tuple, Any
import logging
import uuid

from app.etl.validators import CustomerValidator, ProductValidator, OrderValidator
from config.etl_config import etl_config

logger = logging.getLogger(__name__)


class DataTransformer:
    """Базовый класс для трансформации данных"""

    def clean_text(self, text: str) -> str:
        if pd.isna(text):
            return ''
        return str(text).strip()

    def generate_uuid(self) -> str:
        return str(uuid.uuid4())


class CustomerDataTransformer(DataTransformer):
    """Трансформатор данных клиентов"""

    def __init__(self):
        super().__init__()
        self.validator = CustomerValidator()

    def transform_customer_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        valid_rows = []
        error_rows = []

        for index, row in df.iterrows():
            cleaned_row = row.copy()
            for col in ['full_name', 'email', 'phone', 'address']:
                if col in cleaned_row:
                    cleaned_row[col] = self.clean_text(cleaned_row[col])

            is_valid, errors = self.validator.validate_customer_row(cleaned_row)

            if is_valid:
                transformed_row = self._transform_valid_customer(cleaned_row)
                valid_rows.append(transformed_row)
            else:
                error_row = cleaned_row.to_dict()
                error_row['_errors'] = errors
                error_row['_original_index'] = index
                error_rows.append(error_row)

        valid_df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        errors_df = pd.DataFrame(error_rows) if error_rows else pd.DataFrame()

        logger.info(f"Трансформация клиентов: {len(valid_df)} валидных, {len(errors_df)} с ошибками")
        return valid_df, errors_df

    def _transform_valid_customer(self, row: pd.Series) -> Dict[str, Any]:
        return {
            'customer_id': self.generate_uuid(),
            'full_name': row['full_name'],
            'email': row['email'].lower(),
            'phone': row['phone'],
            'address': row['address'],
            'registration_date': row.get('registration_date')
        }


class ProductDataTransformer(DataTransformer):
    """Трансформатор данных товаров"""

    def __init__(self):
        super().__init__()
        self.validator = ProductValidator()

    def transform_product_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        valid_rows = []
        error_rows = []

        for index, row in df.iterrows():
            cleaned_row = row.copy()
            for col in ['name', 'description', 'sku', 'category']:
                if col in cleaned_row:
                    cleaned_row[col] = self.clean_text(cleaned_row[col])

            is_valid, errors = self.validator.validate_product_row(cleaned_row)

            if is_valid:
                transformed_row = self._transform_valid_product(cleaned_row)
                valid_rows.append(transformed_row)
            else:
                error_row = cleaned_row.to_dict()
                error_row['_errors'] = errors
                error_row['_original_index'] = index
                error_rows.append(error_row)

        valid_df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        errors_df = pd.DataFrame(error_rows) if error_rows else pd.DataFrame()

        logger.info(f"Трансформация товаров: {len(valid_df)} валидных, {len(errors_df)} с ошибками")
        return valid_df, errors_df

    def _transform_valid_product(self, row: pd.Series) -> Dict[str, Any]:
        category = self.clean_text(row.get('category', ''))
        category_code = etl_config.PRODUCT_CATEGORY_MAPPING.get(
            category.upper(), category.upper()
        )

        return {
            'product_id': self.generate_uuid(),
            'name': row['name'],
            'description': row.get('description'),
            'sku': row['sku'].upper(),
            'weight': float(row['weight']),
            'dimensions': row.get('dimensions'),
            'category_code': category_code,
            'price': float(row['price'])
        }


class OrderDataTransformer(DataTransformer):
    """Трансформатор данных заказов"""

    def __init__(self):
        super().__init__()
        self.validator = OrderValidator()

    def transform_order_data(self, df: pd.DataFrame, customer_mapping: Dict[str, str]) -> Tuple[pd.DataFrame, pd.DataFrame]:
        valid_rows = []
        error_rows = []

        for index, row in df.iterrows():
            cleaned_row = row.copy()

            is_valid, errors = self.validator.validate_order_row(cleaned_row)

            # Проверка существования клиента
            customer_email = self.clean_text(row.get('customer_email', '')).lower()
            if customer_email not in customer_mapping:
                errors.append(f"Клиент с email {customer_email} не найден")
                is_valid = False

            if is_valid:
                transformed_row = self._transform_valid_order(cleaned_row, customer_mapping)
                valid_rows.append(transformed_row)
            else:
                error_row = cleaned_row.to_dict()
                error_row['_errors'] = errors
                error_row['_original_index'] = index
                error_rows.append(error_row)

        valid_df = pd.DataFrame(valid_rows) if valid_rows else pd.DataFrame()
        errors_df = pd.DataFrame(error_rows) if error_rows else pd.DataFrame()

        logger.info(f"Трансформация заказов: {len(valid_df)} валидных, {len(errors_df)} с ошибками")
        return valid_df, errors_df

    def _transform_valid_order(self, row: pd.Series, customer_mapping: Dict[str, str]) -> Dict[str, Any]:
        customer_email = self.clean_text(row.get('customer_email', '')).lower()
        payment_method = self.clean_text(row.get('payment_method', ''))
        payment_method_code = etl_config.PAYMENT_METHOD_MAPPING.get(
            payment_method.upper(), payment_method.upper()
        )

        return {
            'order_id': self.generate_uuid(),
            'customer_id': customer_mapping[customer_email],
            'order_date': row.get('order_date'),
            'total_amount': float(row.get('total_amount', 0)),
            'delivery_address': row['delivery_address'],
            'payment_method_code': payment_method_code,
            'order_status_code': 'NEW'
        }