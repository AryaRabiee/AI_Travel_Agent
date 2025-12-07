import os
from .embedding import get_embeding , cosine_similarity
import json


BASE_DIR = os.path.dirname(os.path.abspath(__file__))   
DATA_PATH = os.path.join(BASE_DIR, "embeding_test.json")


SIM_THRESHOLD = 0.4
def find_best_city_or_none(user_question: str):
    query_embedding = get_embeding(user_question)

    db = json.load(open(DATA_PATH, "r", encoding="utf-8"))


    if isinstance(db, list):
        db = {item["city"]: item for item in db}

    best_city = None
    best_score = -1


    for city, data in db.items():

        score = cosine_similarity(query_embedding, data["embedding"])

        print(f"{city}: {score}")   

        if score > best_score:
            best_score = score
            best_city = city

    if best_score < SIM_THRESHOLD:
        return None

    return best_city