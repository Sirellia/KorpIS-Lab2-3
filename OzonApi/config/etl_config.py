import os


class ETLConfig:
    """Конфигурация ETL-процессов для OzonLogistics"""

    # Директории
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    INPUT_DIR = os.path.join(DATA_DIR, 'input')
    OUTPUT_DIR = os.path.join(DATA_DIR, 'output')
    ERRORS_DIR = os.path.join(DATA_DIR, 'errors')

    # Создаём директории если их нет
    for dir_path in [INPUT_DIR, OUTPUT_DIR, ERRORS_DIR]:
        os.makedirs(dir_path, exist_ok=True)

    # Маппинг статусов заказов
    ORDER_STATUS_MAPPING = {
        'NEW': 'NEW',
        'НОВЫЙ': 'NEW',
        'CONFIRMED': 'CONFIRMED',
        'ПОДТВЕРЖДЁН': 'CONFIRMED',
        'PROCESSING': 'PROCESSING',
        'В ОБРАБОТКЕ': 'PROCESSING',
        'SHIPPED': 'SHIPPED',
        'ОТПРАВЛЕН': 'SHIPPED',
        'DELIVERED': 'DELIVERED',
        'ДОСТАВЛЕН': 'DELIVERED',
        'CANCELLED': 'CANCELLED',
        'ОТМЕНЁН': 'CANCELLED',
        'RETURNED': 'RETURNED',
        'ВОЗВРАЩЁН': 'RETURNED',
    }

    # Маппинг статусов отправлений
    SHIPMENT_STATUS_MAPPING = {
        'PREPARING': 'PREPARING',
        'ПОДГОТОВКА': 'PREPARING',
        'IN_TRANSIT': 'IN_TRANSIT',
        'В ПУТИ': 'IN_TRANSIT',
        'AT_WAREHOUSE': 'AT_WAREHOUSE',
        'НА СКЛАДЕ': 'AT_WAREHOUSE',
        'OUT_FOR_DELIVERY': 'OUT_FOR_DELIVERY',
        'У КУРЬЕРА': 'OUT_FOR_DELIVERY',
        'DELIVERED': 'DELIVERED',
        'ДОСТАВЛЕН': 'DELIVERED',
        'FAILED': 'FAILED',
        'НЕ ДОСТАВЛЕН': 'FAILED',
        'RETURNED': 'RETURNED',
        'ВОЗВРАТ': 'RETURNED',
    }

    # Маппинг категорий товаров
    PRODUCT_CATEGORY_MAPPING = {
        'ELECTRONICS': 'ELECTRONICS',
        'ЭЛЕКТРОНИКА': 'ELECTRONICS',
        'CLOTHING': 'CLOTHING',
        'ОДЕЖДА': 'CLOTHING',
        'HOME_GARDEN': 'HOME_GARDEN',
        'ДОМ И САД': 'HOME_GARDEN',
        'BEAUTY': 'BEAUTY',
        'КРАСОТА': 'BEAUTY',
        'SPORTS': 'SPORTS',
        'СПОРТ': 'SPORTS',
        'BOOKS': 'BOOKS',
        'КНИГИ': 'BOOKS',
        'KIDS': 'KIDS',
        'ДЕТСКИЕ ТОВАРЫ': 'KIDS',
        'FOOD': 'FOOD',
        'ПРОДУКТЫ': 'FOOD',
    }

    # Маппинг способов оплаты
    PAYMENT_METHOD_MAPPING = {
        'CARD_ONLINE': 'CARD_ONLINE',
        'КАРТА ОНЛАЙН': 'CARD_ONLINE',
        'CARD_ON_DELIVERY': 'CARD_ON_DELIVERY',
        'КАРТА ПРИ ПОЛУЧЕНИИ': 'CARD_ON_DELIVERY',
        'CASH': 'CASH',
        'НАЛИЧНЫЕ': 'CASH',
        'SBP': 'SBP',
        'СБП': 'SBP',
        'EWALLET': 'EWALLET',
        'ЭЛЕКТРОННЫЙ КОШЕЛЁК': 'EWALLET',
        'CREDIT': 'CREDIT',
        'РАССРОЧКА': 'CREDIT',
    }

    # Маппинг типов ТС
    VEHICLE_TYPE_MAPPING = {
        'VAN': 'VAN',
        'ФУРГОН': 'VAN',
        'TRUCK_SMALL': 'TRUCK_SMALL',
        'МАЛЫЙ ГРУЗОВИК': 'TRUCK_SMALL',
        'TRUCK_MEDIUM': 'TRUCK_MEDIUM',
        'СРЕДНИЙ ГРУЗОВИК': 'TRUCK_MEDIUM',
        'TRUCK_LARGE': 'TRUCK_LARGE',
        'БОЛЬШОЙ ГРУЗОВИК': 'TRUCK_LARGE',
        'MOTORCYCLE': 'MOTORCYCLE',
        'МОТОЦИКЛ': 'MOTORCYCLE',
    }


etl_config = ETLConfig()