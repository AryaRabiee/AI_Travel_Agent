from llm.config import URL , MODEL_NAME_META_70 , OPENROUTER_API_KEY
import requests
from state.memory import history


def is_travel_related(message: str) -> bool:
    url = URL

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = [
        {"role": "system", "content": "You are a classifier. Reply ONLY with 'Yes' or 'No'."},
        {"role": "user", "content": f"Is the following message about travel? {message}"}
    ]

    payload = {
        "model": MODEL_NAME_META_70,
        "messages": messages
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        print("ERROR:", response.text)
        return False

    answer = response.json()["choices"][0]["message"]["content"].strip().lower()

    return answer