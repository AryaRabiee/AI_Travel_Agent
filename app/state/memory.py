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