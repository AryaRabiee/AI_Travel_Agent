from .state_user import user_profile

def save_answer_to_profile(answer: str):
    if user_profile["step"] == 0:
        user_profile["days"] = answer
    elif user_profile["step"] == 1:
        user_profile["weather"] = answer
    elif user_profile["step"] == 2:
        user_profile["places"] = answer
    elif user_profile["step"] == 3:
        user_profile["budget"] = answer
    elif user_profile["step"] == 4:
        user_profile["interests"] = answer
    elif user_profile["step"] == 5:
        user_profile["description"] = answer

    user_profile["step"] += 1
