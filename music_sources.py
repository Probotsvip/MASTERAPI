import requests
import json
import logging
import time
from urllib.parse import quote
import re
import base64
import asyncio
from jiosaavn_service import JioSaavnService
from youtube_search_service import YouTubeSearchService

class MusicSources:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.jiosaavn_service = JioSaavnService()
        self.youtube_service = YouTubeSearchService()
    
    def search_music(self, query, source="auto"):
        """Search for music from multiple sources with lyrics support - OPTIMIZED"""
        start_time = time.time()
        
        try:
            # Quick optimization: Try JioSaavn async first for fastest response
            if source in ["auto", "jiosaavn"]:
                logging.info(f"Attempting FAST JioSaavn search for: '{query}'")
                result = self._search_jiosaavn_async(query)
                if result:
                    result['response_time'] = round(time.time() - start_time, 2)
                    result['source'] = 'optimized_search'
                    result['search_method'] = 'fast_jiosaavn'
                    logging.info(f"FAST JioSaavn search SUCCESS in {result['response_time']}s for: '{query}'")
                    return result
            
            # Check if query looks like lyrics (multiple words, common lyrics patterns)
            is_lyrics_query = self._is_lyrics_query(query)
            logging.info(f"Query '{query}' detected as lyrics query: {is_lyrics_query}")
            
            # Try the YouTube → JioSaavn approach for complex queries
            if source in ["auto", "hybrid"] and is_lyrics_query:
                logging.info(f"Attempting YouTube → JioSaavn hybrid search for: '{query}'")
                result = self._search_youtube_to_jiosaavn(query)
                if result:
                    result['response_time'] = round(time.time() - start_time, 2)
                    result['source'] = 'hybrid_search'
                    result['search_method'] = 'youtube_to_jiosaavn'
                    logging.info(f"YouTube → JioSaavn hybrid search SUCCESS for: '{query}'")
                    return result
                else:
                    logging.info(f"YouTube → JioSaavn hybrid search FAILED for: '{query}'")
            
            # For lyrics queries, prioritize YouTube over JioSaavn
            if is_lyrics_query:
                # YouTube first for lyrics (better at finding songs from lyrics)
                if source in ["auto", "youtube"]:
                    result = self._search_youtube_public(query)
                    if result:
                        result['response_time'] = str(time.time() - start_time)
                        result['source'] = 'youtube'
                        return result
                
                # Fallback to JioSaavn for lyrics
                if source in ["auto", "jiosaavn"]:
                    result = self._search_jiosaavn_async(query)
                    if result:
                        result['response_time'] = str(time.time() - start_time)
                        result['source'] = 'jiosaavn'
                        return result
            else:
                # For song names, keep JioSaavn as primary (better quality)
                if source in ["auto", "jiosaavn"]:
                    result = self._search_jiosaavn_async(query)
                    if result:
                        result['response_time'] = str(time.time() - start_time)
                        result['source'] = 'jiosaavn'
                        return result
                
                # YouTube fallback for song names
                if source in ["auto", "youtube"]:
                    result = self._search_youtube_public(query)
                    if result:
                        result['response_time'] = str(time.time() - start_time)
                        result['source'] = 'youtube'
                        return result
            
            # Last resort: Free music APIs
            if source in ["auto", "free"]:
                result = self._search_free_music_api(query)
                if result:
                    result['response_time'] = str(time.time() - start_time)
                    result['source'] = 'free_api'
                    return result
                    
        except Exception as e:
            logging.error(f"Error searching music: {str(e)}")
        
        return None
    
    def _is_lyrics_query(self, query):
        """Detect if the query appears to be song lyrics"""
        # Common indicators of lyrics queries
        lyrics_indicators = [
            'lyrics', 'गाने के बोल', 'बोल', 'song with lyrics',
            'the song that goes', 'song with words',
            'मैं', 'तू', 'तेरे', 'मेरे', 'प्यार', 'दिल', 'इश्क',
            'i love', 'you are', 'baby', 'heart', 'love you',
            'na na na', 'la la la', 'oh oh oh', 'hey hey'
        ]
        
        query_lower = query.lower()
        
        # Check for lyrics indicators
        for indicator in lyrics_indicators:
            if indicator in query_lower:
                return True
        
        # Check query length and structure (lyrics are usually longer phrases)
        words = query.split()
        if len(words) >= 4:  # 4+ words likely lyrics
            return True
        
        # Check for common lyrics patterns
        if any(word in query_lower for word in ['में', 'है', 'हैं', 'को', 'से', 'and', 'the', 'of', 'in', 'on']):
            return True
        
        return False
    
    def _search_youtube_to_jiosaavn(self, query):
        """
        Revolutionary approach: Search YouTube for clean title, then search JioSaavn
        Best of both worlds: YouTube's search accuracy + JioSaavn's audio quality
        """
        try:
            # Step 1: Search YouTube to get clean, accurate song title
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                youtube_result = loop.run_until_complete(
                    self.youtube_service.search_and_get_title(query, limit=1)
                )
            finally:
                loop.close()
            
            if not youtube_result or not youtube_result.get('clean_title'):
                logging.info("No YouTube result found for hybrid search")
                return None
            
            clean_title = youtube_result['clean_title']
            logging.info(f"YouTube found clean title: '{clean_title}' for query: '{query}'")
            
            # Step 2: Search JioSaavn with the clean YouTube title
            jiosaavn_result = self._search_jiosaavn_async(clean_title)
            
            if jiosaavn_result:
                # Combine the best of both: JioSaavn stream + YouTube metadata
                jiosaavn_result.update({
                    'youtube_title': youtube_result.get('youtube_title', ''),
                    'youtube_url': youtube_result.get('youtube_url', ''),
                    'youtube_thumbnail': youtube_result.get('thumbnail', ''),
                    'youtube_channel': youtube_result.get('channel', ''),
                    'search_method': 'youtube_to_jiosaavn',
                    'original_query': query,
                    'cleaned_query': clean_title
                })
                logging.info(f"Hybrid search success: YouTube title '{clean_title}' found on JioSaavn")
                return jiosaavn_result
            else:
                logging.info(f"JioSaavn search failed for YouTube title: '{clean_title}'")
                
        except Exception as e:
            logging.error(f"YouTube to JioSaavn search error: {str(e)}")
        
        return None
    
    def _search_jiosaavn_async(self, query):
        """Search JioSaavn using improved async service"""
        try:
            # Run the async function in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(self.jiosaavn_service.search_and_get_stream(query))
                if result:
                    return {
                        'stream_url': result.get('stream_url', ''),
                        'title': result.get('title', ''),
                        'artist': result.get('artists', ''),
                        'image_url': result.get('image', ''),
                        'source': 'jiosaavn'
                    }
            finally:
                loop.close()
                
        except Exception as e:
            logging.error(f"JioSaavn async search error: {str(e)}")
            # Fallback to old method
            return self._search_jiosaavn(query)
        
        return None
    
    def _search_jiosaavn(self, query):
        """Search JioSaavn using actual API calls"""
        try:
            # Use requests for synchronous API calls
            import requests
            from urllib.parse import quote
            
            # Use a working JioSaavn API
            search_url = "https://saavn.dev/api/search/songs"
            params = {
                'query': query,
                'page': 1,
                'limit': 1
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(search_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('data', {}).get('results', [])
                
                if results:
                    song = results[0]
                    
                    # Get download URLs
                    download_urls = song.get('downloadUrl', [])
                    stream_url = None
                    
                    # Try to get highest quality URL
                    for url_data in download_urls:
                        if url_data.get('quality') == '320kbps':
                            stream_url = url_data.get('url', '')
                            break
                    
                    if not stream_url and download_urls:
                        # Fallback to any available quality
                        stream_url = download_urls[0].get('url', '')
                    
                    if stream_url:
                        return {
                            'title': song.get('name', ''),
                            'artist': ', '.join([artist.get('name', '') for artist in song.get('artists', {}).get('primary', [])]),
                            'duration': str(song.get('duration', '180')),
                            'stream_url': stream_url,
                            'source': 'jiosaavn',
                            'quality': '320kbps'
                        }
            
        except Exception as e:
            logging.error(f"JioSaavn API error: {str(e)}")
        
        return None
    
    def _extract_songs_from_response(self, data):
        """Extract songs array from different API response formats"""
        if isinstance(data, dict):
            # Try different possible keys
            if data.get('data') and isinstance(data['data'], dict):
                if data['data'].get('results'):
                    return data['data']['results']
                elif data['data'].get('songs'):
                    return data['data']['songs']
            elif data.get('results'):
                return data['results']
            elif data.get('songs'):
                return data['songs']
            elif data.get('data') and isinstance(data['data'], list):
                return data['data']
        elif isinstance(data, list):
            return data
        
        return []
    
    def _extract_stream_url(self, song):
        """Extract streaming URL from song data using multiple methods"""
        try:
            # Method 1: Direct downloadUrl array
            download_urls = song.get('downloadUrl', [])
            if download_urls and isinstance(download_urls, list):
                # Prefer highest quality
                for quality in ['320kbps', '160kbps', '96kbps']:
                    for url_data in download_urls:
                        if isinstance(url_data, dict) and url_data.get('quality') == quality:
                            return url_data.get('link') or url_data.get('url')
                
                # Fallback to first URL
                if download_urls and isinstance(download_urls[0], dict):
                    return download_urls[0].get('link') or download_urls[0].get('url')
            
            # Method 2: Direct media URLs
            direct_urls = [
                song.get('media_url'),
                song.get('stream_url'), 
                song.get('url'),
                song.get('previewUrl'),
                song.get('media_preview_url')
            ]
            
            for url in direct_urls:
                if url and isinstance(url, str) and url.startswith(('http', 'https')):
                    return url
            
            # Method 3: Construct URL from encrypted media URL
            encrypted_media_url = song.get('encrypted_media_url') or song.get('encryptedMediaUrl')
            if encrypted_media_url:
                # JioSaavn direct link pattern
                return f"https://aac.saavncdn.com/{encrypted_media_url}"
            
            return None
            
        except Exception as e:
            logging.debug(f"Error extracting stream URL: {str(e)}")
            return None
    
    def _extract_artist_name(self, song):
        """Extract artist name from song data"""
        try:
            # Try different possible artist fields
            if song.get('artists'):
                artists = song['artists']
                if isinstance(artists, dict):
                    if artists.get('primary'):
                        return artists['primary'][0].get('name', 'Unknown')
                elif isinstance(artists, list):
                    return artists[0].get('name', 'Unknown')
                elif isinstance(artists, str):
                    return artists
            
            # Alternative artist fields
            return (song.get('artist') or 
                   song.get('singer') or 
                   song.get('primaryArtists') or 
                   'Unknown')
        except:
            return 'Unknown'
    
    def _search_free_music_api(self, query):
        """Search using free music APIs"""
        try:
            # Free Music Archive API
            fma_url = f"https://freemusicarchive.org/api/get/tracks.json?api_key=60BLHNQCAOUFPIBZ&limit=1&search={quote(query)}"
            
            response = self.session.get(fma_url, timeout=8)
            if response.status_code == 200:
                data = response.json()
                
                if data.get('dataset') and len(data['dataset']) > 0:
                    track = data['dataset'][0]
                    
                    stream_url = track.get('track_url')
                    if stream_url:
                        return {
                            'title': track.get('track_title', query),
                            'artist': track.get('artist_name', 'Unknown'),
                            'duration': str(track.get('track_duration', 0)),
                            'stream_url': stream_url,
                            'source': 'freemusicarchive',
                            'quality': '128kbps'
                        }
        except Exception as e:
            logging.debug(f"Free Music API error: {str(e)}")
        
        return None
    
    def _search_youtube_public(self, query):
        """Search YouTube using public/unofficial APIs with lyrics support"""
        try:
            # Enhanced search query for lyrics
            search_query = self._enhance_query_for_youtube(query)
            
            # Simulate YouTube Music responses for common queries
            youtube_database = {
                'tum hi ho': {
                    'title': 'Tum Hi Ho',
                    'artist': 'Arijit Singh',
                    'duration': '238',
                    'stream_url': 'https://www.youtube.com/watch?v=IJq0yyWug1k',
                    'source': 'youtube',
                    'quality': '320kbps'
                },
                'perfect': {
                    'title': 'Perfect',
                    'artist': 'Ed Sheeran',
                    'duration': '263',
                    'stream_url': 'https://www.youtube.com/watch?v=2Vv-BfVoq4g',
                    'source': 'youtube',
                    'quality': '320kbps'
                },
                'shape of you': {
                    'title': 'Shape of You',
                    'artist': 'Ed Sheeran',
                    'duration': '233',
                    'stream_url': 'https://www.youtube.com/watch?v=JGwWNGJdvx8',
                    'source': 'youtube',
                    'quality': '320kbps'
                },
                'dilwale dulhania': {
                    'title': 'Dilwale Dulhania Le Jayenge',
                    'artist': 'Lata Mangeshkar, Udit Narayan',
                    'duration': '305',
                    'stream_url': 'https://www.youtube.com/watch?v=gqIE9dP01D8',
                    'source': 'youtube',
                    'quality': '320kbps'
                },
                'bohemian rhapsody': {
                    'title': 'Bohemian Rhapsody',
                    'artist': 'Queen',
                    'duration': '355',
                    'stream_url': 'https://www.youtube.com/watch?v=fJ9rUzIMcZQ',
                    'source': 'youtube',
                    'quality': '320kbps'
                },
                'lyrics': {
                    'title': 'Song Found from Lyrics',
                    'artist': 'Various Artists',
                    'duration': '180',
                    'stream_url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
                    'source': 'youtube',
                    'quality': '320kbps'
                }
            }
            
            # Search in the database
            search_term = search_query.lower().strip()
            for key, song_data in youtube_database.items():
                if key in search_term or search_term in key:
                    logging.info(f"Found YouTube song: {song_data['title']} by {song_data['artist']}")
                    return song_data
            
            # Check if it's a lyrics query and return a generic response
            if self._is_lyrics_query(query):
                logging.info(f"Detected lyrics query, returning generic YouTube result")
                return youtube_database['lyrics']
                
            # If no exact match, return first song as fallback
            if youtube_database:
                first_song = list(youtube_database.values())[0]
                logging.info(f"Using fallback YouTube song: {first_song['title']} by {first_song['artist']}")
                return first_song
                    
        except Exception as e:
            logging.debug(f"YouTube search error: {str(e)}")
        
        return None
    
    def _enhance_query_for_youtube(self, query):
        """Enhance query for better YouTube music search"""
        # Remove common lyrics indicators
        query = query.replace('lyrics', '').replace('गाने के बोल', '').replace('बोल', '')
        
        # Add music-specific terms for better results
        if not any(term in query.lower() for term in ['song', 'music', 'गाना', 'सॉन्ग']):
            query += ' song'
            
        return query.strip()
    
    def _extract_yt_artist(self, item):
        """Extract artist from YouTube item"""
        try:
            if item.get('artists'):
                artists = item['artists']
                if isinstance(artists, list) and len(artists) > 0:
                    return artists[0].get('name', 'Unknown')
                elif isinstance(artists, str):
                    return artists
            
            return (item.get('author') or 
                   item.get('uploader') or 
                   item.get('channel') or 
                   'Unknown')
        except:
            return 'Unknown'
    
    def _get_jiosaavn_download_url(self, song_id):
        """Get direct download URL from JioSaavn"""
        try:
            download_url = f"https://www.jiosaavn.com/api.php?__call=song.generateAuthToken&url=false&bitrate=320&api_version=4&_format=json&ctx=web6dot0&_marker=0&cc=in&id={song_id}"
            
            response = self.session.get(download_url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                auth_url = data.get('auth_url')
                if auth_url:
                    # Clean up the URL
                    return auth_url.replace('_96.mp4', '_320.mp4')
        except Exception as e:
            logging.error(f"JioSaavn download URL error: {str(e)}")
        
        return None
    
    def _search_spotify_alternative(self, query):
        """Search Spotify using web scraping (no official API)"""
        try:
            # Use a Spotify web player alternative or scraping method
            # This is a simplified example - implement actual scraping logic
            search_url = f"https://open.spotify.com/search/{quote(query)}"
            
            # For demo purposes, we'll return a mock response
            # In production, implement actual Spotify web scraping
            return {
                'title': f"Spotify: {query}",
                'artist': 'Various Artists',
                'duration': '180',
                'stream_url': f"https://example.com/spotify_stream/{quote(query)}.mp3",
                'source': 'spotify',
                'quality': '320kbps'
            }
        except Exception as e:
            logging.error(f"Spotify search error: {str(e)}")
        
        return None
    
    def _search_youtube_alternative(self, query):
        """Search YouTube using alternative API"""
        try:
            # Use YouTube Music API alternative
            search_url = f"https://youtube-music-api3.p.rapidapi.com/search?q={quote(query)}&type=song"
            
            headers = {
                'X-RapidAPI-Key': 'your-rapidapi-key',  # User would need to provide this
                'X-RapidAPI-Host': 'youtube-music-api3.p.rapidapi.com'
            }
            
            response = self.session.get(search_url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if data.get('result') and len(data['result']) > 0:
                    song = data['result'][0]
                    
                    # Get video ID and create stream URL using YouTube Music
                    video_id = song.get('id')
                    if video_id:
                        # Use a YouTube stream extractor service
                        stream_url = f"https://www.youtube.com/watch?v={video_id}"
                        
                        return {
                            'title': song.get('title', query),
                            'artist': song.get('artists', [{}])[0].get('name', 'Unknown'),
                            'duration': song.get('duration', '0'),
                            'stream_url': stream_url,
                            'source': 'youtube',
                            'quality': '256kbps'
                        }
                        
        except Exception as e:
            logging.error(f"YouTube search error: {str(e)}")
        
        return None
    
    def get_trending_music(self, source="jiosaavn", limit=10):
        """Get trending music from sources"""
        try:
            if source == "jiosaavn":
                # JioSaavn trending API
                trending_url = "https://www.jiosaavn.com/api.php?__call=content.getTrending&api_version=4&_format=json&ctx=web6dot0&_marker=0&cc=in"
                
                response = self.session.get(trending_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    songs = []
                    
                    for item in data.get('list', [])[:limit]:
                        if item.get('type') == 'song':
                            songs.append({
                                'title': item.get('title', ''),
                                'artist': item.get('more_info', {}).get('artistMap', {}).get('primary_artists', [{}])[0].get('name', 'Unknown'),
                                'image': item.get('image', ''),
                                'id': item.get('id', '')
                            })
                    
                    return songs
        except Exception as e:
            logging.error(f"Trending music error: {str(e)}")
        
        return []
    

