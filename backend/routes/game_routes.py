"""Game state REST endpoint (fallback for initial page load)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from ..auth import get_current_user
from ..models import GameStateSchema

router = APIRouter()

_game_manager = None


def set_game_manager(gm) -> None:  # noqa: ANN001
    global _game_manager
    _game_manager = gm


def _get_user(token: str = Query(...)) -> str:
    return get_current_user(token)


@router.get("/{game_id}/state", response_model=GameStateSchema)
def game_state(game_id: str, user: str = Depends(_get_user)) -> GameStateSchema:
    active = _game_manager.get_game(game_id)
    if active is None:
        raise HTTPException(status_code=404, detail="Game not found")
    if active.seat_for(user) is None:
        raise HTTPException(status_code=403, detail="Not a player in this game")
    return active.build_state_for(user)
