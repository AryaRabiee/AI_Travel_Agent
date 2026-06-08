from llm.config import URL , MODEL_NAME_META_70 , OPENROUTER_API_KEY , MODEL_NAME_OPENAI
import requests
import json
from llm.log import logger
api = "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"
test_url = "https://openrouter.ai/api/v1"

def get_weight_for_feature(user_profile: str):
    profile_text = f"""
        days: {user_profile["profile"]['days']}
        weather: {user_profile["profile"]['weather']}
        places: {user_profile["profile"]['places']}
        budget: {user_profile["profile"]['budget']}
        interests: {user_profile["profile"]['interests']}
        description: {user_profile["profile"]['description']}
        """
    url = URL

    headers = {
        "Authorization": f"Bearer {api}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content":"""
                                You are an AI assistant that reads a user profile and returns a score for each travel feature.
                                Features: religious, historical, modern_city, shopping, nightlife, expensive, hot, cold, four_seasons, nature
                                Rules:
                                - Output MUST be a valid JSON object.
                                - Scores must be between 0 and 1.
                                - Do NOT include any explanation or extra text.
                                - Only output the features listed above.
                                - You should give the score for all feature
"""},
        {"role": "user", "content":profile_text},
    ]

    payload = {
        "model": MODEL_NAME_OPENAI,
        "messages": messages
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        logger.error("ERROR: %s", response.text)
        return False

    scores = response.json()["choices"][0]["message"]["content"].strip().lower()
    try:
        user_weights = json.loads(scores)
        logger.debug("User weights: %s, Type: %s", user_weights, type(user_weights))
    except json.JSONDecodeError as e:
        logger.error("JSON Error: %s", e)
        logger.error("RAW: %s", scores)
        return {}

    return user_weights