import re
from llm.log import logger

QUESTIONS = {
    0: {
        "question": "چند روز قصد سفر دارید؟",
        "type": "number",
        "min": 1,
        "max": 30
    },
    1: {
        "question": "چه نوع آب‌وهوایی دوست دارید؟",
        "type": "choices",
        "choices": ["گرم", "خنک", "سرد", "معتدل"]
    },
    2: {
        "question": "به چه نوع جاهایی علاقه‌مندید؟",
        "type": "choices",
        "choices": ["تاریخی", "طبیعت", "شهری", "تفریحی","زیارتی"]
    },
    3: {
        "question": "بودجه تقریبی شما چقدره؟",
        "type": "choices",
        "choices": ["کم", "متوسط", "زیاد"]
    },
    4: {
        "question": "علاقه‌مندی خاصی دارید؟ ",
        "type": "choices",
        "choices": ["طبیعت","کوه نوردی","خرید", "غذا", "تفریح"]
    }
}


def validation_answer(step, user_message, questions):
    q = questions[step]


    if q["type"] == "number":
        numbers = re.findall(r"\d+", user_message)
        if not numbers:
            return False, "لطفاً مقدار عددی وارد کنید."

        value = int(numbers[0])
        if not (q["min"] <= value <= q["max"]):
            return False, f"عدد باید بین {q['min']} تا {q['max']} باشد."

        return True, value

    if q["type"] == "enum":
        for c in q['values']:
            if c in user_message:
                return True, c

        return False, f"لطفاً یکی از این گزینه‌ها را انتخاب کنید: {', '.join(q['values'])}"
    if q["type"] == "description":
        return True , user_message  


    return False, "پاسخ نامعتبر است، لطفاً دوباره تلاش کنید."