import re
from llm.log import logger

QUESTIONS = {
    0: {
        "question": "چند روز قصد سفر دارید؟",
        "type": "number",
        "min": 1,
        "max": 30,
        "key": "days"  # ✅ اضافه کن
    },
    1: {
        "question": "چه نوع آب‌وهوایی دوست دارید؟",
        "type": "choices",
        "choices": ["گرم", "خنک", "سرد", "معتدل"],
        "key": "weather"  # ✅
    },
    2: {
        "question": "به چه نوع جاهایی علاقه‌مندید؟",
        "type": "choices",
        "choices": ["تاریخی", "طبیعت", "شهری", "تفریحی","زیارتی"],
        "key": "places"  # ✅
    },
    3: {
        "question": "بودجه تقریبی شما چقدره؟",
        "type": "choices",
        "choices": ["کم", "متوسط", "زیاد"],
        "key": "budget"  # ✅
    },
    4: {
        "question": "علاقه‌مندی خاصی دارید؟",
        "type": "choices",
        "choices": ["طبیعت","کوه نوردی","خرید", "غذا", "تفریح", "زیارتی"],
        "key": "interests"  # ✅
    },
    5: {
        "question": "برای اینکه بهتر بتونم به شما پیشنهاد بدم لطفا یه توضیحات کلی درباره مقصدی که میخواین برین بگین",
        "type": "description",
        "key": "description"  # ✅
    }
}

def validation_answer(step, user_message, questions):
    if step not in questions:
        return False, "مرحله نامعتبر است"
    
    q = questions[step]

    if q["type"] == "number":
        numbers = re.findall(r"\d+", user_message)
        if not numbers:
            return False, "لطفاً مقدار عددی وارد کنید."

        value = int(numbers[0])
        
        if not (q["min"] <= value <= q["max"]):
            return False, f"عدد باید بین {q['min']} تا {q['max']} باشد."

        return True, value

    if q["type"] == "choices":  # ✅ تغییر "enum" → "choices"
        for c in q['choices']:  # ✅ تغییر "values" → "choices"
            if c in user_message:
                return True, c

        return False, f"لطفاً یکی از این گزینه‌ها را انتخاب کنید: {', '.join(q['choices'])}"
    
    if q["type"] == "description":
        if not user_message or len(user_message.strip()) < 5:
            return False, "لطفاً توضیحات بیشتری بنویسید (حداقل ۵ کاراکتر)"
        
        return True, user_message.strip()

    return False, "پاسخ نامعتبر است، لطفاً دوباره تلاش کنید."