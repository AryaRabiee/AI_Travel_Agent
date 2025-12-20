from .config import MODEL_NAME_META_70 , OPENROUTER_API_KEY , URL
import json
import requests
from state.memory import history

def user_want_plan(message):
    msg = message.strip().lower()
    return msg in ['باشه',"بده","اره","بله","یه پلن بده","اره میخوام پلن بدی","پلن میخوام","باشه بده","مایل هستم","آره","yes"]




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
            "content": f"""
You are a professional AI travel assistant.

You are given a detailed travel document for a city.
Use ONLY this document to answer the user.
Do NOT invent places, activities, or details not mentioned in the document.

Language:
- Always speak in Persian.

Rules:
1. ONLY create a full, day-by-day travel plan if the user EXPLICITLY asks for a travel plan.
   Examples:
   - "برنامه سفر بده"
   - "پلن سفر می‌خوام"
   - "برام برنامه بچین"

2. If the user asks a QUESTION about the existing plan
   (for example: budget, duration, style, city name, or explanation),
   answer ONLY that question briefly.
   Do NOT repeat the full travel plan.

3. If the user asks to MODIFY the plan
   (for example: cheaper, shorter, more luxury),
   create a revised travel plan using ONLY the given document.

4. If the user asks for the travel plan AGAIN explicitly,
   then provide the full travel plan again.

5. If the question is NOT about travel planning,
   answer politely and briefly, without mentioning the plan.

Be precise, concise, and helpful.
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