import requests
import json
import os

# API_KEY = "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"
API_KEY = "jina_7fedde13af3440c88d1cad18c001c003y14JgGjTbn-LcR3M2h2rOcLT82sI"

url = "https://api.jina.ai/v1/embeddings"

cities_data = []  

DATA_DIR = "data3"

for filename in os.listdir(DATA_DIR):
    if filename.endswith(".md"):
        city_name = filename.replace(".md", "")

        print(f"Processing: {city_name}")

        text = open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8").read()

        data = {
            "model": "jina-embeddings-v3",
            "task": "text-matching",
            "input": [text]
        }

        response = requests.post(url, headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }, data=json.dumps(data))

        embedding = response.json()["data"][0]["embedding"]

        cities_data.append({
            "city": city_name,
            "text": text,
            "embedding": embedding
        })

with open("cities_embeddings_new.json", "w", encoding="utf-8") as f:
    json.dump(cities_data, f, ensure_ascii=False, indent=2)

print("DONE! Embeddings saved in cities_embeddings_new.json")