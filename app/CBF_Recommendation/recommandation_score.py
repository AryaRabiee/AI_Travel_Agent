from .City_Matrix import feaute_weight ,city_df
from .model_weight import get_weight_for_feature
import pandas as pd
import numpy as np
from rag.vector_search import llm_select_best_city
from rag.retrieval import retrieve_top_cities
from llm.log import logger
ALPHA = 0.6
BETA = 0.4

def top_city(user_profile):
    logger.info("profile is %s", user_profile)
    logger.info("Start func top_city")
    candidate = retrieve_top_cities(user_profile)
    logger.info("in top city candidate is %s" , candidate)
    llm_score = llm_select_best_city(user_profile , candidate)
    logger.info("in top city llm_score is %s" , llm_score)
    llm_weight = pd.Series(llm_score)
    logger.info("in top city llm_weight is %s" , llm_weight)
    llm_weight = llm_weight.reindex(city_df.index).fillna(0)
    logger.info("in top city llm_weight is %s" , llm_weight)
    algo_norm_score_llm = (llm_weight - llm_weight.min()) / (llm_weight.max() - llm_weight.min() + 1e-8)
    logger.info("in top city algo_norm_score_llm is %s" , algo_norm_score_llm)
    model_score = get_weight_for_feature(user_profile)
    logger.info("in top city model_score is %s" , model_score)
    model_weight = pd.DataFrame([model_score])
    logger.info("in top city model_weight is %s" , model_weight)

    user_weight_series = model_weight.iloc[0]

    final_weight = user_weight_series * feaute_weight
    logger.info("in top city final_weight is %s" , final_weight)
    score = city_df.mul(final_weight, axis=1).sum(axis=1)
    ranked_cities = score.sort_values(ascending=False)
    logger.info("in top city ranked_cities is %s" , ranked_cities)
    algo_scores = ranked_cities
    algo_norm = (algo_scores - algo_scores.min()) / (algo_scores.max() - algo_scores.min() + 1e-8)
    final_score = ALPHA * algo_norm + BETA * algo_norm_score_llm
    logger.info("in top city final_score is %s" , final_score)
    top_city = final_score.idxmax()
    logger.info("top city is : %s , type top city is: %s" , top_city , type(top_city))
    return {"need_more_info": False, "top_city": top_city}


