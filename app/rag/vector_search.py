
import os
from .embedding import get_embeding , cosine_similarity
import json
import requests
from llm.config import URL , OPENROUTER_API_KEY , MODEL_NAME_META_70


BASE_DIR = os.path.dirname(os.path.abspath(__file__))   
DATA_PATH = os.path.join(BASE_DIR, "embeding_test.json")


SIM_THRESHOLD = 0.4
# def find_best_city_or_none(user_question: str):
#     query_embedding = get_embeding(user_question)

#     db = json.load(open(DATA_PATH, "r", encoding="utf-8"))


#     if isinstance(db, list):
#         db = {item["city"]: item for item in db}

#     best_city = None
#     best_score = -1


#     for city, data in db.items():

#         score = cosine_similarity(query_embedding, data["embedding"])

#         print(f"{city}: {score}")   

#         if score > best_score:
#             best_score = score
#             best_city = city

#     if best_score < SIM_THRESHOLD:
#         return None

#     return best_city



def llm_select_best_city(user_profile, candidates):
    """
    candidates = [
        (city_name, score, context_text)
    ]
    """

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    # ساخت متن شهرهای کاندیدا
    cities_block = ""
    for city, score, text in candidates:
        print(f"City: {city}\nScore: {score}")
        cities_block += f"City: {city}\nScore: {score}\nInfo: {text}\n\n"

    system = """
You are a senior travel recommendation engine.

Your task:
- Evaluate each candidate city based on the USER PROFILE.
- DO NOT rely only on the similarity score.
- Score each candidate from 0 to 100 based on:

  * Interest match
  * Budget match
  * Travel duration fit
  * Travel style fit
  * Season/climate suitability (if mentioned)
  * Cultural/nature/food alignment

Rules:
- After scoring all cities, choose ONLY the city with the highest score.
- Return ONLY the city name.
You MUST return ONLY the name of the city.
No explanations.
No scoring details.
No extra text.
No newlines.
"""

    user = f"""
USER PROFILE:
{user_profile}

CANDIDATE CITIES (from RAG):
{cities_block}

Now:
1. Score each city using the criteria.
2. Select ONLY the highest scoring city.
3. Return ONLY the city name.
"""

    payload = {
        "model": MODEL_NAME_META_70,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]
    }

    r = requests.post(URL, headers=headers, json=payload)
    result = r.json()["choices"][0]["message"]["content"]

    return result.strip()