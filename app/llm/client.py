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
from state.memory import history , conversation_state_memory , cities
from state.handle_user import handle_user_message
from rag.retrieval import retrieve_top_cities
from CBF_Recommendation.model_weight import get_weight_for_feature
from CBF_Recommendation.recommandation_score import top_city
from .travel_plan import places , user_want_plan
from state.route import route_user_message
from .model_manager import chat , plan_agent
from state.travel_question_step import next_travel_question
from state.state_user import user_profile
from state.validation import validation_answer
from llm.log import logger



QUESTIONS = [
    {"key": "days", "type": "number", "min": 1, "max": 30},
    {"key": "weather", "type": "enum", "values": ["گرم", "خنک", "سرد"]},
    {"key": "places", "type": "enum", "values": ["شهری", "طبیعت", "تاریخی"]},
    {"key": "budget", "type": "enum", "values": ["زیاد", "متوسط", "کم"]},
    {"key": "interests", "type": "enum", "values": ["طبیعت", "نفریح", "خرید"]},
    {"key": "description", "type": "description"},


]

# conversation_state = {
#     "phase": "INIT",  
#     # INIT
#     # CITY_ANNOUNCED
#     # WAITING_FOR_PLAN_CONFIRM
#     # PLANNING
#     # FREE_CHAT
#     "best_city": None
# }



def ask_model(best_city: str) -> str:
    global history, conversation_state_memory

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
    conversation_state_memory["phase"] = "WAITING_FOR_PLAN_CONFIRM"
    conversation_state["stage"] = "WAIT_FOR_PLAN"

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
            f"""
        You are a Travel assistant.
        Answer in a friendly Persian tone.
        Be helpful and natural.
        Use your knowledge only to answer questions about travel, cities, itineraries, or related topics.
        If the user asks for specific city info you don't know, respond:
        «اطلاعات دقیقی از این موضوع ندارم»
        If the user's {message} is not related to travel, respond:
        «من فقط یک دستیار سفر هستم و نمی‌توانم به این سوال پاسخ بدهم»
        but if the user's {message} want to know about some city asnwer his question
        and if the user's want to collabrate and  talk to you just like(hello , how are you? ...) answer his question
        Do not invent information unrelated to travel.

            """


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

# def detect_intent(message):
#     plan_keywords = ["برنامه", "پلن سفر", "سفر بچین"]
#     question_keywords = ["بودجه", "چند روز", "کجا", "اسم شهر"]
    
#     if any(k in message for k in plan_keywords):
#         return "WAIT_FOR_PLAN"
#     # elif any(k in message for k in question_keywords):
#     #     return "WAIT_FOR_PLAN"
#     else:
#         return "NORMAL"
# # def user_wants_new_city(message):
# #     keywords = ["شهر دیگه", "عوض کن", "یه شهر دیگه", "مقصد دیگه"]
# #     return any(k in message for k in keywords)


best_city = None




user_profile = {
    "is_travel": None,
    "step": 0,
    "days": None,
    "weather": None,
    "places": None,
    "budget": None,
    "interests": None,
    "description": None
}

conversation_state = {
    "WAITING_CONFIRMATION": False,
    "TRAVEL_MODEL": False,
    "WAIT":False,
    "CHOOSE_CITY":False,
    "WAIT_FOR_PLAN":False,
    "COLLECT_PROFILE":False,
    "NORMAL":True,
    "top_city":None

}

QUESTIONS = [
    {"key": "days", "type": "number", "min": 1, "max": 30},
    {"key": "weather", "type": "enum", "values": ["گرم", "خنک", "سرد"]},
    {"key": "places", "type": "enum", "values": ["شهری", "طبیعت", "تاریخی"]},
    {"key": "budget", "type": "enum", "values": ["کم", "متوسط", "زیاد"]},
    {"key": "interests", "type": "enum", "values": ["طبیعت", "تفریح", "خرید"]},
    {"key": "description", "type": "description"}
]

# def next_travel_question():
#     step = user_profile["step"]
#     if step < len(QUESTIONS):
#         q = QUESTIONS[step]
#         if q["type"] == "number":
#             return f"{q['key']}؟"
#         elif q["type"] == "enum":
#             return f"{q['key']}؟ ({', '.join(q['values'])})"
#         else:
#             return f"{q['key']}؟"
#     return None

def create_profile_v0(message):
    logger.info("start func create profile v0")
    user_profile_or_question = handle_user_message(message)
    if not isinstance(user_profile_or_question , dict):
        logger.info("user profile %s" , user_profile_or_question)
        logger.info("User profile incomplete, asking for more info...")
        return {"need_more_info": True, "message": user_profile_or_question}
    user_profile = user_profile_or_question
    logger.info("finish question and now the profile is %s" , user_profile)
    return {"need_more_info": False, "profile": user_profile}


