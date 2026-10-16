
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI =os.getenv("MONGO_URI")



client = MongoClient(MONGO_URI)

database=client["resume_builder"]
users_collection=database["users"]
otp_collection =database["otp_verifications"]


try:
    client.admin.command('ping')
    print("********You successfully connected to MongoDB!********")
except Exception as e:
    print(e)

