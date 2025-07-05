"""
Quick Start - Flaks Music API
============================

Simple script to test the API quickly.
Perfect for beginners!

Steps:
1. Get API key from https://t.me/jalwagameofficial
2. Replace YOUR_API_KEY below
3. Run: python quick_start.py
"""

import requests

# Your configuration
API_KEY = "YOUR_API_KEY"  # Replace with your actual API key
API_URL = "https://your-domain.replit.app"  # Replace with your actual domain

def search_song(song_name):
    """Search for a song and get stream URL"""
    
    print(f"🎵 Searching for: {song_name}")
    
    # API request
    url = f"{API_URL}/api/stream"
    params = {
        'api_key': API_KEY,
        'query': song_name
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ Song found!")
                print(f"📀 Title: {data.get('title')}")
                print(f"👨‍🎤 Artist: {data.get('artist')}")
                print(f"⏱️ Duration: {data.get('duration')}")
                print(f"🎧 Quality: {data.get('quality')}")
                print(f"⚡ Response Time: {data.get('response_time')}s")
                print(f"🔗 Stream URL: {data.get('stream_url')}")
                print(f"🚀 Powered by: {data.get('powered_by')}")
                return data
            else:
                print("❌ No song found")
                return None
        else:
            print(f"❌ Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None

def main():
    """Main function"""
    print("🎵 Flaks Music API - Quick Start")
    print("=" * 40)
    
    # Check if API key is set
    if API_KEY == "YOUR_API_KEY":
        print("❌ Please set your API key first!")
        print("💬 Get your API key from: https://t.me/jalwagameofficial")
        return
    
    # Test with popular songs
    test_songs = [
        "Tum Hi Ho",
        "Shape of You", 
        "Blinding Lights"
    ]
    
    print("🧪 Testing with popular songs...\n")
    
    for song in test_songs:
        print("-" * 40)
        result = search_song(song)
        print()
        
        if not result:
            break
    
    print("✅ Quick start test completed!")
    print("\n📖 Now you can:")
    print("1. Use this API in your Telegram bot")
    print("2. Integrate with Discord bot")
    print("3. Build web applications")
    print("4. Create music streaming apps")
    
    print("\n📚 Check these files for examples:")
    print("- python_api_example.py (Detailed Python usage)")
    print("- telegram_bot_example.py (Complete Telegram bot)")

if __name__ == "__main__":
    main()