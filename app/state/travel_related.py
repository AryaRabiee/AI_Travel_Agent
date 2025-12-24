from llm.config import URL , MODEL_NAME_META_70 , OPENROUTER_API_KEY
import requests
from state.memory import history
from llm.model_manager import intent_agent


def is_travel_related(message: str) -> bool:


    response = intent_agent(message)
    print("response related is :" ,response)

    return response