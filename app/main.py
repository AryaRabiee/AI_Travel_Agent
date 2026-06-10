from fastapi import FastAPI
from llm.client import ask_model ,rag_answer
from models.message import UserMessage, BotResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_swagger import patch_fastapi
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Travel Assistant" , summary="This is a AI_travel asisstant", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.post("/chat")
def chat(user_message: UserMessage):
    reply = rag_answer(user_message.message)
    return reply
