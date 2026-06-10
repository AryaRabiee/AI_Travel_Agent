import requests
import numpy as np
import os

api_get_embedding = os.getenv("EMBEDDING_API")

def get_embedding(text:str):
    #url = "https://api.jina.ai/v1/embeddings"
    url = "https://openrouter.ai/api/v1/embeddings"

    headers = {
        "Authorization": f"Bearer {api_get_embedding}",
        "Content-Type": "application/json"
    }

    data={"model" : "openai/text-embedding-3-small"  , "input" :[text] , "task": "text-matching"}

    response = requests.post(url , headers=headers , json=data)
    response_json = response.json()

    try:
        return response_json["data"][0]["embedding"]
    except KeyError:
        print("ERROR :" ,response_json)
        return None
    


def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))