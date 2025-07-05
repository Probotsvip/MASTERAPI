#!/usr/bin/env python3
"""
Debug script to test YouTube search functionality
"""
import asyncio
from youtube_search_service import YouTubeSearchService

async def test_youtube_search():
    """Test the YouTube search service with a lyrics query"""
    youtube_service = YouTubeSearchService()
    
    # Test with a lyrics query
    query = "ek baar dekh le mujhe tere pyaar me main doob jaaun"
    print(f"Testing YouTube search for: '{query}'")
    
    try:
        result = await youtube_service.search_and_get_title(query, limit=1)
        print(f"YouTube search result: {result}")
        
        if result:
            print(f"Clean title: {result.get('clean_title', 'N/A')}")
            print(f"YouTube title: {result.get('youtube_title', 'N/A')}")
            print(f"Duration: {result.get('duration', 'N/A')}")
            print(f"Video ID: {result.get('video_id', 'N/A')}")
        else:
            print("No result found")
            
    except Exception as e:
        print(f"Error in YouTube search: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_youtube_search())