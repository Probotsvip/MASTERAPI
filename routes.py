from flask import render_template, request, jsonify, session, redirect, url_for, flash
from app import app, db
from models import APIKey, UsageStats
from music_sources import MusicSources
from proxy_handler import proxy_handler
import time
import logging
from datetime import datetime

music_sources = MusicSources()

@app.route('/')
def index():
    """Main landing page"""
    return render_template('dashboard.html')

@app.route('/admin')
def admin_login():
    """Admin login page"""
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    return render_template('admin.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():
    """Handle admin login"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Simple admin authentication (enhance in production)
    if username == 'admin' and password == 'admin123':
        session['admin_logged_in'] = True
        return redirect(url_for('admin_dashboard'))
    
    flash('Invalid credentials', 'error')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get all API keys
    api_keys = APIKey.get_all_keys()
    
    # Get usage statistics
    usage_stats = UsageStats.get_usage_stats()
    
    return render_template('admin.html', 
                         api_keys=api_keys, 
                         usage_stats=usage_stats,
                         dashboard=True)

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/create_key', methods=['POST'])
def create_api_key():
    """Create new API key"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    owner_name = data.get('owner_name')
    daily_limit = int(data.get('daily_limit', 1000))
    expiry_days = int(data.get('expiry_days', 30))
    
    if not owner_name:
        return jsonify({'error': 'Owner name is required'}), 400
    
    try:
        api_key = APIKey.create_api_key(owner_name, daily_limit, expiry_days)
        return jsonify({'success': True, 'api_key': api_key})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/delete_key', methods=['POST'])
def delete_api_key():
    """Delete API key"""
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    
    try:
        result = APIKey.delete_api_key(api_key)
        if result.deleted_count > 0:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'API key not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stream')
def stream_music():
    """Main music streaming endpoint"""
    start_time = time.time()
    
    # Get API key from request
    api_key = request.args.get('api_key')
    query = request.args.get('query')
    source = request.args.get('source', 'auto')
    
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    # Validate API key
    is_valid, message = APIKey.validate_api_key(api_key)
    if not is_valid:
        return jsonify({'error': message}), 401
    
    try:
        # Search for music
        result = music_sources.search_music(query, source)
        
        if result:
            # Increment API usage
            APIKey.increment_usage(api_key)
            
            # Log usage statistics
            response_time = time.time() - start_time
            UsageStats.log_request(api_key, '/api/stream', query, response_time, True)
            
            # Create proxy URL for stream
            original_stream_url = result.get('stream_url', '')
            if original_stream_url:
                proxy_url = proxy_handler.create_proxy_url(original_stream_url, api_key)
            else:
                proxy_url = ""
            
            # Return professional response with hidden source details
            return jsonify({
                'success': True,
                'title': result.get('title', ''),
                'artist': result.get('artist', ''),
                'duration': result.get('duration', ''),
                'stream_url': proxy_url,  # Your domain URL
                'quality': result.get('quality', '320kbps'),
                'response_time': round(response_time, 2),
                'api_owner': 'https://t.me/INNOCENT_FUCKER',
                'powered_by': 'Flaks Music API',
                'status': 'SUPERFAST_OPTIMIZED'
            })
        else:
            # Log failed request
            response_time = time.time() - start_time
            UsageStats.log_request(api_key, '/api/stream', query, response_time, False)
            
            return jsonify({
                'error': 'No music found for the given query',
                'response_time': response_time
            }), 404
            
    except Exception as e:
        logging.error(f"Stream music error: {str(e)}")
        response_time = time.time() - start_time
        UsageStats.log_request(api_key, '/api/stream', query, response_time, False)
        
        return jsonify({
            'error': 'Internal server error',
            'response_time': response_time
        }), 500

@app.route('/api/search')
def search_music():
    """Search music without streaming"""
    api_key = request.args.get('api_key')
    query = request.args.get('query')
    source = request.args.get('source', 'auto')
    
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    
    # Validate API key
    is_valid, message = APIKey.validate_api_key(api_key)
    if not is_valid:
        return jsonify({'error': message}), 401
    
    try:
        result = music_sources.search_music(query, source)
        
        if result:
            APIKey.increment_usage(api_key)
            return jsonify({
                'success': True,
                'title': result['title'],
                'artist': result['artist'],
                'duration': result['duration'],
                'quality': result['quality'],
                'api_owner': 'https://t.me/INNOCENT_FUCKER',
                'powered_by': 'Flaks Music API'
            })
        else:
            return jsonify({'error': 'No music found'}), 404
            
    except Exception as e:
        logging.error(f"Search music error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/trending')
def get_trending():
    """Get trending music"""
    api_key = request.args.get('api_key')
    source = request.args.get('source', 'jiosaavn')
    limit = int(request.args.get('limit', 10))
    
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    
    # Validate API key
    is_valid, message = APIKey.validate_api_key(api_key)
    if not is_valid:
        return jsonify({'error': message}), 401
    
    try:
        trending = music_sources.get_trending_music(source, limit)
        APIKey.increment_usage(api_key)
        
        return jsonify({
            'success': True,
            'trending': trending,
            'source': source
        })
        
    except Exception as e:
        logging.error(f"Trending music error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/status')
def api_status():
    """Check API status"""
    api_key = request.args.get('api_key')
    
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    
    key_data = APIKey.get_api_key(api_key)
    if not key_data:
        return jsonify({'error': 'Invalid API key'}), 401
    
    return jsonify({
        'success': True,
        'owner': key_data.get('owner_name'),
        'daily_limit': key_data.get('daily_limit'),
        'requests_today': key_data.get('requests_today'),
        'total_requests': key_data.get('total_requests'),
        'expires_at': key_data.get('expires_at').isoformat() if key_data.get('expires_at') else None,
        'is_active': key_data.get('is_active')
    })

@app.route('/proxy/stream/<url_hash>')
def proxy_stream(url_hash):
    """Proxy stream endpoint to hide original URLs"""
    return proxy_handler.stream_audio(url_hash)

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
