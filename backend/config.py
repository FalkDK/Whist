"""Configuration constants for the Whist backend."""

USERS: dict[str, dict[str, str]] = {
    "alice": {"password": "alice123", "display_name": "Alice"},
    "bob": {"password": "bob123", "display_name": "Bob"},
    "carol": {"password": "carol123", "display_name": "Carol"},
    "dave": {"password": "dave123", "display_name": "Dave"},
}

MAX_PLAYERS_PER_GAME = 4
BOT_NAMES = ["Bot-1", "Bot-2", "Bot-3"]
