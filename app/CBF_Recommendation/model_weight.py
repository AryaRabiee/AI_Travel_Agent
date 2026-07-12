import requests
import json
from llm.log import logger
import os


def get_weights_from_profile(user_profile):


    base_weights = {
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
    
    weights = base_weights.copy()
    
    logger.info("Base weights: %s", weights)
    logger.info("Adjusting for profile: %s", user_profile)
    

    places = user_profile.get("places", "")
    
    if places == "تاریخی":
        weights["historical"] = 0.85
        weights["religious"] = 0.7
        weights["modern_city"] = 0.4  
        logger.debug("Adjusted for places=تاریخی")
    
    elif places == "طبیعت":
        weights["nature"] = 0.9
        weights["four_seasons"] = 0.75
        weights["modern_city"] = 0.3  
        weights["shopping"] = 0.35
        weights["nightlife"] = 0.3
        logger.debug("Adjusted for places=طبیعت")
    
    elif places == "شهری":
        weights["modern_city"] = 0.8
        weights["shopping"] = 0.85
        weights["nightlife"] = 0.65
        weights["nature"] = 0.15

    weather = user_profile.get("weather", "")
    
    if weather == "گرم":
        weights["hot"] = 0.8  
        weights["cold"] = 0.05  
        logger.debug("Adjusted for weather=گرم")
    
    elif weather == "خنک":
        weights["cold"] = 0.75
        weights["four_seasons"] = 0.65
        weights["nature"] = 0.55
        weights["hot"] = 0.05
        logger.debug("Adjusted for weather=خنک")
    
    elif weather == "سرد":
        weights["cold"] = 0.8
        weights["four_seasons"] = 0.45
        weights["hot"] = 0.05    
        logger.debug("Adjusted for weather=سرد")

    budget = user_profile.get("budget", "")
    
    if budget == "زیاد":
        weights["expensive"] = 0.85  
        weights["shopping"] = 0.65
        weights["nightlife"] = 0.55
        logger.debug("Adjusted for budget=زیاد")
    
    elif budget == "متوسط":
        weights["expensive"] = 0.5 
        logger.debug("Adjusted for budget=متوسط")
    
    elif budget == "کم":
        weights["expensive"] = 0.05
        weights["shopping"] = 0.2
        weights["nature"] = 0.75    
        logger.debug("Adjusted for budget=کم")
    

    interests = user_profile.get("interests", "")
    
    if "طبیعت" in interests:
        weights["nature"] = min(weights["nature"] + 0.1, 1.0)
        weights["four_seasons"] = min(weights["four_seasons"] + 0.1, 1.0)
        logger.debug("Boosted nature for interests=طبیعت")
    
    if "خرید" in interests:
        weights["shopping"] = min(weights["shopping"] + 0.15, 1.0)
        weights["modern_city"] = min(weights["modern_city"] + 0.1, 1.0)
        weights["expensive"] = min(weights["expensive"] + 0.15, 1.0)
        logger.debug("Boosted shopping for interests=خرید")
    
    if "تفریح" in interests:
        weights["nightlife"] = min(weights["nightlife"] + 0.1, 1.0)
        weights["modern_city"] = min(weights["modern_city"] + 0.1, 1.0)
        logger.debug("Boosted nightlife for interests=تفریح")
    
    if "کوه‌نوردی" in interests or "کوهنوردی" in interests:
        weights["nature"] = min(weights["nature"] + 0.25, 1.0)
        weights["four_seasons"] = min(weights["four_seasons"] + 0.15, 1.0)
        weights["cold"] = min(weights["cold"] + 0.1, 1.0)
        logger.debug("Boosted nature/cold for interests=کوه‌نوردی")
    
    if "غذا" in interests:
        weights["modern_city"] = min(weights["modern_city"] + 0.15, 1.0)
        weights["expensive"] = min(weights["expensive"] + 0.1, 1.0)
        logger.debug("Boosted modern_city for interests=غذا")

    days = user_profile.get("days", 0)
    
    if days and days <= 2:
        weights["modern_city"] = min(weights["modern_city"] + 0.1, 1.0)
        logger.debug("Boosted modern_city for short trip (%d days)", days)
    
    elif days and days >= 7:
        weights["nature"] = min(weights["nature"] + 0.1, 1.0)
        weights["four_seasons"] = min(weights["four_seasons"] + 0.1, 1.0)
        logger.debug("Boosted nature for long trip (%d days)", days)

    for key in weights:
        weights[key] = min(max(weights[key], 0.0), 1.0)
    
    logger.info("Final adjusted weights: %s", weights)
    return weights