"""
announcements.py — Announcement and Leaderboard System
======================================================
Handles real-time announcements of big wins and maintains
leaderboard of top casino winners across the shared database.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Try to use Supabase backend if configured
try:
    from supabase_backend import create_supabase_backend_from_env
    backend = create_supabase_backend_from_env()
    use_supabase = backend is not None
except ImportError:
    use_supabase = False
    backend = None

# File-based storage for announcements
ANNOUNCEMENTS_FILE = Path("announcements.json")
DATA_FILE = Path("accounts.json")


def _ensure_announcements_file() -> None:
    """Ensure announcements file exists."""
    if not ANNOUNCEMENTS_FILE.exists():
        data = {
            "latest_announcement": None,
            "last_updated": None,
            "casino_stats": {}  # Track cumulative casino wins per user
        }
        with open(ANNOUNCEMENTS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


def record_casino_win(username: str, account_number: str, amount_won: float) -> None:
    """
    Record a casino win and update announcements.
    
    Args:
        username: User's display name
        account_number: User's account number
        amount_won: Amount won in this game
    """
    _ensure_announcements_file()
    
    try:
        with open(ANNOUNCEMENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {
            "latest_announcement": None,
            "last_updated": None,
            "casino_stats": {}
        }
    
    # Update cumulative casino stats
    if account_number not in data["casino_stats"]:
        data["casino_stats"][account_number] = {
            "username": username,
            "total_won": 0.0,
            "win_count": 0
        }
    
    data["casino_stats"][account_number]["total_won"] += amount_won
    data["casino_stats"][account_number]["win_count"] += 1
    data["casino_stats"][account_number]["username"] = username  # Update username in case it changed
    
    # Create announcement
    announcement = f"{username} just won ${amount_won:.2f} in the casino! 🎰"
    data["latest_announcement"] = announcement
    data["last_updated"] = datetime.now().isoformat()
    
    with open(ANNOUNCEMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_latest_announcement() -> Optional[str]:
    """Get the latest casino win announcement."""
    _ensure_announcements_file()
    
    try:
        with open(ANNOUNCEMENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("latest_announcement")
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_leaderboard(top_n: int = 5) -> List[Dict]:
    """
    Get top N casino winners with cumulative winnings.
    
    Returns:
        List of dicts with username, account_number, total_won, win_count
    """
    _ensure_announcements_file()
    
    try:
        with open(ANNOUNCEMENTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
    # Get casino stats and sort by total_won
    stats = list(data.get("casino_stats", {}).values())
    stats.sort(key=lambda x: x["total_won"], reverse=True)
    
    return stats[:top_n]


def reset_announcements() -> None:
    """Reset announcements (use with caution!)."""
    data = {
        "latest_announcement": None,
        "last_updated": None,
        "casino_stats": {}
    }
    with open(ANNOUNCEMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
