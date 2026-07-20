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

BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"


def ask_model(best_city: str , session) -> str:
    conversation_state = session.conversation_state

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

    session.conversation_state_memory["phase"] = "WAITING_FOR_PLAN_CONFIRM"
    session.conversation_state["stage"] = "WAIT_FOR_PLAN"

    return messages[-1]["content"]



def rag_answer(user_message, session):
    logger.info("rag_answer called with message: %s", user_message)
    
    stage = session.conversation_state.get("stage", "NORMAL")
    logger.info("Current stage: %s", stage)
    

    if stage == "COLLECT_PROFILE":
        logger.info("COLLECT_PROFILE -> offline validation")
        reply = handle_collect_profile_stage(user_message, session)
        return reply
    

    if stage == "WAITING_CONFIRMATION" and user_want_plan(user_message):
        logger.info("User confirmed -> no intent detection needed")
        reply = handle_waiting_confirmation_stage(
            user_message, 
            intent_data={},     
            session=session
        )
        return reply

    logger.info("Calling intent detection for stage: %s", stage)
    intent_data = handleIntent(user_message, session)
    logger.info("Intent detected: %s", intent_data)
    
    if intent_data.get("city"):
        session.conversation_state["current_city"] = intent_data["city"]
    

    if stage == "NORMAL":
        logger.info("Processing NORMAL stage")
        reply = handle_normal_stage(user_message, intent_data, session)
    
    elif stage == "WAITING_CONFIRMATION":
        logger.info("Processing WAITING_CONFIRMATION stage")
        reply = handle_waiting_confirmation_stage(
            user_message, 
            intent_data, 
            session
        )
    
    elif stage == "WAIT_FOR_PLAN":
        logger.info("Processing WAIT_FOR_PLAN stage")
        reply = handle_wait_for_plan_stage(user_message, intent_data, session)
    
    else:
        logger.warning("Unknown stage: %s", stage)
        reply = "متاسفانه خطایی رخ داد."

    if reply:
        session.history.append({"role": "user", "content": user_message})
        session.history.append({"role": "assistant", "content": reply})
        logger.info("History saved. Total: %d messages", len(session.history))
    
    return reply


def handle_normal_stage(user_message, intent_data, session):
 
    intent = intent_data.get("intent")
    logger.info("NORMAL stage - Intent: %s", intent)
    
    if intent == "start_travel":
        session.conversation_state["stage"] = "WAITING_CONFIRMATION"
        logger.info("Changed stage to WAITING_CONFIRMATION")
        return "باشه آماده هستین چند تا سوال بپرسم؟."
    
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
        file_path = DATA_DIR / f"{city_name_en}.md"


        try:
            with open(file_path, "r", encoding="utf-8") as f:
                doc = f.read()
            return city_info_model(doc, city, user_message, session)

        except FileNotFoundError as e:
            print(f"❌ File not found: {file_path}")
            print(f"Error: {e}")
            
            print("Files in DATA_DIR:")
            for item in DATA_DIR.glob("*.md"):
                print(f"  - {item.name}")
            
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
    
    elif intent == "general_chat":
        logger.info("general_chat")
        reply = chat(user_message, session)
        
        if "میخواین با چند سوال" in reply:
            session.conversation_state["stage"] = "WAITING_CONFIRMATION"
            logger.info("Changed to WAITING_CONFIRMATION (from chat)")
        
        return reply
    else:

        return chat(user_message , session)


