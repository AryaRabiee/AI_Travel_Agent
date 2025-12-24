from llm.config import MODEL_EMBEDING_NAME_JINA , JINA_API_KEY , OPENROUTER_API_KEY_EMBEDDING , MODEL_EMBEDING_NAME
import requests
import numpy as np

def get_embeding(text:str):
    url = "https://api.jina.ai/v1/embeddings"
    # url = "https://openrouter.ai/api/v1/embeddings"

    headers = {
        "Authorization": f"Bearer {JINA_API_KEY}",
        "Content-Type": "application/json"
    }

    data={"model" : MODEL_EMBEDING_NAME_JINA , "input" :[text] , "task": "text-matching"}

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