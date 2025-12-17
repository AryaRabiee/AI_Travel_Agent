from llm.config import URL , MODEL_NAME_META_70 , OPENROUTER_API_KEY
import requests
import json

def get_weight_for_feature(message: str):
    url = URL

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content":"""
                                You are an AI assistant that reads a user message and returns a score for each travel feature.
                                Features: religious, historical, modern_city, shopping, nightlife, expensive, hot, cold, four_seasons, nature
                                Rules:
                                - Output MUST be a valid JSON object.
                                - Scores must be between 0 and 1.
                                - Do NOT include any explanation or extra text.
                                - Only output the features listed above.
                                - You should give the score for all feature
"""},
        {"role": "user", "content":message},
    ]

    payload = {
        "model": MODEL_NAME_META_70,
        "messages": messages
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        print("ERROR:", response.text)
        return False

    scores = response.json()["choices"][0]["message"]["content"].strip().lower()
    try:
        user_weights = json.loads(scores)
        print(user_weights , type(user_weights))
    except json.JSONDecodeError:
        print("خطا: JSON خروجی درست نیست!")

    return user_weights