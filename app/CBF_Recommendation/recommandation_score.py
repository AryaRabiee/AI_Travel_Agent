from .City_Matrix import feaute_weight ,city_df
from .model_weight import get_weights_from_profile
import pandas as pd
import numpy as np
from rag.vector_search import llm_select_best_city
from rag.retrieval import retrieve_top_cities
from llm.log import logger
ALPHA = 0.7
BETA = 0.3

def top_city(user_profile):
    logger.info("profile is %s", user_profile)
    logger.info("Start func top_city")
    
    candidate = retrieve_top_cities(user_profile)
    logger.info("in top city candidate is %s" , candidate)
    
    llm_score = llm_select_best_city(user_profile , candidate)
    logger.info("in top city llm_score is %s" , llm_score)
    
    llm_score = {k.lower(): v for k, v in llm_score.items()}
    logger.info("in top city llm_score (normalized) is %s" , llm_score)
    
    llm_weight = pd.Series(0, index=city_df.index)
    for city, score in llm_score.items():
        if city in city_df.index:
            llm_weight[city] = score
    logger.info("in top city llm_weight (expanded) is %s" , llm_weight)
    
    algo_norm_score_llm = (llm_weight - llm_weight.min()) / (llm_weight.max() - llm_weight.min() + 1e-8)
    logger.info("in top city algo_norm_score_llm is %s" , algo_norm_score_llm)
    
    model_score = get_weights_from_profile(user_profile)
    logger.info("in top city model_score is %s" , model_score)
    
    user_weight_series = pd.Series(model_score)
    final_weight = user_weight_series * feaute_weight
    logger.info("in top city final_weight is %s" , final_weight)
    
    algo_scores = city_df.mul(final_weight, axis=1).sum(axis=1)
    logger.info("in top city algo_scores is %s" , algo_scores)
    
    algo_norm = (algo_scores - algo_scores.min()) / (algo_scores.max() - algo_scores.min() + 1e-8)
    logger.info("in top city algo_norm is %s" , algo_norm)
    
    final_score = ALPHA * algo_norm + BETA * algo_norm_score_llm
    logger.info("in top city final_score is %s" , final_score)
    
    top_city = final_score.idxmax()
    logger.info("top city is : %s , type top city is: %s" , top_city , type(top_city))
    
    return {"need_more_info": False, "top_city": top_city}

