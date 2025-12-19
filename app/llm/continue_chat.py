from .config import MODEL_NAME_META_70 , OPENROUTER_API_KEY , URL
import json
import requests
from state.memory import history


def get_city_plan(best_city):
    with open("llm/cities_embeddings_new.json" , "r" , encoding="utf-8") as f:
        plans = json.load(f)

        for plan in plans:
            if plan["city"] == best_city:
                return plan["text"]

    return None 


def continue_chat(best_city , user_message):
    global history


    city_plan_text = get_city_plan(best_city)
    
    if city_plan_text is None:
        return "متأسفانه برای این شهر هنوز برنامه سفری ندارم."
    
    messages = [
        {
            "role": "system",
            "content": """
You are a professional AI travel assistant.

You are given a detailed travel document for a city.
Use ONLY this document to create a travel plan.
Do not invent places not mentioned in the document.
Speak in Persian.
"""
        }
    ]

    messages += history

    messages.append({
        "role": "user",
        "content": f"""
        City: {best_city}

        Travel document:
        {city_plan_text}

        User request:
        {user_message}

        Please create a practical travel plan.
        """
    })


    
    payload = {
        "model": MODEL_NAME_META_70,
        "messages": messages
    }

    res = requests.post(URL, headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }, json=payload)

    if res.status_code != 200:
        return f"Error: {res.text}"

    reply = res.json()["choices"][0]["message"]["content"]

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})


    return reply