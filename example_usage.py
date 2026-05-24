"""
example_usage.py
================
Examples showing how to use BankingSystem with different storage backends.
"""

# ============================================================================
# Example 1: Using Default JSON Backend (No Changes Required)
# ============================================================================

def example_json_backend():
    """Default behavior — data stored in accounts.json"""
    from bank import BankingSystem

    # Initialize with default JSON backend
    bank = BankingSystem()  # Uses accounts.json

    # Create accounts
    alice = bank.create_account("Alice", "password123", 1000.0)
    bob = bank.create_account("Bob", "securepass", 500.0)

    print(f"Alice: {alice}")
    print(f"Bob: {bob}")

    # Perform transaction
    receipt = bank.transfer(
        from_account=alice["account_number"],
        password="password123",
        to_account=bob["account_number"],
        amount=100.0,
    )
    print(f"Transfer receipt: {receipt}")

    # Data persists in accounts.json
    print(f"New Alice balance: {bank.get_balance(alice['account_number'])}")


# ============================================================================
# Example 2: Using Custom JSON File
# ============================================================================

def example_custom_json_file():
    """Store data in a custom JSON file"""
    from bank import BankingSystem

    bank = BankingSystem(data_file="my_custom_accounts.json")
    # ... same API as Example 1


# ============================================================================
# Example 3: Using Supabase Backend
# ============================================================================

def example_supabase_backend():
    """
    Cloud-hosted data in Supabase PostgreSQL.

    Prerequisites:
    1. Create Supabase project at https://supabase.com
    2. Create tables (see SUPABASE_SETUP.md)
    3. Install supabase: pip install supabase
    4. Set environment variables:
       - SUPABASE_URL
       - SUPABASE_KEY
    """
    import os
    from supabase_backend import SupabaseBackend
    from bank import BankingSystem

    # Get credentials from environment
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("Skipping Supabase example — env vars not set")
        print("Set SUPABASE_URL and SUPABASE_KEY to try this")
        return

    # Create Supabase backend
    backend = SupabaseBackend(url=supabase_url, key=supabase_key)

    # Initialize BankingSystem with Supabase backend
    bank = BankingSystem(backend=backend)

    # Use exactly the same API as JSON backend!
    alice = bank.create_account("Alice", "password123", 1000.0)
    bob = bank.create_account("Bob", "securepass", 500.0)

    receipt = bank.transfer(
        from_account=alice["account_number"],
        password="password123",
        to_account=bob["account_number"],
        amount=100.0,
    )

    # Data now stored in Supabase PostgreSQL
    print(f"Transfer receipt: {receipt}")


# ============================================================================
# Example 4: Migrating from JSON to Supabase
# ============================================================================

def example_migration():
    """
    One-time migration script.
    See migrate_to_supabase.py for the full script.

    Steps:
    1. Create Supabase project
    2. Create tables
    3. Set SUPABASE_URL and SUPABASE_KEY env vars
    4. Run: python migrate_to_supabase.py
    """
    import json
    from pathlib import Path

    # Load existing JSON data
    with open("accounts.json") as fh:
        data = json.load(fh)

    print(f"Loaded {len(data['accounts'])} accounts and {len(data['transactions'])} transactions")

    # The migrate_to_supabase.py script handles the rest


# ============================================================================
# Example 5: Testing Both Backends
# ============================================================================

def test_bank_functionality(bank_instance):
    """
    Generic test that works with any backend.

    Pass BankingSystem instance using any backend (JSON or Supabase).
    """
    # Create test accounts
    alice = bank_instance.create_account("Alice", "pwd1", 1000)
    bob = bank_instance.create_account("Bob", "pwd2", 500)

    # Test deposit
    new_balance = bank_instance.deposit(alice["account_number"], 100)
    assert new_balance == 1100, f"Deposit failed: {new_balance}"

    # Test withdraw
    new_balance = bank_instance.withdraw(
        alice["account_number"], "pwd1", 50
    )
    assert new_balance == 1050, f"Withdraw failed: {new_balance}"

    # Test transfer
    receipt = bank_instance.transfer(
        from_account=alice["account_number"],
        password="pwd1",
        to_account=bob["account_number"],
        amount=100,
    )
    assert receipt["status"] == "success"

    # Test balance
    alice_balance = bank_instance.get_balance(alice["account_number"])
    bob_balance = bank_instance.get_balance(bob["account_number"])
    assert alice_balance == 950, f"Alice balance: {alice_balance}"
    assert bob_balance == 600, f"Bob balance: {bob_balance}"

    # Test transactions
    txs = bank_instance.get_transactions(alice["account_number"])
    assert len(txs) >= 3, f"Expected 3+ transactions, got {len(txs)}"

    print("✓ All tests passed!")


def test_json_backend():
    """Test with JSON backend"""
    from bank import BankingSystem
    bank = BankingSystem("test_json.json")
    test_bank_functionality(bank)


def test_supabase_backend():
    """Test with Supabase backend"""
    import os
    from supabase_backend import SupabaseBackend
    from bank import BankingSystem

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("Skipping Supabase tests — env vars not set")
        return

    backend = SupabaseBackend(url=supabase_url, key=supabase_key)
    bank = BankingSystem(backend=backend)
    test_bank_functionality(bank)


if __name__ == "__main__":
    print("=== Example 1: JSON Backend ===")
    example_json_backend()

    print("\n=== Example 5: Testing Both Backends ===")
    test_json_backend()

    print("\nAll examples completed successfully!")
