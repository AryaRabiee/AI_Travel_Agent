
import os
from .embedding import get_embeding , cosine_similarity
import json
import requests
from llm.config import URL , OPENROUTER_API_KEY , MODEL_NAME_META_70
from llm.model_manager import city_agent


BASE_DIR = os.path.dirname(os.path.abspath(__file__))   
DATA_PATH = os.path.join(BASE_DIR, "rag/cities_embeddings_new.json")


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



# def llm_select_best_city(user_profile, candidates):
#     """
#     candidates = [
#         (city_name, score, context_text)
#     ]
#     """

#     headers = {
#         "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#         "Content-Type": "application/json",
#     }

#     cities_block = ""
#     for city, score, text in candidates:
#         print(f"City: {city}\nScore: {score}")
#         cities_block += f"City: {city}\nScore: {score}\nInfo: {text}\n\n"


    


#     system = """
#  Youare a travel recommendation re-ranking engine.

#  Inpt:
#  - Uer profile
#  - Cndidate cities
#  - Agorithm score (primary)
#  - Cntext information (secondary)

#  Ruls:
#  - Ue the algorithm score as the primary signal.
#  - Yu may adjust each city score by at most ±10% based on semantic fit.
#  - Rnk all cities based on adjusted score.
#  - Rturn ALL the city with score.
#  - OTPUT FORMAT MUST BE a JSON object: { "city_name": score, ... }
#  - D NOT include any extra text or explanation.
#  """
#     user = f"""
#  USE PROFILE:
#  {user_profile}

#  CANIDATE CITIES (from RAG):
#  {candidates}

#  """
#     payload = {
#         "model": MODEL_NAME_META_70,
#         "messages": [
#             {"role": "system", "content": system},
#             {"role": "user", "content": user},
#         ]
#     }

#     r = requests.post(URL, headers=headers, json=payload)
#     print("r in vector search is" , r , "The Type is" , type(r))
#     result = r.json()["choices"][0]["message"]["content"]
#     print("result in vector search is" , result , "The Type is" , type(result))
#     try:
#         top_cities = json.loads(result)
#     except json.JSONDecodeError:
#         print("خطا: خروجی LLM JSON معتبر نیست!")
#         print("RAW OUTPUT:", result)
#         return None

#     return top_cities

def llm_select_best_city(user_profile, candidates):

    response = city_agent(user_profile , candidates)
    return response