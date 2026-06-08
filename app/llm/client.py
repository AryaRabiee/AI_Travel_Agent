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
from state.memory import history , conversation_state_memory , cities , translate
from state.handle_user import handle_user_message
from rag.retrieval import retrieve_top_cities
from CBF_Recommendation.model_weight import get_weight_for_feature
from CBF_Recommendation.recommandation_score import top_city
from .travel_plan import places , user_want_plan
# from state.route import route_user_message
from .model_manager import chat , plan_agent , weather_city_model , city_info_model , modify_plan_model ,chat_open_ai , direct_generate_plan , compare_two_city_model
from state.travel_question_step import next_travel_question
from state.state_user import user_profile , conversation_state
from state.validation import validation_answer
from llm.log import logger
from route.intent import handleIntent 
from route.weather_intent import get_weather_data 


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


city_list = ["تهران" , "مشهد" ,"یزد","شیراز","اصفهان","رشت"]

generate_plan = {
    "city":None,
    "city_message":"لطفا شهر خود را انتخاب کنید",
    "days_message":"لطفا تعداد روز ها را مشخص کنید",
    "days":None,
    "need_city_or_days":False
}


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



QUESTIONS = [
    {"key": "days", "type": "number", "min": 1, "max": 30},
    {"key": "weather", "type": "enum", "values": ["گرم", "خنک", "سرد"]},
    {"key": "places", "type": "enum", "values": ["شهری", "طبیعت", "تاریخی"]},
    {"key": "budget", "type": "enum", "values": ["کم", "متوسط", "زیاد"]},
    {"key": "interests", "type": "enum", "values": ["طبیعت", "تفریح", "خرید"]},
    {"key": "description", "type": "description"}
]

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
    logger.info("Stage is %s" , stage)
    if stage == "WAITING_CONFIRMATION":
        logger.info("Go to WAITING_CONFIRMATION stage")
        intent = handleIntent(user_message)
        logger.info("intent is %s" , intent)
        intent_data = handleIntent(user_message)
        city_indent = intent_data.get("city")
        intent = intent_data.get("intent")
        days = intent_data.get("days")
        goal = intent_data.get("goal")
        if city_indent is not None:
            conversation_state["current_city"] = city_indent
        if intent == "weather":
            city = city_indent or conversation_state.get("current_city")
            city_fa = translate(city)[0]
            if city is None:
                return "برای کدوم شهر؟"

            weather = get_weather_data(city_fa)
            return weather_city_model(weather, city_fa)


        if intent == "city_info":
            city = city_indent or conversation_state.get("current_city")
            city_name_en = translate(city)[1]
            if city is None:
                return "درباره کدوم شهر؟"

            with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
                doc = f.read()

            return city_info_model(doc, city)
        if intent == "direct_generate_plan" or intent == "generate_plan":

            city = city_indent or conversation_state.get("current_city")
            city_name_en = translate(city)[1]
            if city is None:
                return "برای کدوم شهر؟"

            if days is None:
                return "چند روز سفر؟"

            with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
                doc = f.read()

            return direct_generate_plan(city, days, doc)
        
        if intent == "compare_city":
            city1 = intent_data["city1"]
            city2 = intent_data["city2"]
            city1_name_en = translate(city1)[1]
            city2_name_en = translate(city2)[1]
            with open(f"../data/{city1_name_en}.md", "r", encoding="utf-8") as f1:
                doc1 = f1.read()
            with open(f"../data/{city2_name_en}.md", "r", encoding="utf-8") as f2:
                doc2 = f2.read()
            return compare_two_city_model(city1 , city2 , doc1 , doc2)
        
        if user_want_plan(user_message):
            conversation_state["stage"] = "COLLECT_PROFILE"
            profile = create_profile_v0(user_message)
            stage = conversation_state["stage"]
            if profile["need_more_info"]:
                return profile["message"]
        else:
            logger.info("changed to normal after collect")
            conversation_state["stage"] = "NORMAL"
            return chat(user_message)


    if stage == "COLLECT_PROFILE":
        logger.info("Go to stage COLLECT_PROFILE ")
        if user_message.strip() == "0":
            conversation_state["stage"] = "NORMAL"
            return chat("از حالت سوال اومدیم بیرون . یکم درباره سفر ها بگو کلا و سعی کن خیلییی کوتاه و خلاصه و حتما فارسی بگی")
        profile = create_profile_v0(user_message)
        if profile["need_more_info"]:
            return profile["message"]
        conversation_state["profile"] = profile
        city = top_city(conversation_state["profile"])
        logger.info("city top is %s" , city)
        conversation_state["top_city"] = city["top_city"]
        conversation_state["stage"] = "WAIT_FOR_PLAN"
        return ask_model(cities[city["top_city"]])
    
    intent_data = handleIntent(user_message)
    logger.info("intent_data is %s", intent_data)

    city_indent = intent_data.get("city")
    intent = intent_data.get("intent")
    days = intent_data.get("days")
    goal = intent_data.get("goal")

    # stage = conversation_state.get("stage", "NORMAL")

    if city_indent is not None:
        conversation_state["current_city"] = city_indent

    logger.info("intent=%s stage=%s", intent, stage)
    logger.info("city_indent=%s current_city=%s", city_indent, conversation_state["current_city"])


    if intent == "cancel_workflow":
        conversation_state["stage"] = "NORMAL"
        return "باشه، از روند فعلی خارج شدیم."

    if intent == "weather":
        city = city_indent or conversation_state.get("current_city")
        city_fa = translate(city)[0]
        if city is None:
            return "برای کدوم شهر؟"

        weather = get_weather_data(city_fa)
        return weather_city_model(weather, city_fa)


    if intent == "city_info":
        city = city_indent or conversation_state.get("current_city")
        city_name_en = translate(city)[1]
        if city is None:
            return "درباره کدوم شهر؟"

        with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
            doc = f.read()

        return city_info_model(doc, city)

    if intent == "direct_generate_plan":

        city = city_indent or conversation_state.get("current_city")
        city_name_en = translate(city)[1]
        if city is None:
            return "برای کدوم شهر؟"

        if days is None:
            return "چند روز سفر؟"

        with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
            doc = f.read()

        return direct_generate_plan(city, days, doc)
    
    if intent == "compare_city":
        city1 = intent_data["city1"]
        city2 = intent_data["city2"]
        city1_name_en = translate(city1)[1]
        city2_name_en = translate(city2)[1]
        with open(f"../data/{city1_name_en}.md", "r", encoding="utf-8") as f1:
            doc1 = f1.read()
        with open(f"../data/{city2_name_en}.md", "r", encoding="utf-8") as f2:
            doc2 = f2.read()
        return compare_two_city_model(city1 , city2 , doc1 , doc2)





    # if stage == "WAITING_CONFIRMATION":

    #     if user_want_plan(user_message):
    #         conversation_state["stage"] = "COLLECT_PROFILE"

    #         profile = create_profile_v0(user_message)

    #         if profile["need_more_info"]:
    #             return profile["message"]

    #         conversation_state["profile"] = profile
    #         conversation_state["stage"] = "CHOOSE_CITY"

    #         city_result = top_city(profile)
    #         conversation_state["top_city"] = city_result["top_city"]
    #         conversation_state["stage"] = "WAIT_FOR_PLAN"

    #         return ask_model(cities[city_result["top_city"]])

    #     else:
    #         conversation_state["stage"] = "NORMAL"
    #         return chat(user_message)

    # if stage == "COLLECT_PROFILE":

    #     if user_message.strip() == "0":
    #         conversation_state["stage"] = "NORMAL"
    #         return chat("باشه، خارج شدیم.")

    #     profile = create_profile_v0(user_message)

    #     if profile["need_more_info"]:
    #         return profile["message"]

    #     conversation_state["profile"] = profile

    #     city_result = top_city(profile)
    #     conversation_state["top_city"] = city_result["top_city"]

    #     conversation_state["stage"] = "WAIT_FOR_PLAN"

    #     return ask_model(cities[city_result["top_city"]])
    if stage == "WAIT_FOR_PLAN":
        logger.info("go to stage WAIT_FOR_PLAN")

        if user_want_plan(user_message):
            candidate = places(
                conversation_state["profile"],
                conversation_state["top_city"]
            )
            stage = conversation_state["NORMAL"]
            return plan_agent(
                conversation_state["top_city"],
                candidate,
                conversation_state["profile"]["profile"]["days"]
            )
        if generate_plan["city"] is None:

            if user_message not in city_list:
                return "لطفا یکی از شهرهای پشتیبانی شده را وارد کنید"

            generate_plan["city"] = user_message

            if generate_plan["days"] is None:
                return "چند روز سفر مدنظرته؟"

            if generate_plan["days"] is None:

                if not user_message.strip().isdigit():
                    return "لطفا تعداد روز را به صورت عدد وارد کن"

                generate_plan["days"] = int(user_message)

            city = generate_plan["city"]
            days = generate_plan["days"]

            city_name_en = translate(city)[1]

            with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
                doc = f.read()

            conversation_state["stage"] = "NORMAL"

            generate_plan["city"] = None
            generate_plan["days"] = None

            return direct_generate_plan(city, days, doc)
            

        if intent == "weather":
            city = intent_data.get("city") or conversation_state.get("current_city")
            if city:
                weather = get_weather_data(cities[city_indent])
                return weather_city_model(weather, cities[city])

        if intent == "city_info":
            city = intent_data.get("city") or conversation_state.get("current_city")
            with open(f"../data/{city}.md", "r", encoding="utf-8") as f:
                doc = f.read()
            return city_info_model(doc, city)
        conversation_state["stage"] = "NORMAL"
        return "اوکی 👍 اگر آماده بودی بگو 'برنامه' تا ادامه بدیم"



    if intent == "start_travel":
        conversation_state["stage"] = "WAITING_CONFIRMATION"
        return "باشه 🙂 چند سوال می‌پرسم تا برنامه سفر بچینم."
    
    if intent == "generate_plan":
        city = city_indent or conversation_state.get("current_city")
        generate_plan["city"] = city
        generate_plan["days"] = days

        if city and days:
            city_name_en = translate(city)[1]
            with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
                doc = f.read()
            return direct_generate_plan(city, days, doc)
        conversation_state["stage"] = "WAIT_FOR_PLAN"
        if not city:
            return "برای کدوم شهر برنامه میخوای؟"

        return "چند روز سفر مدنظرته؟"
        
        
        
    # if intent == "generate_plan":
    #     conversation_state["stage"] = "WAITING_CONFIRMATION"
    #     return "میخوای چند سوال بپرسم تا برنامه دقیق‌تر بشه؟"

    if intent == "modify_plan":
        return modify_plan_model(
            conversation_state.get("profile"),
            goal,
            conversation_state.get("top_city")
        )
    reply = chat(user_message)

    if reply.strip() == "میخواین با چند سوال، بهترین شهر برای سفرتون رو بهتون پیشنهاد بدم؟":
        conversation_state["stage"] = "WAITING_CONFIRMATION"

    return reply



