"""
Telegram Music Bot using Flaks Music API
=====================================

Complete Telegram bot example that uses Flaks Music API for music streaming.
Perfect for creating your own music bot with superfast responses!

Requirements:
- pip install python-telegram-bot requests aiohttp

Setup:
1. Get your Telegram bot token from @BotFather
2. Get your API key from https://t.me/jalwagameofficial
3. Replace the tokens below and run the bot

Features:
- /start - Welcome message
- /search <song> - Search and send music
- /trending - Get trending songs
- /status - Check API status
- Support for lyrics search
- Inline search results
"""

import logging
import asyncio
import aiohttp
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Configuration
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"  # Get from @BotFather
FLAKS_API_KEY = "YOUR_API_KEY"  # Get from https://t.me/jalwagameofficial
FLAKS_API_URL = "https://your-domain.replit.app"  # Replace with your actual domain

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramMusicBot:
    def __init__(self, bot_token, api_key, api_url):
        self.bot_token = bot_token
        self.api_key = api_key
        self.api_url = api_url
        self.session = None
    
    async def init_session(self):
        """Initialize aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    async def search_music(self, query):
        """Search music using Flaks API"""
        try:
            await self.init_session()
            
            url = f"{self.api_url}/api/stream"
            params = {
                'api_key': self.api_key,
                'query': query
            }
            
            async with self.session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    return data if data.get('success') else None
                else:
                    logger.error(f"API request failed: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Music search error: {str(e)}")
            return None
    
    async def get_trending(self):
        """Get trending music"""
        try:
            await self.init_session()
            
            url = f"{self.api_url}/api/trending"
            params = {'api_key': self.api_key}
            
            async with self.session.get(url, params=params, timeout=15) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Trending error: {str(e)}")
            return None
    
    async def check_api_status(self):
        """Check API status"""
        try:
            await self.init_session()
            
            url = f"{self.api_url}/api/status"
            params = {'api_key': self.api_key}
            
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Status check error: {str(e)}")
            return None

# Initialize bot
music_bot = TelegramMusicBot(TELEGRAM_BOT_TOKEN, FLAKS_API_KEY, FLAKS_API_URL)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    welcome_message = """
🎵 **Welcome to Flaks Music Bot!** 🎵

I can help you find and stream music instantly with superfast responses!

**Commands:**
• Send me any song name to search
• `/search <song name>` - Search for music
• `/trending` - Get trending songs
• `/status` - Check API status

**Features:**
• ⚡ Superfast responses (under 1 second)
• 🎧 320kbps quality audio
• 🔍 Search by song name, artist, or lyrics
• 📱 Works with voice chats
• 🎯 No IP bans or restrictions

**Example:**
Just type: "Tum Hi Ho" or "Shape of You"

Powered by Flaks Music API 🚀
Support: https://t.me/Komal_Music_Support
Updates: https://t.me/KomalMusicUpdate
"""
    
    keyboard = [
        [InlineKeyboardButton("🎵 Search Music", callback_data='search_demo')],
        [InlineKeyboardButton("📈 Trending", callback_data='trending')],
        [InlineKeyboardButton("💬 Support", url='https://t.me/Komal_Music_Support')],
        [InlineKeyboardButton("📢 Updates", url='https://t.me/KomalMusicUpdate')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='Markdown')

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search command handler"""
    if not context.args:
        await update.message.reply_text("Please provide a song name!\nExample: `/search Tum Hi Ho`", parse_mode='Markdown')
        return
    
    query = ' '.join(context.args)
    await search_and_send_music(update, query)

