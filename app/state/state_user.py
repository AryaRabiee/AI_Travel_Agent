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
    "top_city":None,
    "current_city":None

}
generate_plan = {
    "city":None,
    "city_message":"لطفا شهر خود را انتخاب کنید",
    "days_message":"لطفا تعداد روز ها را مشخص کنید",
    "days":None,
    "need_city_or_days":False
}
