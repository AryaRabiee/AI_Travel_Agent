from state.memory import  conversation_state_memory , cities , translate , city_list
from state.handle_user import handle_user_message , create_profile
from CBF_Recommendation.recommandation_score import top_city
from .travel_plan import places , user_want_plan
from .model_manager import chat , plan_agent , weather_city_model , city_info_model , modify_plan_model , direct_generate_plan , compare_two_city_model
# from state.state_user import user_profile , conversation_state , generate_plan
from llm.log import logger
from route.intent import handleIntent 
from route.weather_intent import get_weather_data 
from pathlib import Path
import os

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"


def ask_model(best_city: str , session) -> str:
    conversation_state = session.conversation_state
    history = session.history

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



# def rag_answer(user_message, session):
#     print(session)
#     conversation_state = session.conversation_state
#     generate_plan = session.generate_plan
#     stage = conversation_state.get("stage", "NORMAL")
#     logger.info("Stage is %s" , stage)
#     if stage == "WAITING_CONFIRMATION":
#         logger.info("Go to WAITING_CONFIRMATION stage")
#         intent = handleIntent(user_message)
#         logger.info("intent is %s" , intent)
#         intent_data = handleIntent(user_message)
#         city_indent = intent_data.get("city")
#         intent = intent_data.get("intent")
#         days = intent_data.get("days")
#         goal = intent_data.get("goal")
#         if city_indent is not None:
#             conversation_state["current_city"] = city_indent
#         if intent == "weather":
#             city = city_indent or conversation_state.get("current_city")
#             city_fa = translate(city)[0]
#             if city is None:
#                 return "برای کدوم شهر؟"

#             weather = get_weather_data(city_fa)
#             return weather_city_model(weather, city_fa , user_message)


#         if intent == "city_info":
#             city = city_indent or conversation_state.get("current_city")
#             city_name_en = translate(city)[1]
#             if city is None:
#                 return "درباره کدوم شهر؟"

#             with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
#                 doc = f.read()

#             return city_info_model(doc, city , user_message)
#         if intent == "generate_plan":
#             logger.info("go to intent generatre_plan")
#             city = city_indent or conversation_state.get("current_city")
#             generate_plan["city"] = city
#             generate_plan["days"] = days

#             if city and days:
#                 city_name_en = translate(city)[1]
#                 with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
#                     doc = f.read()
#                 return direct_generate_plan(city, days, doc , session)
#             conversation_state["stage"] = "WAIT_FOR_PLAN"
#             if not city:
#                 return "مقصدتون کدوم شهر هست؟"
#             generate_plan["city"] = city
#             return "چند روز سفر مدنظرتونه؟"
        
#         if intent == "compare_city":
#             city1 = intent_data["city1"]
#             city2 = intent_data["city2"]
#             city1_name_en = translate(city1)[1]
#             city2_name_en = translate(city2)[1]
#             with open(f"../data/{city1_name_en}.md", "r", encoding="utf-8") as f1:
#                 doc1 = f1.read()
#             with open(f"../data/{city2_name_en}.md", "r", encoding="utf-8") as f2:
#                 doc2 = f2.read()
#             return compare_two_city_model(city1 , city2 , doc1 , doc2 , session)
        
#         if user_want_plan(user_message):
#             conversation_state["stage"] = "COLLECT_PROFILE"
#             profile = create_profile(user_message)
#             stage = conversation_state["stage"]
#             if profile["need_more_info"]:
#                 return profile["message"]
#         else:
#             logger.info("changed to normal after collect")
#             conversation_state["stage"] = "NORMAL"
#             return chat(user_message, session)


#     if stage == "COLLECT_PROFILE":
#         logger.info("Go to stage COLLECT_PROFILE ")
#         if user_message.strip() == "0":
#             conversation_state["stage"] = "NORMAL"
#             return chat("از حالت سوال اومدیم بیرون . یکم درباره سفر ها بگو کلا و سعی کن خیلییی کوتاه و خلاصه و حتما فارسی بگی" ,session)
#         profile = create_profile(user_message)
#         if profile["need_more_info"]:
#             return profile["message"]
#         session.user_profile = profile
#         city = top_city(session.user_profile)
#         logger.info("city top is %s" , city)
#         conversation_state["top_city"] = city["top_city"]
#         conversation_state["current_city"] = city["top_city"]
#         conversation_state["stage"] = "WAIT_FOR_PLAN"
#         return ask_model(cities[city["top_city"]])

