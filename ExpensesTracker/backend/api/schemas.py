from pydantic import BaseModel

class AskRequest(BaseModel):
    user_id: str
    question: str

class AskResponse(BaseModel):
    answer: str
    intent: dict
    context_keys: list[str]