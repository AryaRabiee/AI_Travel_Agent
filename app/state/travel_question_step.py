from .state_user import user_profile

def next_travel_question():
    if user_profile["step"] == 0:
        return "چند روز قصد سفر دارید؟"
    if user_profile["step"] == 1:
        return "چه نوع آب‌وهوایی دوست دارید؟ (گرم، خنک، سرد...)"
    if user_profile["step"] == 2:
        return "به چه نوع جاهایی علاقه‌مندید؟ (تاریخی، طبیعت، شهری...)"
    if user_profile["step"] == 3:
        return "بودجه تقریبی شما چقدره؟"
    if user_profile["step"] == 4:
        return "علاقه‌مندی خاصی دارید؟ (غذا، خرید، کوه‌نوردی...)"
    if user_profile["step"] == 5:
        return " برای اینکه بهتر بتونم به شما پیشنهاد بدم لطفا یه توضیحات کلی درباره مقصدی که میخواین برین بگین"

    return None 