#     if stage == "WAIT_FOR_PLAN":
#         logger.info("go to stage WAIT_FOR_PLAN")

#         if user_want_plan(user_message):
#             candidate = places(
#                 session.user_profile,
#                 conversation_state["top_city"]
#             )
#             conversation_state["stage"] = "NORMAL"
#             return plan_agent(
#                 conversation_state["top_city"],
#                 candidate,
#                 session.user_profile["profile"]["days"],
#                 session
#             )
#         logger.info("generate_plan is %s" , generate_plan)
#         if generate_plan["city"] is None:

#             if user_message not in city_list:
#                 return "لطفا یکی از شهرهای پشتیبانی شده را وارد (تهران-شیراز-یزد-رشت-اصفهان-مشهد)"

#             generate_plan["city"] = user_message
#             logger.info("generate_plan is %s" , generate_plan)
#         logger.info("generate_plan is %s" , generate_plan)
#         if generate_plan["days"] is None:

#             if not user_message.strip().isdigit():
#                 return "لطفا تعداد روز را به صورت عدد وارد کن"

#             generate_plan["days"] = int(user_message)
#             logger.info("generate_plan is %s" , generate_plan)
#         if generate_plan["city"] and generate_plan["days"]:
            
#             city = generate_plan["city"]
#             days = generate_plan["days"]

#             city_name_en = translate(city)[1]

#             with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
#                 doc = f.read()

#             conversation_state["stage"] = "NORMAL"

#             generate_plan["city"] = None
#             generate_plan["days"] = None

#             return direct_generate_plan(city, days, doc,session)
        

#     intent_data = handleIntent(user_message)
#     logger.info("intent_data is %s", intent_data)

#     city_indent = intent_data.get("city")
#     intent = intent_data.get("intent")
#     days = intent_data.get("days")
#     goal = intent_data.get("goal")


#     if city_indent is not None:
#         conversation_state["current_city"] = city_indent

#     logger.info("intent=%s stage=%s", intent, stage)
#     logger.info("city_indent=%s current_city=%s", city_indent, conversation_state["current_city"])


#     if intent == "cancel_workflow":
#         conversation_state["stage"] = "NORMAL"
#         return "باشه، از روند فعلی خارج شدیم."

#     if intent == "weather":
#         city = city_indent or conversation_state.get("current_city")
#         city_fa = translate(city)[0]
#         if city is None:
#             return "کدوم شهر مدنظرتونه؟"

#         weather = get_weather_data(city_fa)
#         return weather_city_model(weather, city_fa , user_message)


#     if intent == "city_info":
#         city = city_indent or conversation_state.get("current_city")
#         city_name_en = translate(city)[1]
#         if city is None:
#             return "درباره کدوم شهر میخواین بدونین؟"

#         with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
#             doc = f.read()

#         return city_info_model(doc, city , user_message)

    
#     if intent == "compare_city":
#         city1 = intent_data["city1"]
#         city2 = intent_data["city2"]
#         city1_name_en = translate(city1)[1]
#         city2_name_en = translate(city2)[1]
#         with open(f"../data/{city1_name_en}.md", "r", encoding="utf-8") as f1:
#             doc1 = f1.read()
#         with open(f"../data/{city2_name_en}.md", "r", encoding="utf-8") as f2:
#             doc2 = f2.read()
#         return compare_two_city_model(city1 , city2 , doc1 , doc2,session)

#     if intent == "start_travel":
#         conversation_state["stage"] = "WAITING_CONFIRMATION"
#         return "باشه 🙂 چند سوال می‌پرسم تا برنامه سفر بچینم."
    
#     if intent == "generate_plan":
#         logger.info("go to intent generatre_plan")
#         city = city_indent or conversation_state.get("current_city")
#         generate_plan["city"] = city
#         generate_plan["days"] = days