def handle_waiting_confirmation_stage(user_message, intent_data, session):

    intent = intent_data.get("intent")
    logger.info("WAITING_CONFIRMATION stage - Intent: %s", intent)

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

    if intent == "city_info":
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

    if intent == "generate_plan":
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
    
        
    if intent == "modify_plan":
        if not session.user_profile:
            return "ابتدا یک برنامه درست کنید تا بتوانید آن را تغییر دهید."
        session.conversation_state["stage"] = "NORMAL"
        return modify_plan_model(
            session.user_profile,
            intent_data.get("goal"),
            session.conversation_state.get("top_city"),
            session
        )
    
    if intent == "compare_city":
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
        



    if user_want_plan(user_message):
        logger.info("User confirmed - moving to COLLECT_PROFILE")
        session.conversation_state["stage"] = "COLLECT_PROFILE"

        profile_result = create_profile(user_message,session)
        
        if profile_result["need_more_info"]:
            logger.info("Profile incomplete - asking for more info")
            return profile_result["message"]
        
        logger.info("Profile unexpectedly complete")
        session.user_profile = profile_result["profile"]
        return handle_collect_profile_stage(user_message, session)

    else:
        logger.info("changed to normal after collect")
        session.conversation_state["stage"] = "NORMAL"
        return chat(user_message)


def handle_collect_profile_stage(user_message, session):

    logger.info("COLLECT_PROFILE stage")
    
    if user_message.strip() == "0":
        session.conversation_state["stage"] = "NORMAL"
        logger.info("User exited COLLECT_PROFILE")
        return "بیرون اومدیم از فرآیند. می‌تونم درباره شهرها و سفر‌ها کمکت کنم."
    
    profile_result = create_profile(user_message,session)
    
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
    
    return ask_model(cities[top_city_name] , session)


def handle_wait_for_plan_stage(user_message, intent_data, session):

    logger.info("WAIT_FOR_PLAN stage - Intent: %s", intent_data.get("intent"))
    
    intent = intent_data.get("intent")
    generate_plan = session.generate_plan
    
    logger.info("Intent %s - stage stays WAIT_FOR_PLAN", intent)
    
    if user_want_plan(user_message):
        candidate = places(
                session.user_profile,
                session.conversation_state["top_city"]
            )
        session.conversation_state["stage"] = "NORMAL"
        return plan_agent(
                session.conversation_state["top_city"],
                candidate,
                session.user_profile["days"],
                session
            )

    if intent == "weather":
        city = intent_data.get("city") or session.conversation_state.get("current_city")
        if not city:
            return "درباره کدوم شهر آب‌وهوا رو می‌خواید بدونید؟"
        
        city_fa = translate(city)[0]
        weather = get_weather_data(city_fa)
        session.conversation_state["stage"] = "NORMAL"
        return weather_city_model(weather, city_fa, user_message, session)
    
    if intent == "city_info":
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
            session.conversation_state["stage"] = "NORMAL"
            return city_info_model(doc, city, user_message, session)
        
        except FileNotFoundError:
            logger.error("File not found: data/%s.md", city_name_en)
            return f"متاسفانه اطلاعات {city} موجود نیست."
        except Exception as e:
            logger.error("Error in city_info: %s", e)
            return f"متاسفانه خطایی در دریافت اطلاعات {city} رخ داد."

    
    if intent == "compare_city":
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
            session.conversation_state["stage"]= "NORMAL"
            return compare_two_city_model(city1, city2, doc1, doc2, session)
        
        except FileNotFoundError as e:
            logger.error("File not found: %s", e)
            return "متاسفانه اطلاعات یکی از شهرها موجود نیست."
        except Exception as e:
            logger.error("Error in compare_city: %s", e)
            return "متاسفانه خطایی در مقایسه شهرها رخ داد."
        
    if intent == "modify_plan":
        if not session.user_profile:
            return "ابتدا یک برنامه درست کنید تا بتوانید آن را تغییر دهید."
        session.conversation_state["stage"]= "NORMAL"
        return modify_plan_model(
            session.user_profile,
            intent_data.get("goal"),
            session.conversation_state.get("top_city"),
            session
        )
    if intent == "generate_plan":
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
    else:
        reply = chat(user_message , session)
        return reply

def format_history_for_intent(history):
    """تاریخچه رو به فرمت readable تبدیل کن"""
    text = ""
    for msg in history[-10:]:     
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        text += f"{role}: {content}\n"
    return text

