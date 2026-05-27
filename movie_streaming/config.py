"""
Configuration file for CinemaStream Flask application
"""

import os
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).parent

# Flask Configuration
DEBUG = os.getenv('FLASK_DEBUG', True)
TESTING = os.getenv('TESTING', False)
SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Session Configuration
SESSION_TYPE = 'filesystem'
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds
SESSION_PERMANENT = False
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# Movie Streaming Configuration
MOVIE_SELLER_ACCOUNT = os.getenv('MOVIE_SELLER_ACCOUNT', 'MOVIE_STREAM_01')
MOVIE_SELLER_NAME = os.getenv('MOVIE_SELLER_NAME', 'CinemaStream Distribution')
MOVIE_SELLER_PASSWORD = os.getenv('MOVIE_SELLER_PASSWORD', 'cinema_stream_secure')

# Server Configuration
HOST = os.getenv('FLASK_HOST', '0.0.0.0')
PORT = int(os.getenv('FLASK_PORT', 5000))

# Database Configuration (Supabase)
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Pagination
ITEMS_PER_PAGE = 12

# File Uploads
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = BASE_DIR / 'logs' / 'app.log'

# Create logs directory if it doesn't exist
LOG_FILE.parent.mkdir(exist_ok=True)