#         if city and days:
#             city_name_en = translate(city)[1]
#             with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
#                 doc = f.read()
#             return direct_generate_plan(city, days, doc,session)
#         conversation_state["stage"] = "WAIT_FOR_PLAN"
#         if not city:
#             return "کدوم شهر مدنظرتونه؟"
#         generate_plan["city"] = city
#         return "چند روز سفر مدنظرتونه؟"


#     if intent == "modify_plan":
#         return modify_plan_model(
#             session.user_profile,
#             goal,
#             conversation_state.get("top_city"),
#             session
#         )
#     reply = chat(user_message , session)
#     session.history.append({"role": "user", "content": user_message})
#     session.history.append({"role": "assistant", "content": reply})
#     if reply.strip() == "میخواین با چند سوال، بهترین شهر برای سفرتون رو بهتون پیشنهاد بدم؟":
#         conversation_state["stage"] = "WAITING_CONFIRMATION"

#     return reply



def rag_answer(user_message, session):

    
    logger.info("rag_answer called with message: %s", user_message)
    logger.info("Current stage: %s", session.conversation_state.get("stage", "NORMAL"))
    
    recent_history = format_history_for_intent(session.history)
    current_city = session.conversation_state.get("current_city")
    
    intent_data =  handleIntent(user_message, session)

    logger.info("Intent detected: %s", intent_data)
    
    if intent_data.get("city"):
        session.conversation_state["current_city"] = intent_data["city"]
    
    stage = session.conversation_state.get("stage", "NORMAL")
    
    reply = None

    if stage == "NORMAL":
        logger.info("Processing in NORMAL stage")
        reply = handle_normal_stage(user_message, intent_data, session)
    

    elif stage == "WAITING_CONFIRMATION":
        logger.info("Processing in WAITING_CONFIRMATION stage")
        reply = handle_waiting_confirmation_stage(user_message, intent_data, session)
    

    elif stage == "COLLECT_PROFILE":
        logger.info("Processing in COLLECT_PROFILE stage")
        reply = handle_collect_profile_stage(user_message, session)
    

    elif stage == "WAIT_FOR_PLAN":
        logger.info("Processing in WAIT_FOR_PLAN stage")
        reply = handle_wait_for_plan_stage(user_message, intent_data, session)
    
    else:
        logger.warning("Unknown stage: %s", stage)
        reply = "متاسفانه خطایی رخ داد."
    
    if reply:
        session.history.append({"role": "user", "content": user_message})
        session.history.append({"role": "assistant", "content": reply})
        logger.info("History saved. Total messages: %d", len(session.history))
    
    return reply



