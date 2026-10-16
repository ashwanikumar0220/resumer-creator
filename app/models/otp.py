from datetime import UTC,datetime
from pydantic import BaseModel,Field

class OTPVerification(BaseModel):
    user_id:str
    email:str
    otp_hash:str
    expires_at:int
    purpose:str
    attempts:int=0
    created_at:int=Field(default_factory=lambda:int(datetime.now(UTC).timestamp()))

class OTPVerify(BaseModel):
    email:str
    otp:str