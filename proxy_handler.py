import requests
import logging
from urllib.parse import urlparse, quote
import hashlib
import time
from flask import request, Response, stream_with_context
import os
from pymongo import MongoClient
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ProxyHandler:
    """Proxy handler to hide original stream URLs and show custom domain URLs"""
    
    def __init__(self, mongo_client=None):
        # Use MongoDB for persistent cache across workers
        self.mongo_client = mongo_client
        if self.mongo_client:
            self.db = self.mongo_client['flaks_music_api']
            self.cache_collection = self.db['proxy_cache']
            # Create TTL index for auto-cleanup
            self.cache_collection.create_index("expires_at", expireAfterSeconds=0)
        else:
            self.cache = {}  # Fallback in-memory cache
        self.cache_duration = 3600  # 1 hour cache
        
    def create_proxy_url(self, original_url: str, api_key: str) -> str:
        """Create a proxy URL that hides the original stream URL"""
        # Create a hash of the original URL for security
        url_hash = hashlib.md5(f"{original_url}:{api_key}:{int(time.time() // 3600)}".encode()).hexdigest()
        
        # Store in MongoDB cache or fallback to memory
        if self.mongo_client:
            try:
                expires_at = datetime.utcnow() + timedelta(seconds=self.cache_duration)
                self.cache_collection.replace_one(
                    {'hash': url_hash},
                    {
                        'hash': url_hash,
                        'original_url': original_url,
                        'api_key': api_key,
                        'created_at': datetime.utcnow(),
                        'expires_at': expires_at
                    },
                    upsert=True
                )
            except Exception as e:
                logger.error(f"MongoDB cache error: {e}")
                # Fallback to memory cache
                self.cache[url_hash] = {
                    'original_url': original_url,
                    'timestamp': time.time(),
                    'api_key': api_key
                }
        else:
            # Store in memory cache
            self.cache[url_hash] = {
                'original_url': original_url,
                'timestamp': time.time(),
                'api_key': api_key
            }
        
        # Get current domain from request
        domain = request.host if request else 'localhost:5000'
        protocol = 'https' if request and request.is_secure else 'http'
        
        # Return proxy URL with our domain
        return f"{protocol}://{domain}/proxy/stream/{url_hash}"
    
    def get_original_url(self, url_hash: str) -> str:
        """Get original URL from hash"""
        # Try MongoDB cache first
        if self.mongo_client:
            try:
                cached_item = self.cache_collection.find_one({'hash': url_hash})
                if cached_item:
                    # Check if still valid (MongoDB TTL handles this, but double-check)
                    if datetime.utcnow() < cached_item['expires_at']:
                        return cached_item['original_url']
                    else:
                        # Clean up expired item
                        self.cache_collection.delete_one({'hash': url_hash})
                        return ""
                return ""
            except Exception as e:
                logger.error(f"MongoDB cache read error: {e}")
                # Fall through to memory cache
        
        # Fallback to memory cache
        if url_hash not in self.cache:
            return ""
            
        cached_item = self.cache[url_hash]
        
        # Check if cache is still valid
        if time.time() - cached_item['timestamp'] > self.cache_duration:
            del self.cache[url_hash]
            return ""
            
        return cached_item['original_url']
    
    def stream_audio(self, url_hash: str):
        """Stream audio through proxy"""
        original_url = self.get_original_url(url_hash)
        
        if not original_url:
            return Response("Stream not found or expired", status=404)
        
        try:
            # Headers for audio streaming
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'audio/webm,audio/ogg,audio/wav,audio/*;q=0.9,application/ogg;q=0.7,video/*;q=0.6,*/*;q=0.5',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'identity',
                'Range': request.headers.get('Range', ''),
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            # Make request to original URL
            response = requests.get(original_url, headers=headers, stream=True, timeout=10)
            
            if response.status_code == 200 or response.status_code == 206:
                # Create response with proper headers
                def generate():
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            yield chunk
                
                # Set response headers
                response_headers = {
                    'Content-Type': response.headers.get('Content-Type', 'audio/mpeg'),
                    'Content-Length': response.headers.get('Content-Length', ''),
                    'Accept-Ranges': 'bytes',
                    'Cache-Control': 'public, max-age=3600',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Range'
                }
                
                # Add range header if present
                if 'Content-Range' in response.headers:
                    response_headers['Content-Range'] = response.headers['Content-Range']
                
                return Response(
                    stream_with_context(generate()),
                    status=response.status_code,
                    headers=response_headers
                )
            else:
                logger.error(f"Failed to fetch audio: {response.status_code}")
                return Response("Failed to fetch audio", status=500)
                
        except Exception as e:
            logger.error(f"Error streaming audio: {str(e)}")
            return Response("Error streaming audio", status=500)
    
    def cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, value in self.cache.items()
            if current_time - value['timestamp'] > self.cache_duration
        ]
        
        for key in expired_keys:
            del self.cache[key]
        
        logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")

# Global proxy handler instance
proxy_handler = ProxyHandler()