def handle_normal_stage(user_message, intent_data, session):
    """
    NORMAL stage: کاربر می‌تواند هر کاری بکند
    - سوال عمومی
    - درخواست سفر
    - اطلاعات شهر
    - مقایسه شهرها
    - وضعیت آب‌وهوا
    - تولید برنامه
    """
    intent = intent_data.get("intent")
    logger.info("NORMAL stage - Intent: %s", intent)
    
    if intent == "start_travel":
        session.conversation_state["stage"] = "WAITING_CONFIRMATION"
        logger.info("Changed stage to WAITING_CONFIRMATION")
        return "باشه 🙂 چند سوال می‌پرسم تا برنامه سفر بچینم."
    
    elif intent == "weather":
        city = intent_data.get("city") or session.conversation_state.get("current_city")
        if not city:
            return "درباره کدوم شهر آب‌وهوا رو می‌خواید بدونید؟"
        
        city_fa = translate(city)[0]
        weather = get_weather_data(city_fa)
        return weather_city_model(weather, city_fa, user_message, session)
    
    elif intent == "city_info":
        city = intent_data.get("city") or session.conversation_state.get("current_city")
        if not city:
            return "درباره کدوم شهر می‌خواید بدونید؟"
        
        city_name_en = translate(city)[1]
        try:
            with open(DATA_DIR / f"{city_name_en}.md", "r", encoding="utf-8") as f:
                doc = f.read()
            return city_info_model(doc, city, user_message, session)
        except FileNotFoundError:
            return f"متاسفانه اطلاعات {city} موجود نیست."
        except Exception as e:
                logger.error("Error in generate_plan: %s", e)
                return" متاسفانه خطایی در دریافت اطلاعات رخ داد"    
    elif intent == "compare_city":
        city1 = intent_data.get("city1")
        city2 = intent_data.get("city2")
        
        if not city1 or not city2:
            return "لطفا دو شهر برای مقایسه انتخاب کنید."
        
        city1_name_en = translate(city1)[1]
        city2_name_en = translate(city2)[1]
        
        try:
            with open(DATA_DIR / f"{city1_name_en}.md", "r", encoding="utf-8") as f1:
                doc1 = f1.read()
            with open(DATA_DIR / f"{city2_name_en}.md", "r", encoding="utf-8") as f2:
                doc2 = f2.read()
            return compare_two_city_model(city1, city2, doc1, doc2, session)
        except FileNotFoundError:
            return "متاسفانه اطلاعات یکی از شهرها موجود نیست."
        except Exception as e:
                logger.error("Error in generate_plan: %s", e)
                return" متاسفانه خطایی در دریافت اطلاعات رخ داد"
    elif intent == "generate_plan":
        city = intent_data.get("city") or session.conversation_state.get("current_city")
        days = intent_data.get("days")
        
        if city and days:
            city_name_en = translate(city)[1]
            try:
                with open(DATA_DIR / f"{city_name_en}.md", "r", encoding="utf-8") as f:
                    doc = f.read()
                return direct_generate_plan(city, days, doc, session)
            except FileNotFoundError:
                return f"متاسفانه اطلاعات {city} موجود نیست."
            except Exception as e:
                logger.error("Error in generate_plan: %s", e)
                return" متاسفانه خطایی در دریافت اطلاعات رخ داد"
        session.conversation_state["stage"] = "WAIT_FOR_PLAN"
        session.generate_plan["city"] = city
        session.generate_plan["days"] = days
        
        if not city:
            return "کدوم شهر مدنظرتونه؟"
        return "چند روز سفر مدنظرتونه؟"
    
    elif intent == "modify_plan":
        if not session.user_profile:
            return "ابتدا یک برنامه درست کنید تا بتوانید آن را تغییر دهید."
        
        return modify_plan_model(
            session.user_profile,
            intent_data.get("goal"),
            session.conversation_state.get("top_city"),
            session
        )
    
    elif intent == "cancel_workflow":
        session.conversation_state["stage"] = "NORMAL"
        return "باشه، از روند فعلی خارج شدیم."
    
    else:  
        reply = chat(user_message, session)
        
        if "میخواین با چند سوال" in reply:
            session.conversation_state["stage"] = "WAITING_CONFIRMATION"
            logger.info("Changed stage to WAITING_CONFIRMATION (from chat model)")
        
        return reply


