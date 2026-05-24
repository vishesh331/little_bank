# Little Bank 🏦💰

A complete, integrated banking and gaming ecosystem built with Python. One login, access everything: bank accounts, casino games, movie tickets, and more.

## 🎯 What It Does

Little Bank is a unified platform where users can:

- **Create & manage bank accounts** - Full banking features with secure authentication
- **Play casino games** - Number guessing game to win/lose money
- **Buy movie tickets** - Purchase tickets using your bank balance
- **Track everything** - Complete transaction history across all services
- **Login once** - Access all services with a single session

All services share the same database and user accounts—win money in the casino, spend it on tickets, check your balance everywhere.

## 🚀 Quick Start (5 minutes)

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/little_bank.git
cd little_bank

# Optional: Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies (currently uses only Python stdlib)
# For cloud support (Supabase), install optional dependencies:
# pip install supabase python-dotenv
```

### Running the Application

```bash
# Start the main hub (recommended for new users)
python hub.py

# Or run individual services:
python cli.py              # Banking CLI
python numberguesser.py    # Casino
python movie_tickets.py    # Movie ticket store
```

### First Time Users

1. **Start the hub**: `python hub.py`
2. **Create a new account** or use test account:
   - Account: `1340987248`
   - Password: `12345678`
3. **From the hub menu**, select:
   - 💳 Banking - deposit, withdraw, transfer money
   - 🎰 Casino - play the number guessing game
   - 🎬 Movie Tickets - buy tickets
   - 📊 Transactions - view transaction history

## 📁 Project Structure

```
little_bank/
├── Core Banking Engine
│   ├── bank.py                 # Main banking system (reusable module)
│   ├── session.py              # Session management (login once, access all)
│   └── accounts.json           # Local database
│
├── User Interfaces
│   ├── hub.py                  # Central dashboard (start here!)
│   ├── cli.py                  # Command-line banking interface
│   ├── numberguesser.py        # Casino: number guessing game
│   └── movie_tickets.py        # Movie ticket store
│
├── Cloud Integration (Optional)
│   ├── supabase_backend.py     # Supabase PostgreSQL adapter
│   ├── migrate_to_supabase.py  # Data migration tool
│   ├── .env.example            # Configuration template
│   └── SUPABASE_SCHEMA.sql     # Cloud database schema
│
└── Testing & Documentation
    ├── smoke_test.py           # Automated tests
    ├── example_usage.py        # Code examples
    └── README.md               # This file
```

## 💾 How Storage Works

### Local Storage (Default)
- Uses `accounts.json` file
- Perfect for development and testing
- Works offline
- No configuration needed
- Data persists between runs

### Cloud Storage (Optional)
- Uses Supabase PostgreSQL database
- Perfect for production and multiple users
- Automatic backups and security
- Accessible from anywhere
- Setup takes 5 minutes

**To use cloud storage:**

```bash
# 1. Get a Supabase account (free tier available)
# Visit: https://supabase.com

# 2. Create a new project
# 3. Get your project URL and API key

# 4. Create .env file (copy from .env.example)
cp .env.example .env

# 5. Edit .env with your Supabase credentials
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your_anon_key_here
# USE_SUPABASE=true

# 6. Install cloud dependencies
pip install supabase python-dotenv

# 7. Set up the database schema
python migrate_to_supabase.py

# 8. Run normally - it now uses cloud storage!
python hub.py
```

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     Hub (hub.py)                    │
│  Central login & dashboard          │
└─────────────────┬───────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌────────┐   ┌────────┐   ┌────────────┐
│ CLI    │   │ Casino │   │ Tickets    │
│Banking │   │Numbers │   │Movie Store │
└────────┘   └────────┘   └────────────┘
    │             │             │
    └─────────────┼─────────────┘
                  │
          ┌───────▼────────┐
          │   bank.py      │
          │  Banking       │
          │  Engine        │
          └───────┬────────┘
                  │
          ┌───────▼────────┐
          │   Storage      │
          │ JSON or Cloud  │
          └────────────────┘
```

**Key Design Principles:**

1. **Modular** - Each service is independent
2. **Reusable** - `bank.py` can power any UI or application
3. **Secure** - Session management, password hashing, secure transactions
4. **Scalable** - Start with JSON, scale to cloud seamlessly
5. **Extensible** - Add new services easily without modifying existing ones

## 📖 Commands Reference

### Main Application
```bash
python hub.py              # Start the main hub (recommended)
```

### Individual Services
```bash
python cli.py              # Banking CLI interface
python numberguesser.py    # Casino game
python movie_tickets.py    # Movie ticket store
```

