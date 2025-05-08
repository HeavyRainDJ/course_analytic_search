import requests
import json
from datetime import datetime, timedelta
from tools_for_data.json_cleaner import clean_json

def fetch_all_tgstat_data(channel_id, start_time=None, massive_time=None):
    all_posts = []
    seen_ids = set()
    limit = 50

    # Подготовка диапазонов времени
    if massive_time is None:
        if start_time is None:
            raise ValueError("Нужно указать либо start_time, либо massive_time")
        time_ranges = [{
            'missing_from': start_time,
            'missing_to': datetime.today().strftime('%Y-%m-%d')
        }]
    else:
        time_ranges = massive_time

    for time_range in time_ranges:
        date_start = datetime.strptime(time_range['missing_from'], "%Y-%m-%d").date()
        date_end = datetime.strptime(time_range['missing_to'], "%Y-%m-%d").date()

        print(f"\n>>> Обработка диапазона: {date_start} — {date_end}")

        current_date = date_start
        while current_date <= date_end:
            timestamp_start = int(datetime.combine(current_date, datetime.min.time()).timestamp())
            timestamp_end = int(datetime.combine(current_date + timedelta(days=1), datetime.min.time()).timestamp()) - 1

            url = (
                f"https://api.tgstat.ru/channels/posts?"
                f"token="
                f"&channelId={channel_id}"
                f"&limit={limit}&startTime={timestamp_start}&endTime={timestamp_end}"
                f"&hideForwards=0&hideDeleted=0"
            )

            try:
                response = requests.get(url)
                data = response.json()
            except Exception as e:
                print(f"[!] Ошибка запроса на {current_date}: {e}")
                current_date += timedelta(days=1)
                continue

            if "error" in data:
                print(f"[!] Ошибка на дату {current_date}: {data['error']}")
                current_date += timedelta(days=1)
                continue

            posts = data.get("response", {}).get("items", [])

            if posts:
                new_posts = [post for post in posts if post["id"] not in seen_ids]
                for post in new_posts:
                    seen_ids.add(post["id"])
                    all_posts.append(post)
                print(f"[{current_date}] Загружено {len(new_posts)} новых постов")
            else:
                # Добавляем маркер о пустом дне
                all_posts.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "status": "no_posts"
                })
                print(f"[{current_date}] Нет постов")

            current_date += timedelta(days=1)

    # Очистка
    all_posts = clean_json(all_posts, channel_id)

    if all_posts:
        with open(f"{channel_id}.json", "w", encoding="utf-8") as f:
            json.dump(all_posts, f, ensure_ascii=False, indent=4)
        print(f"\nГотово! Всего постов: {len(all_posts)}")
    else:
        print("\nНичего не загружено, файл не сохранён.")

    return all_posts  # ✅ возвращаем только список постов
