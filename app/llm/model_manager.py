from litellm import completion
import litellm
import json
from state.session import Session
from openai import OpenAI
import os
from llm.log import logger

api = os.getenv("OPENROUTER_API_KEY")
api_key_open_ai = os.getenv("OPENAI_API_KEY")
litellm.set_verbose = True
def call_llm_with_fallback(primary_model, backup_model, messages):
    resp = completion(
        model=primary_model,
        fallbacks=backup_model,
        
        api_key=api,
        messages=messages,
        num_retries = 2
    )
    return resp.choices[0].message.content.strip()


def detect_intent(user_message, recent_history, current_city):

    
    logger.info("detect_intent called | message: %s", user_message)
    
    history_text = format_history_for_prompt(recent_history)
    
    city_context = current_city if current_city else "هیچ شهری انتخاب نشده"
    
    messages = [
        {
            "role": "system",
            "content": f"""You are an intent classification and entity extraction agent for a travel assistant.

Analyze the user's message and return ONLY a valid JSON object.

Rules:
* Return JSON only.
* No explanations.
* No markdown.
* No extra text.
* Choose exactly one intent.
* Never invent cities or days.
* Extract city names whenever they appear.
* If a value is unavailable, return null.

Available intents:
* general_chat
* start_travel
* city_info
* weather
* generate_plan
* modify_plan
* compare_city
* cancel_workflow
* unknown

Intent definitions:

general_chat: Greetings, casual conversation, opinions, small talk.
start_travel: User wants help choosing a destination or asks for travel recommendations.
city_info: User asks about attractions, tourism, transportation, hotels, restaurants, culture.
weather: User asks about weather, temperature, climate, forecast.
generate_plan: User wants a travel itinerary or travel plan.
modify_plan: User wants to modify an existing travel plan.
compare_city: User compares two cities or asks which city is better.
cancel_workflow: User wants to stop the current planning process.

Output schema:

For normal intents:
{{
"intent": "<intent>",
"city": "<city_or_null>",
"days": <number_or_null>,
"goal": "<expensive|cheaper|null>"
}}

For compare_city:
{{
"intent": "compare_city",
"city1": "<city1>",
"city2": "<city2>",
"days": null,
"goal": null
}}

City reference rules:

If user refers to a city indirectly (این شهر، اون شهر، اینجا، آنجا، درباره اش، جاهای دیدنیش، آب و هواش) 
and no explicit city is mentioned, use current_city.

If a new city is explicitly mentioned, use the new city.

If neither exists, return city=null.

Context:
current_city = {city_context}

Use recent_history to resolve follow-up questions.

Example 1 (Context-aware):
History:
- User: "هوای رشت چطوره؟"
- Assistant: "رشت بارانی است..."

Current message: "شیراز چطور؟"

Output:
{{
"intent": "weather",
"city": "shiraz",
"days": null,
"goal": null
}}

Example 2 (Using current_city):
Current message: "جاهای دیدنیش چیه؟"
current_city: "tehran"

Output:
{{
"intent": "city_info",
"city": "tehran",
"days": null,
"goal": null
}}

Example 3 (Compare):
Current message: "تهران بهتره یا شیراز؟"

Output:
{{
"intent": "compare_city",
"city1": "tehran",
"city2": "shiraz",
"days": null,
"goal": null
}}"""
        },
        {
            "role": "user",
            "content": f"""Analyze this user message:

{user_message}

Recent conversation history:
{history_text}

Return ONLY valid JSON, no explanation."""
        }
    ]
    
    try:
        response = call_llm_with_fallback(
            "openrouter/tencent/hy3:free",
            [
                "openrouter/openai/gpt-oss-20b:free",
                "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
                "openrouter/google/gemma-4-26b-a4b-it:free",
                "openrouter/z-ai/glm-4.5-air:free",
                "openrouter/poolside/laguna-m.1:free"
            ],
            messages
        ).strip()
        
        logger.info("LLM response: %s", response)
        
        intent_data = json.loads(response)
        logger.info("Intent parsed: %s", intent_data)
        
        return intent_data
        
    except json.JSONDecodeError as e:
        logger.error("JSON parse error: %s | response: %s", e, response)
        return {
            "intent": "unknown",
            "city": None,
            "days": None,
            "goal": None
        }
    except Exception as e:
        logger.error("Error in detect_intent: %s", e)
        return {
            "intent": "unknown",
            "city": None,
            "days": None,
            "goal": None
        }


