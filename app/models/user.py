from datetime import UTC, datetime
from pydantic import BaseModel,Field

class User(BaseModel):
    email:str
    password_hash:str
    is_verified:bool=False
    
    otp_hash:str | None=None
    otp_expiry:int | None=None

    role:str="user"
    created_at:int=Field(default_factory=lambda:int(datetime.now(UTC).timestamp()))
