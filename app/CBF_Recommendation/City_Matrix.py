import pandas as pd


data = {
    "city": ["تهران", "مشهد", "اصفهان"],
    "religious": [0.1, 1.0, 0.2],
    "historical": [0.4, 0.5, 1.0],
    "modern_city": [1.0, 0.3, 0.4],
    "shopping": [1.0, 0.6, 0.5],
    "nightlife": [0.9, 0.2, 0.3],
    "expensive": [0.8, 0.4, 0.6],
    "hot": [1.0, 0.0, 1.0]
}

df = pd.DataFrame(data)

print(df)