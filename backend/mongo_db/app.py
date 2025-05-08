from flask import Flask, request, jsonify
from logic import add_collection, insert_json, get_data, check_collection_status
from embedder.embedding_model import vectorize_documents
from flask_cors import  CORS
from mongo_db.test_not_prod import get_json_response, get_clean_json_response
from api_handlers.api_tg_stat.hand_posts import fetch_all_tgstat_data
import requests
from grafana_module.logging_loki import save_posts_to_log
app = Flask(__name__)
CORS(app)


from tools_for_data.json_cleaner import extract_tg_name

@app.route("/add_collection", methods=["POST"])
def add_collection_route():
    data = request.json
    return jsonify({"message": add_collection(data["db_name"], data["name"], data.get("data", []))})

@app.route("/insert", methods=["POST"])
def insert_route():
    data = request.json
    return jsonify({"message": insert_json(data["db_name"], data["name"], data["data"])})

@app.route("/get_data", methods=["GET"])
def get_data_route():
    db_name = request.args.get("db_name")
    collection_name = request.args.get("collection")
    start_date = request.args.get("start_date")  # e.g., "2025-04-10"

    if not db_name or not collection_name:
        return jsonify({"error": "db_name and collection parameters are required"}), 400

    filter_query = {}
    if start_date:
        filter_query["date"] = {"$gte": start_date}

    data = get_data(db_name, collection_name, filter_query)
    return jsonify(data)  # Только массив данных


@app.route("/check_collection_status", methods=["GET"])
def check_collection_status_route():
    db_name = request.args.get("db_name")
    collection = request.args.get("collection")
    start_date = request.args.get("start_date")

    if not all([db_name, collection, start_date]):
        return jsonify({"error": "Отсутствуют параметры запроса"}), 400

    result = check_collection_status(db_name, collection, start_date)
    return jsonify(result)

@app.route("/vectorize_and_add_collection", methods=["POST"])
def vectorize_and_add_collection_route():
    data = request.json
    if not all(k in data for k in ("db_name", "name", "data")):
        return jsonify({"error": "db_name, name, and data fields are required."}), 400

    vectorized_data = vectorize_documents(data["data"])
    message = add_collection(data["db_name"], data["name"], vectorized_data)
    return jsonify({"message": message})


@app.route("/tgstat_pipeline", methods=["POST"])
def tgstat_pipeline():
    data = request.json
    start_date = data.get("start_date")
    tg_name = extract_tg_name(data)

    params_for_check = {
        "db_name": "storage_parse",
        "collection": tg_name,
        "start_date": start_date
    }

    status, response = get_json_response(f"http://127.0.0.1:5000/check_collection_status", params=params_for_check)
    print(status, response)

    status_check = response["data"].get("status")
    missing_data = response["data"].get("missing_ranges")

    # 🟠 1. Коллекция не найдена
    if status_check == 'not_found':
        data_tg_stat_api = fetch_all_tgstat_data(tg_name, start_date, None)

        if not data_tg_stat_api["data"]:
            return jsonify({
                "message": "Данные не получены. Канал не содержит постов за указанный диапазон.",
                "status": "no_new_data"
            }), 200

        response = requests.post(f"http://127.0.0.1:5000/add_collection", json=data_tg_stat_api)

        if response.status_code == 200:
            documents_to_vectorize = data_tg_stat_api["data"]
            payload = {
                "db_name": "storage_processing",
                "name": tg_name,
                "data": documents_to_vectorize
            }
            response = requests.post(f"http://127.0.0.1:5000/vectorize_and_add_collection", json=payload)

            if response.status_code == 200:
                raw_data = get_clean_json_response(
                    "http://127.0.0.1:5000/get_data",
                    params={"db_name": "storage_parse", "collection": tg_name, "start_date": start_date}
                )
                save_posts_to_log(tg_name,raw_data)
                return jsonify({"raw_data": raw_data, "status": "inserted"})
            else:
                return jsonify({"error": "Ошибка vectorize_and_add_collection"}), 500
        else:
            return jsonify({"error": "Ошибка загрузки данных в БД"}), 500

    # 🟢 2. Все данные на месте
    elif status_check == 'ok':
        raw_data = get_clean_json_response(
            "http://127.0.0.1:5000/get_data",
            params={"db_name": "storage_parse", "collection": tg_name, "start_date": start_date}
        )
        save_posts_to_log(tg_name, raw_data)
        return jsonify({"raw_data": raw_data, "status": "ok"})

    # 🟡 3. Есть пропущенные дни
    elif status_check == 'missing_data':
        data_tg_stat_api = fetch_all_tgstat_data(tg_name, None, missing_data)

        if not data_tg_stat_api["data"]:
            # 🔁 Вернуть то, что уже есть
            raw_data = get_clean_json_response(
                "http://127.0.0.1:5000/get_data",
                params={"db_name": "storage_parse", "collection": tg_name, "start_date": start_date}
            )
            return jsonify({
                "message": "Новых данных не найдено, но возвращены уже имеющиеся в БД.",
                "status": "partial_existing",
                "raw_data": raw_data
            }), 200

        # ✅ Есть новые данные — вставка
        response = requests.post(f"http://127.0.0.1:5000/insert", json=data_tg_stat_api)
        print(data_tg_stat_api, response)

        if response.status_code == 200:
            documents_to_vectorize = vectorize_documents(data_tg_stat_api["data"])
            payload = {
                "db_name": "storage_processing",
                "name": tg_name,
                "data": documents_to_vectorize
            }
            response = requests.post(f"http://127.0.0.1:5000/add_collection", json=payload)

            if response.status_code == 200:
                raw_data = get_clean_json_response(
                    "http://127.0.0.1:5000/get_data",
                    params={"db_name": "storage_parse", "collection": tg_name, "start_date": start_date}
                )
                save_posts_to_log(tg_name, raw_data)
                return jsonify({"raw_data": raw_data, "status": "updated"})
            else:
                return jsonify({"error": "Ошибка добавления обработанных данных"}), 500
        else:
            return jsonify({"error": "Ошибка вставки недостающих данных"}), 500

    # ❌ Неизвестный статус — fallback
    return jsonify({"error": "Неизвестный статус"}), 500


# ✅ Новый endpoint для получения векторизованных данных отдельно
@app.route("/get_processed_data", methods=["GET"])
def get_processed_data():
    db_name = request.args.get("db_name")
    collection = request.args.get("collection")
    start_date = request.args.get("start_date")

    if not db_name or not collection:
        return jsonify({"error": "db_name and collection parameters are required"}), 400

    try:
        result = get_clean_json_response(
            "http://127.0.0.1:5000/get_data",
            params={"db_name": db_name, "collection": collection, "start_date": start_date}
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