def format_history_for_prompt(history):
    """
    تاریخچه رو برای prompt فرمت کن
    
    history: list of {"role": "user/assistant", "content": "..."}
    return: formatted string
    """
    if not history:
        return "[No history]"
    
    text = ""
    for msg in history[-6:]:  # آخر 6 پیام
        role = msg.get("role", "unknown").capitalize()
        content = msg.get("content", "")
        text += f"{role}: {content}\n"
    
    return text.strip() if text else "[No history]"




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

    result = call_llm_with_fallback("openrouter/openai/gpt-oss-120b:free",            
            [
                          "openrouter/openai/gpt-oss-20b:free",
                          "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
                          "openrouter/google/gemma-4-26b-a4b-it:free",
                          "openrouter/z-ai/glm-4.5-air:free",
                          "openrouter/poolside/laguna-m.1:free"      
            ],
            messages)
    print("result in model manager" , result , "The type is:" , type(result))
    try:
        top_cities = json.loads(result)
    except json.JSONDecodeError:
        print("خطا: خروجی LLM JSON معتبر نیست!")
        print("RAW OUTPUT:", result)
        return None

    return top_cities

def plan_agent(best_city, candidate,days , session):
    user_message = f"لطفا بهم به اندازه {days} روز برنامه سفر بده . این هم از مکان های برگزیده {candidate}"
    
    messages = [
        {
            "role": "system",
            "content": f"""
    You are a professional AI Travel Planner.

    Language Rules:
    - Always answer in Persian.
    - Use a friendly and professional tone.
    - Write naturally like a travel expert.
    - Never answer in English.

    You will receive:
    1. A city name.
    2. A list of selected attractions.
    3. The number of travel days.

    Your task:
    Create a personalized day-by-day travel itinerary.

    Important Rules:

    1. Use ONLY the attractions provided in the candidate list.

    2. NEVER invent:
    - new attractions
    - new museums
    - new restaurants
    - new parks
    - new activities
    - any place not present in the candidate list

    3. The itinerary MUST contain exactly {days} travel days.

    4. Organize attractions logically across the days.

    5. Try to balance the itinerary:
    - avoid placing all major attractions on one day
    - distribute activities reasonably
    - avoid repetition

    6. For each day:
    - mention the places to visit
    - briefly explain why they are interesting
    - provide a natural travel suggestion

    7. Do NOT output JSON.

    8. Do NOT output Python dictionaries.

    9. Do NOT output bullet-point databases.

    10. Write the result as a real travel itinerary.

    11. If there are more attractions than needed:
    - prioritize higher-priority attractions first

    12. If there are fewer attractions than needed:
    - distribute the available attractions across the days
    - do NOT invent new places

    13. Never repeat the same attraction multiple times unless absolutely necessary.

    Output Format:

    برنامه سفر {days} روزه برای [CITY]

    روز اول:
    ...

    روز دوم:
    ...

    روز سوم:
    ...

    and so on...

    The final answer should feel like a real travel plan created by a human travel advisor.
    """
        }
    ]


    messages.append(
        {
            "role": "user",
            "content": f"""
    شهر انتخاب شده:
    {best_city}

    تعداد روزهای سفر:
    {days}

    مکان‌های منتخب:

    {candidate}

    لطفاً بر اساس این اطلاعات یک برنامه سفر کامل و کاربردی تهیه کن.
    """
        }
    )
    try:
        res = call_llm_with_fallback("openrouter/openai/gpt-oss-120b:free",            
                [
                            "openrouter/openai/gpt-oss-20b:free",
                            "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
                            "openrouter/google/gemma-4-26b-a4b-it:free",
                            "openrouter/z-ai/glm-4.5-air:free",
                            "openrouter/poolside/laguna-m.1:free"      
                ],
                messages)
        print(type(res))
        print(res)
        # if res.status_code != 200:
        #     return f"Error: {res.text}"

        # reply = res.json()["choices"][0]["message"]["content"]

        return res

    except Exception as e:
        logger.error(f"error from plan agent {e}")
        return "متاسفانه سرویس موقتاً فعال نیست."



