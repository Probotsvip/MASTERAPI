#!/usr/bin/env python3
"""Create a test API key for demonstration"""

import os
from pymongo import MongoClient
from models import APIKey

# Setup MongoDB connection
MONGO_DB_URI = os.environ.get("MONGO_URI", "mongodb+srv://jaydipmore74:xCpTm5OPAfRKYnif@cluster0.5jo18.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient(MONGO_DB_URI)
db = client.flaks_music_api

# Create test API key
print("Creating test API key...")
try:
    api_key = APIKey.create_api_key("Test User", 100, 7)
    print(f"✅ Test API key created: {api_key}")
    print(f"   Owner: Test User")
    print(f"   Daily limit: 100")
    print(f"   Expiry: 7 days")
except Exception as e:
    print(f"❌ Error creating API key: {e}")