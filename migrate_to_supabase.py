"""
migrate_to_supabase.py
======================
One-time migration script to import accounts.json data into Supabase.

Before running:
1. Create Supabase project at https://supabase.com
2. Run this SQL in Supabase SQL Editor (see SUPABASE_SCHEMA.sql):
   - accounts table
   - transactions table
3. Create .env file with SUPABASE_URL and SUPABASE_KEY (copy .env.example)

Then run:
  python migrate_to_supabase.py
"""

import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:
    print("⚠️  python-dotenv not found. Installing...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv

try:
    from supabase_backend import SupabaseBackend, BankingError
except ImportError:
    print("Error: supabase_backend module not found. Ensure you're in the project directory.")
    sys.exit(1)


def load_json_data(json_file: str) -> dict:
    """Load accounts.json and return as dict."""
    path = Path(json_file)
    if not path.exists():
        raise FileNotFoundError(f"Accounts file not found: {json_file}")

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    
    return data


def verify_data(data: dict) -> tuple[int, int]:
    """Verify data structure. Returns (account_count, transaction_count)."""
    if "accounts" not in data or "transactions" not in data:
        raise ValueError("Invalid data structure. Expected 'accounts' and 'transactions' keys.")
    
    accounts = data["accounts"]
    transactions = data["transactions"]
    
    if not isinstance(accounts, dict):
        raise ValueError("'accounts' should be a dict.")
    if not isinstance(transactions, list):
        raise ValueError("'transactions' should be a list.")
    
    # Verify account structure
    for acc_num, acc_data in accounts.items():
        required = {"account_number", "username", "password_hash", "balance", "created_at"}
        if not required.issubset(acc_data.keys()):
            raise ValueError(f"Account {acc_num} missing required fields: {required}")
    
    # Verify transaction structure
    for tx in transactions:
        required = {"transaction_id", "type", "from_account", "to_account", "amount", "timestamp"}
        if not required.issubset(tx.keys()):
            raise ValueError(f"Transaction missing required fields: {required}")
    
    return len(accounts), len(transactions)


def migrate():
    """Migrate accounts.json to Supabase."""
    # Load environment variables from .env
    load_dotenv()
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    accounts_json_file = os.getenv("ACCOUNTS_JSON_FILE", "accounts.json")

    # Validate credentials
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL and SUPABASE_KEY environment variables are required.")
        print("\nConfiguration from .env file:")
        print(f"  SUPABASE_URL = {supabase_url or '(not set)'}")
        print(f"  SUPABASE_KEY = {('*' * 10) if supabase_key else '(not set)'}")
        print("\nTo fix:")
        print("  1. Copy .env.example to .env")
        print("  2. Fill in your Supabase credentials")
        print("  3. Run this script again")
        sys.exit(1)

    try:
        print("\n" + "=" * 60)
        print("SUPABASE MIGRATION")
        print("=" * 60)
        
        # Load and verify data
        print(f"\n📂 Loading data from {accounts_json_file}...")
        data = load_json_data(accounts_json_file)
        account_count, tx_count = verify_data(data)
        print(f"   ✓ Found {account_count} accounts and {tx_count} transactions")

        # Connect to Supabase
        print(f"\n🔗 Connecting to Supabase...")
        print(f"   URL: {supabase_url}")
        backend = SupabaseBackend(url=supabase_url, key=supabase_key)
        print("   ✓ Connected successfully")

        # Migrate data
        print(f"\n📤 Migrating data to Supabase...")
        backend.save(data)
        print(f"   ✓ {account_count} accounts imported")
        print(f"   ✓ {tx_count} transactions imported")

        # Success message
        print("\n" + "=" * 60)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 60)
        
        print("\nYour application can now use Supabase by:")
        print("  1. Creating a SupabaseBackend instance:")
        print("     from supabase_backend import create_supabase_backend_from_env")
        print("     backend = create_supabase_backend_from_env()")
        print("\n  2. Using it with BankingSystem:")
        print("     from bank import BankingSystem")
        print("     bank = BankingSystem(backend=backend)")
        print("\n  3. Or enable automatic loading in hub.py:")
        print("     Set USE_SUPABASE=true in .env")
        
        print("\n💾 Your accounts.json file has been preserved as a backup.")
        print("   You can delete it once you've verified everything works.")
        
    except FileNotFoundError as e:
        print(f"\n❌ File error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"\n❌ Data validation error: {e}")
        sys.exit(1)
    except BankingError as e:
        print(f"\n❌ Supabase error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    migrate()
