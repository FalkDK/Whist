"""Deal and round helpers for Whist."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .cards import Card
from .deck import Deck
from .scoring import Scoreboard


@dataclass
class Deal:
    """Represents a single 13-trick deal."""

    players: list[str]
    deck: Deck = field(default_factory=Deck)
    hands: dict[str, list[Card]] = field(init=False)
    scoreboard: Scoreboard = field(init=False)

    def __post_init__(self) -> None:
        if len(self.players) != 4:
            raise ValueError("Whist expects four players")
        self.deck.shuffle()
        self.hands = {
            player: self.deck.deal(13) for player in self.players
        }
        self.scoreboard = Scoreboard(self.players)

    def record_trick(self, winner: str) -> None:
        self.scoreboard.record_trick(winner)

    def partnership_points(self) -> dict[str, int]:
        return self.scoreboard.partnership_points()

    def hand_for(self, player: str) -> Iterable[Card]:
        if player not in self.hands:
            raise ValueError("player must be part of the deal")
        return list(self.hands[player])
