import requests
import json
import os


api_get_embedding = os.getenv("EMBEDDING_API_KEY")
url_embedding = os.getenv("EMBEDDING_URL")
cities_data = []  

DATA_DIR = "data"

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

        response = requests.post(url_embedding, headers={
            "Authorization": f"Bearer {api_get_embedding}",
            "Content-Type": "application/json"
        }, data=json.dumps(data))

        embedding = response.json()["data"][0]["embedding"]

        cities_data.append({
            "city": city_name,
            "text": text,
            "embedding": embedding
        })

with open("cities_embeddings_city_info.json", "w", encoding="utf-8") as f:
    json.dump(cities_data, f, ensure_ascii=False, indent=2)

print("DONE! Embeddings saved in cities_embeddings_city_info.json")