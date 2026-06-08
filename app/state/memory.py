history = [
    
]

conversation_state_memory = {
    "phase": "INIT",
    "best_city": None
}

cities = {
    "rasht":"رشت",
    "shiraz":"شیراز",
    "tehran":"تهران",
    "yazd":"یزد",
    "mashhad":"مشهد",
    "esfahan":"اصفهان",
    
}

cities_p = {
    "رشت":"rasht",
    "شیراز":"shiraz",
    "تهران":"tehran",
    "یزد":"yazd",
    "مشهد":"mashhad",
    "اصفهان":"esfahan",
}
CITY_SIGNATURE = {
    "رشت": "nature",
    "tehran": "recreational",
    "مشهد": "religious",
    "شیراز":"historical",
    "یزد":"historical",
    "اصفهان":"historical"
}

intrest_dict = {
    "طبیعت":"nature",
    "خرید":"recreational",
    "تاریخی":"historical",
    "شهری":"recreational",
    "زیارت":"religious"
}
import re

def translate(city):
    if re.fullmatch(r"[A-Za-z]+", city):
        city_per =cities[city]
        return city_per , city
    else:
        city_en = cities_p[city]
        return city , city_en