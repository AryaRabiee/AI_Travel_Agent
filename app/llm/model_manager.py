from litellm import completion
import json
from .config import MODEL_NAME_HERMAS , MODEL_NAME_META_70 , OPENROUTER_API_KEY
from state.memory import history
from state.memory import conversation_state_memory
api = "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"
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

def call_llm(primary_model, backup_model, messages):
    resp = completion(model=primary_model ,api_key=api, messages = messages)
    return resp["choices"][0]["message"]["content"]

def call_llm_with_fallback(primary_model, backup_model, messages):
    resp = completion(
        model=primary_model,
        fallbacks=[backup_model],
        api_key=api,
        messages=messages,
        num_retries = 2
    )
    
    return resp.choices[0].message.content.strip()


def intent_agent(user_message):
    messages = [
                {"role": "system", "content": """
        You are a travel assistant classifier.
        Classify the user's message into one of three categories:
        - 'Yes' if the message is about travel.
        - 'SMALLTALK' if the message is just greetings or casual conversation (hello, how are you, etc.).
        - 'No' if the message is not related to travel.

        Reply with ONLY one of these three keywords: Yes, SMALLTALK, No.
        """},
        {"role": "user", "content": f"what do you think about this user's message? {user_message}"},
    ]
    return call_llm_with_fallback("openrouter/meta-llama/llama-3.3-70b-instruct:free", "openrouter/nousresearch/hermes-3-llama-3.1-405b:free", messages).strip().lower()



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

    result = call_llm_with_fallback("openrouter/openai/gpt-oss-120b:free","openrouter/meta-llama/llama-3.3-70b-instruct:free",messages)
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

    res = call_llm_with_fallback("nousresearch/hermes-3-llama-3.1-405b:free","openrouter/meta-llama/llama-3.3-70b-instruct:free",messages)
    # if res.status_code != 200:
    #     return f"Error: {res.text}"

    reply = res.json()["choices"][0]["message"]["content"]

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": reply})

    
    return reply


def fall_back(user_message):
    global history



    messages = [
        {"role": "system", "content":
            f"""
        You are a Travel assistant.
        Answer in a friendly Persian tone.
        Be helpful and natural.
        Use your knowledge only to answer questions about travel, cities, itineraries, or related topics.
        If the user asks for specific city info you don't know, respond:
        «اطلاعات دقیقی از این موضوع ندارم»
        If the user's {user_message} is not related to travel, respond:
        «من فقط یک دستیار سفر هستم و نمی‌توانم به این سوال پاسخ بدهم»
        but if the user's {user_message} want to know about some city asnwer his question
        and if the user's want to collabrate and  talk to you just like(hello , how are you? ...) answer his question friendly dont talk about travel just answer
        Do not invent information unrelated to travel.

            """


        }
    ]

    messages += history

    messages.append({"role": "user", "content": user_message})


    res = call_llm_with_fallback("openrouter/meta-llama/llama-3.3-70b-instruct:free","openrouter/meta-llama/llama-3.3-70b-instruct:free",messages)
    print(res , type(res))
    # if res.status_code != 200:
    #     return f"Error: {res.text}"

    # reply = res.json()["choices"][0]["message"]["content"]

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": res})

    return res



def detect_intent(user_message):
    messages = [
        {"role": "system", "content":
         "Classify user intent. Reply ONLY with one word: SMALLTALK, TRAVEL, OFFTOPIC"},
        {"role": "user", "content": user_message}
    ]
    res = call_llm_with_fallback("openrouter/meta-llama/llama-3.3-70b-instruct:free","openrouter/meta-llama/llama-3.3-70b-instruct:free", messages)
    return res.strip().upper()



def chat(user_message):
    global history

    a = False

    messages = [
        {"role": "system", "content":
            f"""
You are a friendly Persian-speaking Travel Assistant. Follow these rules carefully:

1. **Travel Start Question (only once per conversation):**
   - Only ask this question **if and only if** the user clearly shows interest in travel, cities, or destinations.  
   - Ask exactly once per conversation:  
     "میخواین با چند سوال، بهترین شهر برای سفرتون رو بهتون پیشنهاد بدم؟"
   - **Do not include any extra text, explanation, or greeting** with this question.  
   - **Never ask this question more than once.**
   - After asking, **stop and wait for the user's answer**. Do not continue the conversation, give suggestions, or interpret the answer. The backend system will handle the user's reply.

2. **Smalltalk and General Conversation:**
   - Respond naturally and friendly in Persian for casual chat.  
   - Do not force travel content.  

3. **Travel Information Questions:**
   - Answer accurately about cities, destinations, or travel information.  
   - If you don’t know the answer, respond: "اطلاعات دقیقی از این موضوع ندارم."  

4. **Non-Travel Questions:**
   - Politely respond: "من فقط یک دستیار سفر هستم و نمی‌توانم به این سوال پاسخ بدهم."  

5. **Important Behavior Rules:**
   - Never invent information unrelated to travel.  
   - Maintain a friendly Persian tone.  
   - Only ask the start question **once per conversation**, and only when the conversation clearly goes toward travel.  
   - After asking, wait for the user to respond. Do not continue chatting or take any action until the backend processes the user's answer.  

**Goal:** Ensure that whenever the conversation clearly indicates interest in travel or cities, the model asks **exactly once**:  
"میخواین با چند سوال، بهترین شهر برای سفرتون رو بهتون پیشنهاد بدم؟"  
No extra messages or explanations should be included. After asking, **pause completely** and let the backend handle the user's reply. Handle smalltalk and travel information naturally in all other cases.







            """


        }
    ]

    messages += history

    messages.append({"role": "user", "content": user_message})


    res = call_llm_with_fallback("openrouter/openai/gpt-oss-120b:free","openrouter/meta-llama/llama-3.3-70b-instruct:free",messages)
    print(res , type(res))
    # if res.status_code != 200:
    #     return f"Error: {res.text}"

    # reply = res.json()["choices"][0]["message"]["content"]

    history.append({"role": "user", "content": user_message})
    history.append({"role": "assistant", "content": res})

    return res