### Utilities
```bash
python smoke_test.py           # Run automated tests
python example_usage.py        # See code examples
python migrate_to_supabase.py  # Migrate data to cloud
```

## 🧪 Testing

Run the test suite to verify everything is working:

```bash
python smoke_test.py
```

This will:
- Create test accounts
- Test deposits, withdrawals, and transfers
- Verify transaction history
- Test casino gameplay
- Clean up test data

## 🔐 Security Notes

### What's Already Secured
✅ Passwords are hashed (not stored in plain text)  
✅ Session management prevents re-login  
✅ Balance validation prevents overdrafts  
✅ All transactions are logged  

### For Production Deployment
⚠️ Use Supabase or another cloud database  
⚠️ Enable HTTPS/SSL encryption  
⚠️ Use strong passwords for accounts  
⚠️ Implement rate limiting on API calls  
⚠️ Enable Row-Level Security (RLS) in Supabase  
⚠️ Keep `.env` file secret (already in `.gitignore`)  

## 📊 Example Usage (for Developers)

### Import bank.py in Your Own Project

```python
from bank import BankingSystem, InsufficientFundsError

bank = BankingSystem()

# Create account
account = bank.create_account(
    username="alice",
    password="secretpassword",
    initial_balance=1000.0
)
print(f"Account created: {account['account_number']}")

# Transfer money
receipt = bank.transfer(
    from_account=account['account_number'],
    password="secretpassword",
    to_account="bob_account",
    amount=100.0
)

if receipt['status'] == 'success':
    print(f"Transfer successful! Transaction ID: {receipt['transaction_id']}")
```

### Session Management

```python
from session import get_current_session, save_session

# Check if user is already logged in
session = get_current_session()
if session:
    print(f"Welcome back, {session['username']}!")
else:
    print("Please login first")
```

## 🎮 Gameplay Features

### Casino (Number Guessing)
- Guess a number between 1-100
- Win money if you're within 10 of the correct number
- Lose your bet if you're too far off
- Try multiple times to increase winnings

### Movie Tickets
- Browse available movies
- See prices and availability
- Purchase tickets with your bank balance
- Transaction recorded in your history

## 🚧 Future Enhancements

Possible additions with the current architecture:
- Web interface (Flask/Django)
- Mobile app support
- More casino games (slots, poker)
- Sports betting
- Cryptocurrency integration
- Loan system
- Recurring payments/subscriptions
- Analytics dashboard
- Social features (send money to friends)

## 📝 File Descriptions

| File | Purpose |
|------|---------|
| `bank.py` | Core banking engine - can be imported into any project |
| `hub.py` | Main dashboard - login once, access everything |
| `session.py` | Session management - keeps you logged in |
| `cli.py` | Command-line banking interface |
| `numberguesser.py` | Casino game (number guessing) |
| `movie_tickets.py` | Movie ticket purchasing system |
| `supabase_backend.py` | Cloud database adapter (optional) |
| `migrate_to_supabase.py` | Tool to move data to cloud |
| `accounts.json` | Local database (JSON file) |
| `SUPABASE_SCHEMA.sql` | SQL schema for cloud database |
| `smoke_test.py` | Automated test suite |
| `example_usage.py` | Code examples for developers |

## 🐛 Troubleshooting

### "accounts.json not found" Error
- Make sure you're running from the project root directory
- The file will be created automatically on first run

### Session not persisting
- Check that `.session_token.tmp` file is readable
- Make sure you're running from the same directory each time

### Cloud (Supabase) connection fails
- Verify `.env` file has correct credentials
- Check internet connection
- Make sure `USE_SUPABASE=true` is set in `.env`
- Verify Supabase project is active

### Module not found errors
- For Python 3.7-3.11: works with standard library only
- For cloud features: `pip install supabase python-dotenv`

## 💡 Tips for New Users

1. **Start with the hub** - `python hub.py` gives you the best experience
2. **Use test accounts** - Try the included test account before creating your own
3. **Explore the code** - `bank.py` is well-commented and great for learning
4. **Check example_usage.py** - See how to use the banking engine
5. **Run tests first** - `python smoke_test.py` confirms everything works

## 📜 License

This project is provided as-is for educational and demonstration purposes.

## 🤝 Contributing

Found a bug? Have an idea? Feel free to open an issue or submit a pull request!

## 👤 Author

Created for learning and demonstration purposes.

---

**Ready to get started?** Run `python hub.py` now!

For more details, check out the code - it's well-commented and easy to understand.
