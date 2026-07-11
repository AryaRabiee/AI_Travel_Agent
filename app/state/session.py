from dataclasses import dataclass, field

@dataclass
class Session:

    history: list = field(default_factory=list)

    user_profile: dict | None = None

    conversation_state: dict = field(default_factory=lambda: {
        "stage": "NORMAL",
        "top_city": None,
        "current_city": None,
    })

    generate_plan: dict = field(default_factory=lambda: {
        "city":None,
        "city_message":"لطفا شهر خود را انتخاب کنید",
        "days_message":"لطفا تعداد روز ها را مشخص کنید",
        "days":None,
        "need_city_or_days":False
    })