# def rag_answer(user_message):
#     result = test(user_message)
#     if result["need_more_info"]:
#         return result["message"]
#     return True




    # profile_text = f"""
    #     days: {user_profile["profile"]['days']}
    #     weather: {user_profile["profile"]['weather']}
    #     places: {user_profile["profile"]['places']}
    #     budget: {user_profile["profile"]['budget']}
    #     interests: {user_profile["profile"]['interests']}
    #     description: {user_profile["profile"]['description']}
    #     """



def rag_answer(user_message):
    stage = conversation_state.get("stage", "NORMAL")
    logger.info("stage is %s", stage)

    if stage == "WAITING_CONFIRMATION":
        logger.info("Go to WAITING_CONFIRMATION")
        if user_want_plan(user_message):
            conversation_state["stage"] = "COLLECT_PROFILE"
            logger.info("Go to COLLECT_PROFILE line 0")
            profile = create_profile_v0(user_message)
            logger.info("profile is %s" , profile)
            if profile["need_more_info"]:
                logger.info("profile message is %s" , profile["message"])
                return profile["message"]
        else:
            logger.info("changed to normal after collect")
            conversation_state["stage"] = "NORMAL"
            return chat(user_message)

    if stage == "COLLECT_PROFILE":
        logger.info("Go to COLLECT_PROFILE line 1")
        if user_message.strip() == "0":
            conversation_state["stage"] = "NORMAL"
            return chat("از حالت سوال اومدیم بیرون . یکم درباره سفر ها بگو کلا و سعی کن خیلییی کوتاه و خلاصه و حتما فارسی بگی")

        profile = create_profile_v0(user_message)
        logger.info("in line 1 profile is %s" , profile)
        if profile["need_more_info"]:
            return profile["message"]
        logger.info("changed state to choose city")
        conversation_state["profile"] = profile
        conversation_state["stage"] = "CHOOSE_CITY"
        print(conversation_state)
        stage = conversation_state["stage"]
    if stage == "CHOOSE_CITY":
        logger.info("Go to CHOOSE_CITY")
        city = top_city(conversation_state["profile"])
        print(f"city is {city}")
        print(f"conversation_state is {conversation_state}")
        conversation_state["top_city"] = city["top_city"]
        conversation_state["stage"] = "NORMAL"
        stage = conversation_state["stage"]
        return ask_model(cities[city["top_city"]])
    
    if stage =="WAIT_FOR_PLAN":
        if user_want_plan(user_message):
            print("start plan")
            candidate = places(conversation_state["profile"] , conversation_state["top_city"])
            print("candidate is" , candidate)
            return plan_agent(conversation_state["top_city"] ,candidate,conversation_state["profile"]["profile"]["days"] )

    reply = chat(user_message)
    if reply.strip() == "میخواین با چند سوال، بهترین شهر برای سفرتون رو بهتون پیشنهاد بدم؟":
        conversation_state["stage"] = "WAITING_CONFIRMATION"

    return reply





# def rag_answer(user_message):
    # global conversation_state, best_city, history

    # phase = conversation_state["phase"]
    # print("state is", phase)

    # if phase == "INIT":
    #     result = top_city(user_message)

    #     if result["need_more_info"]:
    #         return result["message"]

    #     best_city = result["top_city"]
    #     conversation_state["best_city"] = best_city
    #     conversation_state["phase"] = "WAITING_FOR_PLAN_CONFIRM"

    #     return ask_model(best_city)

    # if phase == "WAITING_FOR_PLAN_CONFIRM":
    #     if user_want_plan(user_message):
    #         conversation_state["phase"] = "PLANNING"
    #         return continue_chat(best_city, "برنامه سفر لطفاً")
    #     else:
    #         conversation_state["phase"] = "FALL_BACK"
    #         return ask_model_fallback(user_message)

    # if phase == "FALL_BACK":

    #     if user_want_plan(user_message):
    #         conversation_state["phase"] = "PLANNING"
    #         return continue_chat(best_city, "برنامه سفر لطفاً")

    #     if user_wants_new_city(user_message):
    #         conversation_state["phase"] = "INIT"
    #         conversation_state["best_city"] = None
    #         return "باشه  بگو چه سفری مدنظرت هست تا یه شهر جدید پیشنهاد بدم."

    #     if is_travel_related(user_message):
    #         conversation_state["phase"] = "WAITING_FOR_PLAN_CONFIRM"
    #         return ask_model_fallback(user_message)

    #     return (
    #         "من فقط دستیار سفر هستم 🌍\n"
    #         "اگر درباره مقصد یا برنامه سفر سوالی دارید خوشحال میشم کمک کنم."
    #     )

    # # -------- PLANNING --------
    # if phase == "PLANNING":

    #     if user_wants_new_city(user_message):
    #         conversation_state["phase"] = "INIT"
    #         conversation_state["best_city"] = None
    #         return "باشه  بگو چه سفری مدنظرت هست تا از اول بررسی کنیم."

    #     return continue_chat(best_city, user_message)

