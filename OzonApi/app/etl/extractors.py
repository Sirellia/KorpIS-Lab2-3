import pandas as pd
import os
from typing import List, Dict, Any
import logging
from config.etl_config import etl_config

logger = logging.getLogger(__name__)


class DataExtractor:
    """Базовый класс для извлечения данных из файлов"""

    def __init__(self):
        self.supported_formats = ['.csv', '.xlsx', '.xls']

    def list_available_files(self) -> List[str]:
        """Получить список доступных файлов для обработки"""
        files = []
        if os.path.exists(etl_config.INPUT_DIR):
            for file in os.listdir(etl_config.INPUT_DIR):
                if any(file.lower().endswith(fmt) for fmt in self.supported_formats):
                    files.append(file)
        logger.info(f"Найдено файлов для обработки: {files}")
        return files

    def extract_from_csv(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Извлечение данных из CSV файла"""
        try:
            df = pd.read_csv(file_path, encoding='utf-8', **kwargs)
            logger.info(f"Успешно извлечено {len(df)} записей из CSV: {file_path}")
            return df
        except UnicodeDecodeError:
            # Пробуем другую кодировку
            df = pd.read_csv(file_path, encoding='cp1251', **kwargs)
            logger.info(f"Успешно извлечено {len(df)} записей из CSV (cp1251): {file_path}")
            return df
        except Exception as e:
            logger.error(f"Ошибка при чтении CSV файла {file_path}: {str(e)}")
            raise

    def extract_from_excel(self, file_path: str, sheet_name=0, **kwargs) -> pd.DataFrame:
        """Извлечение данных из Excel файла"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
            logger.info(f"Успешно извлечено {len(df)} записей из Excel: {file_path}")
            return df
        except Exception as e:
            logger.error(f"Ошибка при чтении Excel файла {file_path}: {str(e)}")
            raise

    def extract_data(self, file_path: str, **kwargs) -> pd.DataFrame:
        """Универсальный метод извлечения данных"""

        # Нормализуем путь
        file_path = os.path.normpath(file_path)

        # Если путь абсолютный - используем как есть
        if os.path.isabs(file_path):
            full_path = file_path
        # Если путь уже содержит data/input или data\input - используем как есть
        elif 'data' + os.sep + 'input' in file_path or 'data/input' in file_path:
            full_path = file_path
        else:
            # Иначе добавляем префикс
            full_path = os.path.join(etl_config.INPUT_DIR, file_path)

        # Финальная нормализация
        full_path = os.path.normpath(full_path)

        logger.info(f"Попытка чтения файла: {full_path}")

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Файл не найден: {full_path}")

        if full_path.lower().endswith('.csv'):
            return self.extract_from_csv(full_path, **kwargs)
        elif full_path.lower().endswith(('.xlsx', '.xls')):
            return self.extract_from_excel(full_path, **kwargs)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {full_path}")


class CustomerDataExtractor(DataExtractor):
    """Экстрактор для данных клиентов"""

    def extract_customers_data(self, file_path: str) -> pd.DataFrame:
        """Извлечение данных клиентов"""
        df = self.extract_data(file_path)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        df = df.dropna(how='all')
        logger.info(f"Извлечены данные клиентов: {len(df)} записей, колонки: {list(df.columns)}")
        return df


class ProductDataExtractor(DataExtractor):
    """Экстрактор для данных товаров"""

    def extract_products_data(self, file_path: str, sheet_name='Products') -> pd.DataFrame:
        """Извлечение данных товаров"""
        try:
            df = self.extract_data(file_path, sheet_name=sheet_name)
        except:
            # Если не Excel или нет такого листа - читаем как обычный файл
            df = self.extract_data(file_path)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        df = df.dropna(how='all')
        logger.info(f"Извлечены данные товаров: {len(df)} записей")
        return df


class OrderDataExtractor(DataExtractor):
    """Экстрактор для данных заказов"""

    def extract_orders_data(self, file_path: str, sheet_name='Orders') -> pd.DataFrame:
        """Извлечение данных заказов"""
        try:
            df = self.extract_data(file_path, sheet_name=sheet_name)
        except:
            df = self.extract_data(file_path)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        df = df.dropna(how='all')
        logger.info(f"Извлечены данные заказов: {len(df)} записей")
        return df

    def extract_order_items_data(self, file_path: str, sheet_name='OrderItems') -> pd.DataFrame:
        """Извлечение данных позиций заказов"""
        try:
            df = self.extract_data(file_path, sheet_name=sheet_name)
        except:
            df = self.extract_data(file_path)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        df = df.dropna(how='all')
        logger.info(f"Извлечены данные позиций заказов: {len(df)} записей")
        return df