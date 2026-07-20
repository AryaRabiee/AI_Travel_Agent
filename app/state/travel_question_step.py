from llm.log import logger
from .validation import QUESTIONS
def next_travel_question(user_profile):
    step = user_profile["step"]
    
    if step not in QUESTIONS:
        return None  # تمام شد
    
    q = QUESTIONS[step]
    question = q["question"]
    
    # گزینه‌ها اضافه کن
    if q["type"] == "choices":
        choices = ", ".join(q["choices"])
        return f"{question}\n({choices})"
    
    return question


