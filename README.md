# 🎵 Flaks Music API

**Fast, reliable music streaming API with 320kbps quality** perfect for Telegram bots, mobile apps, and music applications.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Uptime](https://img.shields.io/badge/uptime-99.9%25-brightgreen.svg)

## ✨ Features

- **⚡ Ultra Fast**: Response time < 1 second
- **🎵 320kbps Quality**: High-quality audio streaming
- **🔐 Secure API**: Key-based authentication system
- **📊 Admin Panel**: Beautiful dashboard for API key management
- **🌐 Proxy URLs**: Hides original JioSaavn URLs, shows your domain
- **📈 Analytics**: Usage tracking and statistics
- **🚀 Production Ready**: Optimized for Heroku, VPS, and cloud deployment
- **🔄 Auto-Fallback**: Multiple music sources with intelligent fallback

## 🚀 Live Demo

**API Base URL:** `https://your-domain.herokuapp.com/`

### Quick Test
```bash
curl "https://your-domain.herokuapp.com/api/stream?api_key=YOUR_API_KEY&query=tum+hi+ho"
```

**Response:**
```json
{
  "success": true,
  "title": "Tum Hi Ho",
  "artist": "Mithoon",
  "stream_url": "https://your-domain.com/proxy/stream/abc123xyz",
  "quality": "320kbps",
  "source": "jiosaavn",
  "response_time": 0.97
}
```

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [API Documentation](#api-documentation)
- [Deployment Guide](#deployment-guide)
- [Admin Panel](#admin-panel)
- [Configuration](#configuration)
- [Example Usage](#example-usage)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/flaks-music-api.git
cd flaks-music-api
```

### 2. Install Dependencies
```bash
pip install -r heroku_requirements.txt
```

### 3. Set Environment Variables
```bash
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/database"
export SESSION_SECRET="your-secret-key-here"
```

### 4. Run Application
```bash
python main.py
```

### 5. Access Admin Panel
- URL: `http://localhost:5000/admin/login`
- Username: `admin`
- Password: `admin123`

### 6. Create API Key
1. Login to admin panel
2. Create new API key
3. Start using the API!

## 📖 API Documentation

### Base URL
```
https://your-domain.herokuapp.com/
```

### Authentication
All API requests require an API key parameter:
```
?api_key=YOUR_API_KEY
```

### Endpoints

#### 1. Stream Music 🎵
**GET** `/api/stream`

Search and get direct streaming URL for music.

**Parameters:**
- `api_key` (required): Your API key
- `query` (required): Song name, artist, or search query
- `source` (optional): Music source (`auto`, `jiosaavn`, `spotify`, `youtube`)

**Example:**
```bash
curl "https://your-domain.com/api/stream?api_key=YOUR_KEY&query=geruva"
```

**Response:**
```json
{
  "success": true,
  "title": "Gerua",
  "artist": "Pritam",
  "stream_url": "https://your-domain.com/proxy/stream/hash123",
  "quality": "320kbps",
  "source": "jiosaavn",
  "duration": "",
  "response_time": 0.97
}
```

#### 2. Search Music 🔍
**GET** `/api/search`

Search for music without getting stream URL (faster).

**Parameters:**
- `api_key` (required): Your API key
- `query` (required): Search query

**Example:**
```bash
curl "https://your-domain.com/api/search?api_key=YOUR_KEY&query=arijit+singh"
```

#### 3. Trending Music 📈
**GET** `/api/trending`

Get trending music from JioSaavn.

**Parameters:**
- `api_key` (required): Your API key
- `limit` (optional): Number of songs (default: 10)

**Example:**
```bash
curl "https://your-domain.com/api/trending?api_key=YOUR_KEY&limit=5"
```

#### 4. API Status 📊
**GET** `/api/status`

Check your API key status and usage.

**Parameters:**
- `api_key` (required): Your API key

**Example:**
```bash
curl "https://your-domain.com/api/status?api_key=YOUR_KEY"
```

**Response:**
```json
{
  "success": true,
  "api_key": "user_abc123...",
  "owner": "Your Name",
  "daily_limit": 1000,
  "daily_used": 45,
  "created_at": "2025-01-01T00:00:00Z",
  "expires_at": "2025-02-01T00:00:00Z"
}
```

## 🚀 Deployment Guide

### 📦 Heroku Deployment

#### Step 1: Prepare Files
All required files are included:
- `Procfile` ✅
- `heroku_requirements.txt` ✅
- `main.py` ✅

#### Step 2: Create Heroku App
```bash
# Install Heroku CLI
# Visit: https://devcenter.heroku.com/articles/heroku-cli

# Login to Heroku
heroku login

# Create new app
heroku create your-music-api-name

# Set environment variables
heroku config:set MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/database"
heroku config:set SESSION_SECRET="your-secret-key-here"
```

#### Step 3: Deploy
```bash
# Add Heroku remote
git remote add heroku https://git.heroku.com/your-music-api-name.git

# Deploy
git add .
git commit -m "Initial deployment"
git push heroku main
```

#### Step 4: Open Application
```bash
heroku open
```

Your API will be available at: `https://your-music-api-name.herokuapp.com/`

### 🖥️ VPS Deployment

#### Option 1: Docker Deployment
```bash
# Clone repository
git clone https://github.com/yourusername/flaks-music-api.git
cd flaks-music-api

# Create environment file
nano .env
```

**`.env` file:**
```
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/database
SESSION_SECRET=your-secret-key-here
```

```bash
# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f
```

#### Option 2: Direct VPS Deployment
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# Clone repository
git clone https://github.com/yourusername/flaks-music-api.git
cd flaks-music-api

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r heroku_requirements.txt

# Set environment variables
export MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net/database"
export SESSION_SECRET="your-secret-key-here"

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 2 --daemon main:app
```

#### Setup Nginx (Optional)
```bash
# Install Nginx
sudo apt install nginx -y

# Create config
sudo nano /etc/nginx/sites-available/flaks-music-api
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/flaks-music-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 🔧 Admin Panel

### Access Admin Panel
**URL:** `https://your-domain.com/admin/login`

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

**⚠️ Security:** Change default password in production!

### Admin Features
- 📊 **Dashboard**: Overview of API usage and statistics
- 🔑 **API Key Management**: Create, view, and delete API keys
- 📈 **Usage Analytics**: Track requests, response times, and success rates
- 👥 **User Management**: Monitor API key owners and their usage
- 🎨 **Modern UI**: Beautiful, responsive design with dark/light theme

### Creating API Keys
1. Login to admin panel
2. Click "Create New API Key"
3. Fill in details:
   - Owner name
   - Daily limit (default: 1000)
   - Expiry days (default: 30)
4. Copy the generated API key
5. Start using in your applications!

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MONGO_URI` | Yes | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/db` |
| `SESSION_SECRET` | Yes | Secret key for sessions | `your-secret-key-here` |
| `PORT` | No | Port number (Heroku sets automatically) | `5000` |

### MongoDB Setup

#### Option 1: MongoDB Atlas (Recommended)
1. Visit [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create free cluster
3. Create database user
4. Get connection string
5. Use in `MONGO_URI`

#### Option 2: Local MongoDB
```bash
# Install MongoDB
sudo apt install mongodb -y

# Start service
sudo systemctl start mongodb

# Use connection string
MONGO_URI=mongodb://localhost:27017/flaks_music_api
```

### Production Security

**Change default admin credentials:**
```python
# In app.py, modify:
admin_user = {
    "username": "your-admin-username",
    "password": "your-secure-password",
    "created_at": datetime.utcnow()
}
```

**Use strong session secret:**
```bash
# Generate secure secret
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 💻 Example Usage

### Python Example
```python
import requests
import asyncio
import aiohttp

API_KEY = "user_abc123..."
BASE_URL = "https://your-domain.herokuapp.com"

async def get_music_stream(query):
    """Get music stream URL"""
    url = f"{BASE_URL}/api/stream"
    params = {
        'api_key': API_KEY,
        'query': query
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data['success']:
                    return data['stream_url']
    return None

# Usage
async def main():
    stream_url = await get_music_stream("tum hi ho")
    print(f"Stream URL: {stream_url}")

asyncio.run(main())
```

### Telegram Bot Example
```python
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import aiohttp

API_KEY = "user_abc123..."
BASE_URL = "https://your-domain.herokuapp.com"

async def music_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /music command"""
    if not context.args:
        await update.message.reply_text("Usage: /music <song name>")
        return
    
    query = " ".join(context.args)
    await update.message.reply_text("🔍 Searching for music...")
    
    # Get stream URL
    url = f"{BASE_URL}/api/stream"
    params = {'api_key': API_KEY, 'query': query}
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            if response.status == 200:
                data = await response.json()
                if data['success']:
                    # Send audio
                    await context.bot.send_audio(
                        chat_id=update.effective_chat.id,
                        audio=data['stream_url'],
                        title=data['title'],
                        performer=data['artist']
                    )
                    return
    
    await update.message.reply_text("❌ Music not found!")

# Setup bot
app = Application.builder().token("YOUR_BOT_TOKEN").build()
app.add_handler(CommandHandler("music", music_command))
app.run_polling()
```

### JavaScript Example
```javascript
const API_KEY = 'user_abc123...';
const BASE_URL = 'https://your-domain.herokuapp.com';

async function getMusicStream(query) {
    try {
        const response = await fetch(`${BASE_URL}/api/stream?api_key=${API_KEY}&query=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success) {
            return data.stream_url;
        }
    } catch (error) {
        console.error('Error:', error);
    }
    return null;
}

// Usage
getMusicStream('geruva').then(streamUrl => {
    if (streamUrl) {
        console.log('Stream URL:', streamUrl);
        // Play audio using HTML5 audio element
        const audio = new Audio(streamUrl);
        audio.play();
    }
});
```

### cURL Examples
```bash
# Search for music
curl "https://your-domain.com/api/stream?api_key=YOUR_KEY&query=tum+hi+ho"

# Get trending music
curl "https://your-domain.com/api/trending?api_key=YOUR_KEY&limit=5"

# Check API status
curl "https://your-domain.com/api/status?api_key=YOUR_KEY"

# Search without stream (faster)
curl "https://your-domain.com/api/search?api_key=YOUR_KEY&query=arijit+singh"
```

## 🔧 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed
**Error:** `ServerSelectionTimeoutError`

**Solution:**
- Check `MONGO_URI` format
- Ensure database user has correct permissions
- Verify network access (whitelist IP in MongoDB Atlas)

#### 2. API Key Not Working
**Error:** `Invalid API key`

**Solution:**
- Check API key format
- Ensure key hasn't expired
- Verify daily limit not exceeded

#### 3. Slow Response Times
**Possible Causes:**
- Network latency
- JioSaavn server issues
- High server load

**Solutions:**
- Use caching (Redis recommended)
- Increase server resources
- Implement request queuing

#### 4. Admin Panel Not Accessible
**Error:** `404 Not Found`

**Solution:**
- Check URL: `/admin/login`
- Verify admin user exists in database
- Check Flask routes are loaded

### Performance Optimization

#### 1. Enable Caching
```python
# Add Redis caching
import redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Cache search results for 1 hour
def cache_search_result(query, result):
    r.setex(f"search:{query}", 3600, json.dumps(result))
```

#### 2. Database Indexing
```javascript
// MongoDB indexes for better performance
db.api_keys.createIndex({"api_key": 1})
db.usage_stats.createIndex({"api_key": 1, "timestamp": -1})
```

#### 3. Load Balancing
```yaml
# docker-compose.yml for multiple workers
version: '3.8'
services:
  app1:
    build: .
    ports: ["5001:5000"]
  app2:
    build: .
    ports: ["5002:5000"]
  nginx:
    image: nginx
    ports: ["80:80"]
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### Monitoring

#### Health Check Endpoint
```bash
curl "https://your-domain.com/health"
```

#### API Analytics
- Check admin panel for usage statistics
- Monitor response times
- Track error rates

### Support

**Issues:** [GitHub Issues](https://github.com/yourusername/flaks-music-api/issues)
**Documentation:** [Wiki](https://github.com/yourusername/flaks-music-api/wiki)
**Contact:** your-email@domain.com

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 🌟 Show Your Support

Give a ⭐️ if this project helped you!

---

**Made with ❤️ for the developer community**

**Deploy Status:** [![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)