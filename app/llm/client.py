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
from CBF_Recommendation.model_weight import get_weight_for_feature
from CBF_Recommendation.recommandation_score import top_city
from .continue_chat import continue_chat , user_want_plan

conversation_state = {
    "phase": "INIT",  
    # INIT
    # CITY_ANNOUNCED
    # WAITING_FOR_PLAN_CONFIRM
    # PLANNING
    # FREE_CHAT
    "best_city": None
}



def ask_model(best_city: str) -> str:
    global history, conversation_state

    messages = [
        {
            "role": "system",
            "content": """
You are a professional AI travel assistant.
Speak Persian.
Explain briefly why the city fits the user.
Ask if they want a travel plan.
"""
        },
        {
            "role": "assistant",
            "content": f"""
بهترین شهر برای سفر شما **{best_city}** 🌍  
این شهر با توجه به علایق و شرایطی که گفتید انتخاب مناسبی برای شماست.

اگر دوست دارید، می‌تونم براتون یک برنامه سفر کامل هم آماده کنم. مایل هستید؟
"""
        }
    ]

    history.extend(messages)
    conversation_state["phase"] = "WAITING_FOR_PLAN_CONFIRM"

    return messages[-1]["content"]

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

def detect_intent(message):
    plan_keywords = ["برنامه", "پلن سفر", "سفر بچین"]
    question_keywords = ["بودجه", "چند روز", "کجا", "اسم شهر"]
    
    if any(k in message for k in plan_keywords):
        return "PLAN_REQUEST"
    # elif any(k in message for k in question_keywords):
    #     return "PLAN_QUESTION"
    else:
        return "FREE_CHAT"



best_city = None
def rag_answer(user_message):
    global history, best_city , conversation_state
    intent = detect_intent(user_message)

    print("State now is :" , conversation_state["phase"])
    print("intent now is :" , intent)


    if conversation_state["phase"] == "INIT":
        result = top_city(user_message)
        if result["need_more_info"]:
            return result["message"]
        best_city = result["top_city"]
        print(best_city)
        conversation_state["best_city"] = best_city
        conversation_state["phase"] = "WAITING_FOR_PLAN_CONFIRM"
        return ask_model(best_city)

    if conversation_state["phase"] == "WAITING_FOR_PLAN_CONFIRM":
        if user_want_plan(user_message):
            conversation_state["phase"] = "PLANNING"
            return continue_chat(conversation_state["best_city"], "برنامه سفر لطفاً")
        else:
            conversation_state["phase"] = "FREE_CHAT"
            return ask_model_fallback(user_message)


    # if conversation_state["phase"] == "PLANNING":
    #     return continue_chat(conversation_state["best_city"], user_message)
    return ask_model_fallback(user_message)
    
    # user_profile = handle_user_message(message)
    # if not isinstance(user_profile, dict):
    #     print("Profile NOT complete — sending question:", user_profile)
    #     return user_profile 
    # candidates = retrieve_top_cities(user_profile)
    # best_city = llm_select_best_city(message, candidates)
    # return best_city

    # best_city = find_best_city_or_none(user_question)

    # if best_city is None:
    #     return ask_model_fallback(user_question)

    # db = json.load(open(DATA_PATH, "r", encoding="utf-8"))
    # if isinstance(db, list):
    #     db = {item["city"]: item for item in db}

    # city_context = db[best_city]["text"]

    # return ask_model(city_context, user_question, best_city)