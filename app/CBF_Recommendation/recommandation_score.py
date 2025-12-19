from .City_Matrix import feaute_weight ,city_df
from .model_weight import get_weight_for_feature
import pandas as pd
import numpy as np
from rag.vector_search import llm_select_best_city
from rag.retrieval import retrieve_top_cities
from state.handle_user import handle_user_message
ALPHA = 0.6
BETA = 0.4

def top_city(user_message):
    print("Start")
    user_profile_or_question = handle_user_message(user_message)
    if not isinstance(user_profile_or_question , dict):
        print("User profile incomplete, asking for more info...")
        return {"need_more_info": True, "message": user_profile_or_question}
    user_profile = user_profile_or_question
    print("The user profile is" , user_profile)
    candidate = retrieve_top_cities(user_profile)
    llm_score = llm_select_best_city(user_profile , candidate)
    print("LLM_Score" ,llm_score )
    llm_weight = pd.Series(llm_score)
    llm_weight = llm_weight.reindex(city_df.index).fillna(0)
    print("llm_weight" ,llm_weight )
    algo_norm_score_llm = (llm_weight - llm_weight.min()) / (llm_weight.max() - llm_weight.min() + 1e-8)
    print("algo_norm_score_llm" ,algo_norm_score_llm )
    model_score = get_weight_for_feature(user_message)
    model_weight = pd.DataFrame([model_score])

    user_weight_series = model_weight.iloc[0]

    final_weight = user_weight_series * feaute_weight
    score = city_df.mul(final_weight, axis=1).sum(axis=1)
    ranked_cities = score.sort_values(ascending=False)
    algo_scores = ranked_cities
    algo_norm = (algo_scores - algo_scores.min()) / (algo_scores.max() - algo_scores.min() + 1e-8)
    print("Feature Score:" , algo_norm)
    final_score = ALPHA * algo_norm + BETA * algo_norm_score_llm
    print("final_score :",final_score)
    top_city = final_score.idxmax()
    print("top3_city :",top_city , "type top city is" , type(top_city))
    return {"need_more_info": False, "top_city": top_city}


