import os
import requests
import json
import numpy as np
import sys
from test_weather_api import get_weather_data_test

OPENROUTER_API_KEY = "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"
JINA_API_KEY = "jina_7fedde13af3440c88d1cad18c001c003y14JgGjTbn-LcR3M2h2rOcLT82sI"
SYSTEM_PROMPT = """
You are a professional **Travel Assistant AI**, specialized in **Iranian cities and domestic tourism**.

Your responsibilities:
- Provide accurate and practical travel information about Iranian destinations.
- Suggest must-see places, activities, foods, and cultural highlights.
- Provide approximate travel costs, transportation options, distances, and best travel seasons.
- Always ask clarifying questions if the user request is incomplete or ambiguous.
- Prefer information coming from RAG (retrieved documents) over your own guesses.
- Create structured travel plans (e.g., Day 1, Day 2, etc.) when the user requests trip planning.

Critical Rules:
1. **Never hallucinate.** If you are unsure say: "اطلاعات دقیقی درباره این موضوع ندارم."
2. **Never invent locations, distances, or historical facts.**
3. **Only answer travel-related questions.**
4. If the user asks something unrelated to travel → politely redirect them back to travel topics.
5. Keep your tone friendly, clear, and concise.
6. When giving recommendations, include short reasons (why it’s good).
7. If multiple answers are possible, ask a short clarifying question first.

Response Style:
- Use short paragraphs.
- Prefer Persian (Farsi) unless the user requests English.
- Provide structured, useful answers (lists are fine).

Your purpose:
Help the user plan their trip smoothly and realistically.
"""



MODEL_NAME = "meta-llama/llama-3.3-70b-instruct:free"
# MODEL_NAME = "nousresearch/hermes-3-llama-3.1-405b:free"
MODEL_EMBEDING_NAME = "openai/text-embedding-3-small"    
MODEL_EMBEDING_NAME_JINA = "jina-embeddings-v3"
# MODEL_NAME = 'deepseek/deepseek-chat-v3-0324:free'
#meta-llama/llama-3.3-70b-instruct:free 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
# meta-llama/llama-3.3-70b-instruct:free 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 for 
history = []  # chat history

def ask_model(context: str, message: str, best_city: str) -> str:
    global history

    weather = get_weather_data_test(best_city)
    print(f"weather {best_city} is {weather}")

    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    assistant_prompt = f"""
Follow all instructions **strictly** and do not add any external information.

1) You must answer **only based on the following context** and nothing else:
---
{context}
---
Do NOT use outside knowledge, assumptions, or general facts.

2) You must talk **only about the city: {best_city}**.
Do NOT mention, compare, or refer to any other city.

3) All output must be **in Persian (Farsi)**.

4) At the end of your answer, add this sentence:
"آب‌وهوای فعلی {best_city}: {weather}"

5) Do NOT add any unrelated details. Stay strictly within the given context.

6) After explaining about the city, you must ask the user a few **travel-related questions** specifically about visiting {best_city}.

7) After your questions, also ask:
"بودجه تقریبی شما برای این سفر چقدر است؟ در صورتی که مایل باشید بودجه خود را بگویید تا برنامه دقیق‌تری ارائه کنم. اما اگر نخواستید بودجه را اعلام کنید، باز هم برنامه سفر را برایتان پیشنهاد می‌کنم."

8) Never answer or ask anything outside the scope of travel to {best_city}.
"""

    # ساخت پیام‌ها (system + assistant_defaults + history + new message)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "assistant", "content": assistant_prompt},
    ]

    # اضافه کردن تاریخچه مکالمه (این مهم‌ترین بخشه)
    messages += history

    # پیام جدید کاربر
    messages.append({"role": "user", "content": message})

    payload = {
        "model": MODEL_NAME,
        "messages": messages
    }

    res = requests.post(url, headers=headers, json=payload)

    if res.status_code != 200:
        return f"Error: {res.text}"

    reply = res.json()["choices"][0]["message"]["content"]

    # ذخیره مکالمه در حافظه
    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})

    return reply

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_embeding(text:str):
    url = "https://api.jina.ai/v1/embeddings"

    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "Content-Type": "application/json"
    }

    data={"model" : MODEL_EMBEDING_NAME_JINA , "input" :[text] , "task": "text-matching"}

    response = requests.post(url , headers=headers , json=data)
    response_json = response.json()

    try:
        return response_json["data"][0]["embedding"]
    except KeyError:
        print("ERROR :" ,response_json)
        return None
    
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



def ask_model_fallback(message: str) -> str:
    global history

    url = "https://openrouter.ai/api/v1/chat/completions"

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
        "model": MODEL_NAME,
        "messages": messages
    }

    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        return f"Error: {res.text}"

    reply = res.json()["choices"][0]["message"]["content"]

    history.append({"role": "user", "content": message})
    history.append({"role": "assistant", "content": reply})

    return reply

def rag_answer(user_question):

    best_city = find_best_city_or_none(user_question)

    if best_city is None:
        return ask_model_fallback(user_question)

    db = json.load(open(DATA_PATH, "r", encoding="utf-8"))
    if isinstance(db, list):
        db = {item["city"]: item for item in db}

    city_context = db[best_city]["text"]

    return ask_model(city_context, user_question, best_city)


    