def handle_waiting_confirmation_stage(user_message, intent_data, session):
    """
    WAITING_CONFIRMATION stage: در انتظار تایید شروع سفر
    فقط intent‌های مرتبط با سفر رو پذیر می‌کنه
    """
    intent = intent_data.get("intent")
    logger.info("WAITING_CONFIRMATION stage - Intent: %s", intent)
    

    if user_want_plan(user_message):
        logger.info("User confirmed - moving to COLLECT_PROFILE")
        session.conversation_state["stage"] = "COLLECT_PROFILE"

        profile_result = create_profile(user_message, session)
        
        if profile_result["need_more_info"]:
            logger.info("Profile incomplete - asking for more info")
            return profile_result["message"]
        
        logger.info("Profile unexpectedly complete")
        session.user_profile = profile_result["profile"]
        return handle_collect_profile_stage(user_message, session)

    if intent == "cancel_workflow":
        logger.info("User cancelled workflow")
        session.conversation_state["stage"] = "NORMAL"
        return "باشه، از روند فعلی خارج شدیم."
    

    if intent == "weather":
        logger.info("Weather intent detected")
        
        city = intent_data.get("city") or session.conversation_state.get("current_city")
        
        if not city:
            logger.warning("No city found for weather")
            return "درباره کدوم شهر آب‌وهوا رو می‌خواید بدونید؟"
        
        try:
            city_fa = translate(city)[0]
            logger.info("Getting weather for: %s", city_fa)
            
            weather = get_weather_data(city_fa)
            return weather_city_model(weather, city_fa, user_message,session)
        except Exception as e:
            logger.error("Error getting weather: %s", e)
            return f"متاسفانه خطایی در دریافت اطلاعات آب‌وهوای {city} رخ داد."
    

    elif intent == "city_info":
        logger.info("City info intent detected")
        
        city = intent_data.get("city") or session.conversation_state.get("current_city")
        
        if not city:
            logger.warning("No city found for city_info")
            return "درباره کدوم شهر می‌خواید بدونید؟"
        
        try:
            city_name_en = translate(city)[1]
            logger.info("Getting info for: %s", city_name_en)
            
            with open(f"data/{city_name_en}.md", "r", encoding="utf-8") as f:
                doc = f.read()
            
            return city_info_model(doc, city, user_message, session)
        
        except FileNotFoundError:
            logger.error("File not found: data/%s.md", city_name_en)
            return f"متاسفانه اطلاعات {city} موجود نیست."
        except Exception as e:
            logger.error("Error in city_info: %s", e)
            return f"متاسفانه خطایی در دریافت اطلاعات {city} رخ داد."
    

    elif intent == "compare_city":
        logger.info("Compare city intent detected")
        
        city1 = intent_data.get("city1")
        city2 = intent_data.get("city2")
        
        if not city1 or not city2:
            logger.warning("Missing cities for comparison")
            return "لطفا دو شهر برای مقایسه انتخاب کنید."
        
        try:
            city1_name_en = translate(city1)[1]
            city2_name_en = translate(city2)[1]
            
            logger.info("Comparing %s vs %s", city1_name_en, city2_name_en)
            
            with open(DATA_DIR / f"{city1_name_en}.md", "r", encoding="utf-8") as f1:
                doc1 = f1.read()
            
            with open(DATA_DIR / f"{city2_name_en}.md", "r", encoding="utf-8") as f2:
                doc2 = f2.read()
            
            return compare_two_city_model(city1, city2, doc1, doc2, session)
        
        except FileNotFoundError as e:
            logger.error("File not found: %s", e)
            return "متاسفانه اطلاعات یکی از شهرها موجود نیست."
        except Exception as e:
            logger.error("Error in compare_city: %s", e)
            return "متاسفانه خطایی در مقایسه شهرها رخ داد."

    elif intent == "generate_plan":
        logger.info("Generate plan intent detected")
        
        city = intent_data.get("city") or session.conversation_state.get("current_city")
        days = intent_data.get("days")
        
        logger.info("City: %s | Days: %s", city, days)
        
        if city and days:
            try:
                city_name_en = translate(city)[1]
                logger.info("Generating plan for %s (%d days)", city_name_en, days)
                
                with open(DATA_DIR / f"{city_name_en}.md", "r", encoding="utf-8") as f:
                    doc = f.read()
                
                return direct_generate_plan(city, days, doc, session)
            
            except FileNotFoundError:
                logger.error("File not found: data/%s.md", city_name_en)
                return f"متاسفانه اطلاعات {city} موجود نیست."
            except Exception as e:
                logger.error("Error in generate_plan: %s", e)
                return" متاسفانه خطایی در دریافت اطلاعات رخ داد"
        
        logger.info("Incomplete plan info - moving to WAIT_FOR_PLAN")
        session.conversation_state["stage"] = "WAIT_FOR_PLAN"
        session.generate_plan["city"] = city
        session.generate_plan["days"] = days
        
        if not city:
            logger.info("Asking for city")
            return "کدوم شهر مدنظرتونه؟"
        
        logger.info("Asking for days")
        return "چند روز سفر مدنظرتونه؟"

    else:
        logger.info("Unknown intent or general_chat in WAITING_CONFIRMATION")
        return "لطفاً برای ادامه، «بله» بگویید یا سوال خود را مطرح کنید.\n\nمثال:\n✓ بله\n✓ بده\n✓ آره\n✓ شیراز چطور؟"


