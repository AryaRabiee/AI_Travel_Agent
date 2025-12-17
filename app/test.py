from CBF_Recommendation.City_Matrix import feaute_weight ,df
from CBF_Recommendation.model_weight import get_weight_for_feature
import pandas as pd
import numpy as np

user_message = "میخوام یک سفر طبیعت‌گردی داشته باشم، هوا خنک باشه و بودجه متوسط"
print("srart")
model_score = get_weight_for_feature(user_message)
model_weight = pd.DataFrame([model_score])
print("done")
scores = model_weight * feaute_weight
final_weight = scores.iloc[0]

city_scores = df.mul(final_weight, axis=1).sum(axis=1)

ranked_cities = city_scores.sort_values(ascending=False)



print(ranked_cities)