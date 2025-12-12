from .state_user import user_profile
from .travel_question_step import next_travel_question
from .save_answer import save_answer_to_profile
from .travel_related import is_travel_related
import json

def handle_user_message(message):

    if user_profile["is_travel"] is None:
        related = is_travel_related(message)
        print("related is" , related)

        if related == "yes":
            user_profile["is_travel"] = True
            return next_travel_question()

        else:
            user_profile["is_travel"] = False
            return "باشه، هر کمکی خواستی من در خدمتم."

    save_answer_to_profile(message)

    nxt = next_travel_question()

    if nxt is None:
        print("Profile_User is :" , user_profile , "type is :" , type(user_profile))
        return user_profile
    return nxt
