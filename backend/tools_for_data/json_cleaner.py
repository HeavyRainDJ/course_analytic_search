import re
from datetime import datetime

def clean_json(data, name_channel):
    result = {
        "db_name": "storage_parse",
        "name": f"{name_channel}",
        "data": []
    }

    for item in data:
        # Пропускаем "пустышки" с меткой "no_posts"
        if item.get("status") == "no_posts":
            continue

        # Проверяем и преобразуем timestamp → date
        try:
            formatted_date = datetime.utcfromtimestamp(item["date"]).strftime("%Y-%m-%d")
        except Exception as e:
            print(f"[!] Ошибка обработки даты: {item.get('date')} ({e})")
            continue

        clean_text = clean_html(item.get("text", ""))
        if not clean_text:
            continue

        formatted_entry = {
            "id": str(item["id"]),
            "text": clean_text,
            "date": formatted_date,
            "views": item["views"]
        }

        result["data"].append(formatted_entry)

    return result


def clean_html(raw_html):
    clean_text = re.sub(r'<[^>]+>', '', raw_html)  # Удаляет HTML-теги
    clean_text = re.sub(r'\s+', ' ', clean_text)   # Убирает переносы строк, табы и лишние пробелы
    return clean_text.strip()

def extract_tg_name(data):
    tg_name = data.get("tg_name", "")
    # Используем регулярное выражение для извлечения имени канала
    match = re.search(r't\.me/([a-zA-Z0-9_]+)', tg_name)
    if match:
        return match.group(1)
    return None

