from fastapi import FastAPI ,HTTPException
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
    if not user_message.message or len(user_message.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="پیام خالی است")
    
    if len(user_message.message) > 1000:
        raise HTTPException(status_code=400, detail="پیام خیلی طولانی است")
    
    message = user_message.message.strip()
    
    session_id, session = session_store.get(user_message.session_id)

    reply = rag_answer(message, session)

    return {
        "session_id": session_id,
        "reply": reply
    }
