"""
bank.py — Reusable Banking Module
==================================
A small, self-contained banking API designed to be imported into
other Python projects (e.g. an e-commerce checkout, movie ticket
system, subscription service, etc.).

Public API
----------
    bank = BankingSystem()

    # Account management
    bank.create_account(username, password, initial_balance=0.0) -> AccountInfo
    bank.get_account(account_number)                              -> AccountInfo
    bank.get_balance(account_number)                             -> float

    # Authentication
    bank.authenticate(account_number, password)                  -> AccountInfo

    # Transactions
    bank.deposit(account_number, amount)                         -> float  (new balance)
    bank.withdraw(account_number, password, amount)              -> float  (new balance)
    bank.transfer(from_account, password, to_account, amount)    -> TransactionReceipt

    # History
    bank.get_transactions(account_number)                        -> list[TransactionRecord]

Custom Exceptions (importable)
------------------------------
    AccountNotFoundError
    AuthenticationError
    InsufficientFundsError
    InvalidAmountError

Usage example
-------------
    from bank import BankingSystem, InsufficientFundsError

    bank = BankingSystem()
    receipt = bank.transfer(
        from_account="1234567890",
        password="secret",
        to_account="9876543210",
        amount=150.00,          # set programmatically — never prompted from the user
    )
    print(receipt["status"])    # "success"
"""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, TypedDict


# ---------------------------------------------------------------------------
# Type aliases (informational — Python does not enforce these at runtime)
# ---------------------------------------------------------------------------

class AccountInfo(TypedDict):
    account_number: str
    username: str
    balance: float
    created_at: str


class TransactionReceipt(TypedDict):
    transaction_id: str
    type: str
    from_account: Optional[str]
    to_account: Optional[str]
    amount: float
    new_balance: float
    timestamp: str
    status: str


# ---------------------------------------------------------------------------
# Custom exceptions
# ---------------------------------------------------------------------------

class BankingError(Exception):
    """Base class for all banking errors."""


class AccountNotFoundError(BankingError):
    """Raised when no account matches the given account number."""


class AuthenticationError(BankingError):
    """Raised when the password does not match the stored hash."""


class InsufficientFundsError(BankingError):
    """Raised when a withdrawal or transfer exceeds the available balance."""


class InvalidAmountError(BankingError):
    """Raised when a monetary amount is zero, negative, or non-numeric."""


# ---------------------------------------------------------------------------
# Default JSON schema
# ---------------------------------------------------------------------------

_EMPTY_DATA: dict = {
    "accounts": {},      # { account_number: _AccountRecord }
    "transactions": [],  # [ _TransactionRecord ]
}

# Internal record shapes (not exported — implementation detail)
#   _AccountRecord  = { account_number, username, password_hash, balance, created_at }
#   _TransactionRecord = { transaction_id, type, from_account, to_account,
#                          amount, timestamp }


# ---------------------------------------------------------------------------
# BankingSystem
# ---------------------------------------------------------------------------

