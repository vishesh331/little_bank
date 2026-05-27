"""
hub.py — Central Dashboard for All Services
============================================
A unified entry point where users can:
  - Log in once
  - Access all services (banking, games, ticket booking, etc.)
  - Manage their account across the entire ecosystem

Run:
    python hub.py
"""

import getpass
import sys
import os
from pathlib import Path

from colorama import Fore, Style, init

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
from session import create_session, clear_session, get_current_session
from announcements import get_latest_announcement

# Try to use Supabase backend if configured
try:
    from supabase_backend import create_supabase_backend_from_env
    backend = create_supabase_backend_from_env()
    bank = BankingSystem(backend=backend) if backend else BankingSystem()
except ImportError:
    # supabase-py not installed, use JSON backend
    bank = BankingSystem()

init(autoreset=True)


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _separator(char: str = "─", width: int = 60) -> None:
    print(char * width)


def _header(title: str) -> None:
    _separator()
    print(f"  {title}")
    _separator()


def _pause() -> None:
    input("\nPress Enter to continue...")


def _show_announcements() -> None:
    """Display latest casino win announcement if available."""
    announcement = get_latest_announcement()
    if announcement:
        _separator("═", 60)
        print(f"{Fore.GREEN}📢 {announcement}{Style.RESET_ALL}")
        _separator("═", 60)
        print()


# ---------------------------------------------------------------------------
# Login flow
# ---------------------------------------------------------------------------

def screen_login() -> dict | None:
    """
    Authenticate user and return their account info.
    Returns None if authentication fails.
    """
    _header("🏦  Login")
    print("  Enter your account credentials to continue.")
    print()
    
    account_number = input("  Account number: ").strip()
    password = getpass.getpass("  Password: ")

    try:
        info = bank.authenticate(account_number, password)
        # Create session so other services don't need to re-authenticate
        create_session(info["account_number"], info["username"])
        return info
    except (AccountNotFoundError, AuthenticationError) as exc:
        print(f"\n  ❌ {exc}")
        _pause()
        return None


def screen_create_account() -> dict | None:
    """
    Guide a new user through account creation.
    Returns the created account info, or None if creation was cancelled.
    """
    _header("🆕 Create New Account")
    print("  Enter the details to create a new bank account.")
    print()

    username = input("  Username: ").strip()
    if not username:
        print("\n  ❌ Username must not be empty.")
        _pause()
        return None

    password = getpass.getpass("  Password: ")
    password_confirm = getpass.getpass("  Confirm password: ")
    if password != password_confirm:
        print("\n  ❌ Passwords do not match.")
        _pause()
        return None

    initial_balance = 0.0
    initial_balance_input = input("  Initial deposit amount (optional, default 0.00): $").strip()
    if initial_balance_input:
        try:
            initial_balance = float(initial_balance_input)
        except ValueError:
            print("\n  ❌ Invalid deposit amount.")
            _pause()
            return None

    try:
        info = bank.create_account(username=username, password=password, initial_balance=initial_balance)
        create_session(info["account_number"], info["username"])
        print(f"\n  ✅ Account created successfully! Your account number is {info['account_number']}")
        _pause()
        return info
    except ValueError as exc:
        print(f"\n  ❌ {exc}")
        _pause()
        return None


# ---------------------------------------------------------------------------
# Account overview
# ---------------------------------------------------------------------------

def screen_account_overview(info: dict) -> None:
    """Display user's account summary."""
    _header(f"👤 {info['username']}")
    print(f"  Account #  : {info['account_number']}")
    print(f"  Balance    : ${info['balance']:.2f}")
    print(f"  Created    : {info['created_at'][:10]}")
    _pause()


