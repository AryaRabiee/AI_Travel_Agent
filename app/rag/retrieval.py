import json
from .embedding import get_embeding
from .embedding import cosine_similarity
from state.handle_user import handle_user_message


DATA_PATH = "rag/cities_embeddings_new.json"
TOP_K = 3

def retrieve_top_cities(user_profile):

    print("profile user is :",user_profile,"type is :" , type(user_profile))
    if not isinstance(user_profile, dict):
        print("❌ user_profile is not a dict:", type(user_profile), user_profile)
        raise TypeError("user_profile must be a dict!")
    profile_text = (
        f"Days: {user_profile.get('days')}\n"
        f"Weather: {user_profile.get('weather')}\n"
        f"Interests: {user_profile.get('interests')}\n"
        f"Budget: {user_profile.get('budget')}\n"
        f"Description: {user_profile.get('description')}"
    )

    query_emb = get_embeding(profile_text)

    db = json.load(open(DATA_PATH, "r", encoding="utf-8"))

    scored = []

    for city in db:
        score = cosine_similarity(query_emb, city["embedding"])
        scored.append((city["city"], score, city["text"]))

    # sort top-k
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:TOP_K]

