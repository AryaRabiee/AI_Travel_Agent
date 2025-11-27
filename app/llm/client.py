import os
import requests

OPENROUTER_API_KEY = "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"
SYSTEM_PROMPT = """
You are a professional **Travel Assistant AI**, specialized in **Iranian cities and domestic tourism**.

Your responsibilities:
- Provide accurate and practical travel information about Iranian destinations.
- Suggest must-see places, activities, foods, and cultural highlights.
- Provide approximate travel costs, transportation options, distances, and best travel seasons.
- Always ask clarifying questions if the user request is incomplete or ambiguous.
- Prefer information coming from RAG (retrieved documents) over your own guesses.

Critical Rules:
1. **Never hallucinate.** If you are unsure say: "اطلاعات دقیقی درباره این موضوع ندارم."
2. **Never invent locations, distances, or historical facts.**
3. **Only answer travel-related questions.**
4. If the user asks something unrelated to travel → politely redirect them back to travel topics.
5. Keep your tone friendly, clear, and concise.
6. When giving recommendations, include short reasons (why it’s good).
7. If multiple answers are possible, ask a short clarifying question first.

Response Style:
- Use short paragraphs.
- Prefer Persian (Farsi) unless the user requests English.
- Provide structured, useful answers (lists are fine).

Your purpose:
Help the user plan their trip smoothly and realistically.
"""


MODEL_NAME = "nousresearch/hermes-3-llama-3.1-405b:free"    
# MODEL_NAME = 'deepseek/deepseek-chat-v3-0324:free'
#meta-llama/llama-3.3-70b-instruct:free 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
# meta-llama/llama-3.3-70b-instruct:free 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 for 
def ask_model(message: str) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        return data['choices'][0]['message']['content']
    else:
        return f"Error {response.status_code}: {response.text}"
