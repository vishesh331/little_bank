"""
session.py — Session Management for the Integrated Platform
============================================================
Manages user login sessions across the entire system.

When a user logs in via hub.py, their session is stored in a temporary file.
Other services check this file before prompting for login credentials.

Services can:
- get_current_session() — Check if user is logged in
- clear_session() — Log out the current user

This allows seamless transitions between hub and other services without
re-authentication, while still requiring login if services are run directly.

Implementation Details
----------------------
- Sessions are stored in a temporary session file (session_token.tmp)
- Session file contains account_number and is created on login
- Session is automatically cleared on logout or hub exit
- Direct service launches don't find the session file, so they prompt for login
"""

import json
import os
from pathlib import Path
from typing import Optional, TypedDict


class SessionInfo(TypedDict):
    account_number: str
    username: str


# Session file location (in the same directory as the scripts)
_SESSION_FILE = Path(__file__).parent / ".session_token.tmp"


def create_session(account_number: str, username: str) -> None:
    """
    Create a new session for the given account.
    
    Parameters
    ----------
    account_number : str
        The user's account number.
    username : str
        The user's display name.
    
    Called by: hub.py on successful login
    """
    session_data: SessionInfo = {
        "account_number": account_number,
        "username": username,
    }
    try:
        with open(_SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2)
    except OSError as exc:
        raise RuntimeError(f"Failed to create session: {exc}")


def get_current_session() -> Optional[SessionInfo]:
    """
    Retrieve the current user's session if one exists.
    
    Returns
    -------
    SessionInfo dict if a valid session exists, None otherwise.
    
    Called by: numberguesser.py, movie_tickets.py, etc. to check for active session
    """
    if not _SESSION_FILE.exists():
        return None
    
    try:
        with open(_SESSION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Validate the session data has required fields
        if isinstance(data, dict) and "account_number" in data and "username" in data:
            return SessionInfo(
                account_number=data["account_number"],
                username=data["username"],
            )
    except (json.JSONDecodeError, OSError):
        pass
    
    return None


def clear_session() -> None:
    """
    Clear the current session (log out the user).
    
    Called by: hub.py on logout or program exit
    """
    if _SESSION_FILE.exists():
        try:
            _SESSION_FILE.unlink()
        except OSError:
            pass


def is_session_active() -> bool:
    """
    Check if there is an active session without retrieving details.
    
    Returns
    -------
    bool : True if session exists, False otherwise.
    """
    return get_current_session() is not None
