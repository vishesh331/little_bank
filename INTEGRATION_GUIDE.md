# CinemaStream Integration Guide

## Overview

The CinemaStream movie distribution service has been successfully integrated into your Little Bank ecosystem. This document explains how everything works together.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      hub.py (CLI Hub)                       │
│         Central entry point for all services                │
└─────────────┬───────────────────────────────────────────────┘
              │
              ├─► Banking System (bank.py)
              ├─► Casino (numberguesser.py)
              ├─► Movie Tickets (movie_tickets.py)
              └─► CinemaStream Web App (Flask)
                  
                  ┌─────────────────────────────────┐
                  │  movie_streaming/app.py         │
                  │  (Flask Web Application)        │
                  └────────────┬────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
              ┌─────▼──────┐      ┌──────▼────────┐
              │  Templates │      │  Static Files │
              │  (HTML UI) │      │ (CSS/JS/IMG)  │
              └────────────┘      └───────────────┘
                    │
         ┌──────────┴──────────┐
         │                     │
    ┌────▼─────┐        ┌─────▼──────┐
    │ Front-End │        │  Backend   │
    │ (React    │        │  (Flask    │
    │  Logic)   │        │  Routes)   │
    └──────────┘        └─────┬──────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
              ┌─────▼────────┐    ┌──────▼──────┐
              │  bank.py     │    │  Supabase   │
              │  Module      │    │  (Optional) │
              └──────────────┘    └─────────────┘
```

## How It Works

### 1. User Login Flow

```
User → hub.py Login
    ↓
bank.authenticate() [banking system]
    ↓
create_session() [creates .session_token.tmp]
    ↓
User has access to all services
```

### 2. Accessing CinemaStream

**Via CLI Hub**:
```
hub.py → Services Menu → Option 4: CinemaStream
→ Flask app launches at http://localhost:5000
→ Browser opens automatically
```

**Direct Access**:
```
cd movie_streaming
python app.py
→ Navigate to http://localhost:5000
```

### 3. Movie Purchase Flow

```
User browses catalog
    ↓
Clicks movie → Payment modal appears
    ↓
Enters password → Confirms purchase
    ↓
Flask calls bank.transfer() [to MOVIE_STREAM_01 account]
    ↓
Payment successful → Redirect to player
    ↓
Video streams via YouTube embed
    ↓
Purchase saved to flask_session
```

## Key Integration Points

### Banking System Integration

**File**: `movie_streaming/app.py` (lines ~20-40)

```python
from bank import BankingSystem, ...

# Try Supabase first, fall back to JSON
try:
    from supabase_backend import create_supabase_backend_from_env
    backend = create_supabase_backend_from_env()
    bank = BankingSystem(backend=backend) if backend else BankingSystem()
except ImportError:
    bank = BankingSystem()
```

**Functions Used**:
- `bank.authenticate(account, password)` → Login
- `bank.get_balance(account)` → Check balance
- `bank.transfer(from, password, to, amount)` → Process payment
- `bank.get_account(account)` → Verify seller account exists

### Session Management

**File**: `hub.py` (lines ~286-318)

```python
def launch_movie_streaming(info: dict) -> None:
    """Launch CinemaStream with user session"""
    # Automatically opens browser
    # Flask reads session but creates separate web session
    # Balance updates on return
```

### Database Integration

The system supports two database backends:

**Local (Default)**:
- Uses `accounts.json` from parent directory
- Movies configuration in `app.py`
- Session stored in `flask_session`

**Cloud (Supabase)**:
- Configure in `.env` file:
  ```
  SUPABASE_URL=your_url
  SUPABASE_KEY=your_key
  ```
- Automatic fallback to JSON if not configured

## File Structure Explained

```
ultron/
├── bank.py                      ← Banking module (used by all services)
├── session.py                   ← Session management
├── accounts.json                ← User accounts database
├── hub.py                       ← CLI hub (modified to include CinemaStream)
├── movie_tickets.py             ← CLI movie tickets (unchanged)
├── numberguesser.py             ← Casino game (unchanged)
├── supabase_backend.py          ← Supabase integration
├── .env                         ← Environment configuration
└── movie_streaming/             ← NEW: CinemaStream web app
    ├── app.py                   ← Flask application
    ├── config.py                ← Configuration
    ├── requirements.txt         ← Dependencies
    ├── README.md                ← Full documentation
    ├── start.bat / start.sh     ← Quick start scripts
    ├── templates/
    │   ├── base.html           ← Navigation template
    │   ├── login.html          ← Login page
    │   ├── catalog.html        ← Movie catalog
    │   ├── player.html         ← Video player
    │   ├── purchases.html      ← Purchase history
    │   └── error.html          ← Error page
    └── static/
        ├── css/style.css       ← Apple TV styling
        ├── js/main.js          ← Frontend logic
        └── images/thumbnails/  ← Movie posters
