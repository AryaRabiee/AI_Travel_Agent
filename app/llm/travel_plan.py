import json
import requests
from state.memory import history , CITY_SIGNATURE , intrest_dict
from .model_manager import plan_agent
import random

def user_want_plan(message):
    msg = message.strip().lower()
    return msg in ['باشه',"بده","اره","بله","یه پلن بده","اره میخوام پلن بدی","پلن میخوام","باشه بده","مایل هستم","آره","yes"]

def places(profile_user, top_city):
    print("start func place")
    with open(f"../plan_data/{top_city}.json", "r", encoding="utf-8") as f:
        doc = json.load(f)
    candidate = []

    for place in doc["places"]:
        if profile_user["profile"]["budget"] in place["budget"] or (
            profile_user["profile"]["budget"] == "متوسط"
            and "کم" in place["budget"]
        ):
            candidate.append(place)

    total_place_count = profile_user["profile"]["days"] * 2
    interest_count_priority = round(total_place_count * 0.4)
    interest_count_random = round(total_place_count * 0.2)
    signature_count = round(total_place_count * 0.2)

    random_count = total_place_count - interest_count_priority - interest_count_random - signature_count

    interest_places = [place for place in candidate if place["type"] == intrest_dict[profile_user["profile"]["interests"]]]
    signature_places = [place for place in candidate if place["type"] == CITY_SIGNATURE[top_city]]
    other_place = [place for place in candidate if place["type"] not in (CITY_SIGNATURE[top_city], intrest_dict[profile_user["profile"]["interests"]])]

    interest_places = sorted(interest_places, key=lambda x: x["priority"], reverse=True)

    selected = []

    selected.extend(interest_places[:interest_count_priority])

    remaining_interest = [p for p in interest_places if p not in selected]
    selected.extend(
        random.sample(
            remaining_interest,
            min(interest_count_random, len(remaining_interest))
        )
    )

    remaining_signature = [p for p in signature_places if p not in selected]
    selected.extend(
        random.sample(
            remaining_signature,
            min(signature_count, len(remaining_signature))
        )
    )

    remaining_other = [p for p in other_place if p not in selected]
    selected.extend(
        random.sample(
            remaining_other,
            min(random_count, len(remaining_other))
        )
    )

    if len(selected) < total_place_count:
        remaining_pool = [p for p in candidate if p not in selected]
        need = total_place_count - len(selected)
        selected.extend(
            random.sample(
                remaining_pool,
                min(need, len(remaining_pool))
            )
        )
    candidate_text = ""

    for place in candidate:
        candidate_text += f"""
    نام: {place["name"]}
    نوع: {place["type"]}
    اولویت: {place["priority"]}
    مدت بازدید: {place["duration_hours"]} ساعت
    توضیح: {place["description"]}

    """
    return candidate_text


# def plan_agent(candidate , top_city , days):
#     reply = plan_agent(top_city ,candidate ,days)