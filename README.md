# Little Bank 🏦💰

A complete, integrated banking and gaming ecosystem built with Python. One login, access everything: bank accounts, casino games, movie tickets, and more.

## 🎯 What It Does

Little Bank is a unified platform where users can:

- **Create & manage bank accounts** - Full banking features with secure authentication
- **Play casino games** - Number guessing game to win/lose money
- **Buy movie tickets** - Purchase tickets using your bank balance
- **Track everything** - Complete transaction history across all services
- **Login once** - Access all services with a single session
- **See live announcements** 📢 - Watch real-time casino wins from players worldwide
- **Compete on leaderboard** 🏆 - Check top casino winners and their cumulative earnings

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
   - Account: `1756652179`
   - Password: `test`
   - Balance: `1000000$` yess 1 Million $ (the cheeky thing is that you can transef money from test account to your account, have fun)
3. **From the hub menu**, select:
   - 💳 Banking - deposit, withdraw, transfer money
   - 🎰 Casino - play the number guessing game
   - 🎬 Movie Tickets - buy tickets
   - 📊 Transactions - view transaction history

## 🌍 Shared Demo Database

**This repository is configured with a SHARED SUPABASE DATABASE!**

This means:
- 🌎 **Anyone who clones this project connects to the SAME database**
- 👥 **All users worldwide share the same accounts and balances**
- 💰 **When someone wins money in the casino, it's real within this demo**
- 📊 **You can see transactions from players across the world**
- 🎮 **It's a global shared playground!**

### 📢 Live Announcements & Leaderboard

The shared database makes for exciting real-time experiences:

**Announcements:**
- When any player wins at the casino, their win is announced in **GREEN TEXT** at the top of the hub
- See real-time: `"Alice just won $500 in the casino! 🎰"`
- Only the latest big win is shown at a time
- Creates a sense of community and competition

**Casino Leaderboard:**
- View the **top 5 casino winners** with cumulative earnings
- See who has won the most money total across all games
- Accessible from the casino menu (option 2)
- Shows win count and total winnings for each player
- Medals for top 3: 🥇 🥈 🥉

### Example Fun Scenario:
1. Alice clones the project in London, creates an account, wins $500 at the casino
   - 📢 Green announcement appears: "Alice just won $500 in the casino!"
2. Bob in Tokyo sees the announcement when he starts the hub
3. Bob gets inspired, plays, and wins $300
   - 📢 New announcement: "Bob just won $300 in the casino!"
   - Alice sees it and plays again
4. They could even transfer money to each other!
5. Both can check the leaderboard to see who's winning overall

### ⚠️ Important Notes:
- Since the database is **shared with everyone**, any account you create is **visible to all users**
- Don't use real passwords - this is a demo! 🎭
- The balances and transactions are **real within this demo** - you're all playing in the same economy
- Announcements and leaderboard are tracked in real-time
- If someone resets the database, everyone's data resets (it's a demo after all!)

### Want Your Own Private Database?
If you'd like a private database just for yourself or your team:

```bash
# 1. Sign up for Supabase (free tier available)
# https://supabase.com

# 2. Get your project credentials

# 3. Update .env file with YOUR credentials:
# SUPABASE_URL=https://your-project.supabase.co
# SUPABASE_KEY=your_anon_key

# 4. Now only YOU (and people with your credentials) can access it
```

**The magic of this setup:** Clone anywhere, get instant access to a shared economy with live announcements and competition! 🎉

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

### Cloud Storage (Default) ✅ **SHARED & READY**
- Uses **shared Supabase PostgreSQL database**
- **Already configured!** No setup needed
- Anyone worldwide who clones this can immediately play together
- Everyone shares accounts, money, and transactions
- Perfect for a global demo and learning experience!
- Automatic backups and security

**Just run it:**
```bash
pip install supabase python-dotenv
python hub.py
# You're now connected to the shared world database!
```

### Local Storage (Optional)
- Uses `accounts.json` file
- Perfect for testing without cloud
- Works offline
- Only you have access to the data
- Data persists between runs

**To use local storage instead:**
```bash
# Edit .env and change:
# USE_SUPABASE=false

# Now it will use accounts.json for local testing
python hub.py
```

### Switch Between Storage Anytime
The beauty of this setup is you can switch between shared and local anytime:
- **Want to play with friends worldwide?** Use cloud (default)
- **Want to test locally without affecting others?** Use local
- **Want your own private database?** Get Supabase credentials and update `.env`

All without changing any code! 🎉

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

### Casino (Number Guesser)
- Guess a number between 1-10
- Win 4x your bet if correct
- 3 attempts per game
- **NEW:** Real-time announcements when you win
- **NEW:** Compete on leaderboard with cumulative winnings
- View top 5 casino winners with medal rankings

**How it works:**
1. Enter your bet amount
2. Play the guessing game (3 attempts)
3. If you win, announcement goes to all players 📢
4. Check leaderboard to see your rank 🏆

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
| `numberguesser.py` | Casino game with leaderboard (number guessing) |
| `movie_tickets.py` | Movie ticket purchasing system |
| `announcements.py` | Real-time announcements and leaderboard tracking |
| `supabase_backend.py` | Cloud database adapter (optional) |
| `migrate_to_supabase.py` | Tool to move data to cloud |
| `accounts.json` | Local database (JSON file) |
| `announcements.json` | Announcements and casino leaderboard stats |
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
