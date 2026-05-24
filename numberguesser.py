import getpass
import hashlib
import json
import os
from pathlib import Path
import time
from colorama import init, Fore, Style

init(autoreset=True)  # Initialize colorama for colored output

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
from announcements import record_casino_win

# Try to use Supabase backend if configured
try:
    from supabase_backend import create_supabase_backend_from_env
    backend = create_supabase_backend_from_env()
    bank = BankingSystem(backend=backend) if backend else BankingSystem()
except ImportError:
    # supabase-py not installed, use JSON backend
    bank = BankingSystem()

# ----- Constants -----
CASINO_NAME = "Chance Casino"
CASINO_ACCOUNT = "CASINO0001"
CASINO_PASSWORD = "casino_secret"
DATA_FILE = Path("accounts.json")

# ----- UI Helpers -----

def _separator() -> None:
    print("─" * 70)


def show_leaderboard() -> None:
    """Display top 5 casino winners leaderboard."""
    from announcements import get_leaderboard
    
    _separator()
    print(f"🏆 {CASINO_NAME} - TOP WINNERS 🏆".center(70))
    _separator()
    
    leaderboard = get_leaderboard(top_n=5)
    
    if not leaderboard:
        print("  No winners yet. Be the first! 🎰")
        _separator()
        return
    
    for rank, winner in enumerate(leaderboard, 1):
        username = winner.get("username", "Unknown")
        total_won = winner.get("total_won", 0)
        win_count = winner.get("win_count", 0)
        
        medal = {
            1: "🥇",
            2: "🥈", 
            3: "🥉"
        }.get(rank, f"#{rank}")
        
        print(f"  {medal} {rank}. {username}")
        print(f"      Total Winnings: ${total_won:,.2f}")
        print(f"      Wins: {win_count}")
        print()
    
    _separator()


# ----- Casino bootstrap -----

