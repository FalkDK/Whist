"""Pydantic schemas for API request/response serialization."""

from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    token: str
    display_name: str


class CreateGameRequest(BaseModel):
    bot_count: int = 3


class CardSchema(BaseModel):
    rank: str
    suit: str
    label: str


class PlaySchema(BaseModel):
    player: str
    card: CardSchema


class TrickSchema(BaseModel):
    plays: list[PlaySchema]
    winner: str | None = None


class GameStateSchema(BaseModel):
    game_id: str
    players: list[str]
    trump_suit: str | None
    trump_card: CardSchema | None
    your_hand: list[CardSchema]
    legal_moves: list[CardSchema]
    current_trick: list[PlaySchema]
    expected_player: str
    tricks_played: int
    tricks_remaining: int
    trick_counts: dict[str, int]
    partnership_scores: dict[str, int]
    completed_tricks: list[TrickSchema]
    is_complete: bool
    seat: str


class LobbyGameSchema(BaseModel):
    game_id: str
    host: str
    players: list[str]
    bot_count: int
    needed: int
    status: str
