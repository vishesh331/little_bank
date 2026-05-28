"""
movie_streaming/app.py — Apple TV-like Movie Distribution Service
==================================================================
A Flask-based streaming service that integrates with the bank.py module
for secure payment processing using Supabase backend.

Run:
    python movie_streaming/app.py

Features:
    - Browse movies with prices and thumbnails
    - Secure payment via existing bank accounts
    - Stream movies via embedded YouTube
    - Purchase history tracking
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path to import bank module
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()

from flask import Flask, render_template, request, jsonify, redirect, url_for, session as flask_session
from functools import wraps
import json
from datetime import datetime

# Import banking system
from bank import BankingSystem, InsufficientFundsError, AuthenticationError, AccountNotFoundError

# Try to use Supabase backend
try:
    from supabase_backend import create_supabase_backend_from_env
    backend = create_supabase_backend_from_env()
    bank = BankingSystem(backend=backend) if backend else BankingSystem()
except (ImportError, Exception) as e:
    print(f"Warning: Could not initialize Supabase backend: {e}")
    print("Falling back to local JSON backend")
    bank = BankingSystem()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-change-this-in-production')

# Movie streaming account (seller)
MOVIE_SELLER_NAME = "CinemaStream Distribution"
MOVIE_SELLER_PASSWORD = "cinema_stream_secure"
MOVIE_SELLER_ACCOUNT = None  # Will be set by _ensure_seller_account()

# Load movies from JSON file
def _load_movies():
    """Load movie catalog from movies.json file."""
    try:
        movies_file = Path(__file__).parent / 'movies.json'
        with open(movies_file, 'r') as f:
            data = json.load(f)
            return data.get('movies', [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Warning: Could not load movies.json: {e}")
        return []

MOVIES = _load_movies()

# Ensure movie seller account exists
def _ensure_seller_account():
    """Create movie seller account if it doesn't exist."""
    global MOVIE_SELLER_ACCOUNT
    
    # Try to find existing seller account by username
    try:
        data = bank._load()
        for account_num, account_record in data.get("accounts", {}).items():
            if account_record.get("username") == MOVIE_SELLER_NAME:
                MOVIE_SELLER_ACCOUNT = account_num
                return
    except Exception:
        pass
    
    # If not found, create new seller account
    try:
        account_info = bank.create_account(
            username=MOVIE_SELLER_NAME,
            password=MOVIE_SELLER_PASSWORD,
            initial_balance=0.0
        )
        MOVIE_SELLER_ACCOUNT = account_info['account_number']
    except Exception as e:
        print(f"Warning: Could not create seller account: {e}")
        raise

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_account' not in flask_session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Home page - redirect to catalog if logged in."""
    if 'user_account' in flask_session:
        return redirect(url_for('catalog'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if request.method == 'POST':
        account_number = request.form.get('account_number', '').strip()
        password = request.form.get('password', '').strip()

        try:
            account = bank.authenticate(account_number, password)
            flask_session['user_account'] = account_number
            flask_session['user_name'] = account.get('username', 'User')
            return redirect(url_for('catalog'))
        except (AuthenticationError, AccountNotFoundError) as e:
            return render_template('login.html', error=str(e))

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user."""
    flask_session.clear()
    return redirect(url_for('login'))

@app.route('/catalog')
@login_required
def catalog():
    """Display movie catalog."""
    balance = bank.get_balance(flask_session['user_account'])
    return render_template(
        'catalog.html',
        movies=MOVIES,
        user_name=flask_session.get('user_name'),
        balance=balance
    )

@app.route('/api/movie/<int:movie_id>')
@login_required
def get_movie(movie_id):
    """Get movie details."""
    for movie in MOVIES:
        if movie['id'] == movie_id:
            return jsonify(movie)
    return jsonify({'error': 'Movie not found'}), 404

@app.route('/api/balance')
@login_required
def get_balance():
    """Get user's current balance."""
    try:
        balance = bank.get_balance(flask_session['user_account'])
        return jsonify({'balance': balance})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/process-payment', methods=['POST'])
@login_required
def process_payment():
    """Process movie purchase payment."""
    data = request.get_json()
    movie_id = data.get('movie_id')
    password = data.get('password', '').strip()

    # Find the movie
    movie = None
    for m in MOVIES:
        if m['id'] == movie_id:
            movie = m
            break

    if not movie:
        return jsonify({'error': 'Movie not found'}), 404

    # Process payment
    try:
        receipt = bank.transfer(
            from_account=flask_session['user_account'],
            password=password,
            to_account=MOVIE_SELLER_ACCOUNT,
            amount=movie['price']
        )
        
        # Store purchase in session
        if 'purchases' not in flask_session:
            flask_session['purchases'] = []
        
        purchase = {
            'movie_id': movie_id,
            'movie_title': movie['title'],
            'amount': movie['price'],
            'transaction_id': receipt['transaction_id'],
            'timestamp': datetime.now().isoformat()
        }
        flask_session['purchases'].append(purchase)
        flask_session.modified = True

        return jsonify({
            'success': True,
            'message': f"Successfully purchased '{movie['title']}'",
            'transaction_id': receipt['transaction_id'],
            'remaining_balance': receipt['new_balance']
        })

    except InsufficientFundsError:
        return jsonify({'error': 'Insufficient funds. Please deposit money.'}), 400
    except AuthenticationError:
        return jsonify({'error': 'Invalid password.'}), 401
    except AccountNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/watch/<int:movie_id>')
@login_required
def watch_movie(movie_id):
    """Verify purchase and show video player."""
    # Check if user has purchased this movie
    purchases = flask_session.get('purchases', [])
    purchased = any(p['movie_id'] == movie_id for p in purchases)

    if not purchased:
        return redirect(url_for('catalog'))

    # Get movie details
    movie = None
    for m in MOVIES:
        if m['id'] == movie_id:
            movie = m
            break

    if not movie:
        return redirect(url_for('catalog'))

    balance = bank.get_balance(flask_session['user_account'])
    return render_template(
        'player.html', 
        movie=movie,
        balance=balance,
        user_name=flask_session.get('user_name'),
    )

@app.route('/purchases')
@login_required
def purchases():
    """Show user's purchase history."""
    purchases_list = flask_session.get('purchases', [])
    balance = bank.get_balance(flask_session['user_account'])
    return render_template(
        'purchases.html', 
        purchases=purchases_list,
        balance=balance,
        user_name=flask_session.get('user_name'),
    )

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', error='Server error'), 500

if __name__ == '__main__':
    _ensure_seller_account()
    app.run(debug=True, port=5000, host='0.0.0.0')
