# file: db_config.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file (optional)
load_dotenv()

MONGO_URI = "mongodb://localhost:27017/"

if not MONGO_URI:
    raise Exception("MONGO_URI environment variable not set! Please set it to your MongoDB connection string.")

client = MongoClient(MONGO_URI)
db = client.get_database('smart_ebanking') # You can name your database here

# You can create collections here to be imported by services
users_collection = db.users
accounts_collection = db.accounts
transactions_collection = db.transactions
billers_collection = db.billers
  