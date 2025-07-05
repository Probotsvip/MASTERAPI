#!/usr/bin/env python3
"""Quick script to create a test API key"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import APIKey

# Create a test API key
test_key = APIKey.create_api_key("Demo User", daily_limit=1000, expiry_days=30)
print(f"✅ Test API key created: {test_key}")
print(f"📋 Copy this key for testing: {test_key}")