from sentence_transformers import SentenceTransformer


MODEL_NAME = 'ai-forever/sbert_large_mt_nlu_ru'
# Загружаем модель один раз при старте приложения
model = SentenceTransformer(MODEL_NAME)

def vectorize_documents(documents):
    result = []
    for doc in documents:
        text = doc.get("text")
        if not text:
            continue
        vector = model.encode(text).tolist()
        doc["text_vector"] = vector
        result.append(doc)
    return result