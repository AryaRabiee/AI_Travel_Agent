from .travel_question_step import next_travel_question
from .validation import validation_answer
from llm.log import logger




QUESTIONS = [
    {
        "key": "days",
        "type": "number",
        "min": 1,
        "max": 30,
        "question": "چند روز قصد سفر دارید؟"
    },
    {
        "key": "weather",
        "type": "enum",
        "values": ["گرم", "خنک", "سرد"],
        "question": "چه نوع آب‌وهوایی دوست دارید؟"
    },
    {
        "key": "places",
        "type": "enum",
        "values": ["شهری", "طبیعت", "تاریخی"],
        "question": "به چه نوع جاهایی علاقه‌مندید؟"
    },
    {
        "key": "budget",
        "type": "enum",
        "values": ["کم", "متوسط", "زیاد"],
        "question": "بودجه تقریبی شما چقدره؟"
    },
    {
        "key": "interests",
        "type": "enum",
        "values": ["طبیعت", "تفریح", "خرید"],
        "question": "علاقه‌مندی خاصی دارید؟"
    },
    {
        "key": "description",
        "type": "description",
        "question": "لطفا توضیحات کلی درباره مقصدتون بگین"
    },
]


def create_profile(message , session):
    logger.info("start func create profile v0")
    user_profile_or_question = handle_user_message(message,session)
    if not isinstance(user_profile_or_question , dict):
        logger.info("user profile %s" , user_profile_or_question)
        logger.info("User profile incomplete, asking for more info...")
        return {"need_more_info": True, "message": user_profile_or_question}
    user_profile = user_profile_or_question
    logger.info("finish question and now the profile is %s" , user_profile)
    return {"need_more_info": False, "profile": user_profile}


def handle_user_message(message , session):

    if session.user_profile["is_travel"] is None:
        session.user_profile["is_travel"] = True
        session.user_profile["step"] = 0
        return next_travel_question(session.user_profile)
        


    step = session.user_profile["step"]
    print("Step is" ,step)

    valid, result = validation_answer(step, message, QUESTIONS)
    print("valid : " , valid , "result:" , result)

    if not valid:
        return result  
    
    session.user_profile[QUESTIONS[step]["key"]] = result
    session.user_profile["step"] += 1
    print("User profile is" , session.user_profile)

    nxt = next_travel_question(session.user_profile)
    print(nxt)
    if nxt is None:
        return session.user_profile

    return nxt