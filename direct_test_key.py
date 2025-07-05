#!/usr/bin/env python3
"""Create a test API key directly in database"""

import os
import secrets
from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB connection
MONGO_DB_URI = os.environ.get("MONGO_URI", "mongodb+srv://jaydipmore74:xCpTm5OPAfRKYnif@cluster0.5jo18.mongodb.net/?retryWrites=true&w=majority")
client = MongoClient(MONGO_DB_URI)
db = client.flaks_music_api

# Generate test API key
api_key = f"test_demo_{secrets.token_hex(16)}"
expiry_date = datetime.utcnow() + timedelta(days=7)

# Insert directly into database
key_data = {
    "api_key": api_key,
    "owner_name": "Demo User",
    "daily_limit": 100,
    "requests_today": 0,
    "total_requests": 0,
    "is_active": True,
    "created_at": datetime.utcnow(),
    "expires_at": expiry_date
}

try:
    db.api_keys.insert_one(key_data)
    print(f"✅ Test API key created: {api_key}")
    print(f"   Owner: Demo User")
    print(f"   Daily limit: 100")
    print(f"   Expires: {expiry_date}")
    print(f"\nTest it with:")
    print(f"curl 'http://localhost:5000/api/stream?api_key={api_key}&query=ye%20tune%20kya%20kiya'")
except Exception as e:
    print(f"❌ Error: {e}")