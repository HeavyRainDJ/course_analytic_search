import pytest
import requests
from bson import ObjectId
from api_handlers.api_tg_stat.hand_posts import fetch_all_tgstat_data
# как он мутит энкодинг
BASE_URL = "http://127.0.0.1:5000"

# Функция сериализации для ObjectId
def json_serializer(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    raise TypeError("Type not serializable")

# Упрощённый геттер с безопасной JSON-обработкой
def get_json_response(url, **kwargs):
    try:
        response = requests.get(url, **kwargs)
        status_code = response.status_code
        print(response)
        try:
            data = response.json()  # Попытка разобрать JSON-ответ
        except Exception:
            # Если не удалось разобрать JSON, возвращаем ошибку в структурированном формате
            data = {"error": "Ошибка при разборе JSON ответа"}

        # Структурированный формат данных, аналогичный MongoDB
        return status_code, {"data": data, "status": status_code}

    except requests.exceptions.RequestException as e:
        # В случае ошибок соединения, возвращаем ошибку в структурированном формате
        return 500, {"error": f"Request failed: {str(e)}", "status": 500}
def get_clean_json_response(url, **kwargs):
    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()  # выбросит исключение при 4xx/5xx

        return response.json()  # Просто возвращаем json-ответ

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []  # или None, или {"error": "..."} — как тебе удобнее