async def search_and_send_music(update, query):
    """Search and send music"""
    # Show searching message
    searching_msg = await update.message.reply_text(f"🔍 Searching for: *{query}*\n⏳ Please wait...", parse_mode='Markdown')
    
    try:
        # Search music
        result = await music_bot.search_music(query)
        
        if result:
            # Delete searching message
            await searching_msg.delete()
            
            # Prepare music info
            title = result.get('title', 'Unknown Title')
            artist = result.get('artist', 'Unknown Artist')
            duration = result.get('duration', 'Unknown')
            stream_url = result.get('stream_url', '')
            quality = result.get('quality', '320kbps')
            response_time = result.get('response_time', 0)
            
            # Create caption
            caption = f"""
🎵 **{title}**
👨‍🎤 **Artist:** {artist}
⏱️ **Duration:** {duration}
🎧 **Quality:** {quality}
⚡ **Response Time:** {response_time}s

Powered by Flaks Music API 🚀
"""
            
            # Create inline keyboard
            keyboard = [
                [InlineKeyboardButton("📱 Use in Voice Chat", callback_data=f'voice_{stream_url}')],
                [InlineKeyboardButton("🔗 Direct Link", url=stream_url)],
                [InlineKeyboardButton("🎵 Search More", callback_data='search_demo')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send audio
            try:
                await update.message.reply_audio(
                    audio=stream_url,
                    caption=caption,
                    parse_mode='Markdown',
                    reply_markup=reply_markup,
                    title=title,
                    performer=artist
                )
            except Exception as e:
                # If audio sending fails, send as message with link
                await update.message.reply_text(
                    f"{caption}\n🔗 **Stream URL:** {stream_url}",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
        else:
            # Update searching message with no results
            await searching_msg.edit_text(f"❌ No results found for: *{query}*\n\nTry searching with:\n• Full song name\n• Artist name\n• Song lyrics", parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        await searching_msg.edit_text(f"❌ Error searching for: *{query}*\n\nPlease try again later.", parse_mode='Markdown')

async def trending_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trending command handler"""
    trending_msg = await update.message.reply_text("📈 Getting trending songs...", parse_mode='Markdown')
    
    try:
        result = await music_bot.get_trending()
        
        if result and result.get('success'):
            songs = result.get('songs', [])
            
            if songs:
                trending_text = "📈 **Trending Songs:**\n\n"
                
                for i, song in enumerate(songs[:10], 1):
                    title = song.get('title', 'Unknown')
                    artist = song.get('artist', 'Unknown')
                    trending_text += f"{i}. {title} - {artist}\n"
                
                trending_text += "\n💡 *Click on any song name to search*"
                
                # Create keyboard with trending songs
                keyboard = []
                for song in songs[:5]:  # Show top 5 as buttons
                    title = song.get('title', 'Unknown')
                    keyboard.append([InlineKeyboardButton(f"🎵 {title}", callback_data=f'play_{title}')])
                
                reply_markup = InlineKeyboardMarkup(keyboard)
                await trending_msg.edit_text(trending_text, parse_mode='Markdown', reply_markup=reply_markup)
            else:
                await trending_msg.edit_text("📈 No trending songs available right now.", parse_mode='Markdown')
        else:
            await trending_msg.edit_text("❌ Failed to get trending songs.", parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Trending error: {str(e)}")
        await trending_msg.edit_text("❌ Error getting trending songs.", parse_mode='Markdown')

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Status command handler"""
    status_msg = await update.message.reply_text("📊 Checking API status...", parse_mode='Markdown')
    
    try:
        result = await music_bot.check_api_status()
        
        if result:
            usage = result.get('usage', 'N/A')
            limit = result.get('limit', 'N/A')
            remaining = result.get('remaining', 'N/A')
            
            status_text = f"""
📊 **API Status:** ✅ Active

📈 **Usage Stats:**
• Used: {usage}
• Limit: {limit}
• Remaining: {remaining}

⚡ **Performance:** Superfast
🎧 **Quality:** 320kbps
🔒 **Status:** Secure

Powered by Flaks Music API 🚀
"""
            await status_msg.edit_text(status_text, parse_mode='Markdown')
        else:
            await status_msg.edit_text("❌ Failed to check API status.", parse_mode='Markdown')
            
    except Exception as e:
        logger.error(f"Status error: {str(e)}")
        await status_msg.edit_text("❌ Error checking status.", parse_mode='Markdown')

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages as music search"""
    query = update.message.text.strip()
    
    # Ignore commands
    if query.startswith('/'):
        return
    
    # Search for music
    await search_and_send_music(update, query)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == 'search_demo':
        await query.edit_message_text(
            "🎵 **Search Demo:**\n\nTry sending me:\n• Tum Hi Ho\n• Shape of You\n• Blinding Lights\n• Any song name or lyrics!",
            parse_mode='Markdown'
        )
    elif data == 'trending':
        await trending_command(update, context)
    elif data.startswith('play_'):
        song_name = data.replace('play_', '')
        await search_and_send_music(update, song_name)
    elif data.startswith('voice_'):
        stream_url = data.replace('voice_', '')
        await query.edit_message_text(
            f"📱 **Voice Chat Usage:**\n\n1. Copy this link: `{stream_url}`\n2. Open Telegram Voice Chat\n3. Click 'Share Music'\n4. Paste the link\n5. Everyone can hear! 🎵",
            parse_mode='Markdown'
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Main function to run the bot"""
    # Check configuration
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN":
        print("❌ Please set your Telegram bot token!")
        print("💬 Get it from @BotFather")
        return
    
    if FLAKS_API_KEY == "YOUR_API_KEY":
        print("❌ Please set your Flaks API key!")
        print("💬 Get it from https://t.me/jalwagameofficial")
        return
    
    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("trending", trending_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_error_handler(error_handler)
    
    # Run bot
    print("🚀 Starting Flaks Music Bot...")
    print("💬 Bot is ready to receive messages!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()