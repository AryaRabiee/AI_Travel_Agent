from .config import MODEL_NAME_META_70 , OPENROUTER_API_KEY , URL
import json
import requests
from state.memory import history



def continue_chat():
    global history

    payload = {
        "model": MODEL_NAME_META_70,
        "messages": history
    }

    res = requests.post(URL, headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }, json=payload)

    if res.status_code != 200:
        return f"Error: {res.text}"

    reply = res.json()["choices"][0]["message"]["content"]

    history.append({
        "role": "assistant",
        "content": reply
    })

    return reply