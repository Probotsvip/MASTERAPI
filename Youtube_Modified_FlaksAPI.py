import asyncio
import os
import re
import json
from typing import Union
import requests
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from AviaxMusic.utils.database import is_on_off
from AviaxMusic.utils.formatters import time_to_seconds
import os
import glob
import random
import logging
import aiohttp
import config

# Flaks Music API Configuration
FLAKS_API_URL = "https://your-domain.replit.app"  # Replace with your actual domain
FLAKS_API_KEY = "YOUR_API_KEY"  # Replace with your actual API key


def cookie_txt_file():
    cookie_dir = f"{os.getcwd()}/cookies"
    cookies_files = [f for f in os.listdir(cookie_dir) if f.endswith(".txt")]

    cookie_file = os.path.join(cookie_dir, random.choice(cookies_files))
    return cookie_file


async def get_audio_stream_from_api(query: str):
    """Get audio stream URL from our Music Stream API with API key"""
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                'query': query,
                'api_key': FLAKS_API_KEY
            }
            async with session.get(
                f"{FLAKS_API_URL}/api/stream",
                params=params,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('success'):
                        return data.get('stream_url'), data.get('title', query)
                    else:
                        print(f"❌ API search failed for: {query}")
                        return None, None
                else:
                    print(f"❌ Music API failed with status: {response.status}")
                    return None, None
    except Exception as e:
        print(f"❌ Error calling Music Stream API: {str(e)}")
        return None, None


async def download_song_flaks_api(query: str):
    """Download song using Flaks Music API - gets stream URL and downloads file"""
    try:
        # Get stream URL from API
        stream_url, title = await get_audio_stream_from_api(query)
        
        if not stream_url:
            print(f"❌ No stream URL received for: {query}")
            return None
            
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', title or query).strip()
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        
        # Setup download path
        download_folder = "downloads"
        os.makedirs(download_folder, exist_ok=True)
        file_path = os.path.join(download_folder, f"{safe_title}.mp3")
        
        # Check if file already exists
        if os.path.exists(file_path):
            print(f"✅ File already exists: {file_path}")
            return file_path
        
        # Download from stream URL
        print(f"🎵 Downloading via Flaks API: {title}")
        async with aiohttp.ClientSession() as session:
            async with session.get(stream_url) as file_response:
                if file_response.status == 200:
                    with open(file_path, 'wb') as f:
                        while True:
                            chunk = await file_response.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                    
                    print(f"✅ Downloaded successfully: {file_path}")
                    return file_path
                else:
                    print(f"❌ Failed to download audio: {file_response.status}")
                    return None
                    
    except Exception as e:
        print(f"❌ Flaks API download error: {str(e)}")
        return None


async def download_song_fallback(link: str):
    """Fallback to original YouTube download if Flaks API fails"""
    try:
        video_id = link.split('v=')[-1].split('&')[0]
        
        # First try to get title from YouTube for better search
        try:
            results = VideosSearch(link, limit=1)
            result_data = (await results.next())["result"]
            if result_data:
                youtube_title = result_data[0]["title"]
                # Try Flaks API with YouTube title
                flaks_result = await download_song_flaks_api(youtube_title)
                if flaks_result:
                    return flaks_result
        except:
            pass
        
        # If Flaks API fails, fallback to original method
        print("🔄 Falling back to original YouTube download...")
        
        download_folder = "downloads"
        for ext in ["mp3", "m4a", "webm"]:
            file_path = f"{download_folder}/{video_id}.{ext}"
            if os.path.exists(file_path):
                print(f"File already exists: {file_path}")
                return file_path
        
        # Original API download code (keep as fallback)
        song_url = f"{config.API_URL}/song/{video_id}?api={config.API_KEY}"
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.get(song_url) as response:
                        if response.status != 200:
                            raise Exception(f"API request failed with status code {response.status}")
                        data = await response.json()
                        status = data.get("status", "").lower()
                        if status == "downloading":
                            await asyncio.sleep(2)
                            continue
                        elif status == "error":
                            error_msg = data.get("error") or data.get("message") or "Unknown error"
                            raise Exception(f"API error: {error_msg}")
                        elif status == "done":
                            download_url = data.get("link")
                            if not download_url:
                                raise Exception("API response did not provide a download URL.")
                            break
                        else:
                            raise Exception(f"Unexpected status '{status}' from API.")
                except Exception as e:
                    print(f"Error while checking API status: {e}")
                    return None

            try:
                file_format = data.get("format", "mp3")
                file_extension = file_format.lower()
                file_name = f"{video_id}.{file_extension}"
                download_folder = "downloads"
                os.makedirs(download_folder, exist_ok=True)
                file_path = os.path.join(download_folder, file_name)

                async with session.get(download_url) as file_response:
                    with open(file_path, 'wb') as f:
                        while True:
                            chunk = await file_response.content.read(8192)
                            if not chunk:
                                break
                            f.write(chunk)
                    return file_path
            except aiohttp.ClientError as e:
                print(f"Network or client error occurred while downloading: {e}")
                return None
            except Exception as e:
                print(f"Error occurred while downloading song: {e}")
                return None
        return None
    except Exception as e:
        print(f"Fallback download error: {str(e)}")
        return None


async def check_file_size(link):
    async def get_format_info(link):
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_txt_file(),
            "-J",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            print(f'Error:\n{stderr.decode()}')
            return None
        return json.loads(stdout.decode())

    def parse_size(formats):
        total_size = 0
        for format in formats:
            if 'filesize' in format:
                total_size += format['filesize']
        return total_size

    info = await get_format_info(link)
    if info is None:
        return None
    
    formats = info.get('formats', [])
    if not formats:
        print("No formats found.")
        return None
    
    total_size = parse_size(formats)
    return total_size

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        """Video download remains unchanged - uses original YouTube method"""
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies",cookie_txt_file(),
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_txt_file()} --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = playlist.split("\n")
            for key in result:
                if key == "":
                    result.remove(key)
        except:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True, "cookiefile" : cookie_txt_file()}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except:
                    continue
                if not "dash" in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except:
                        continue
                    formats_available.append(
                        {
                            "format": format["format"],
                            "filesize": format["filesize"],
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        }
                    )
        return formats_available, link

    async def slider(
        self,
        link: str,
        query_type: int,
        videoid: Union[bool, str] = None,
    ):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        loop = asyncio.get_running_loop()
        
        def audio_dl():
            """Original audio download function - kept as fallback"""
            ydl_optssx = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile" : cookie_txt_file(),
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def video_dl():
            """Video download remains unchanged"""
            ydl_optssx = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile" : cookie_txt_file(),
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            info = x.extract_info(link, False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz

        def song_video_dl():
            """Song video download remains unchanged"""
            formats = f"{format_id}+140"
            fpath = f"downloads/{title}"
            ydl_optssx = {
                "format": formats,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile" : cookie_txt_file(),
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            x.download([link])

        def song_audio_dl():
            """Song audio download remains unchanged"""
            fpath = f"downloads/{title}.%(ext)s"
            ydl_optssx = {
                "format": format_id,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile" : cookie_txt_file(),
                "prefer_ffmpeg": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
            }
            x = yt_dlp.YoutubeDL(ydl_optssx)
            x.download([link])

        # Modified logic to use Flaks API for audio downloads
        if songvideo:
            # Use Flaks API for song video audio
            downloaded_file = await download_song_fallback(link)
            if not downloaded_file:
                fpath = f"downloads/{link}.mp3"
                return fpath
            return downloaded_file
            
        elif songaudio:
            # Use Flaks API for song audio
            downloaded_file = await download_song_fallback(link)
            if not downloaded_file:
                fpath = f"downloads/{link}.mp3"
                return fpath
            return downloaded_file
            
        elif video:
            # Video download logic remains unchanged
            if await is_on_off(1):
                direct = True
                downloaded_file = await download_song_fallback(link)
            else:
                proc = await asyncio.create_subprocess_exec(
                    "yt-dlp",
                    "--cookies",cookie_txt_file(),
                    "-g",
                    "-f",
                    "best[height<=?720][width<=?1280]",
                    f"{link}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await proc.communicate()
                if stdout:
                    downloaded_file = stdout.decode().split("\n")[0]
                    direct = False
                else:
                   file_size = await check_file_size(link)
                   if not file_size:
                     print("None file Size")
                     return
                   total_size_mb = file_size / (1024 * 1024)
                   if total_size_mb > 250:
                     print(f"File size {total_size_mb:.2f} MB exceeds the 100MB limit.")
                     return None
                   direct = True
                   downloaded_file = await loop.run_in_executor(None, video_dl)
        else:
            # Default audio download - USE FLAKS API
            print("🎵 Using Flaks Music API for audio download...")
            direct = True
            downloaded_file = await download_song_fallback(link)
            
        return downloaded_file, direct