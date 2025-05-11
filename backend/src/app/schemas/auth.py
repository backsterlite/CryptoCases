from pydantic import BaseModel, ConfigDict

class TelegramAuthRequest(BaseModel):
    init_data: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    
    model_config = ConfigDict(from_attributes=True)
