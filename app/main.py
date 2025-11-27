from fastapi import FastAPI
from llm.client import ask_model
from models.message import UserMessage, BotResponse

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "سلام! من دستیار سفر شما هستم. پیام خود را به /chat بفرستید."}

@app.post("/chat", response_model=BotResponse)
def chat(user_message: UserMessage):
    reply = ask_model(user_message.message)
    return BotResponse(reply=reply)