def screen_transaction_history(info: dict) -> None:
    """Display transaction history."""
    _header("📊 Transaction History")
    transactions = bank.get_transactions(info["account_number"])
    
    if not transactions:
        print("  No transactions yet.")
    else:
        for tx in transactions:
            is_out = tx["from_account"] == info["account_number"]
            direction = "↑ OUT" if is_out else "↓ IN "
            amount_text = f"${tx['amount']:>9.2f}"
            if is_out:
                amount_text = f"{Fore.RED}{amount_text}{Style.RESET_ALL}"
            else:
                amount_text = f"{Fore.GREEN}{amount_text}{Style.RESET_ALL}"
            print(
                f"  {tx['timestamp'][:19]}  {direction}  {amount_text}  [{tx['type']}]"
            )
    _pause()


def screen_banking_menu(info: dict) -> None:
    """Banking operations: deposit, withdraw, transfer."""
    while True:
        _header(f"🏦 Banking")
        print(f"  Account: {info['account_number']}")
        print(f"  Balance: ${info['balance']:.2f}\n")
        print("  [1] Check balance")
        print("  [2] Deposit")
        print("  [3] Withdraw")
        print("  [4] Transfer money")
        print("  [5] Transaction history")
        print("  [0] Back to main menu")
        _separator()

        choice = input("  Choice: ").strip()

        if choice == "1":
            balance = bank.get_balance(info["account_number"])
            print(f"\n  💰 Current balance: ${balance:.2f}")
            _pause()

        elif choice == "2":
            try:
                amount = float(input("  Deposit amount: $"))
                new_balance = bank.deposit(info["account_number"], amount)
                print(f"\n  ✅ Deposited ${amount:.2f}")
                print(f"     New balance: ${new_balance:.2f}")
                info["balance"] = new_balance
            except (InvalidAmountError, ValueError) as exc:
                print(f"\n  ❌ {exc}")
            _pause()

        elif choice == "3":
            try:
                amount = float(input("  Withdrawal amount: $"))
                password = getpass.getpass("  Confirm password: ")
                new_balance = bank.withdraw(info["account_number"], password, amount)
                print(f"\n  ✅ Withdrew ${amount:.2f}")
                print(f"     New balance: ${new_balance:.2f}")
                info["balance"] = new_balance
            except (InsufficientFundsError, AuthenticationError,
                    InvalidAmountError, ValueError) as exc:
                print(f"\n  ❌ {exc}")
            _pause()

        elif choice == "4":
            try:
                to_account = input("  Recipient account number: ").strip()
                amount = float(input("  Transfer amount: $"))
                password = getpass.getpass("  Your password: ")

                print(f"\n  ⚠️  ${amount:.2f} will be transferred to account {to_account}.")
                confirm = input("  Confirm? (y/n): ").strip().lower()
                if confirm != "y":
                    print("  Transfer cancelled.")
                    _pause()
                    continue

                receipt = bank.transfer(
                    from_account=info["account_number"],
                    password=password,
                    to_account=to_account,
                    amount=amount,
                )
                print(f"\n  ✅ Transfer successful!")
                print(f"     Transaction ID: {receipt['transaction_id']}")
                print(f"     Amount: ${receipt['amount']:.2f}")
                print(f"     New balance: ${receipt['new_balance']:.2f}")
                info["balance"] = receipt["new_balance"]
            except (AccountNotFoundError, AuthenticationError,
                    InsufficientFundsError, InvalidAmountError, ValueError) as exc:
                print(f"\n  ❌ {exc}")
            _pause()

        elif choice == "5":
            screen_transaction_history(info)

        elif choice == "0":
            break
        else:
            print("  Invalid choice. Please try again.")


# ---------------------------------------------------------------------------
# Game launchers
# ---------------------------------------------------------------------------

def launch_casino(info: dict) -> None:
    """Launch the casino number guesser game."""
    _header("🎰 Launching Casino...")
    print(f"  Logged in as: {info['username']}")
    print(f"  Current balance: ${info['balance']:.2f}")
    print("\n  🎮 Starting Number Guesser...")
    print()
    _separator()
    
    # Import and run casino game directly (to maintain session)
    from numberguesser import main as casino_main
    casino_main()
    
    # Refresh balance after game
    info["balance"] = bank.get_balance(info["account_number"])


