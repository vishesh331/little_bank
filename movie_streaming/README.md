# CinemaStream - Movie Distribution Service

A beautiful, Apple TV-inspired Flask web application for movie distribution and streaming with secure payment integration.

## Features

- **Apple TV-like UI**: Modern, responsive design with gradient backgrounds and glassmorphism
- **Secure Payment Processing**: Integrates with the banking system for real transaction processing
- **Movie Catalog**: Browse, search, and filter movies by genre
- **Payment Confirmation**: Modal-based payment confirmation with balance verification
- **Video Streaming**: Embedded YouTube video player for purchased movies
- **Purchase History**: Track all your movie purchases and transaction details
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Session Management**: Persistent user sessions with secure authentication

## Installation

### Prerequisites

- Python 3.8+
- Flask
- Supabase account (for backend persistence)

### Setup Steps

1. **Navigate to the movie_streaming directory**:
   ```bash
   cd movie_streaming
   ```

2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the parent directory with your Supabase credentials:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_anon_key
   FLASK_SECRET_KEY=your_secret_key_here
   ```

5. **Run the application**:
   ```bash
   python app.py
   ```

6. **Access the application**:
   Open your browser and navigate to `http://localhost:5000`

## Project Structure

```
movie_streaming/
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── templates/
│   ├── base.html              # Base template with navigation
│   ├── login.html             # User login page
│   ├── catalog.html           # Movie catalog with search & filters
│   ├── player.html            # Video player page
│   ├── purchases.html         # Purchase history
│   └── error.html             # Error page
├── static/
│   ├── css/
│   │   └── style.css          # Custom Apple TV styling
│   ├── js/
│   │   └── main.js            # Frontend JavaScript logic
│   └── images/
│       └── thumbnails/        # Movie poster images
└── README.md                   # Documentation
```

## Usage

### User Flow

1. **Login**: Enter your bank account number and password
2. **Browse**: Explore the catalog with search and genre filters
3. **Purchase**: Click on a movie to trigger payment confirmation
4. **Confirm**: Enter your password and confirm the purchase
5. **Stream**: Watch your purchased movie via embedded YouTube
6. **History**: View all your purchases and transaction details

### Default Demo Account

For testing purposes, a demo account is pre-configured:
- **Account Number**: `demo001`
- **Password**: `password123`

### Available Movies

The system comes with 7 sample movies:

1. **Galactic Odyssey** (Sci-Fi) - $500
2. **The Last Lighthouse** (Mystery) - $500
3. **Robots vs. Wizards** (Action) - $500
4. **Neon Dreams** (Cyberpunk) - $500
5. **Mountain Echoes** (Drama) - $500
6. **Quantum Heist** (Thriller) - $500
7. **Eternal Sunset** (Romance) - $500

### Seller Configuration

The movie distribution seller account is configured with:
- **Account Number**: `MOVIE_STREAM_01`
- **Name**: `CinemaStream Distribution`
- **Password**: `cinema_stream_secure` (for initialization only)

You can modify these in `app.py` to customize the seller details.

## API Endpoints

### Authentication
- `GET /` - Home page (redirects to catalog if logged in)
- `GET /login` - Login page
- `POST /login` - Process login
- `GET /logout` - Logout user

### Movie Management
- `GET /catalog` - Display all movies
- `GET /api/movie/<movie_id>` - Get movie details (JSON)
- `GET /api/balance` - Get user's current balance (JSON)

### Purchases & Streaming
- `POST /api/process-payment` - Process movie purchase
- `GET /watch/<movie_id>` - Stream purchased movie
- `GET /purchases` - View purchase history

## Customization

### Adding New Movies

Edit the `MOVIES` list in `app.py`:

```python
MOVIES = [
    {
        "id": 8,
        "title": "Your Movie Title",
        "price": 500.0,
        "description": "Movie description",
        "thumbnail": "https://image-url.com/poster.jpg",
        "youtube_id": "YouTube_Video_ID",
        "rating": "4.5/5",
        "genre": "Genre"
    },
    # ... more movies
]
```

### Changing Movie Prices

Simply modify the `price` field for any movie in the `MOVIES` list. Prices are validated against user balances during checkout.

### Customizing Styling

Edit `static/css/style.css` to modify:
- Color scheme (gradients, accents)
- Layout and spacing
- Responsive breakpoints
- Animations and transitions

### Adding Movie Thumbnails

1. Store image files in `static/images/thumbnails/`
2. Update the `thumbnail` field in the MOVIES list to point to your local or external image URL

## Integration with Banking System

This service integrates with the parent project's banking system:

- **Account Verification**: Uses `bank.authenticate()` for login
- **Balance Checking**: Verifies user has sufficient funds
- **Payment Processing**: Uses `bank.transfer()` for secure transactions
- **Supabase Backend**: All transactions stored in Supabase when configured

The movie seller receives all payments in their configured account (`MOVIE_STREAM_01`).

## Security Features

- **Password Protection**: All payments require password confirmation
- **Transaction Hashing**: Secure banking integration with encrypted credentials
- **Session Management**: Flask session management with secure cookies
- **Balance Verification**: Real-time balance checking before transactions
- **Error Handling**: Graceful error messages without exposing sensitive details

## Troubleshooting

### "Movie seller account not found"
- Ensure the application creates the seller account on first run
- Check database connectivity

### "Insufficient funds"
- User needs to deposit money in their bank account
- Check current balance in the navbar

### Videos not playing
- Ensure YouTube video IDs are valid
- Check internet connection
- YouTube may block embedded videos in some regions

### Login issues
- Verify account number format
- Check password is correct
- Ensure account exists in the banking system

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### Testing Payment Flow

1. Create test accounts using the banking system
2. Deposit funds to test accounts
3. Login and purchase movies
4. Verify transactions in the database

## Deployment

### Production Deployment

1. **Set environment variables** in production environment
2. **Use a production WSGI server** (Gunicorn, uWSGI):
   ```bash
   gunicorn --workers 4 app:app
   ```
3. **Enable HTTPS** using a reverse proxy (Nginx, Apache)
4. **Configure Supabase** for reliable backend storage
5. **Set secure Flask secret key** in environment

### Running with Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Browser Compatibility

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

Part of the Little Bank ecosystem project.

## Support

For issues or feature requests, refer to the main project documentation.

---

**Version**: 1.0.0  
**Last Updated**: 2026-05-27
