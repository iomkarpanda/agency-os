from pydantic import BaseModel
from datetime import datetime
import uuid



class UserInput(BaseModel):
    username:str
    password1:str
    password2:str
    display_name:str
    email:str
class UserOut(BaseModel):
    id: uuid.UUID
    username: str
    display: str
    email: str
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoginInput(BaseModel):
    email:str
    password:str