def launch_movie_tickets(info: dict) -> None:
    """Launch the movie ticket booking system."""
    _header("🎬 Launching Movie Ticket System...")
    print(f"  Logged in as: {info['username']}")
    print(f"  Current balance: ${info['balance']:.2f}")
    print("\n  🎞️  Starting Movie Ticket Booking...")
    print()
    _separator()
    
    # Import and run movie tickets directly (to maintain session)
    from movie_tickets import main as tickets_main
    tickets_main()
    
    # Refresh balance after purchase
    info["balance"] = bank.get_balance(info["account_number"])


def launch_movie_streaming(info: dict) -> None:
    """Launch the CinemaStream movie distribution service."""
    import webbrowser
    import time
    import subprocess
    
    _header("🎥 Launching CinemaStream...")
    print(f"  Logged in as: {info['username']}")
    print(f"  Current balance: ${info['balance']:.2f}")
    print("\n  🌐 Starting CinemaStream Web Service...")
    print("     Flask server is starting at http://localhost:5000")
    print("     Your browser will open automatically...")
    print()
    _separator()
    
    # Start Flask app
    try:
        # Change to movie_streaming directory and run the app
        movie_streaming_path = Path(__file__).parent / "movie_streaming"
        
        # Open browser after a short delay
        time.sleep(2)
        webbrowser.open("http://localhost:5000")
        
        # Run the Flask app (this will block until the server is stopped)
        os.chdir(movie_streaming_path)
        exec(open("app.py").read())
        
    except Exception as e:
        print(f"\n  ❌ Error launching CinemaStream: {e}")
        print("     Make sure you have Flask installed: pip install -r movie_streaming/requirements.txt")
        _pause()
    finally:
        # Refresh balance after streaming session
        info["balance"] = bank.get_balance(info["account_number"])


def screen_services_menu(info: dict) -> None:
    """Main menu for all available services."""
    while True:
        _header("🎯 Services")
        print(f"  Welcome, {info['username']}!")
        print(f"  Balance: ${info['balance']:.2f}\n")
        print("  [1] 💰 Banking")
        print("  [2] 🎰 Casino - Number Guesser")
        print("  [3] 🎬 Movie Tickets")
        print("  [4] 🎥 CinemaStream - Movie Distribution")
        print("  [5] 👤 Account Overview")
        print("  [6] 📊 Transaction History")
        print("  [0] 🚪 Logout")
        _separator()

        choice = input("  Choice: ").strip()

        if choice == "1":
            screen_banking_menu(info)
        elif choice == "2":
            launch_casino(info)
        elif choice == "3":
            launch_movie_tickets(info)
        elif choice == "4":
            launch_movie_streaming(info)
        elif choice == "5":
            screen_account_overview(info)
        elif choice == "6":
            screen_transaction_history(info)
        elif choice == "0":
            clear_session()  # Clear session on logout
            print("\n  👋 Logged out. Goodbye!")
            break
        else:
            print("  Invalid choice. Please try again.")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Main loop: choose login/create account then access services."""
    # Show announcements at startup
    _show_announcements()

    while True:
        _header("🏦  Welcome to the Integrated Platform")
        print("  Please choose an option:")
        print("  [1] Login")
        print("  [2] Create a new account")
        print("  [0] Exit")
        _separator()

        choice = input("  Choice: ").strip()
        if choice == "1":
            info = screen_login()
        elif choice == "2":
            info = screen_create_account()
        elif choice == "0":
            print("Goodbye!")
            clear_session()
            sys.exit(0)
        else:
            print("  Invalid choice. Please try again.")
            continue

        if info is None:
            again = input("\nReturn to startup menu? (y/n): ").strip().lower()
            if again != "y":
                print("Goodbye!")
                clear_session()
                sys.exit(0)
            continue

        # Successfully logged in or created account
        screen_services_menu(info)

        # After logout, prompt to login/create again or exit
        again = input("\nLogin again? (y/n): ").strip().lower()
        if again != "y":
            print("Goodbye!")
            clear_session()
            sys.exit(0)


if __name__ == "__main__":
    main()
