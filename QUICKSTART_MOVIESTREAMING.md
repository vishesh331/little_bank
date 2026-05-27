# Quick Start Guide - CinemaStream Movie Distribution

## What's New?

You now have a beautiful, Apple TV-inspired movie distribution service integrated into your system! 🎬

## Quick Start

### Option 1: Web-Based (Recommended)

1. **Install dependencies**:
   ```bash
   cd movie_streaming
   pip install -r requirements.txt
   ```

2. **Run the application**:
   - **Windows**: Double-click `start.bat`
   - **Linux/Mac**: `bash start.sh` or `python3 app.py`

3. **Open your browser**:
   - Navigate to `http://localhost:5000`
   - Login with your bank account credentials

4. **Browse and stream**:
   - Browse the movie catalog
   - Click a movie to purchase
   - Confirm payment with your password
   - Stream immediately via YouTube embed

### Option 2: CLI Integration

If you prefer using the CLI hub:

1. Run `python hub.py`
2. Select "CinemaStream - Movie Distribution" from the services menu
3. Your browser will automatically open the web interface

## Features at a Glance

✨ **Beautiful UI**
- Apple TV-inspired design
- Responsive layout (mobile, tablet, desktop)
- Smooth animations and transitions
- Dark mode with neon accents

💳 **Secure Payments**
- Uses your existing bank account
- Real transaction processing
- Payment confirmation modal
- Balance verification

🎬 **Movie Streaming**
- 7 sample movies included
- Genre filtering and search
- Purchase history tracking
- Embedded YouTube player

📱 **Responsive Design**
- Works on all devices
- Touch-friendly interface
- Mobile-optimized navigation

## Demo Account

For testing, use these credentials:
- **Account**: demo001
- **Password**: password123

Or create your own account!

## File Structure

```
movie_streaming/
├── app.py                    # Main Flask application
├── config.py                 # Configuration settings
├── requirements.txt          # Dependencies
├── start.bat / start.sh      # Quick start scripts
├── README.md                 # Full documentation
├── templates/
│   ├── base.html            # Navigation & layout
│   ├── login.html           # Login page
│   ├── catalog.html         # Movie browsing
│   ├── player.html          # Video player
│   ├── purchases.html       # History
│   └── error.html           # Error page
└── static/
    ├── css/style.css        # Apple TV styling
    ├── js/main.js           # Frontend logic
    └── images/thumbnails/   # Movie posters
```

## Adding New Movies

Edit `app.py` and add to the `MOVIES` list:

```python
{
    "id": 8,
    "title": "Your Movie Title",
    "price": 500.0,
    "description": "Movie description",
    "thumbnail": "https://image-url.com/poster.jpg",
    "youtube_id": "YouTube_Video_ID",
    "rating": "4.5/5",
    "genre": "Genre"
}
```

## Customizing Prices

All movies default to $500, but you can set custom prices:

```python
{
    "id": 8,
    "title": "Premium Movie",
    "price": 750.0,  # Custom price
    ...
}
```

## Troubleshooting

**Port 5000 already in use?**
```bash
# Change port in app.py:
if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Use different port
```

**Videos not loading?**
- Check internet connection
- Ensure YouTube video IDs are correct
- Some regions may block YouTube embeds

**Login issues?**
- Verify account exists in banking system
- Check password is correct
- Create new account if needed

**Database connection?**
- Ensure Supabase credentials in .env
- Falls back to JSON if not configured

## Integration with Hub

The movie streaming service is fully integrated into hub.py:
1. Login through hub.py
2. Select "CinemaStream - Movie Distribution"
3. Browser opens automatically
4. Your session persists across services

## Database

- **Local**: Uses accounts.json (default)
- **Cloud**: Uses Supabase if configured in .env
- Movies and transactions sync across both

## Next Steps

1. ✅ Install dependencies: `pip install -r movie_streaming/requirements.txt`
2. ✅ Start the server: `python app.py`
3. ✅ Open browser: `http://localhost:5000`
4. ✅ Login with your bank account
5. ✅ Browse and purchase movies!

## Support

- Full documentation: See `movie_streaming/README.md`
- Issues? Check troubleshooting section above
- Questions? Review the code comments

---

**Enjoy CinemaStream! 🎬🍿**
