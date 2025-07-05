#!/usr/bin/env python3
"""
Test script for the enhanced YouTube → JioSaavn search functionality
Demonstrates the new approach for better music discovery
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from youtube_search_service import YouTubeSearchService
from music_sources import MusicSources

async def test_youtube_search():
    """Test the YouTube search service"""
    youtube_service = YouTubeSearchService()
    
    test_queries = [
        "tum hi ho lyrics",
        "perfect ed sheeran",
        "मैं तेरे प्यार में बावरा हूं",
        "shape of you",
        "dilwale dulhania le jayenge title song"
    ]
    
    print("🔍 Testing YouTube Search Service")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            result = await youtube_service.search_and_get_title(query)
            if result:
                print(f"✅ YouTube Title: {result['youtube_title']}")
                print(f"🔧 Clean Title: {result['clean_title']}")
                print(f"⏱️  Duration: {result['duration']}")
                print(f"📺 Channel: {result['channel']}")
            else:
                print("❌ No result found")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def test_enhanced_music_search():
    """Test the enhanced music search with YouTube → JioSaavn approach"""
    music_sources = MusicSources()
    
    test_queries = [
        "tum hi ho lyrics",
        "perfect ed sheeran",
        "shape of you",
        "dilwale dulhania le jayenge"
    ]
    
    print("\n\n🎵 Testing Enhanced Music Search (YouTube → JioSaavn)")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        try:
            result = music_sources.search_music(query, source="hybrid")
            if result:
                print(f"✅ Found: {result.get('title', 'Unknown Title')}")
                print(f"🎤 Artist: {result.get('artist', 'Unknown Artist')}")
                print(f"🔗 Stream URL: {result.get('stream_url', 'No URL')}")
                print(f"📱 Source: {result.get('source', 'Unknown')}")
                print(f"⏱️  Response Time: {result.get('response_time', '0')}s")
                
                # Show YouTube metadata if available
                if result.get('youtube_title'):
                    print(f"📺 YouTube Title: {result['youtube_title']}")
                    print(f"🔧 Search Method: {result.get('search_method', 'standard')}")
            else:
                print("❌ No result found")
        except Exception as e:
            print(f"❌ Error: {str(e)}")

async def main():
    """Main test function"""
    print("🚀 Enhanced Music Search Test Suite")
    print("Testing the revolutionary YouTube → JioSaavn approach")
    print("=" * 70)
    
    # Test YouTube search service
    await test_youtube_search()
    
    # Test enhanced music search
    test_enhanced_music_search()
    
    print("\n" + "=" * 70)
    print("✅ Test suite completed!")
    print("This demonstrates how we now:")
    print("1. Search YouTube for accurate song titles (even from lyrics)")
    print("2. Use those clean titles to find high-quality streams on JioSaavn")
    print("3. Combine the best of both platforms!")

if __name__ == "__main__":
    asyncio.run(main())