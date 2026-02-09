"""Simple token-based authentication with hardcoded users."""

from __future__ import annotations

import secrets

from fastapi import HTTPException, WebSocket

from .config import USERS

_tokens: dict[str, str] = {}  # token -> username


def login(username: str, password: str) -> tuple[str, str]:
    """Validate credentials and return (token, display_name)."""
    user = USERS.get(username)
    if not user or user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = secrets.token_urlsafe(32)
    _tokens[token] = username
    return token, user["display_name"]


def get_current_user(token: str) -> str:
    """Resolve a token to a username."""
    if token not in _tokens:
        raise HTTPException(status_code=401, detail="Invalid token")
    return _tokens[token]


async def ws_authenticate(websocket: WebSocket) -> str:
    """Authenticate a WebSocket connection from query param."""
    token = websocket.query_params.get("token")
    if not token or token not in _tokens:
        await websocket.close(code=4001)
        raise ValueError("Unauthorized WebSocket connection")
    return _tokens[token]