def chat(user_message, session):
    """
    General chat handler - برای گفتگوی عمومی
    
    تاریخچه رو مدیریت می‌کنه و پاسخ دادن دهنده
    """
    logger.info("chat called | message: %s", user_message)
    
    recent_history = session.history[-10:]
    
    messages = [
    {
        "role": "system",
        "content": """You are a friendly Persian-speaking Travel Assistant.

IMPORTANT: 
- When user shows interest in travel/cities, ask EXACTLY once:
  "میخواین با چند سوال، بهترین شهر برای سفرتون رو بهتون پیشنهاد بدهم؟"
- Use this question ONLY when user clearly wants travel help
- Never repeat this question
- For other topics: answer naturally in Persian

Rules:
1. Answer in Persian only
2. Never invent information
3. For unknown: "اطلاعات دقیقی ندارم"
4. For non-travel: "من فقط دستیار سفر هستم"
5. Be friendly and concise"""
    }
    ]
    
    messages.extend(recent_history)
    
    messages.append({"role": "user", "content": user_message})
    
    logger.info("Sending %d messages to LLM", len(messages))
    
    try:
        res = call_llm_with_fallback(
            "openrouter/openai/gpt-oss-120b:free",
            [
                "openrouter/openai/gpt-oss-20b:free",
                "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
                "openrouter/google/gemma-4-26b-a4b-it:free",
                "openrouter/z-ai/glm-4.5-air:free",
                "openrouter/poolside/laguna-m.1:free"
            ],
            messages
        )
        
        logger.info("LLM response: %s", res[:100])

        return res
        
    except Exception as e:
        logger.error("Error in chat: %s", e)
        return "متاسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید."





def weather_city_model(weather, city, user_message, session):

    
    preference_note = ""
    
    if session.user_profile:
        weather_pref = session.user_profile.get("weather")
        if weather_pref:
            preference_note = f"\n(User prefers {weather_pref} weather)"
    
    messages = [
        {
            "role": "system",
            "content": f"""You are a travel weather assistant speaking in Persian.

City: {city}
Weather Data:
{weather}
{preference_note}

Instructions:
1. Answer user's weather question
2. Use ONLY provided data
3. Keep response brief in Persian
4. Don't invent data

User's question: {user_message}"""
        }
    ]
    try:
        res = call_llm_with_fallback(
            "openrouter/google/gemma-4-31b-it:free",
            [
                "openrouter/openai/gpt-oss-20b:free",
                "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
                "openrouter/google/gemma-4-26b-a4b-it:free",
                "openrouter/z-ai/glm-4.5-air:free",
                "openrouter/poolside/laguna-m.1:free"
            ],
            messages
        ).strip()
        return res
    except Exception as e:
        logger.error(f"Error from wether_city_model {e}")
        return "متاسفانه سرویس موقتاً فعال نیست."

   

def city_info_model(doc, city, user_message, session):

    
    interests_context = ""
    
    if session.user_profile:
        places = session.user_profile.get("places")
        interests = session.user_profile.get("interests")
        
        if places or interests:
            interests_context = f"""
User's Interests:
- Prefers: {places or 'not specified'} places
- Interested in: {interests or 'not specified'}

Highlight relevant aspects for this user.
"""
    
    messages = [
        {
            "role": "system",
            "content": f"""You are a knowledgeable travel guide speaking in Persian.

{interests_context}

City: {city}
Information:
{doc}

Instructions:
1. Answer the user's question about {city}
2. Use ONLY provided information
3. {"Focus on aspects matching user's interests" if session.user_profile else "Give a general helpful answer"}
4. Keep response concise in Persian
5. Don't invent information

User's question: {user_message}"""
        }
    ]
    try:
        res = call_llm_with_fallback(
            "openrouter/openai/gpt-oss-120b:free",
            [
                "openrouter/openai/gpt-oss-20b:free",
                "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
                "openrouter/google/gemma-4-26b-a4b-it:free",
                "openrouter/z-ai/glm-4.5-air:free",
                "openrouter/poolside/laguna-m.1:free"
            ],
            messages
        ).strip()
        return res
    except Exception as e:
        logger.info(f"Error from city_info_model {e}")
        return "متاسفانه سرویس موقتاً فعال نیست."


