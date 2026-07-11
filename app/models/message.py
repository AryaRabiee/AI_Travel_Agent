from pydantic import BaseModel
from typing import Optional

class UserMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
class BotResponse(BaseModel):
    reply: str
