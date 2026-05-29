import requests
import json
import os

# API_KEY = "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"
API_KEY = "jina_7fedde13af3440c88d1cad18c001c003y14JgGjTbn-LcR3M2h2rOcLT82sI"

url_jina = "https://api.jina.ai/v1/embeddings"
url_open = "https://openrouter.ai/api/v1/embeddings"
api = "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"

cities_data = []  

DATA_DIR = "data3"

for filename in os.listdir(DATA_DIR):
    if filename.endswith(".md"):
        city_name = filename.replace(".md", "")

        print(f"Processing: {city_name}")

        text = open(os.path.join(DATA_DIR, filename), "r", encoding="utf-8").read()

        data = {
            "model": "openai/text-embedding-3-small",
            "task": "text-matching",
            "input": [text]
        }

        response = requests.post(url_open, headers={
            "Authorization": f"Bearer {api}",
            "Content-Type": "application/json"
        }, data=json.dumps(data))

        embedding = response.json()["data"][0]["embedding"]

        cities_data.append({
            "city": city_name,
            "text": text,
            "embedding": embedding
        })

with open("cities_embeddings_new_open.json", "w", encoding="utf-8") as f:
    json.dump(cities_data, f, ensure_ascii=False, indent=2)

print("DONE! Embeddings saved in cities_embeddings_new_open.json")