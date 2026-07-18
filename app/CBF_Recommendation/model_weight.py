import requests
import json
from llm.log import logger
import os


def get_weights_from_profile(user_profile):
    """محاسبه weights بر اساس profile کاربر"""
    
    weights = {
        "religious": 0,
        "historical": 0,
        "modern_city": 0,
        "shopping": 0,
        "nightlife": 0,
        "expensive": 0,
        "hot": 0,
        "cold": 0,
        "four_seasons": 0,
        "nature": 0,    
    }
    
    logger.info("Adjusting weights for profile: %s", user_profile)
    
    # Places
    places = user_profile.get("places", "")
    if places == "تاریخی":
        weights.update({"historical": 0.85, "religious": 0.6, "modern_city": 0.4})
    elif places == "طبیعت":
        weights.update({"nature": 0.9, "four_seasons": 0.75, "modern_city": 0.3, "shopping": 0.35, "nightlife": 0.3})
    elif places == "شهری":
        weights.update({"modern_city": 0.8, "shopping": 0.85, "nightlife": 0.65, "nature": 0.15})
    elif places == "زیارتی":
        weights.update({"religious": 0.9})

    weather = user_profile.get("weather", "")
    if weather == "گرم":
        weights.update({"hot": 0.8, "cold": 0.05})
    elif weather == "خنک":
        weights.update({"cold": 0.75, "four_seasons": 0.65, "nature": 0.55, "hot": 0.05})
    elif weather == "سرد":
        weights.update({"cold": 0.8, "four_seasons": 0.45, "hot": 0.05})
    
    # Budget
    budget = user_profile.get("budget", "")
    if budget == "زیاد":
        weights.update({"expensive": 0.85, "shopping": 0.65, "nightlife": 0.55})
    elif budget == "متوسط":
        weights["expensive"] = 0.5
    elif budget == "کم":
        weights.update({"expensive": 0.05, "shopping": 0.2, "nature": 0.75})
    
    # ✅ Interests - boost existing weights
    interests = user_profile.get("interests", "")
    if "طبیعت" in interests:
        weights["nature"] = min(weights["nature"] + 0.1, 1.0)
        weights["four_seasons"] = min(weights["four_seasons"] + 0.1, 1.0)
    if "خرید" in interests:
        weights["shopping"] = min(weights["shopping"] + 0.15, 1.0)
        weights["modern_city"] = min(weights["modern_city"] + 0.1, 1.0)
        weights["expensive"] = min(weights["expensive"] + 0.15, 1.0)
    if "تفریح" in interests:
        weights["nightlife"] = min(weights["nightlife"] + 0.1, 1.0)
        weights["modern_city"] = min(weights["modern_city"] + 0.1, 1.0)
    if "کوه‌نوردی" in interests or "کوهنوردی" in interests:
        weights["nature"] = min(weights["nature"] + 0.25, 1.0)
        weights["four_seasons"] = min(weights["four_seasons"] + 0.15, 1.0)
        weights["cold"] = min(weights["cold"] + 0.1, 1.0)
    if "غذا" in interests:
        weights["modern_city"] = min(weights["modern_city"] + 0.15, 1.0)
        weights["expensive"] = min(weights["expensive"] + 0.1, 1.0)
    # ✅ NEW: زیارتی
    if "زیارتی" in interests:
        weights["religious"] = min(weights["religious"] + 0.2, 1.0)
        weights["historical"] = min(weights["historical"] + 0.15, 1.0)
        logger.debug("Boosted religious/historical for interests=زیارتی")
    
    # ✅ Description - extract keywords
    description = user_profile.get("description", "")
    if description:
        # اگه "طبیعت" در توضیحات باشد
        if "طبیعت" in description or "کوه" in description or "جنگل" in description:
            weights["nature"] = min(weights["nature"] + 0.15, 1.0)
            weights["four_seasons"] = min(weights["four_seasons"] + 0.1, 1.0)
            logger.debug("Boosted nature based on description")
        
        # اگه "تاریخی" در توضیحات باشد
        if "تاریخی" in description or "ایرانی" in description or "باستانی" in description:
            weights["historical"] = min(weights["historical"] + 0.15, 1.0)
            weights["religious"] = min(weights["religious"] + 0.1, 1.0)
            logger.debug("Boosted historical based on description")
        
        # اگه "شهری" در توضیحات باشد
        if "شهری" in description or "خرید" in description or "رستوران" in description:
            weights["modern_city"] = min(weights["modern_city"] + 0.15, 1.0)
            weights["shopping"] = min(weights["shopping"] + 0.1, 1.0)
            logger.debug("Boosted modern_city based on description")
    

    
    # Clamp all weights to 0-1
    weights = {k: min(max(v, 0.0), 1.0) for k, v in weights.items()}
    
    logger.info("Final weights: %s", weights)
    return weights