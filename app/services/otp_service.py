import secrets
from pwdlib import PasswordHash
import time

password_hash=PasswordHash.recommended()

def generate_otp()->str:
    return str(secrets.randbelow(900000)+100000)

def hash_otp(otp:str)->str:
    return password_hash.hash(otp)

def get_otp_expiry()->int:
    return int(time.time())+600

def verify_otp(plain_otp:str,hashed_otp:str)->bool:
    return password_hash.verify(plain_otp,hashed_otp)