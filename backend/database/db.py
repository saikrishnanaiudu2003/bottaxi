from common.utils import *
import certifi
from motor.motor_asyncio import AsyncIOMotorClient
from mongoengine import connect

# MongoDB connection setup for motor
client = AsyncIOMotorClient(
    'mongodb+srv://myAtlasDBUser:Sai123@myatlasclusteredu.qifwasp.mongodb.net/bottaxi?retryWrites=true&w=majority',
    tlsCAfile=certifi.where()
)

# Explicitly set the connection for mongoengine
connect(
    db="bottaxi",  # Name of the database
    host='mongodb+srv://myAtlasDBUser:Sai123@myatlasclusteredu.qifwasp.mongodb.net/bottaxi?retryWrites=true&w=majority',
    alias='default'  # Default alias that mongoengine will use
)
