"""Match helpers for tracking multiple deals."""

from __future__ import annotations

from dataclasses import dataclass, field

from .match import Game
from .cards import Suit


@dataclass
class Match:
    """Aggregates multiple deals and tracks cumulative partnership points."""

    players: list[str]
    games: list[Game] = field(default_factory=list)
    scores: dict[str, int] = field(init=False)

    def __post_init__(self) -> None:
        if len(self.players) != 4:
            raise ValueError("Whist expects four players")
        self.scores = {"north_south": 0, "east_west": 0}

    def start_game(self, trump: Suit | None = None) -> Game:
        game = Game(self.players, trump=trump)
        self.games.append(game)
        return game

    def record_game(self, game: Game) -> dict[str, int]:
        if game not in self.games:
            raise ValueError("game must be part of this match")
        result = game.score()
        self.scores["north_south"] += result["north_south"]
        self.scores["east_west"] += result["east_west"]
        return result

    def total_score(self) -> dict[str, int]:
        return dict(self.scores)