class BankingSystem:
    """
    Core banking engine with pluggable storage backend.

    Parameters
    ----------
    data_file : str | Path
        Path to the JSON file used for persistence (default: "accounts.json").
        Ignored if backend is provided.
    backend : object, optional
        Custom storage backend with load() and save() methods.
        If None, uses local JSON file storage (default).
    """

    def __init__(self, data_file: str | Path = "accounts.json", backend=None) -> None:
        if backend is not None:
            self._backend = backend
            self._data_file = None
        else:
            self._data_file = Path(data_file)
            self._backend = None
        self._ensure_storage()

    # ------------------------------------------------------------------
    # Account management
    # ------------------------------------------------------------------

    def create_account(
        self,
        username: str,
        password: str,
        initial_balance: float = 0.0,
    ) -> AccountInfo:
        """
        Create a new bank account.

        Parameters
        ----------
        username        : Display name for the account holder.
        password        : Plain-text password (stored as a SHA-256 hash).
        initial_balance : Starting balance (default 0.0).

        Returns
        -------
        AccountInfo dict (without password hash).
        """
        if not username or not username.strip():
            raise ValueError("Username must not be empty.")
        if not password:
            raise ValueError("Password must not be empty.")
        _validate_amount(initial_balance, allow_zero=True)

        data = self._load()
        account_number = self._unique_account_number(data)

        data["accounts"][account_number] = {
            "account_number": account_number,
            "username": username.strip(),
            "password_hash": _hash_password(password),
            "balance": round(initial_balance, 2),
            "created_at": _now(),
        }
        self._save(data)
        return _public_account(data["accounts"][account_number])

    def get_account(self, account_number: str) -> AccountInfo:
        """Return public account information (no password hash)."""
        data = self._load()
        return _public_account(self._require_account(data, account_number))

    def get_balance(self, account_number: str) -> float:
        """Return the current balance for an account."""
        return self.get_account(account_number)["balance"]

    # ------------------------------------------------------------------
    # Authentication
    # ------------------------------------------------------------------

    def authenticate(self, account_number: str, password: str) -> AccountInfo:
        """
        Verify credentials and return public account info on success.

        Raises
        ------
        AccountNotFoundError  : account_number does not exist.
        AuthenticationError   : password is incorrect.
        """
        data = self._load()
        record = self._require_account(data, account_number)
        if record["password_hash"] != _hash_password(password):
            raise AuthenticationError("Incorrect password.")
        return _public_account(record)

    # ------------------------------------------------------------------
    # Transactions
    # ------------------------------------------------------------------

    def deposit(self, account_number: str, amount: float) -> float:
        """
        Deposit money into an account (no authentication required).

        Returns the new balance.
        """
        _validate_amount(amount)
        data = self._load()
        record = self._require_account(data, account_number)
        record["balance"] = round(record["balance"] + amount, 2)
        self._log(data, "deposit", None, account_number, amount)
        self._save(data)
        return record["balance"]

    def withdraw(
        self,
        account_number: str,
        password: str,
        amount: float,
    ) -> float:
        """
        Withdraw money from an account (authentication required).

        Returns the new balance.

        Raises
        ------
        InsufficientFundsError : balance < amount.
        """
        _validate_amount(amount)
        self.authenticate(account_number, password)  # raises on bad credentials
        data = self._load()
        record = self._require_account(data, account_number)

        if record["balance"] < amount:
            raise InsufficientFundsError(
                f"Insufficient funds — balance: ${record['balance']:.2f}, "
                f"requested: ${amount:.2f}."
            )

        record["balance"] = round(record["balance"] - amount, 2)
        self._log(data, "withdrawal", account_number, None, amount)
        self._save(data)
        return record["balance"]

    def transfer(
        self,
        from_account: str,
        password: str,
        to_account: str,
        amount: float,
    ) -> TransactionReceipt:
        """
        Transfer money between two accounts.

        This is the primary integration point for external projects.
        The *amount* is always passed programmatically by the caller —
        it is never prompted from the end-user inside this function.
        The external project is free to hardcode it, calculate it,
        or take it as user input however it sees fit.

        Parameters
        ----------
        from_account : Sender's account number.
        password     : Sender's password (used for authentication).
        to_account   : Recipient's account number.
        amount       : Exact amount to transfer (set by the calling project).

        Returns
        -------
        TransactionReceipt dict with status, IDs, and new balance.

        Raises
        ------
        AccountNotFoundError   : Either account does not exist.
        AuthenticationError    : Sender's password is wrong.
        InsufficientFundsError : Sender's balance < amount.
        InvalidAmountError     : Amount is zero or negative.

        Example (movie ticket project)
        -----
            TICKET_PRICE = 250.00  # set by the seller, never prompted
            receipt = bank.transfer(
                from_account=buyer_account,
                password=buyer_password,
                to_account=CINEMA_ACCOUNT,
                amount=TICKET_PRICE,
            )
            if receipt["status"] == "success":
                issue_ticket()
        """
        _validate_amount(amount)
        self.authenticate(from_account, password)  # raises on bad credentials

        data = self._load()
        sender = self._require_account(data, from_account)

        # Validate destination separately so the error is descriptive
        if to_account not in data["accounts"]:
            raise AccountNotFoundError(
                f"Destination account '{to_account}' not found."
            )
        recipient = data["accounts"][to_account]

        if sender["balance"] < amount:
            raise InsufficientFundsError(
                f"Insufficient funds — balance: ${sender['balance']:.2f}, "
                f"transfer amount: ${amount:.2f}."
            )

        # Atomic update (both sides before saving)
        sender["balance"] = round(sender["balance"] - amount, 2)
        recipient["balance"] = round(recipient["balance"] + amount, 2)

        tx_id = self._log(data, "transfer", from_account, to_account, amount)
        self._save(data)

        return TransactionReceipt(
            transaction_id=tx_id,
            type="transfer",
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            new_balance=sender["balance"],
            timestamp=_now(),
            status="success",
        )

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def get_transactions(self, account_number: str) -> list[dict]:
        """
        Return all transactions involving *account_number*,
        sorted from newest to oldest.
        """
        # Validate account exists first
        data = self._load()
        self._require_account(data, account_number)
        return sorted(
            [
                tx for tx in data.get("transactions", [])
                if tx.get("from_account") == account_number
                or tx.get("to_account") == account_number
            ],
            key=lambda tx: tx["timestamp"],
            reverse=True,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_storage(self) -> None:
        """Ensure storage backend is ready (create JSON file if needed)."""
        if self._backend is not None:
            # Backend handles its own initialization
            return

        # JSON file backend
        if not self._data_file.exists():
            self._save(_EMPTY_DATA.copy())
            return

        # If the file exists but is empty or contains invalid JSON, reset it
        # to the empty schema rather than leaving the system in a broken state.
        try:
            # Attempt to load existing data; _load wraps JSON errors as BankingError
            self._load()
        except BankingError:
            self._save(_EMPTY_DATA.copy())

    def _load(self) -> dict:
        if self._backend is not None:
            return self._backend.load()

        try:
            with open(self._data_file, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            raise BankingError(
                f"Failed to read data file '{self._data_file}': {exc}"
            ) from exc

    def _save(self, data: dict) -> None:
        if self._backend is not None:
            self._backend.save(data)
            return

        try:
            with open(self._data_file, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2, ensure_ascii=False)
        except OSError as exc:
            raise BankingError(
                f"Failed to write data file '{self._data_file}': {exc}"
            ) from exc

    def _require_account(self, data: dict, account_number: str) -> dict:
        """Return the raw account record or raise AccountNotFoundError."""
        record = data["accounts"].get(account_number)
        if record is None:
            raise AccountNotFoundError(
                f"No account found with number '{account_number}'."
            )
        return record

    def _unique_account_number(self, data: dict) -> str:
        """Generate a unique 10-digit account number."""
        for _ in range(10):
            candidate = str(uuid.uuid4().int)[:10]
            if candidate not in data["accounts"]:
                return candidate
        raise BankingError("Could not generate a unique account number.")

    def _log(
        self,
        data: dict,
        tx_type: str,
        from_account: Optional[str],
        to_account: Optional[str],
        amount: float,
    ) -> str:
        """Append a transaction record and return its ID."""
        tx_id = str(uuid.uuid4())
        data.setdefault("transactions", []).append(
            {
                "transaction_id": tx_id,
                "type": tx_type,
                "from_account": from_account,
                "to_account": to_account,
                "amount": round(amount, 2),
                "timestamp": _now(),
            }
        )
        return tx_id


# ---------------------------------------------------------------------------
# Module-level helpers (private)
# ---------------------------------------------------------------------------

def _hash_password(password: str) -> str:
    """Return the SHA-256 hex digest of *password*."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _validate_amount(amount: float, *, allow_zero: bool = False) -> None:
    """Raise InvalidAmountError for non-positive (or negative) amounts."""
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise InvalidAmountError(f"Amount must be a number, got: {amount!r}")
    if allow_zero and amount < 0:
        raise InvalidAmountError("Amount must not be negative.")
    if not allow_zero and amount <= 0:
        raise InvalidAmountError("Amount must be greater than zero.")


def _public_account(record: dict) -> AccountInfo:
    """Strip the password hash before returning account data externally."""
    return AccountInfo(
        account_number=record["account_number"],
        username=record["username"],
        balance=record["balance"],
        created_at=record["created_at"],
    )


def _now() -> str:
    """Return the current UTC timestamp as an ISO-8601 string."""
    return datetime.utcnow().isoformat() + "Z"
