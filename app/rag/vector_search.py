
import os
from llm.model_manager import city_agent




def llm_select_best_city(user_profile, candidates):

    response = city_agent(user_profile , candidates)
    return response