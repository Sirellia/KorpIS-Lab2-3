import pandas as pd
import re
from datetime import datetime, date
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class DataValidator:
    """Базовый класс для валидации данных"""

    @staticmethod
    def validate_email(email: str) -> bool:
        if pd.isna(email):
            return False  # Email обязателен для клиентов
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, str(email)))

    @staticmethod
    def validate_phone(phone: str) -> bool:
        if pd.isna(phone):
            return False  # Телефон обязателен для клиентов
        pattern = r'^[\+]?[0-9\s\-\(\)]{10,15}$'
        return bool(re.match(pattern, str(phone)))

    @staticmethod
    def validate_required_fields(row: pd.Series, required_fields: List[str]) -> List[str]:
        missing_fields = []
        for field in required_fields:
            if field not in row or pd.isna(row[field]) or str(row[field]).strip() == '':
                missing_fields.append(field)
        return missing_fields


class CustomerValidator(DataValidator):
    """Валидатор для данных клиентов"""

    REQUIRED_FIELDS = ['full_name', 'email', 'phone', 'address']

    def validate_customer_row(self, row: pd.Series) -> Tuple[bool, List[str]]:
        errors = []

        missing_fields = self.validate_required_fields(row, self.REQUIRED_FIELDS)
        if missing_fields:
            errors.append(f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")

        if 'email' in row and not self.validate_email(row['email']):
            errors.append("Неверный формат email")

        if 'phone' in row and not self.validate_phone(row['phone']):
            errors.append("Неверный формат телефона")

        return len(errors) == 0, errors


class ProductValidator(DataValidator):
    """Валидатор для данных товаров"""

    REQUIRED_FIELDS = ['name', 'sku', 'weight', 'category', 'price']

    def validate_product_row(self, row: pd.Series) -> Tuple[bool, List[str]]:
        errors = []

        missing_fields = self.validate_required_fields(row, self.REQUIRED_FIELDS)
        if missing_fields:
            errors.append(f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")

        # Проверка веса
        try:
            weight = float(row.get('weight', 0))
            if weight <= 0:
                errors.append("Вес должен быть положительным числом")
        except (ValueError, TypeError):
            errors.append("Неверный формат веса")

        # Проверка цены
        try:
            price = float(row.get('price', 0))
            if price < 0:
                errors.append("Цена не может быть отрицательной")
        except (ValueError, TypeError):
            errors.append("Неверный формат цены")

        return len(errors) == 0, errors


class OrderValidator(DataValidator):
    """Валидатор для данных заказов"""

    REQUIRED_FIELDS = ['customer_email', 'delivery_address', 'payment_method']

    def validate_order_row(self, row: pd.Series) -> Tuple[bool, List[str]]:
        errors = []

        missing_fields = self.validate_required_fields(row, self.REQUIRED_FIELDS)
        if missing_fields:
            errors.append(f"Отсутствуют обязательные поля: {', '.join(missing_fields)}")

        # Проверка суммы
        try:
            amount = float(row.get('total_amount', 0))
            if amount < 0:
                errors.append("Сумма заказа не может быть отрицательной")
        except (ValueError, TypeError):
            errors.append("Неверный формат суммы заказа")

        return len(errors) == 0, errors