# def rag_answer(user_message):
#     intent_data = handleIntent(user_message)
#     logger.info("intent_data is %s" , intent_data)
#     city_indent = intent_data["city"]
#     if city_indent is not None:
#         conversation_state["current_city"] = city_indent
#     logger.info("current city is %s" , conversation_state["current_city"])
#     intent = intent_data["intent"]
#     logger.info("intent is %s" , intent)
#     stage = conversation_state.get("stage", "NORMAL")
#     logger.info("stage is %s", stage)

#     if intent == "weather":
#         if city_indent is not None:
#             weather = get_weather_data(cities[city_indent])
#             return weather_city_model(weather ,cities[city_indent] )
#         else:
#             return "چه شهری مدنظر دارین؟"


#     if intent == "city_info":
#         city = city_indent or conversation_state.get("current_city")

#         if city is None:
#             return "درباره کدوم شهر منظورتونه؟"

#         with open(f"../data/{city}.md", "r", encoding="utf-8") as f:
#             file = f.read()
#         return city_info_model(file , city)

#     if intent == "start_travel":
#         conversation_state["stage"] = "WAITING_CONFIRMATION"

#     if intent == "generate_plan":
#         conversation_state["stage"] = "WAITING_CONFIRMATION"

#     if intent == "modify_plan":
#         goal = intent_data["goal"]
#         return modify_plan_model(user_profile , goal , conversation_state["top_city"])
    
