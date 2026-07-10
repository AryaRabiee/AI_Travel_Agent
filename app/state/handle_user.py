from .state_user import user_profile
from .travel_question_step import next_travel_question
from .validation import validation_answer
from llm.log import logger




QUESTIONS = [
    {"key": "days", "type": "number", "min": 1, "max": 30},
    {"key": "weather", "type": "enum", "values": ["گرم", "خنک", "سرد"]},
    {"key": "places", "type": "enum", "values": ["شهری", "طبیعت", "تاریخی"]},
    {"key": "budget", "type": "enum", "values": ["زیاد", "متوسط", "کم"]},
    {"key": "interests", "type": "enum", "values": ["طبیعت", "نفریح", "خرید"]},
    {"key": "description", "type": "description"},


]



def create_profile(message):
    logger.info("start func create profile v0")
    user_profile_or_question = handle_user_message(message)
    if not isinstance(user_profile_or_question , dict):
        logger.info("user profile %s" , user_profile_or_question)
        logger.info("User profile incomplete, asking for more info...")
        return {"need_more_info": True, "message": user_profile_or_question}
    user_profile = user_profile_or_question
    logger.info("finish question and now the profile is %s" , user_profile)
    return {"need_more_info": False, "profile": user_profile}



def handle_user_message(message):

    if user_profile["is_travel"] is None:
        user_profile["is_travel"] = True
        user_profile["step"] = 0
        return next_travel_question()
        


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

