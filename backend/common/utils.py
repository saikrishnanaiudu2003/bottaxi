from fastapi import FastAPI,APIRouter,Request,UploadFile, Form, File,HTTPException,Depends

from bson import ObjectId
from datetime import datetime,timedelta
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
import os
import smtplib
from database.db import client
from models.models import *
import random
from twilio.rest import Client
import logging
import aiofiles
import os
from uuid import uuid4
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt


SECREAT_KEY="EVENTSKEY"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

def generate_random_otp() -> int:
    return random.randint(100000, 999999)

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'your_twilio_account_sid')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'your_twilio_auth_token')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', 'your_twilio_phone_number')

# Initialize Twilio client
client = Client("ACe4437d0d81fffb8dedd1a5cf9cc05323", "d3ebe5158a1f60e6dc1ec7d505949f9d")
async def send_otp(mobile_number: str, otp_code: str):
    """
    Sends OTP to the user's phone number using Twilio SMS service.
    """
    try:
        message = client.messages.create(
            body=f"Your Verification Code is {otp_code}",
            from_='+14243534550',  # Your Twilio number
            to="+918074743506"  # The user's phone number
        )
        print(f"OTP sent successfully to {mobile_number}. Message SID: {message.sid}")
    except Exception as e:
        raise Exception(f"Error sending OTP with Twilio: {str(e)}")
def validate_phone_number(phone_number):
    """Utility to validate a phone number."""
    return phone_number.isdigit() and len(phone_number) == 10


IMAGE_FOLDER = Path("uploads/captain_images")
IMAGE_FOLDER.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff"}

# Utility function to save images
async def save_image(file: UploadFile, folder: Path) -> str:
    ext = os.path.splitext(file.filename)[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"File type {ext} is not supported.")
    
    # Use the original file name provided by the user
    safe_filename = file.filename.replace(" ", "_")  # Replace spaces with underscores
    file_path = folder / safe_filename
    
    # Check if file already exists and append a counter if necessary
    counter = 1
    while file_path.exists():
        name, ext = os.path.splitext(safe_filename)
        file_path = folder / f"{name}_{counter}{ext}"
        counter += 1
    
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    
    return str(file_path)

security = HTTPBearer() 

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_token(user_id):
    expiration_time = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
    payload = {
        "user_id": user_id,
        "exp": expiration_time
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)  # Use the same SECRET_KEY
    return token

def get_current_user(token: HTTPAuthorizationCredentials = Depends(security)) -> str:
    try:
        print(f"Token received: {token.credentials}")  # Debugging print
        
        # Decode the JWT token
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        
        print(f"Decoded payload: {payload}")  # Debugging print
        
        # Extract user_id from payload
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: user_id missing.")
        
        # Ensure the user ID is valid
        if not ObjectId.is_valid(user_id):
            raise HTTPException(status_code=400, detail="Invalid user ID.")
        
        return user_id
    except jwt.PyJWTError as e:
        print(f"Error decoding token: {e}")  # Debugging print
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    except Exception as e:
        print(f"Unexpected error: {e}")  # Debugging print
        raise HTTPException(status_code=500, detail="Internal Server Error")