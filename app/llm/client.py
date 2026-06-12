from state.memory import history , conversation_state_memory , cities , translate , city_list
from state.handle_user import handle_user_message , create_profile
from CBF_Recommendation.recommandation_score import top_city
from .travel_plan import places , user_want_plan
from .model_manager import chat , plan_agent , weather_city_model , city_info_model , modify_plan_model ,chat_open_ai , direct_generate_plan , compare_two_city_model
from state.state_user import user_profile , conversation_state , generate_plan
from llm.log import logger
from route.intent import handleIntent 
from route.weather_intent import get_weather_data 


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
            return weather_city_model(weather, city_fa , user_message)


        if intent == "city_info":
            city = city_indent or conversation_state.get("current_city")
            city_name_en = translate(city)[1]
            if city is None:
                return "درباره کدوم شهر؟"

            with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
                doc = f.read()

            return city_info_model(doc, city , user_message)
        if intent == "generate_plan":
            logger.info("go to intent generatre_plan")
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
                return "مقصدتون کدوم شهر هست؟"
            generate_plan["city"] = city
            return "چند روز سفر مدنظرتونه؟"
        
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
            profile = create_profile(user_message)
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
        profile = create_profile(user_message)
        if profile["need_more_info"]:
            return profile["message"]
        conversation_state["profile"] = profile
        city = top_city(conversation_state["profile"])
        logger.info("city top is %s" , city)
        conversation_state["top_city"] = city["top_city"]
        conversation_state["current_city"] = city["top_city"]
        conversation_state["stage"] = "WAIT_FOR_PLAN"
        return ask_model(cities[city["top_city"]])

    if stage == "WAIT_FOR_PLAN":
        logger.info("go to stage WAIT_FOR_PLAN")

        if user_want_plan(user_message):
            candidate = places(
                conversation_state["profile"],
                conversation_state["top_city"]
            )
            conversation_state["stage"] = "NORMAL"
            return plan_agent(
                conversation_state["top_city"],
                candidate,
                conversation_state["profile"]["profile"]["days"]
            )
        logger.info("generate_plan is %s" , generate_plan)
        if generate_plan["city"] is None:

            if user_message not in city_list:
                return "لطفا یکی از شهرهای پشتیبانی شده را وارد (تهران-شیراز-یزد-رشت-اصفهان-مشهد)"

            generate_plan["city"] = user_message
            logger.info("generate_plan is %s" , generate_plan)
        logger.info("generate_plan is %s" , generate_plan)
        if generate_plan["days"] is None:

            if not user_message.strip().isdigit():
                return "لطفا تعداد روز را به صورت عدد وارد کن"

            generate_plan["days"] = int(user_message)
            logger.info("generate_plan is %s" , generate_plan)
        if generate_plan["city"] and generate_plan["days"]:
            
            city = generate_plan["city"]
            days = generate_plan["days"]

            city_name_en = translate(city)[1]

            with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
                doc = f.read()

            conversation_state["stage"] = "NORMAL"

            generate_plan["city"] = None
            generate_plan["days"] = None

            return direct_generate_plan(city, days, doc)
        

    intent_data = handleIntent(user_message)
    logger.info("intent_data is %s", intent_data)

    city_indent = intent_data.get("city")
    intent = intent_data.get("intent")
    days = intent_data.get("days")
    goal = intent_data.get("goal")


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
            return "کدوم شهر مدنظرتونه؟"

        weather = get_weather_data(city_fa)
        return weather_city_model(weather, city_fa , user_message)


    if intent == "city_info":
        city = city_indent or conversation_state.get("current_city")
        city_name_en = translate(city)[1]
        if city is None:
            return "درباره کدوم شهر میخواین بدونین؟"

        with open(f"../data/{city_name_en}.md", "r", encoding="utf-8") as f:
            doc = f.read()

        return city_info_model(doc, city , user_message)

    
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

    if intent == "start_travel":
        conversation_state["stage"] = "WAITING_CONFIRMATION"
        return "باشه 🙂 چند سوال می‌پرسم تا برنامه سفر بچینم."
    
    if intent == "generate_plan":
        logger.info("go to intent generatre_plan")
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
            return "کدوم شهر مدنظرتونه؟"
        generate_plan["city"] = city
        return "چند روز سفر مدنظرتونه؟"


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




