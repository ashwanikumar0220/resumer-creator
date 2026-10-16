import jwt
from datetime import datetime,timedelta,timezone
import os
from typing import Any

JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM=os.getenv("JWT_ALGORITHM")
JWT_EXPIRE_MINUTES=int(os.getenv("JWT_EXPIRE_MINUTES",60))



# *******create token***********

def create_access_token(user_id:str):
    try:
        payload:dict[str,Any]={
        "user_id":user_id
        }

        expire = datetime.now(timezone.utc)+timedelta(minutes=JWT_EXPIRE_MINUTES)

        payload["exp"] = expire

        token =jwt.encode(
            payload,
            JWT_SECRET_KEY,
            algorithm=JWT_ALGORITHM
        )

        return token

    except Exception as e:
        print("JWT creation error:",e)
        return None

# *******verify token ********

def verify_access_token(token:str):
    try:
        payload=jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=JWT_ALGORITHM
        )
        return payload
    
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None

    except jwt.InvalidTokenError:
        print("Token invalid")
        return None

    except Exception as e:
        print("JWT verification error:",e)
        return None