from pydantic import BaseModel

class AskRequest(BaseModel):
    user_id: str
    question: str

class AskResponse(BaseModel):
    answer_local: str
    answer_gemini: str
    intent: dict
    context_keys: list[str]