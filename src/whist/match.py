"""High-level game loop for a single Whist deal."""

from __future__ import annotations

from dataclasses import dataclass, field

from .cards import Card, Suit
from .round import Round


@dataclass
class Game:
    """Coordinates a single Whist deal from first lead to final score."""

    players: list[str]
    trump: Suit | None = None
    round: Round = field(init=False)

    def __post_init__(self) -> None:
        self.round = Round(self.players, trump=self.trump)

    def expected_player(self) -> str:
        return self.round.expected_player()

    def play(self, player: str, card: Card) -> str | None:
        return self.round.play(player, card)

    def play_trick(self, plays: dict[str, Card]) -> str:
        return self.round.play_trick(plays)

    def is_complete(self) -> bool:
        return self.round.is_complete()

    def score(self) -> dict[str, int]:
        if not self.is_complete():
            raise ValueError("game is not complete")
        return self.round.score()

    def state(self) -> dict[str, object]:
        return self.round.state()
