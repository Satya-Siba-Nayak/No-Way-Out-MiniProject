"""
Save System — JSON-based save/load for player progress.
"""

import json
import os
from datetime import datetime

# Default save path (relative to project root)
SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SAVE_FILE = os.path.join(SAVE_DIR, "savegame.json")


def save_game(player_name, current_room, puzzles_solved, player_pos):
    """
    Save current game state to JSON.

    Args:
        player_name:    str — the player's display name
        current_room:   str — e.g. "easy_room"
        puzzles_solved: list[str] — IDs of solved puzzles
        player_pos:     tuple(int, int) — player x, y
    """
    os.makedirs(SAVE_DIR, exist_ok=True)

    data = {
        "player_name": player_name,
        "current_room": current_room,
        "puzzles_solved": list(puzzles_solved),
        "player_position": list(player_pos),
        "timestamp": datetime.now().isoformat(),
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return True


def load_game():
    """
    Load saved game state. Returns the data dict, or None if no save exists.
    """
    if not os.path.exists(SAVE_FILE):
        return None

    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, IOError):
        return None


def has_save():
    """Check whether a save file exists."""
    return os.path.exists(SAVE_FILE)


def delete_save():
    """Delete the save file (for New Game)."""
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
