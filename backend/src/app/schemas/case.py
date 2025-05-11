from pydantic import BaseModel

class CaseOpenRequest(BaseModel):
    case_id: str

class CaseResult(BaseModel):
    token: str
    network: str
    amount: str