"""
Flaks Music API - Python Usage Example
====================================

Simple Python script to use the Flaks Music API for music streaming.
Perfect for Telegram bots, Discord bots, or any Python application.

Requirements:
- requests library: pip install requests
- aiohttp library (for async): pip install aiohttp

Usage:
1. Get your API key from https://t.me/jalwagameofficial
2. Replace 'YOUR_API_KEY' with your actual API key
3. Run the script: python python_api_example.py
"""

import requests
import asyncio
import aiohttp
import time

# Configuration
API_BASE_URL = "https://your-domain.replit.app"  # Replace with your actual domain
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key

class FlaksMusicAPI:
    """Simple Python wrapper for Flaks Music API"""
    
    def __init__(self, api_key, base_url=API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
    
    def search_and_stream(self, query):
        """
        Search for music and get stream URL
        
        Args:
            query (str): Song name, artist, or lyrics
            
        Returns:
            dict: Music info with stream URL or None if failed
        """
        try:
            url = f"{self.base_url}/api/stream"
            params = {
                'api_key': self.api_key,
                'query': query
            }
            
            print(f"🎵 Searching for: {query}")
            start_time = time.time()
            
            response = self.session.get(url, params=params, timeout=30)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Found: {data.get('title')} by {data.get('artist')}")
                    print(f"⚡ Response time: {response_time:.2f}s")
                    return data
                else:
                    print(f"❌ No results found for: {query}")
                    return None
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
            return None
    
    def search_only(self, query):
        """
        Search for music without stream URL (faster)
        
        Args:
            query (str): Song name or artist
            
        Returns:
            dict: Music info without stream URL
        """
        try:
            url = f"{self.base_url}/api/search"
            params = {
                'api_key': self.api_key,
                'query': query
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Search failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Search exception: {str(e)}")
            return None
    
    def get_trending(self):
        """Get trending music"""
        try:
            url = f"{self.base_url}/api/trending"
            params = {'api_key': self.api_key}
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Trending exception: {str(e)}")
            return None
    
    def check_status(self):
        """Check API key status and usage"""
        try:
            url = f"{self.base_url}/api/status"
            params = {'api_key': self.api_key}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception as e:
            print(f"Status check exception: {str(e)}")
            return None

# Async version for better performance
class AsyncFlaksMusicAPI:
    """Async Python wrapper for Flaks Music API"""
    
    def __init__(self, api_key, base_url=API_BASE_URL):
        self.api_key = api_key
        self.base_url = base_url
    
    async def search_and_stream(self, query):
        """Async search and stream"""
        try:
            url = f"{self.base_url}/api/stream"
            params = {
                'api_key': self.api_key,
                'query': query
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=30) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data if data.get('success') else None
                    else:
                        return None
                        
        except Exception as e:
            print(f"Async search exception: {str(e)}")
            return None
    
    async def search_multiple(self, queries):
        """Search multiple songs concurrently"""
        tasks = [self.search_and_stream(query) for query in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [result for result in results if result and not isinstance(result, Exception)]

# Example usage functions
def basic_usage_example():
    """Basic usage example"""
    print("=== Basic Usage Example ===")
    
    # Initialize API
    api = FlaksMusicAPI(API_KEY)
    
    # Search for a song
    result = api.search_and_stream("Tum Hi Ho")
    
    if result:
        print(f"Title: {result['title']}")
        print(f"Artist: {result['artist']}")
        print(f"Duration: {result['duration']}")
        print(f"Stream URL: {result['stream_url']}")
        print(f"Quality: {result['quality']}")
        print(f"Response Time: {result['response_time']}s")
    else:
        print("No results found")

def telegram_bot_example():
    """Example for Telegram bot usage"""
    print("\n=== Telegram Bot Example ===")
    
    api = FlaksMusicAPI(API_KEY)
    
    # Simulate user request
    user_query = "Shape of You Ed Sheeran"
    
    result = api.search_and_stream(user_query)
    
    if result:
        # This is what you would send to Telegram
        stream_url = result['stream_url']
        title = result['title']
        artist = result['artist']
        
        print(f"📱 Telegram Bot Response:")
        print(f"🎵 Now playing: {title} by {artist}")
        print(f"🔗 Stream URL: {stream_url}")
        print(f"💨 Found in {result['response_time']}s")
        
        # For Telegram: bot.send_audio(chat_id, stream_url, title=title, performer=artist)
    else:
        print("❌ Song not found")

def lyrics_search_example():
    """Example of searching by lyrics"""
    print("\n=== Lyrics Search Example ===")
    
    api = FlaksMusicAPI(API_KEY)
    
    # Search using lyrics
    lyrics_query = "main rahoon ya na rahoon"
    
    result = api.search_and_stream(lyrics_query)
    
    if result:
        print(f"🎤 Found song from lyrics: {result['title']}")
        print(f"👨‍🎤 Artist: {result['artist']}")
        print(f"🎧 Stream URL: {result['stream_url']}")
    else:
        print("No song found from these lyrics")

async def async_usage_example():
    """Async usage example"""
    print("\n=== Async Usage Example ===")
    
    api = AsyncFlaksMusicAPI(API_KEY)
    
    # Search multiple songs at once
    queries = [
        "Tum Hi Ho",
        "Shape of You",
        "Blinding Lights",
        "Levitating"
    ]
    
    print(f"🔄 Searching {len(queries)} songs concurrently...")
    start_time = time.time()
    
    results = await api.search_multiple(queries)
    
    end_time = time.time()
    print(f"⚡ Found {len(results)} songs in {end_time - start_time:.2f}s")
    
    for result in results:
        if result:
            print(f"  ✅ {result['title']} by {result['artist']}")

def check_api_status():
    """Check API status"""
    print("\n=== API Status Check ===")
    
    api = FlaksMusicAPI(API_KEY)
    status = api.check_status()
    
    if status:
        print(f"✅ API Status: Active")
        print(f"📊 Usage: {status.get('usage', 'N/A')}")
        print(f"📈 Limit: {status.get('limit', 'N/A')}")
    else:
        print("❌ Failed to check API status")

def main():
    """Main function to run examples"""
    print("🎵 Flaks Music API - Python Examples")
    print("=" * 50)
    
    # Check if API key is set
    if API_KEY == "YOUR_API_KEY":
        print("❌ Please set your API key first!")
        print("💬 Get your API key from: https://t.me/jalwagameofficial")
        return
    
    # Run examples
    basic_usage_example()
    telegram_bot_example()
    lyrics_search_example()
    check_api_status()
    
    # Run async example
    print("\n🔄 Running async example...")
    asyncio.run(async_usage_example())

if __name__ == "__main__":
    main()