#     if intent == "direct_generate_plan":
#         city = intent_data["city"]
#         days = intent_data["days"]
#         with open(f"../data/{city}.md", "r", encoding="utf-8") as f:
#             file = f.read()
        


#     if stage == "WAITING_CONFIRMATION":
#         intent = handleIntent(user_message)
#         if user_want_plan(user_message):
#             conversation_state["stage"] = "COLLECT_PROFILE"
#             profile = create_profile_v0(user_message)
#             stage = conversation_state["stage"]
#             if profile["need_more_info"]:
#                 return profile["message"]
#         else:
#             logger.info("changed to normal after collect")
#             conversation_state["stage"] = "NORMAL"
#             return chat(user_message)

#     if stage == "COLLECT_PROFILE":
#         intent = handleIntent(user_message)
#         if user_message.strip() == "0":
#             conversation_state["stage"] = "NORMAL"
#             return chat("از حالت سوال اومدیم بیرون . یکم درباره سفر ها بگو کلا و سعی کن خیلییی کوتاه و خلاصه و حتما فارسی بگی")

#         profile = create_profile_v0(user_message)
#         if profile["need_more_info"]:
#             return profile["message"]
#         conversation_state["profile"] = profile
#         conversation_state["stage"] = "CHOOSE_CITY"
#         stage = conversation_state["stage"]
#     if stage == "CHOOSE_CITY":
#         intent = handleIntent(user_message)
#         city = top_city(conversation_state["profile"])
#         conversation_state["top_city"] = city["top_city"]
#         stage = conversation_state["stage"]
#         return ask_model(cities[city["top_city"]])
    
#     if stage =="WAIT_FOR_PLAN":
#         intent = handleIntent(user_message)
#         if user_want_plan(user_message):
#             candidate = places(conversation_state["profile"] , conversation_state["top_city"])
#             return plan_agent(conversation_state["top_city"] ,candidate,conversation_state["profile"]["profile"]["days"] )
#         else:
#             conversation_state["stage"] = "NORMAL"

#     reply = chat(user_message)
#     if reply.strip() == "میخواین با چند سوال، بهترین شهر برای سفرتون رو بهتون پیشنهاد بدم؟":
#         conversation_state["stage"] = "WAITING_CONFIRMATION"

#     return reply



