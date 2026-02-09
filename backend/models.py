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


class BidSchema(BaseModel):
    number: int
    bid_type: str  # "uptown" | "downtown" | "no_trump"


class GameStateSchema(BaseModel):
    game_id: str
    phase: str  # "bidding" | "kitty" | "playing" | "complete"
    players: list[str]
    seat: str

    # Bidding phase
    expected_bidder: str | None = None
    bids: dict[str, BidSchema | None] = {}
    bid_winner: str | None = None
    winning_bid: BidSchema | None = None

    # Kitty phase / playing phase
    trump_suit: str | None = None
    direction: str | None = None
    kitty: list[CardSchema] = []

    # Hand info (all phases)
    your_hand: list[CardSchema] = []
    legal_moves: list[CardSchema] = []

    # Playing phase
    current_trick: list[PlaySchema] = []
    expected_player: str | None = None
    tricks_played: int = 0
    tricks_remaining: int = 12
    trick_counts: dict[str, int] = {}
    partnership_scores: dict[str, int] = {}
    completed_tricks: list[TrickSchema] = []
    is_complete: bool = False


class LobbyGameSchema(BaseModel):
    game_id: str
    host: str
    players: list[str]
    bot_count: int
    needed: int
    status: str
