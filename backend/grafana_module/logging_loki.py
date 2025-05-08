import os
import json
from datetime import datetime, timedelta

def save_posts_to_log(tg_name, posts):
    log_dir = os.path.join(os.path.dirname(__file__), "..", "logs", "telegram_parsed")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{tg_name}.log")

    with open(log_path, "a", encoding="utf-8") as f:
        for i, post in enumerate(posts):
            try:
                # создаем уникальный timestamp
                ts = datetime.strptime(post["date"], "%Y-%m-%d") + timedelta(seconds=i * 5)
                post["timestamp"] = ts.isoformat()  # не обязательно, просто для логов
            except Exception as e:
                print(f"[!] Пропущено: {e}")
                continue

            f.write(json.dumps(post, ensure_ascii=False) + "\n")
