import os
import requests
import json
import numpy as np
import sys
from utils.weather import get_weather_data
from rag.embedding import cosine_similarity , get_embeding
from rag.vector_search import  DATA_PATH , llm_select_best_city
from .prompts import SYSTEM_PROMPT , ASISTANT_PROMPTS
from .config import MODEL_NAME_META_70 , OPENROUTER_API_KEY , URL
from state.travel_related import is_travel_related
from state.memory import history
from state.handle_user import handle_user_message
from rag.retrieval import retrieve_top_cities

def ask_model(context: str, message: str, best_city: str) -> str:
    global history

    weather = get_weather_data(best_city)
    print(f"weather {best_city} is {weather}")

    url = URL

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    assistant_prompt = ASISTANT_PROMPTS

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": assistant_prompt},
    ]

    messages += history

    messages.append({"role": "user", "content": message})

    payload = {
        "model": MODEL_NAME_META_70,
        "messages": messages
    }

    res = requests.post(url, headers=headers, json=payload)

    if res.status_code != 200:
        return f"Error: {res.text}"

    reply = res.json()["choices"][0]["message"]["content"]

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})

    return reply


def ask_model_fallback(message: str) -> str:
    global history

    url = URL

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content":
            "You are a friendly Persian assistant.\n"
            "You may use your general knowledge.\n"
            "Be helpful and answer naturally.\n"
            "If user asks for specific city info you don’t know, say:\n"
            "«اطلاعات دقیقی از این موضوع ندارم»"
        }
    ]

    messages += history

    messages.append({"role": "user", "content": message})

    payload = {
        "model": MODEL_NAME_META_70,
        "messages": messages
    }

    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        return f"Error: {res.text}"

    reply = res.json()["choices"][0]["message"]["content"]

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})

    return reply

def rag_answer(message):
    user_profile = handle_user_message(message)
    if not isinstance(user_profile, dict):
        print("Profile NOT complete — sending question:", user_profile)
        return user_profile 
    candidates = retrieve_top_cities(user_profile)
    best_city = llm_select_best_city(message, candidates)
    return best_city

    # best_city = find_best_city_or_none(user_question)

    # if best_city is None:
    #     return ask_model_fallback(user_question)

    # db = json.load(open(DATA_PATH, "r", encoding="utf-8"))
    # if isinstance(db, list):
    #     db = {item["city"]: item for item in db}

    # city_context = db[best_city]["text"]

    # return ask_model(city_context, user_question, best_city)