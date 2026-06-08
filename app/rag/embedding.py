from llm.config import MODEL_EMBEDING_NAME_JINA , JINA_API_KEY , OPENROUTER_API_KEY_EMBEDDING , MODEL_EMBEDING_NAME
import requests
import numpy as np
api = "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"
def get_embeding(text:str):
    #url = "https://api.jina.ai/v1/embeddings"
    url = "https://openrouter.ai/api/v1/embeddings"

    headers = {
        "Authorization": f"Bearer {api}",
        "Content-Type": "application/json"
    }

    data={"model" : MODEL_EMBEDING_NAME , "input" :[text] , "task": "text-matching"}

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