```

## Modified Files

### hub.py Changes

**Addition**: `launch_movie_streaming()` function (after line 300)
- Opens CinemaStream web interface
- Handles Flask server startup
- Refreshes balance on return

**Modification**: `screen_services_menu()` function
- Added menu option 4 for CinemaStream
- Updated menu display (was [4] Account Overview, now [4] CinemaStream, [5] Account, [6] History, etc.)

## Configuration

### Environment Variables

Create `.env` in the project root:

```env
# Banking (Optional - defaults to JSON)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# Flask (Optional - auto-generated if not provided)
FLASK_SECRET_KEY=your-secret-key-change-this-in-production

# Server (Optional - defaults shown)
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
```

### Movie Configuration

Edit `movie_streaming/app.py` to customize:

```python
# Movie prices (default $500)
MOVIES = [
    {
        "id": 1,
        "title": "Movie Title",
        "price": 500.0,  # ← Change here
        ...
    }
]

# Seller account details
MOVIE_SELLER_ACCOUNT = "MOVIE_STREAM_01"
MOVIE_SELLER_NAME = "CinemaStream Distribution"
```

## API Endpoints

### Authentication
- `GET /` - Home (redirects to catalog if logged in)
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /logout` - Logout

### Movies
- `GET /catalog` - Display catalog
- `GET /api/movie/<id>` - Get movie details (JSON)
- `GET /api/balance` - Get user balance (JSON)

### Purchases
- `POST /api/process-payment` - Process purchase
- `GET /watch/<movie_id>` - Stream video
- `GET /purchases` - Purchase history

## Security Features

✅ **Session Security**
- Flask session cookies
- HTTP-only cookies
- Password-protected payments

✅ **Transaction Security**
- Password confirmation required
- Real banking integration
- Supabase encryption (if configured)

✅ **User Privacy**
- No stored passwords (hashed in bank)
- Sessions clear on logout
- No user tracking

⚠️ **For Production**
- Set `SESSION_COOKIE_SECURE=True` (requires HTTPS)
- Use strong `FLASK_SECRET_KEY`
- Enable HTTPS on server
- Restrict CORS if needed

## Deployment

### Local Development
```bash
cd movie_streaming
python app.py
# Access: http://localhost:5000
```

### Production (Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY movie_streaming/ .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]
```

## Troubleshooting

### Flask not starting
```bash
# Verify Python installation
python --version

# Install dependencies
pip install -r movie_streaming/requirements.txt

# Run with verbose output
python -u app.py
```

### Port already in use
```bash
# Use different port
FLASK_PORT=5001 python app.py

# Or kill process using port 5000
# Windows: netstat -ano | findstr :5000
# Linux: lsof -i :5000 | grep LISTEN
```

### Database connection issues
```bash
# Check if Supabase credentials are correct
# Falls back to JSON automatically if not configured

# Verify accounts.json exists
ls -la accounts.json
```

### Templates not loading
```bash
# Ensure templates are in correct directory
movie_streaming/templates/

# Verify file names match exactly (case-sensitive on Linux)
```

## Monitoring & Logs

The Flask app logs to console by default. For file logging:

```python
# Add to app.py
import logging
logging.basicConfig(filename='logs/app.log', level=logging.INFO)
```

View logs:
```bash
tail -f logs/app.log  # Linux/Mac
type logs/app.log     # Windows
```

## Performance Optimization

### Caching
```python
# Add to app.py for movie list caching
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/catalog')
@cache.cached(timeout=300)  # 5 minutes
def catalog():
    ...
```

### Database Indexing
Supabase automatically indexes foreign keys. For JSON, consider:
- Filtering in-memory for small datasets
- Moving to Supabase for large datasets

### Load Testing
```bash
# Test with Apache Bench
ab -n 100 -c 10 http://localhost:5000/catalog
```

## Maintenance

### Regular Tasks
- [ ] Monitor error logs
- [ ] Update dependencies: `pip install --upgrade -r movie_streaming/requirements.txt`
- [ ] Backup accounts.json weekly
- [ ] Clear old sessions periodically

### Updating Movies
1. Edit `app.py` MOVIES list
2. Add thumbnail URLs or upload images
3. Set appropriate prices
4. Test purchase flow

### Upgrading Flask
```bash
pip install --upgrade Flask
# Test thoroughly before production deployment
```

## Future Enhancements

Possible additions:
- [ ] Movie recommendations engine
- [ ] Watchlist/favorites feature
- [ ] Social sharing (purchase with friends)
- [ ] Movie reviews and ratings
- [ ] Subscription plans (monthly rental)
- [ ] Multiple video sources (not just YouTube)
- [ ] Search by actor/director
- [ ] Parental controls
- [ ] Rental vs purchase options
- [ ] Wishlist feature

## Support & Contact

For issues:
1. Check error logs in Flask output
2. Review troubleshooting section above
3. Check movie_streaming/README.md
4. Verify banking system is working: `python hub.py`

---

**Integration Complete!** 🎉

Your CinemaStream movie distribution service is now fully integrated with your Little Bank ecosystem. Users can:
1. Login via hub.py
2. Access CinemaStream directly
3. Purchase movies with their bank account
4. Stream immediately

Enjoy!
