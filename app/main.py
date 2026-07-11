from fastapi import FastAPI
from llm.client import ask_model ,rag_answer
from models.message import UserMessage, BotResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_swagger import patch_fastapi
from dotenv import load_dotenv
from state.session_store import SessionStore

load_dotenv()
session_store = SessionStore()
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

    session_id, session = session_store.get(user_message.session_id)

    reply = rag_answer(
        user_message.message,
        session
    )

    return {
        "session_id": session_id,
        "reply": reply
    }
