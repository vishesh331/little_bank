"""
Supabase Storage Backend for BankingSystem
===========================================
A drop-in replacement storage backend that uses Supabase PostgreSQL
instead of local JSON files.

Configuration (environment variables):
    SUPABASE_URL      - Your Supabase project URL
    SUPABASE_KEY      - Your Supabase anon/service key
    SUPABASE_TABLES   - Set to 'yes' to auto-create tables on init (optional)

Usage:
    from supabase_backend import SupabaseBackend
    from bank import BankingSystem

    backend = SupabaseBackend(url="...", key="...")
    bank = BankingSystem(backend=backend)
"""

import json
from typing import Optional
from supabase import create_client


class SupabaseBackend:
    """
    Storage backend backed by Supabase PostgreSQL.
    
    This backend stores the same data structure as the JSON backend:
    - accounts table: account_number (PK), username, password_hash, balance, created_at
    - transactions table: transaction_id (PK), type, from_account, to_account, amount, timestamp
    """

    def __init__(self, url: str, key: str, auto_create_tables: bool = False) -> None:
        """
        Initialize Supabase connection.

        Parameters
        ----------
        url : str
            Supabase project URL (e.g., https://xxxxx.supabase.co)
        key : str
            Supabase anon or service role key
        auto_create_tables : bool
            If True, create tables on initialization (default: False)
        """
        self.client = create_client(url, key)
        self._url = url
        self._key = key

        if auto_create_tables:
            self._create_tables()

    # -----------------------------------------------------------------------
    # Public API (mirrors JSON backend interface)
    # -----------------------------------------------------------------------

    def load(self) -> dict:
        """
        Load all data (accounts + transactions).
        
        Returns a dict matching the JSON schema:
        {
            "accounts": { account_number: { account_number, username, password_hash, balance, created_at } },
            "transactions": [ { transaction_id, type, from_account, to_account, amount, timestamp } ]
        }
        """
        try:
            # Fetch all accounts
            accounts_resp = self.client.table("accounts").select("*").execute()
            accounts_list = accounts_resp.data if accounts_resp.data else []

            # Fetch all transactions
            transactions_resp = self.client.table("transactions").select("*").execute()
            transactions_list = transactions_resp.data if transactions_resp.data else []

            # Convert accounts list to dict keyed by account_number
            accounts_dict = {acc["account_number"]: acc for acc in accounts_list}

            return {
                "accounts": accounts_dict,
                "transactions": transactions_list,
            }
        except Exception as exc:
            raise BankingError(f"Failed to load data from Supabase: {exc}") from exc

    def save(self, data: dict) -> None:
        """
        Persist data (accounts + transactions).

        This is a full replace (upsert) — all accounts and transactions
        are synchronized with the database.

        Parameters
        ----------
        data : dict
            Data dict with "accounts" and "transactions" keys
        """
        try:
            accounts = data.get("accounts", {})
            transactions = data.get("transactions", [])

            # Upsert all accounts
            for account_number, account_data in accounts.items():
                self.client.table("accounts").upsert(account_data).execute()

            # For transactions, we append only new ones (idempotent by transaction_id)
            # Fetch existing transaction IDs
            existing_resp = self.client.table("transactions").select("transaction_id").execute()
            existing_ids = {tx["transaction_id"] for tx in (existing_resp.data or [])}

            # Insert only new transactions
            new_transactions = [
                tx for tx in transactions if tx["transaction_id"] not in existing_ids
            ]
            if new_transactions:
                self.client.table("transactions").insert(new_transactions).execute()

        except Exception as exc:
            raise BankingError(f"Failed to save data to Supabase: {exc}") from exc

    # -----------------------------------------------------------------------
    # Table initialization (one-time setup)
    # -----------------------------------------------------------------------

    def _create_tables(self) -> None:
        """Create accounts and transactions tables (idempotent)."""
        try:
            # Use raw SQL via RPC or direct client calls
            # This is a convenience for initial setup; in production you'd use
            # Supabase migrations via the dashboard or CLI.

            # For now, we'll assume tables exist. In production, use:
            # supabase migration new create_banking_tables
            # supabase migration up

            # Minimal check: try to query; if tables don't exist, raise a helpful error
            try:
                self.client.table("accounts").select("account_number").limit(1).execute()
                self.client.table("transactions").select("transaction_id").limit(1).execute()
            except Exception:
                raise BankingError(
                    "Tables 'accounts' and 'transactions' do not exist in Supabase. "
                    "Please create them via the Supabase dashboard or migrations:\n"
                    "  accounts table: (account_number TEXT PRIMARY KEY, username TEXT, "
                    "password_hash TEXT, balance NUMERIC(12,2), created_at TEXT)\n"
                    "  transactions table: (transaction_id TEXT PRIMARY KEY, type TEXT, "
                    "from_account TEXT, to_account TEXT, amount NUMERIC(12,2), timestamp TEXT)"
                )
        except Exception as exc:
            if isinstance(exc, BankingError):
                raise
            raise BankingError(f"Failed to create tables in Supabase: {exc}") from exc


class BankingError(Exception):
    """Base class for banking/storage errors."""


def create_supabase_backend_from_env() -> Optional['SupabaseBackend']:
    """
    Create SupabaseBackend from environment variables.
    
    Returns None if USE_SUPABASE is not set to 'true' in .env
    
    Environment variables:
    - USE_SUPABASE: set to 'true' to enable Supabase
    - SUPABASE_URL: project URL
    - SUPABASE_KEY: anon key
    - SUPABASE_AUTO_CREATE_TABLES: set to 'true' to auto-create on init
    """
    import os
    
    if os.getenv("USE_SUPABASE", "false").lower() != "true":
        return None
    
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    auto_create = os.getenv("SUPABASE_AUTO_CREATE_TABLES", "false").lower() == "true"
    
    if not url or not key:
        raise BankingError(
            "USE_SUPABASE is true but SUPABASE_URL or SUPABASE_KEY not set. "
            "Check your .env file."
        )
    
    return SupabaseBackend(url=url, key=key, auto_create_tables=auto_create)
