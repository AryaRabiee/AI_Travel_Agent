from .state_user import user_profile
from .travel_question_step import next_travel_question
from .save_answer import save_answer_to_profile
from .travel_related import is_travel_related
import json
from .validation import validation_answer
from llm.model_manager import fall_back




QUESTIONS = [
    {"key": "days", "type": "number", "min": 1, "max": 30},
    {"key": "weather", "type": "enum", "values": ["گرم", "خنک", "سرد"]},
    {"key": "places", "type": "enum", "values": ["شهری", "طبیعت", "تاریخی"]},
    {"key": "budget", "type": "enum", "values": ["زیاد", "متوسط", "کم"]},
    {"key": "interests", "type": "enum", "values": ["طبیعت", "نفریح", "خرید"]},
    {"key": "description", "type": "description"},


]




def handle_user_message(message):

    if user_profile["is_travel"] is None:
        # related = is_travel_related(message)
        related = "yes" # for test
        print("related is", related)

        if related == "yes":
            user_profile["is_travel"] = True
            user_profile["step"] = 0
            return next_travel_question()
        
        # if related =="smalltalk":
        #     return fall_back(message)

        # else:
        #     user_profile["is_travel"] = False
        #     return "سلام من یک دستیار سفر هستم و فقط به سوالات مربوط به سفر پاسخ میدم"

    step = user_profile["step"]
    print("Step is" ,step)

    valid, result = validation_answer(step, message, QUESTIONS)
    print("valid : " , valid , "result:" , result)

    if not valid:
        return result  
    
    user_profile[QUESTIONS[step]["key"]] = result
    user_profile["step"] += 1
    print("User profile is" , user_profile)

    nxt = next_travel_question()
    print(nxt)
    if nxt is None:
        return user_profile

    return nxt

