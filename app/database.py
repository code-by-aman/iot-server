from pymongo import MongoClient
from app.config import settings

client = MongoClient(settings.DATABASE_URL)
db = client["iot_db"]
data_collection = db["sensor_data"]
user_collection = db["users"]