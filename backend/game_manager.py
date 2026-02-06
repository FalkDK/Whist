"""Manages active game instances and bridges the whist engine with the network layer."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field

from fastapi import WebSocket

from whist import Card, Game, Match, Rank, Suit

from .bot import BotPlayer
from .models import (
    CardSchema,
    GameStateSchema,
    PlaySchema,
    TrickSchema,
)

SEAT_NAMES = ["North", "East", "South", "West"]


def _serialize_card(card: Card) -> CardSchema:
    return CardSchema(rank=card.rank.value, suit=card.suit.value, label=card.label())


def _deserialize_card(data: dict) -> Card:
    return Card(rank=Rank(data["rank"]), suit=Suit(data["suit"]))


@dataclass
class ActiveGame:
    """Wraps a whist Match/Game with multiplayer metadata."""

    game_id: str
    seat_names: list[str]  # always the 4 cardinal seat names
    username_to_seat: dict[str, str] = field(default_factory=dict)
    seat_to_username: dict[str, str] = field(default_factory=dict)
    bot_seats: set[str] = field(default_factory=set)
    bots: dict[str, BotPlayer] = field(default_factory=dict)
    match: Match = field(init=False)
    current_game: Game = field(init=False)
    subscribers: dict[str, WebSocket] = field(default_factory=dict)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    host: str = ""

    def __post_init__(self) -> None:
        self.match = Match(self.seat_names)
        self.current_game = self.match.start_game()

    @property
    def human_seats(self) -> set[str]:
        return set(self.seat_names) - self.bot_seats

    def seat_for(self, username: str) -> str | None:
        return self.username_to_seat.get(username)

    def build_state_for(self, username: str) -> GameStateSchema:
        seat = self.username_to_seat[username]
        game = self.current_game
        rnd = game.round
        deal = rnd.deal

        trump_suit = rnd.trump.value if rnd.trump else None
        trump_card = _serialize_card(deal.trump_card) if deal.trump_card else None

        hand = [_serialize_card(c) for c in deal.hand_for(seat)]

        expected = game.expected_player()
        if expected == seat and not game.is_complete():
            legal = [_serialize_card(c) for c in deal.legal_moves(seat, rnd.current_trick)]
        else:
            legal = []

        current_trick = [
            PlaySchema(player=self._display_name(p), card=_serialize_card(c))
            for p, c in rnd.current_trick.plays
        ]

        completed = []
        for trick in rnd.completed_tricks:
            plays = [
                PlaySchema(player=self._display_name(p), card=_serialize_card(c))
                for p, c in trick.plays
            ]
            winner = trick.winner(rnd.trump)
            completed.append(TrickSchema(plays=plays, winner=self._display_name(winner) if winner else None))

        display_players = [self._display_name(s) for s in self.seat_names]

        trick_counts = {self._display_name(k): v for k, v in deal.trick_counts().items()}
        partnership = deal.partnership_points()

        return GameStateSchema(
            game_id=self.game_id,
            players=display_players,
            trump_suit=trump_suit,
            trump_card=trump_card,
            your_hand=hand,
            legal_moves=legal,
            current_trick=current_trick,
            expected_player=self._display_name(expected),
            tricks_played=len(rnd.completed_tricks),
            tricks_remaining=13 - len(rnd.completed_tricks),
            trick_counts=trick_counts,
            partnership_scores=partnership,
            completed_tricks=completed,
            is_complete=game.is_complete(),
            seat=self._display_name(seat),
        )

    def play_card(self, seat: str, card: Card) -> str | None:
        return self.current_game.play(seat, card)

    def auto_play_bots(self) -> list[tuple[str, Card, str | None]]:
        """Play for all consecutive bot seats. Returns (seat, card, trick_winner) tuples."""
        results: list[tuple[str, Card, str | None]] = []
        while not self.current_game.is_complete():
            expected = self.current_game.expected_player()
            if expected not in self.bot_seats:
                break
            bot = self.bots[expected]
            card = bot.choose_card(self.current_game)
            winner = self.current_game.play(expected, card)
            results.append((expected, card, winner))
        return results

    def _display_name(self, seat: str) -> str:
        """Return a human-friendly name for a seat."""
        if seat in self.seat_to_username:
            return self.seat_to_username[seat]
        return seat


class GameManager:
    """Central registry of all active games."""

    def __init__(self) -> None:
        self._games: dict[str, ActiveGame] = {}

    def create_game(
        self,
        host_username: str,
        human_usernames: list[str],
        bot_count: int,
        game_id: str | None = None,
    ) -> ActiveGame:
        if game_id is None:
            game_id = uuid.uuid4().hex[:8]
        active = ActiveGame(game_id=game_id, seat_names=list(SEAT_NAMES), host=host_username)

        # Assign humans to seats
        for i, username in enumerate(human_usernames):
            seat = SEAT_NAMES[i]
            active.username_to_seat[username] = seat
            active.seat_to_username[seat] = username

        # Assign bots to remaining seats
        bot_index = 0
        for i in range(len(human_usernames), 4):
            seat = SEAT_NAMES[i]
            bot_name = f"Bot-{bot_index + 1}"
            active.bot_seats.add(seat)
            active.bots[seat] = BotPlayer(seat, seed=bot_index)
            active.seat_to_username[seat] = bot_name
            bot_index += 1

        self._games[game_id] = active
        return active

    def get_game(self, game_id: str) -> ActiveGame | None:
        return self._games.get(game_id)

    def list_games(self) -> list[ActiveGame]:
        return list(self._games.values())
