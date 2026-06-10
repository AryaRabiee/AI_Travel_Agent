import json
from .embedding import get_embedding
from .embedding import cosine_similarity
from state.handle_user import handle_user_message
import faiss
import numpy as np


DATA_PATH = "rag/cities_embeddings_new_open.json"
TOP_K = 3

def retrieve_top_cities(user_profile):
    print("Start retrive")

    print("profile user is :",user_profile,"type is :" , type(user_profile))
    if not isinstance(user_profile, dict):
        print(" user_profile is not a dict:", type(user_profile), user_profile)
        raise TypeError("user_profile must be a dict!")
    profile_text = (
        f"Days: {user_profile.get('days')}\n"
        f"Weather: {user_profile.get('weather')}\n"
        f"Interests: {user_profile.get('interests')}\n"
        f"Budget: {user_profile.get('budget')}\n"
        f"Description: {user_profile.get('description')}"
    )
    query_emb = get_embedding(profile_text)
    query_emb = np.array([query_emb] , dtype="float32")
    faiss.normalize_L2(query_emb)
    index = faiss.read_index("rag/cities_flat_open.index")
    k = 5
    D , I = index.search(query_emb , k)

    db = json.load(open(DATA_PATH, "r", encoding="utf-8"))

    top_cities = []
    for idx, score in zip(I[0], D[0]):
        print("idx" , idx)
        print("Score" , score)
        city_info = db[idx]
        print("City_info" , city_info)
        top_cities.append((
         city_info["city"],
            float(score),
            city_info["text"],)
            
        )
    top_cities.sort(key=lambda x : x[1] , reverse=True)

    print("retrival candidate" , top_cities[:TOP_K])

    return top_cities[:TOP_K]