from datetime import datetime, timedelta
from app import api_keys_collection, usage_stats_collection, admin_users_collection
import secrets
import string

class APIKey:
    @staticmethod
    def generate_key():
        """Generate a secure API key"""
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    
    @staticmethod
    def create_api_key(owner_name, daily_limit=1000, expiry_days=30):
        """Create a new API key"""
        api_key = APIKey.generate_key()
        key_data = {
            "api_key": api_key,
            "owner_name": owner_name,
            "daily_limit": daily_limit,
            "requests_today": 0,
            "total_requests": 0,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=expiry_days),
            "is_active": True,
            "last_used": None
        }
        api_keys_collection.insert_one(key_data)
        return api_key
    
    @staticmethod
    def get_api_key(api_key):
        """Get API key data"""
        return api_keys_collection.find_one({"api_key": api_key})
    
    @staticmethod
    def validate_api_key(api_key):
        """Validate API key and check limits"""
        key_data = api_keys_collection.find_one({"api_key": api_key})
        
        if not key_data:
            return False, "Invalid API key"
        
        if not key_data.get("is_active", False):
            return False, "API key is inactive"
        
        # Check expiry date if it exists
        if key_data.get("expires_at"):
            if key_data.get("expires_at") < datetime.utcnow():
                return False, "API key has expired"
        elif key_data.get("expiry_date"):
            # Handle string date format
            expiry_str = key_data.get("expiry_date")
            try:
                expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
                if expiry_date < datetime.utcnow():
                    return False, "API key has expired"
            except:
                pass  # Skip validation if date format is invalid
        
        # Check daily limit
        if key_data.get("requests_today", 0) >= key_data.get("daily_limit", 1000):
            return False, "Daily request limit exceeded"
        
        return True, "Valid"
    
    @staticmethod
    def increment_usage(api_key):
        """Increment API key usage"""
        api_keys_collection.update_one(
            {"api_key": api_key},
            {
                "$inc": {"requests_today": 1, "total_requests": 1},
                "$set": {"last_used": datetime.utcnow()}
            }
        )
    
    @staticmethod
    def get_all_keys():
        """Get all API keys for admin panel"""
        return list(api_keys_collection.find())
    
    @staticmethod
    def delete_api_key(api_key):
        """Delete an API key"""
        return api_keys_collection.delete_one({"api_key": api_key})
    
    @staticmethod
    def reset_daily_counters():
        """Reset daily request counters (run via cron)"""
        api_keys_collection.update_many(
            {},
            {"$set": {"requests_today": 0}}
        )

class UsageStats:
    @staticmethod
    def log_request(api_key, endpoint, query, response_time, success):
        """Log API request for analytics"""
        usage_stats_collection.insert_one({
            "api_key": api_key,
            "endpoint": endpoint,
            "query": query,
            "response_time": response_time,
            "success": success,
            "timestamp": datetime.utcnow()
        })
    
    @staticmethod
    def get_usage_stats(api_key=None, days=7):
        """Get usage statistics"""
        match_filter = {"timestamp": {"$gte": datetime.utcnow() - timedelta(days=days)}}
        if api_key:
            match_filter["api_key"] = api_key
        
        return list(usage_stats_collection.find(match_filter).sort("timestamp", -1))
