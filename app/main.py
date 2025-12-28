from fastapi import FastAPI
from llm.client import ask_model ,rag_answer
from models.message import UserMessage, BotResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # برای توسعه
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# @app.get("/")
# def read_root():
#     return {"message": "سلام! من دستیار سفر شما هستم. پیام خود را به /chat بفرستید."}
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.post("/chat")
def chat(user_message: UserMessage):
    reply = rag_answer(user_message.message)
    return reply
