"""Lobby REST endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..auth import get_current_user
from ..models import CreateGameRequest, LobbyGameSchema

router = APIRouter()

# These will be set from main.py
_lobby_manager = None


def set_lobby_manager(lm) -> None:  # noqa: ANN001
    global _lobby_manager
    _lobby_manager = lm


def _get_user(token: str = Query(...)) -> str:
    return get_current_user(token)


@router.get("", response_model=list[LobbyGameSchema])
def list_games(user: str = Depends(_get_user)) -> list[LobbyGameSchema]:
    return [e.to_schema() for e in _lobby_manager.list_entries()]


@router.post("/create", response_model=LobbyGameSchema)
def create_game(body: CreateGameRequest, user: str = Depends(_get_user)) -> LobbyGameSchema:
    entry = _lobby_manager.create(user, body.bot_count)
    return entry.to_schema()


@router.post("/{game_id}/join", response_model=LobbyGameSchema)
def join_game(game_id: str, user: str = Depends(_get_user)) -> LobbyGameSchema:
    entry = _lobby_manager.join(game_id, user)
    return entry.to_schema()