def modify_plan_model(profile , goal , city , session):
    
    messages = [
        {
            "role":"system",
            "content":f"""
                You are an expert travel planner.

                You receive:
                - User profile
                - Selected city
                - User modification goal

                Your task is to modify the travel recommendation according to the goal.

                Possible goals:
                - cheaper
                - luxury
                - nature
                - historical
                - shorter
                - longer

                Rules:
                1. Answer only in Persian.
                2. Keep the original city unchanged.
                3. Respect the user's profile.
                4. Explain what changes should be made to the trip.
                5. If the goal is "cheaper":
                - suggest lower-cost attractions
                - reduce expensive activities
                - recommend budget-friendly options

                6. If the goal is "luxury":
                - suggest premium attractions and experiences

                7. If the goal is "nature":
                - focus more on nature-related places

                8. If the goal is "historical":
                - focus more on historical places

                9. Be practical and specific.

                User Profile:
                {profile}

                City:
                {city}

                Goal:
                {goal}
                """
        }

    ],
    try:
        res =  call_llm_with_fallback("openrouter/google/gemma-4-31b-it:free",
                [
                            "openrouter/openai/gpt-oss-20b:free",
                            "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
                            "openrouter/google/gemma-4-26b-a4b-it:free",
                            "openrouter/z-ai/glm-4.5-air:free",
                            "openrouter/poolside/laguna-m.1:free"      
                ],
                    messages).strip().lower()
        return res
    except Exception as e:
        logger.info(f"Error from modify_plan_model {e}")
        return "متاسفانه سرویس موقتاً فعال نیست."


def direct_generate_plan(city , days , doc,session):
    messages = [
        {
            "role":"system",
            "content":f"""
            You are a professional travel itinerary generator.

            You will be given:
            - a city name
            - number of days
            - a city travel document (trusted source)

            Your task:
            Create a detailed, practical day-by-day travel plan ONLY based on the provided document.

            IMPORTANT RULES:
            - Do NOT use external knowledge.
            - Do NOT invent places not in the document.
            - If information is missing, skip it instead of guessing.
            - Always stay consistent with the city and document.
            - Output MUST be in Persian.
            - Be natural, human-like, and descriptive (not just bullet points).
            - Each day should include a clear itinerary with logical flow (morning / afternoon / evening if possible).

            OUTPUT FORMAT (STRICT):

            روز ۱:
            ...

            روز ۲:
            ...

            ...

            INPUT:

            City: {city}
            Number of days: {days}

            City Document:
            {doc}

            Now generate the travel plan.
            """

        }
    ]
    try:
        res = call_llm_with_fallback("openrouter/google/gemma-4-31b-it:free",
                [
                            "openrouter/openai/gpt-oss-20b:free",
                            "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
                            "openrouter/google/gemma-4-26b-a4b-it:free",
                            "openrouter/z-ai/glm-4.5-air:free",
                            "openrouter/poolside/laguna-m.1:free"      
                ],
                    messages).strip().lower()
        return res
    except Exception as e:
        logger.info(f"Error from direct_generate_plan {e}")
        return "متاسفانه سرویس موقتاً فعال نیست."


def compare_two_city_model(city1, city2, doc1, doc2, session):
    """
    مقایسه دو شهر
    ✅ user_profile اختیاری است
    """
    
    interests_context = ""
    
    if session.user_profile:
        places = session.user_profile.get("places")
        interests = session.user_profile.get("interests")
        budget = session.user_profile.get("budget")
        weather_pref = session.user_profile.get("weather")
        
        if any([places, interests, budget, weather_pref]):
            interests_context = f"""
User's Preferences (if available):
- Preferred place types: {places or 'not specified'}
- Interests: {interests or 'not specified'}
- Budget: {budget or 'not specified'}
- Weather preference: {weather_pref or 'not specified'}

Consider these preferences when comparing cities.
Which city better matches their interests?
"""
    
    if not interests_context:
        interests_context = """
No user preferences available.
Provide a general comparison of both cities.
Highlight strengths and weaknesses of each.
"""
    
    messages = [
        {
            "role": "system",
            "content": f"""You are a travel assistant speaking in Persian.

Compare two cities for travel.

{interests_context}

City 1 - {city1}:
{doc1}

City 2 - {city2}:
{doc2}

Instructions:
1. Compare these cities in Persian
2. {"Focus on user's preferences" if session.user_profile else "Give a balanced general comparison"}
3. Use ONLY provided information
4. Don't invent information
5. Be specific and helpful
6. End with a recommendation"""
        }
    ]
    
    logger.info("Comparing %s vs %s | profile: %s", 
                city1, city2, 
                "available" if session.user_profile else "None")
    try:
        res = call_llm_with_fallback(
            "openrouter/openai/gpt-oss-120b:free",
            [
                "openrouter/openai/gpt-oss-20b:free",
                "openrouter/nvidia/nemotron-3-super-120b-a12b:free",
                "openrouter/google/gemma-4-26b-a4b-it:free",
                "openrouter/z-ai/glm-4.5-air:free",
                "openrouter/poolside/laguna-m.1:free"
            ],
            messages
        ).strip()
        return res
    except Exception as e:
        logger.info(f"Error from compare_two_city {e}")
        return "متاسفانه سرویس موقتاً فعال نیست."
