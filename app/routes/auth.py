from fastapi import APIRouter,HTTPException

from app.schemas.user import UserCreate,UserLogin
from app.database.mongodb import users_collection,otp_collection
from app.services.auth_service import hash_password,verify_password
from app.models.user import User
from app.models.otp import OTPVerification,OTPVerify
from app.services.otp_service import generate_otp,hash_otp,get_otp_expiry,verify_otp
from app.services.email_service import send_email
import time


router = APIRouter()

# ******** SIGNUP ROUTE ********

@router.post("/signup")
async def signup(user:UserCreate):
    existing_user=users_collection.find_one({"email":user.email})

    if existing_user:
        return{"message":"email already exists!"}

    hashed_password=hash_password(user.password)
    new_user=User(
        email=user.email,
        password_hash=hashed_password
    )

    result= users_collection.insert_one(new_user.model_dump())
    otp=generate_otp()
    otp_hash=hash_otp(otp)
    expires_at=get_otp_expiry()

    otp_record =OTPVerification(
        user_id=str(result.inserted_id),
        email=user.email,
        otp_hash=otp_hash,
        purpose="signup",
        expires_at=expires_at
        )
    otp_collection.insert_one(otp_record.model_dump())
    send_email(
        to_email=user.email,
        subject="Verify your email",
        html=f"<h1>You OTP is: {otp}</h1><p>This OTP will expire in 10 minutes.</p>"
        )
    return{
        "message":"User Created Successfully!"
    }

@router.post("/verify-otp")
def verify_user_otp(data:OTPVerify):

    otp_record = otp_collection.find_one({
        "email":data.email,
        "purpose":"signup"
    })

    if not otp_record:
        raise HTTPException(
            status_code=404,
            detail="OTP not found"
        )
    if otp_record["expires_at"]<int(time.time()):
        raise HTTPException(
            status_code=400,
            detail="OTP has expired"
        )
    if not verify_otp(data.otp,otp_record["otp_hash"]):
        raise HTTPException(
            status_code=400,
            detail="Invaild OTP"
        )
    users_collection.update_one(
        {"email":data.email},
        {"$set":{"is_verified":True}}
    )

    otp_collection.delete_one({
        "_id":otp_record["_id"]
    })

    return{
        "message":"Email verified successfully!"
    }


# ***** LOGIN ROUTE ******

@router.post("/login")
def login(user:UserLogin):

    existing_user=users_collection.find_one(
        {"email":user.email}
    )
    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    if not verify_password(user.password,existing_user["password_hash"]):
        raise HTTPException(
            status_code=401,
            detail="Invaild password"
        )
    if not existing_user["is_verified"]:
        raise HTTPException(
            status_code=403,
            detail="Please verify your gmail first"
        )
