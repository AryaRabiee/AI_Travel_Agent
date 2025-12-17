import pandas as pd


data = {
    "city": ["تهران", "مشهد", "اصفهان","یزد","رشت","شیراز"],
    "religious": [0.1, 1.0, 0.3 , 0.25 , 0.1 , 0.3],
    "historical": [0.55, 0.45, 1.0 , 0.9 , 0.3 , 0.9],
    "modern_city": [1.0, 0.3, 0.7 , 0.4 , 0.4 , 0.7],
    "shopping": [1.0, 0.6, 0.5 , 0.4 , 0.4 , 0.5],
    "nightlife": [0.9, 0.2, 0.3 ,0.6 , 0.3 , 0.4],
    "expensive": [0.8, 0.4, 0.6 , 0.4 , 0.4 , 0.6],
    "hot": [0.8, 0.8, 0.8 , 0.95 , 0.3 , 0.4],
    "cold":[0.2 , 0.3 , 0.3 , 0.3 , 0.5 , 0.4],
    "four_seasons":[0.4 , 0.7 , 0.5 , 0.1 , 0.7 , 0.8],
    "nature":[0.0 , 0.0 , 0.0 , 0.0 , 1.0 , 0.1],

}


feaute_score = {
    "religious":0.5,
    "historical":0.65,
    "modern_city":0.8,
    "shopping":0.8,
    "nightlife":0.7,
    "expensive":0.4,
    "hot":0.4,
    "cold":0.45,
    "four_seasons":0.65,
    "nature":0.7
}


df = pd.DataFrame(data)
city_df = df.set_index("city")
feaute_weight = pd.Series(feaute_score)
print(feaute_weight.shape)