def _ensure_casino_account() -> None:
    """Ensure the casino target account exists in the shared JSON storage."""
    try:
        bank.get_account(CASINO_ACCOUNT)
        return
    except AccountNotFoundError:
        pass

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"accounts": {}, "transactions": []}

    data["accounts"][CASINO_ACCOUNT] = {
        "account_number": CASINO_ACCOUNT,
        "username": CASINO_NAME,
        "password_hash": hashlib.sha256(
            CASINO_PASSWORD.encode("utf-8")
        ).hexdigest(),
        "balance": 0.0,
        "created_at": "2024-01-01T00:00:00Z",
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ----- Payment Processing -----

def process_payment(bet_amount: float, buyer_account: str = None) -> bool:
    """
    Collect buyer credentials and process a transfer to the casino account.
    
    If buyer_account is provided (from session), skip account entry.
    Otherwise, prompt for credentials.
    """
    print(f"\n  You selected: {bet_amount}")
    print(f"  Price       : ${bet_amount:.2f}")
    _separator()
    print("  Please enter your bank details to complete the purchase.")

    # If we have a session, buyer account is already set
    if buyer_account is None:
        buyer_account = input("  Your account number : ").strip()
    else:
        print(f"  Using account       : {buyer_account}")
    
    buyer_password = getpass.getpass("  Your password       : ")

    # Authenticate credentials first, before asking for confirmation.
    try:
        bank.authenticate(buyer_account, buyer_password)
    except AuthenticationError:
        print("\n  ❌ Payment failed: incorrect password.")
        return False
    except AccountNotFoundError as exc:
        print(f"\n  ❌ Payment failed: {exc}")
        return False

    print(f"\n  ⚠️  ${bet_amount:.2f} will be charged to account {buyer_account}.")
    confirm = input("  Confirm purchase? (y/n): ").strip().lower()
    if confirm != "y":
        print("  Purchase cancelled.")
        return False

    try:
        receipt = bank.transfer(
            from_account=buyer_account,
            password=buyer_password,
            to_account=CASINO_ACCOUNT,
            amount=bet_amount,
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

    print("\n  ✅ Payment successful!")
    print(f"     Transaction ID : {receipt['transaction_id']}")
    print(f"     Amount charged : ${receipt['amount']:.2f}")
    print(f"     Remaining bal  : ${receipt['new_balance']:.2f}")
    _separator()
    print("  🎟️  PAYMENT COMPLETE")
    print("     Enjoy the game!")
    _separator()
    return True

#------ Game Logic -----
def number_guesser(bet_amount: float) -> None:
    import random
    max_attempts = 3
    _separator()

    number_to_guess = random.randint(1, 10)
    
    for attempt in range(max_attempts):
        print(f"Attempt {attempt + 1} of {max_attempts}")
        if attempt > 0:
            print(" attempts left: ", max_attempts - attempt)
        try:
            user_guess = int(input("Enter your guess: "))
            if user_guess < 1 or user_guess > 10:
                print("Please guess a number between 1 and 10.")
                continue
            elif user_guess < number_to_guess:
                print("Too low! Try again.")
            elif user_guess > number_to_guess:
                print("Too high! Try again.")
        except ValueError:
            print("Invalid input. Please enter a number.")
            return
        if user_guess == number_to_guess:
            print("Congratulations! You guessed the correct number!")
            print("-"*50)
            print("your prize money is being processed...")
            time.sleep(2)  # Simulate processing time
            print("Prize money is equal to", bet_amount *4)
            # Process payment to the user (casino pays the user)
            try:
                winner_account = input("Enter your account number to receive the prize: ").strip()
                receipt = bank.transfer(
                    from_account=CASINO_ACCOUNT,
                    password=CASINO_PASSWORD,
                    to_account=winner_account,
                    amount=bet_amount * 4,  # User wins 4x their bet
                )
                print("Transfering prize money to your account...")
                time.sleep(2)  # Simulate transfer time
                print("\n  ✅ Prize transfer successful!")
                print(f"     Transaction ID : {receipt['transaction_id']}")
                print(f"     Amount won     : ${receipt['amount']:.2f}")
                
                # Record this win for announcements and leaderboard
                try:
                    winner_info = bank.get_account(winner_account)
                    record_casino_win(
                        username=winner_info.get("username", "Player"),
                        account_number=winner_account,
                        amount_won=bet_amount * 4
                    )
                except Exception:
                    pass  # Silently fail if we can't record the win

            except Exception as exc:
                print(f"\n  ❌ Prize transfer failed: {exc}")
                print("Please take a screenshot and contact support to resolve this issue.")
            break
        elif attempt == max_attempts - 1:
            print(f"Game over! You've used all {max_attempts} attempts.")
            print(f"the correct number was {number_to_guess}. Better luck next time!")
            

# ----- Entry point -----

def main() -> None:
    _ensure_casino_account()
    _separator()
    print(f"Welcome to {CASINO_NAME}!")
    print("Try your luck at the Number Guesser Game!")
    _separator()

    # Check if user is logged in via hub
    session = get_current_session()
    buyer_account = session["account_number"] if session else None
    
    if session:
        print(f"✓ Logged in as: {session['username']}")
        print()

    print("  1. Play Number Guesser Game")
    print("  2. View Leaderboard (Top Winners)")
    print("  0. Exit")
    print()
    
    choice = input("  Select option: ").strip()
    
    if choice == "2":
        show_leaderboard()
        return
    elif choice == "0":
        print("Thank you for visiting! Goodbye!")
        return
    elif choice != "1":
        print("Invalid option. Please try again.")
        return

    try:
        bet_amount = float(input("Enter your bet amount: "))
    except ValueError:
        print("Invalid bet amount. Please enter a number.")
        return

    if bet_amount <= 0:
        print("Bet amount must be greater than zero.")
        return

    if process_payment(bet_amount, buyer_account):
        number_guesser(bet_amount)
    else:
        _separator()
        print("Unable to start the game without successful payment. Please retry.")
        _separator()


if __name__ == "__main__":
    while True:
        main()
        play_again = input("\nDo you want to play again? (y/n): ").strip().lower()
        if play_again != "y":
            print("Thank you for playing! Goodbye!")
            break
        else:           
            print("\nStarting a new game...\n")
            time.sleep(1)  # Simulate loading time


    