def handle_collect_profile_stage(user_message, session):
    """
    COLLECT_PROFILE stage
    ✅ بدون LLM - صرفاً offline validation
    """
    logger.info("COLLECT_PROFILE stage")
    
    if user_message.strip() == "0":
        session.conversation_state["stage"] = "NORMAL"
        session.user_profile = None
        logger.info("User exited COLLECT_PROFILE")
        return "بیرون اومدیم از فرآیند. می‌تونم درباره شهرها و سفر‌ها کمکت کنم."
    
    profile_result = create_profile(user_message, session)
    
    if profile_result["need_more_info"]:
        logger.info("Asking for more info")
        return profile_result["message"]
    
    logger.info("Profile complete")
    session.user_profile = profile_result["profile"]
    
    city_recommendation = top_city(session.user_profile)
    top_city_name = city_recommendation["top_city"]
    
    logger.info("Recommended city: %s", top_city_name)
    
    session.conversation_state["top_city"] = top_city_name
    session.conversation_state["current_city"] = top_city_name
    session.conversation_state["stage"] = "WAIT_FOR_PLAN"
    
    return ask_model(cities[top_city_name])


def handle_wait_for_plan_stage(user_message, intent_data, session):
    """
    WAIT_FOR_PLAN stage: انتظار تایید برای تولید برنامه
    کاربر باید شهر و تعداد روز رو مشخص کنه
    """
    logger.info("WAIT_FOR_PLAN stage")
    
    generate_plan = session.generate_plan
    
    if user_want_plan(user_message):
        
        if generate_plan["city"] and generate_plan["days"]:
            city = generate_plan["city"]
            days = generate_plan["days"]
            city_name_en = translate(city)[1]
            
            try:
                with open(DATA_DIR / f"{city_name_en}.md", "r", encoding="utf-8") as f:
                    doc = f.read()
                
                session.conversation_state["stage"] = "NORMAL"
                session.generate_plan = {
                    "city": None,
                    "days": None,
                    "need_city_or_days": False
                }
                
                return direct_generate_plan(city, days, doc, session)
            except FileNotFoundError:
                return f"متاسفانه اطلاعات {city} موجود نیست."
            except Exception as e:
                logger.error("Error in generate_plan: %s", e)
                return" متاسفانه خطایی در دریافت اطلاعات رخ داد"
            
        if not generate_plan["city"]:
            return "کدوم شهر مدنظرتونه؟"
        if not generate_plan["days"]:
            return "چند روز سفر مدنظرتونه؟"
    
    if not generate_plan["city"]:
        city = intent_data.get("city")
        
        if city:

            city_name_en = translate(city)[1]
            generate_plan["city"] = city
            logger.info("City set to: %s", city)
            return "چند روز سفر مدنظرتونه؟"
        else:
            return generate_plan["city_message"]
    
    if not generate_plan["days"]:
        days = intent_data.get("days")
        
        if days:
            generate_plan["days"] = days
            logger.info("Days set to: %d", days)
            
            city = generate_plan["city"]
            city_name_en = translate(city)[1]
            
            try:
                with open(DATA_DIR / f"{city_name_en}.md", "r", encoding="utf-8") as f:
                    doc = f.read()
                
                session.conversation_state["stage"] = "NORMAL"
                session.generate_plan = {
                    "city": None,
                    "days": None,
                    "need_city_or_days": False
                }
                
                return direct_generate_plan(city, days, doc, session)
            except FileNotFoundError:
                return f"متاسفانه اطلاعات {city} موجود نیست."
            except Exception as e:
                logger.error("Error in generate_plan: %s", e)
                return" متاسفانه خطایی در دریافت اطلاعات رخ داد"
        else:
            return generate_plan["days_message"]
    
    return "لطفاً اطلاعات کامل کنید."




def format_history_for_intent(history):
    """تاریخچه رو به فرمت readable تبدیل کن"""
    text = ""
    for msg in history[-10:]:     
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        text += f"{role}: {content}\n"
    return text

