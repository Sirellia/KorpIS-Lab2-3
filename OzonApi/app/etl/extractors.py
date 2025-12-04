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
            df = pd.read_csv(file_path, **kwargs)
            logger.info(f"Успешно извлечено {len(df)} записей из CSV: {file_path}")
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
        if not os.path.isabs(file_path):
            file_path = os.path.join(etl_config.INPUT_DIR, file_path)

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл не найден: {file_path}")

        if file_path.lower().endswith('.csv'):
            return self.extract_from_csv(file_path, **kwargs)
        elif file_path.lower().endswith(('.xlsx', '.xls')):
            return self.extract_from_excel(file_path, **kwargs)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {file_path}")


class CustomerDataExtractor(DataExtractor):
    """Экстрактор для данных клиентов"""

    def extract_customers_data(self, file_path: str) -> pd.DataFrame:
        """Извлечение данных клиентов"""
        df = self.extract_data(file_path)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        df = df.dropna(how='all')
        logger.info(f"Извлечены данные клиентов: {len(df)} записей")
        return df


class ProductDataExtractor(DataExtractor):
    """Экстрактор для данных товаров"""

    def extract_products_data(self, file_path: str, sheet_name='Products') -> pd.DataFrame:
        """Извлечение данных товаров"""
        df = self.extract_data(file_path, sheet_name=sheet_name)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        df = df.dropna(how='all')
        logger.info(f"Извлечены данные товаров: {len(df)} записей")
        return df


class OrderDataExtractor(DataExtractor):
    """Экстрактор для данных заказов"""

    def extract_orders_data(self, file_path: str, sheet_name='Orders') -> pd.DataFrame:
        """Извлечение данных заказов"""
        df = self.extract_data(file_path, sheet_name=sheet_name)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        df = df.dropna(how='all')
        logger.info(f"Извлечены данные заказов: {len(df)} записей")
        return df

    def extract_order_items_data(self, file_path: str, sheet_name='OrderItems') -> pd.DataFrame:
        """Извлечение данных позиций заказов"""
        df = self.extract_data(file_path, sheet_name=sheet_name)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        df = df.dropna(how='all')
        logger.info(f"Извлечены данные позиций заказов: {len(df)} записей")
        return df