"""
movie_tickets.py — Example Integration with bank.py
=====================================================
Demonstrates how an external project (a movie ticket store) can import
bank.py and process payments without touching the bank's internals.

Key design point
----------------
The ticket price is set by the *seller* (this script), never by the buyer.
The buyer only provides their account number and password to authorize
the payment. The amount flows programmatically into bank.transfer().

Run:
    python movie_tickets.py
"""

import getpass
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from bank import (
    BankingSystem,
    AccountNotFoundError,
    AuthenticationError,
    InsufficientFundsError,
    InvalidAmountError,
)
from session import get_current_session

# Try to use Supabase backend if configured
try:
    from supabase_backend import create_supabase_backend_from_env
    backend = create_supabase_backend_from_env()
    bank = BankingSystem(backend=backend) if backend else BankingSystem()
except ImportError:
    # supabase-py not installed, use JSON backend
    bank = BankingSystem()

# ---------------------------------------------------------------------------
# Cinema configuration (seller side — set by the business, not the buyer)
# ---------------------------------------------------------------------------

CINEMA_NAME    = "StarPlex Cinemas"
CINEMA_ACCOUNT = "CINEMA0001"       # the cinema's bank account number
CINEMA_PASSWORD = "cinema_secret"   # only needed to create the demo account

MOVIES = [
    {"id": 1, "title": "Galactic Odyssey",     "price": 250.00},
    {"id": 2, "title": "The Last Lighthouse",  "price": 300.00},
    {"id": 3, "title": "Robots vs. Wizards",   "price": 200.00},
]

# ---------------------------------------------------------------------------
# Bootstrap: ensure cinema account exists
# ---------------------------------------------------------------------------

def _ensure_cinema_account() -> None:
    """Create a cinema account in the bank if one does not already exist."""
    try:
        bank.get_account(CINEMA_ACCOUNT)
    except AccountNotFoundError:
        # Manually insert a pre-set account number for the cinema
        import json
        from pathlib import Path

        data_file = Path("accounts.json")
        try:
            with open(data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"accounts": {}, "transactions": []}

        import hashlib
        data["accounts"][CINEMA_ACCOUNT] = {
            "account_number": CINEMA_ACCOUNT,
            "username": CINEMA_NAME,
            "password_hash": hashlib.sha256(CINEMA_PASSWORD.encode()).hexdigest(),
            "balance": 0.0,
            "created_at": "2024-01-01T00:00:00Z",
        }
        with open(data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------

def _separator() -> None:
    print("─" * 50)


def _show_movies() -> None:
    _separator()
    print(f"  🎬  {CINEMA_NAME} — Now Showing")
    _separator()
    for movie in MOVIES:
        print(f"  [{movie['id']}]  {movie['title']:<28} ${movie['price']:.2f}")
    _separator()


def _select_movie() -> dict | None:
    _show_movies()
    try:
        choice = int(input("Select a movie (number): ").strip())
    except ValueError:
        print("Invalid choice.")
        return None
    for movie in MOVIES:
        if movie["id"] == choice:
            return movie
    print("Movie not found.")
    return None


# ---------------------------------------------------------------------------
# Payment flow
# ---------------------------------------------------------------------------

def process_payment(movie: dict, buyer_account: str = None) -> bool:
    """
    Collect buyer credentials and call bank.transfer() with the seller-set price.
    
    If buyer_account is provided (from session), skip account entry.
    Otherwise, prompt for credentials.
    
    Returns True if payment succeeded, False otherwise.
    """
    print(f"\n  You selected: {movie['title']}")
    print(f"  Price       : ${movie['price']:.2f}")
    _separator()
    print("  Please enter your bank details to complete the purchase.")

    # If we have a session, buyer account is already set
    if buyer_account is None:
        buyer_account = input("  Your account number : ").strip()
    else:
        print(f"  Using account       : {buyer_account}")
    
    buyer_password = getpass.getpass("  Your password       : ")

    # Confirm before charging
    print(f"\n  ⚠️  ${movie['price']:.2f} will be charged to account {buyer_account}.")
    confirm = input("  Confirm purchase? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Purchase cancelled.")
        return False

    # === The amount is passed programmatically — never prompted from the buyer ===
    try:
        receipt = bank.transfer(
            from_account=buyer_account,
            password=buyer_password,
            to_account=CINEMA_ACCOUNT,
            amount=movie["price"],          # ← set by seller, not user input
        )
    except AuthenticationError:
        print("\n  ❌ Payment failed: incorrect password.")
        return False
    except AccountNotFoundError as exc:
        print(f"\n  ❌ Payment failed: {exc}")
        return False
    except InsufficientFundsError as exc:
        print(f"\n  ❌ Payment failed: {exc}")
        return False
    except InvalidAmountError as exc:
        print(f"\n  ❌ Payment failed: {exc}")
        return False

    # Payment succeeded — issue ticket
    print("\n  ✅ Payment successful!")
    print(f"     Transaction ID : {receipt['transaction_id']}")
    print(f"     Amount charged : ${receipt['amount']:.2f}")
    print(f"     Remaining bal  : ${receipt['new_balance']:.2f}")
    _separator()
    print(f"  🎟️  TICKET ISSUED")
    print(f"     Movie : {movie['title']}")
    print(f"     Enjoy the show!")
    _separator()
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    _ensure_cinema_account()

    # Check if user is logged in via hub
    session = get_current_session()
    buyer_account = session["account_number"] if session else None
    
    if session:
        print("\n  ✓ Logged in as:", session['username'])

    while True:
        movie = _select_movie()
        if movie is None:
            continue

        success = process_payment(movie, buyer_account)

        print()
        again = input("Buy another ticket? (y/n): ").strip().lower()
        if again != "y":
            print("Thank you for visiting StarPlex Cinemas!")
            break


if __name__ == "__main__":
    main()
