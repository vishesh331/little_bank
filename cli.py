"""
cli.py — Interactive Command-Line Interface for the Banking System
=================================================================
Run this file directly to use the banking system interactively:

    python cli.py

This is intentionally kept separate from bank.py so that bank.py
remains a clean, importable module with no side-effects on import.
"""

import getpass
import sys
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from colorama import Fore, Style, init

from bank import (
    BankingSystem,
    AccountNotFoundError,
    AuthenticationError,
    InsufficientFundsError,
    InvalidAmountError,
)

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

def _separator(char: str = "─", width: int = 48) -> None:
    print(char * width)


def _header(title: str) -> None:
    _separator()
    print(f"  {title}")
    _separator()


def _pause() -> None:
    input("\nPress Enter to continue...")


# ---------------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------------

def screen_create_account() -> None:
    _header("Create New Account")
    username = input("Full name: ").strip()
    if not username:
        print("Name cannot be empty.")
        return
    password = getpass.getpass("Choose a password: ")
    if not password:
        print("Password cannot be empty.")
        return
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.")
        return

    try:
        info = bank.create_account(username, password)
        print(f"\n✅ Account created successfully!")
        print(f"   Account number : {info['account_number']}")
        print(f"   Username       : {info['username']}")
        print(f"   Balance        : ${info['balance']:.2f}")
        print("\n⚠️  Save your account number — you will need it to log in.")
    except ValueError as exc:
        print(f"Error: {exc}")
    _pause()


def screen_login() -> None:
    _header("Login")
    account_number = input("Account number: ").strip()
    password = getpass.getpass("Password: ")

    try:
        info = bank.authenticate(account_number, password)
    except (AccountNotFoundError, AuthenticationError) as exc:
        print(f"\n❌ {exc}")
        _pause()
        return

    screen_account_menu(info)


def screen_account_menu(info: dict) -> None:
    while True:
        _header(f"Welcome, {info['username']}")
        print(f"  Account : {info['account_number']}")
        print(f"  Balance : ${info['balance']:.2f}\n")
        print("  [1] Check balance")
        print("  [2] Deposit")
        print("  [3] Withdraw")
        print("  [4] Transfer money")
        print("  [5] Transaction history")
        print("  [0] Logout")
        _separator()

        choice = input("Choice: ").strip()

        if choice == "1":
            balance = bank.get_balance(info["account_number"])
            print(f"\n💰 Current balance: ${balance:.2f}")
            _pause()

        elif choice == "2":
            try:
                amount = float(input("Deposit amount: $"))
                new_balance = bank.deposit(info["account_number"], amount)
                print(f"\n✅ Deposited ${amount:.2f}. New balance: ${new_balance:.2f}")
                info["balance"] = new_balance
            except (InvalidAmountError, ValueError) as exc:
                print(f"\n❌ {exc}")
            _pause()

        elif choice == "3":
            try:
                amount = float(input("Withdrawal amount: $"))
                password = getpass.getpass("Confirm password: ")
                new_balance = bank.withdraw(info["account_number"], password, amount)
                print(f"\n✅ Withdrew ${amount:.2f}. New balance: ${new_balance:.2f}")
                info["balance"] = new_balance
            except (InsufficientFundsError, AuthenticationError,
                    InvalidAmountError, ValueError) as exc:
                print(f"\n❌ {exc}")
            _pause()

        elif choice == "4":
            try:
                to_account = input("Recipient account number: ").strip()
                amount = float(input("Transfer amount: $"))
                password = getpass.getpass("Your password: ")

                print(f"\nYou are about to transfer ${amount:.2f} to account {to_account}.")
                confirm = input("Confirm? (y/n): ").strip().lower()
                if confirm != "y":
                    print("Transfer cancelled.")
                    _pause()
                    continue

                receipt = bank.transfer(
                    from_account=info["account_number"],
                    password=password,
                    to_account=to_account,
                    amount=amount,
                )
                print(f"\n✅ Transfer successful!")
                print(f"   Transaction ID : {receipt['transaction_id']}")
                print(f"   Amount         : ${receipt['amount']:.2f}")
                print(f"   New balance    : ${receipt['new_balance']:.2f}")
                info["balance"] = receipt["new_balance"]
            except (AccountNotFoundError, AuthenticationError,
                    InsufficientFundsError, InvalidAmountError, ValueError) as exc:
                print(f"\n❌ {exc}")
            _pause()

        elif choice == "5":
            transactions = bank.get_transactions(info["account_number"])
            _header("Transaction History")
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

        elif choice == "0":
            print("Logged out. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

def main() -> None:
    while True:
        _header("🏦  Simple Banking System")
        print("  [1] Create new account")
        print("  [2] Login")
        print("  [0] Exit")
        _separator()

        choice = input("Choice: ").strip()

        if choice == "1":
            screen_create_account()
        elif choice == "2":
            screen_login()
        elif choice == "0":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
