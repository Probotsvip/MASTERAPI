#!/usr/bin/env python3
"""
Flaks Music API - Example Usage for Telegram Music Bots
========================================================

This script demonstrates how to use the Flaks Music API in your Telegram music bot.
No more IP bans, cookie issues, or yt-dlp problems!

Response time: 0.3-0.5 seconds
No cookies needed
No IP bans
Direct stream URLs compatible with VLC and Telegram

Usage:
1. Get your API key from the admin panel
2. Replace YOUR_API_KEY with your actual key
3. Use the functions in your Telegram bot
"""

import aiohttp
import asyncio
import logging

# Your API Configuration
YOUR_API_KEY = "CtFbvBpJso0rYZe5wCZhsXco482AaT8D"  # Replace with your actual API key
MUSIC_API_BASE_URL = "http://localhost:5000"  # Replace with your deployed URL

async def get_audio_stream_from_api(query: str):
    """
    Get audio stream URL from Flaks Music API
    
    Args:
        query (str): Song name, artist, or search query
    
    Returns:
        tuple: (stream_url, title) or (None, None) if failed
    """
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                'query': query,
                'api_key': YOUR_API_KEY
            }
            
            async with session.get(
                f"{MUSIC_API_BASE_URL}/api/stream",
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"✅ Found: {data.get('title')} by {data.get('artist')}")
                    print(f"⚡ Response time: {data.get('response_time'):.2f}s")
                    print(f"🎵 Source: {data.get('source')}")
                    print(f"🔊 Quality: {data.get('quality')}")
                    print(f"🔗 Stream URL: {data.get('stream_url')}")
                    
                    return data.get('stream_url'), data.get('title', query)
                    
                elif response.status == 401:
                    print("❌ Invalid API key or limit exceeded")
                    return None, None
                    
                elif response.status == 404:
                    print(f"❌ No music found for: {query}")
                    return None, None
                    
                else:
                    print(f"❌ API error: {response.status}")
                    return None, None
                    
    except Exception as e:
        logging.error(f"Error calling Flaks Music API: {str(e)}")
        return None, None

async def search_music_without_stream(query: str):
    """
    Search for music without getting stream URL (faster for search results)
    
    Args:
        query (str): Search query
    
    Returns:
        dict: Music info or None if failed
    """
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                'query': query,
                'api_key': YOUR_API_KEY
            }
            
            async with session.get(
                f"{MUSIC_API_BASE_URL}/api/search",
                params=params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        'title': data.get('title'),
                        'artist': data.get('artist'),
                        'duration': data.get('duration'),
                        'source': data.get('source'),
                        'quality': data.get('quality')
                    }
                    
                return None
                
    except Exception as e:
        logging.error(f"Error searching music: {str(e)}")
        return None

async def get_trending_music():
    """
    Get trending music from JioSaavn
    
    Returns:
        list: List of trending songs
    """
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                'api_key': YOUR_API_KEY,
                'source': 'jiosaavn',
                'limit': 10
            }
            
            async with session.get(
                f"{MUSIC_API_BASE_URL}/api/trending",
                params=params,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    return data.get('trending', [])
                    
                return []
                
    except Exception as e:
        logging.error(f"Error getting trending music: {str(e)}")
        return []

async def check_api_status():
    """
    Check your API key status and usage
    
    Returns:
        dict: API status info
    """
    try:
        async with aiohttp.ClientSession() as session:
            params = {'api_key': YOUR_API_KEY}
            
            async with session.get(
                f"{MUSIC_API_BASE_URL}/api/status",
                params=params,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    
                    print(f"👤 Owner: {data.get('owner')}")
                    print(f"📊 Usage: {data.get('requests_today')}/{data.get('daily_limit')} requests today")
                    print(f"📈 Total requests: {data.get('total_requests')}")
                    print(f"⏰ Expires: {data.get('expires_at')}")
                    print(f"✅ Status: {'Active' if data.get('is_active') else 'Inactive'}")
                    
                    return data
                    
                return None
                
    except Exception as e:
        logging.error(f"Error checking API status: {str(e)}")
        return None

# Example for Telegram Bot Integration
async def telegram_music_handler(query: str):
    """
    Example function for handling music requests in Telegram bot
    
    Args:
        query (str): User's music request
    
    Returns:
        str: Stream URL for Telegram voice chat or file sending
    """
    print(f"🔍 Searching for: {query}")
    
    # Get stream URL
    stream_url, title = await get_audio_stream_from_api(query)
    
    if stream_url:
        print(f"🎵 Ready to stream: {title}")
        # This URL can be used directly in:
        # - ctx.bot.send_audio() for file sending
        # - VLC for voice chat streaming  
        # - FFmpeg for processing
        return stream_url
    else:
        print("❌ Could not find the requested music")
        return None

# Demo functions
async def demo_basic_usage():
    """Demo: Basic music streaming"""
    print("\n🎵 DEMO: Basic Music Streaming")
    print("=" * 50)
    
    queries = ["tum hi ho", "shape of you", "despacito", "blinding lights"]
    
    for query in queries:
        print(f"\n🔍 Searching: {query}")
        stream_url, title = await get_audio_stream_from_api(query)
        
        if stream_url:
            print(f"✅ Success: {title}")
        else:
            print(f"❌ Failed: {query}")
        
        await asyncio.sleep(1)  # Rate limiting

async def demo_api_status():
    """Demo: Check API key status"""
    print("\n📊 DEMO: API Key Status")
    print("=" * 50)
    
    await check_api_status()

async def demo_trending():
    """Demo: Get trending music"""
    print("\n🔥 DEMO: Trending Music")
    print("=" * 50)
    
    trending = await get_trending_music()
    
    if trending:
        print(f"Found {len(trending)} trending songs:")
        for i, song in enumerate(trending[:5], 1):
            print(f"{i}. {song.get('title')} - {song.get('artist')}")
    else:
        print("No trending music found")

async def main():
    """Main demo function"""
    print("🚀 Flaks Music API - Demo Script")
    print("=" * 50)
    print("✅ No yt-dlp required")
    print("✅ No cookies needed") 
    print("✅ No IP bans")
    print("✅ Fast 0.3-0.5s response time")
    print("✅ Compatible with VLC & Telegram")
    
    # Run demos
    await demo_api_status()
    await demo_basic_usage()
    await demo_trending()
    
    print("\n🎉 Demo completed!")
    print("\nIntegration Tips:")
    print("1. Replace YOUR_API_KEY with your actual key")
    print("2. Update MUSIC_API_BASE_URL to your deployed domain")
    print("3. Use get_audio_stream_from_api() in your Telegram bot")
    print("4. Stream URLs work directly with VLC and Telegram")

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run demo
    asyncio.run(main())