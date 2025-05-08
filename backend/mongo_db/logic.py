from init import get_db
from datetime import datetime, timedelta
from config import DB_NAMES

#создание новой коллекции для нового тг канала который не парсился с занесением сразу json-file
def add_collection(db_name, collection_name, json_data):
    db = get_db(db_name)
    if collection_name in db.list_collection_names():
        return f"Коллекция {collection_name} уже существует в базе {db_name}."
    collection = db[collection_name]
    if isinstance(json_data, list):
        collection.insert_many(json_data)
    else:
        collection.insert_one(json_data)
    return f"Коллекция {collection_name} создана и данные добавлены в базе {db_name}."

#закидывание в коллекцию новой информации

def insert_json(db_name, collection_name, json_data):
    db = get_db(db_name)
    collection = db[collection_name]
    if isinstance(json_data, list):
        result = collection.insert_many(json_data)
    else:
        result = collection.insert_one(json_data)
    return f"Добавлено {len(result.inserted_ids) if hasattr(result, 'inserted_ids') else 1} записей в базу {db_name}."

# получение данных для дальнейшней обработки из колеккци
def get_data(db_name, collection_name, filter_query=None):
    db = get_db(db_name)
    collection = db[collection_name]
    cursor = collection.find(filter_query or {}, {"_id": 0})
    return list(cursor)




def check_collection_status(db_name, collection_name, start_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    today = datetime.today().date()

    if db_name not in DB_NAMES:
        return {"status": "invalid_db", "message": f"БД {db_name} не разрешена."}

    db = get_db(db_name)

    if collection_name not in db.list_collection_names():
        return {
            "status": "not_found",
            "message": "Коллекция не найдена. Запуск дальнейших процессов..."
        }

    collection = db[collection_name]
    docs = list(collection.find())

    if not docs:
        return {"status": "empty_collection", "message": "Коллекция существует, но пуста."}

    date_field = "date"
    available_dates = set()

    for doc in docs:
        if date_field not in doc:
            continue

        raw_date = doc[date_field]

        try:
            if isinstance(raw_date, str):
                parsed_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
            elif isinstance(raw_date, datetime):
                parsed_date = raw_date.date()
            else:
                continue

            available_dates.add(parsed_date)
        except Exception as e:
            print(f"[!] Ошибка при обработке даты: {raw_date} — {e}")

    if not available_dates:
        return {"status": "no_date_field", "message": "Нет корректных полей даты в документах."}

    # Генерация всех ожидаемых дат
    expected_dates = [start_date + timedelta(days=i) for i in range((today - start_date).days + 1)]
    missing = sorted([d for d in expected_dates if d not in available_dates])

    if not missing:
        return {"status": "ok", "message": "Все данные на месте."}

    # Разбиваем подряд идущие даты в интервалы
    missing_ranges = []
    range_start = missing[0]

    for i in range(1, len(missing)):
        if (missing[i] - missing[i - 1]).days > 1:
            missing_ranges.append({
                "missing_from": range_start.strftime("%Y-%m-%d"),
                "missing_to": missing[i - 1].strftime("%Y-%m-%d")
            })
            range_start = missing[i]

    # Добавляем последний диапазон
    missing_ranges.append({
        "missing_from": range_start.strftime("%Y-%m-%d"),
        "missing_to": missing[-1].strftime("%Y-%m-%d")
    })

    return {"status": "missing_data", "missing_ranges": missing_ranges}
