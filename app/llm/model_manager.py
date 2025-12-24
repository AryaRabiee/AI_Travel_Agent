from litellm import completion
import json
from .config import MODEL_NAME_HERMAS , MODEL_NAME_META_70 , OPENROUTER_API_KEY
from state.memory import history
from state.memory import conversation_state
# from llm.continue_chat import get_city_plan
def get_city_plan(best_city):
    with open("llm/cities_embeddings_new.json" , "r" , encoding="utf-8") as f:
        plans = json.load(f)

        for plan in plans:
            if plan["city"] == best_city:
                return plan["text"]

    return None 
MODELS = {
    "intent_primary":MODEL_NAME_META_70,
    "intent_backup":MODEL_NAME_HERMAS,
    "is_related":MODEL_NAME_META_70,
    "ask_model":MODEL_NAME_META_70,
    "free_chat":MODEL_NAME_HERMAS,
    "City":MODEL_NAME_META_70,
    "plan":MODEL_NAME_HERMAS
}

def call_llm(model_name , messages):
    resp = completion(model=model_name ,api_key=OPENROUTER_API_KEY, messages = messages)
    return resp["choices"][0]["message"]["content"]

def try_fall_back(primary_model, backup_model, messages):
    try:
        return call_llm(model_name=primary_model , messages=messages)
    except Exception as e:
        print(f"Primary model failed: {e}, using backup...")
        return call_llm(model_name=backup_model , messages=messages)


def intent_agent(user_message):
    messages = [
        {"role": "system", "content": "You are a classifier. Reply ONLY with 'Yes' or 'No'."},
        {"role": "user", "content": f"Is the following message about travel? {user_message}"}
    ]
    return try_fall_back("openrouter/meta-llama/llama-3.3-70b-instruct:free", "nousresearch/hermes-3-llama-3.1-405b:free", messages).strip().lower()



def city_agent(user_profile , candidates):

    cities_block = ""
    for city, score, text in candidates:
        print(f"City: {city}\nScore: {score}")
        cities_block += f"City: {city}\nScore: {score}\nInfo: {text}\n\n"


    system = """
You are a travel recommendation re-ranking engine.

Input:
- User profile
- Candidate cities
- Algorithm score (primary)
- Context information (secondary)

Rules:
- Use the algorithm score as the primary signal.
- You may adjust each city score by at most ±10% based on semantic fit.
- Rank all cities based on adjusted score.
- Return ALL the city with score.
- OUTPUT FORMAT MUST BE a JSON object: { "city_name": score, ... }
- Do NOT include any extra text or explanation.
"""

    user = f"""
USER PROFILE:
{user_profile}

CANDIDATE CITIES (from RAG):
{cities_block}

"""
    messages= [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]

    result = try_fall_back("openrouter/meta-llama/llama-3.3-70b-instruct:free", "nousresearch/hermes-3-llama-3.1-405b:free", messages)
    print("result in model manager" , result , "The type is:" , type(result))
    try:
        top_cities = json.loads(result)
    except json.JSONDecodeError:
        print("خطا: خروجی LLM JSON معتبر نیست!")
        print("RAW OUTPUT:", result)
        return None

    return top_cities

def plan_agent(best_city, user_message,):
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

    res = try_fall_back("nousresearch/hermes-3-llama-3.1-405b:free","openrouter/meta-llama/llama-3.3-70b-instruct:free",messages)
    if res.status_code != 200:
        return f"Error: {res.text}"

    reply = res.json()["choices"][0]["message"]["content"]

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})

    
    return reply