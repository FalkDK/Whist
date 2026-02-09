"""Match helpers for tracking multiple deals in Bid Whist."""

from __future__ import annotations

from dataclasses import dataclass, field

from .match import Game
from .scoring import GAME_TARGET


@dataclass
class Match:
    """Aggregates multiple deals with dealer rotation and game target scoring.

    A match ends when a partnership reaches +GAME_TARGET or falls to -GAME_TARGET.
    """

    players: list[str]
    games: list[Game] = field(default_factory=list)
    scores: dict[str, int] = field(init=False)
    _dealer_index: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        if len(self.players) != 4:
            raise ValueError("Bid Whist expects four players")
        self.scores = {"north_south": 0, "east_west": 0}

    def start_game(self) -> Game:
        """Start the next deal with the current dealer."""
        game = Game(self.players, dealer_index=self._dealer_index)
        self.games.append(game)
        return game

    def record_game(self, game: Game) -> dict[str, int]:
        """Record a completed game's score and rotate the dealer."""
        if game not in self.games:
            raise ValueError("game must be part of this match")
        result = game.score()
        self.scores["north_south"] += result.get("north_south", 0)
        self.scores["east_west"] += result.get("east_west", 0)
        # Rotate dealer clockwise
        self._dealer_index = (self._dealer_index + 1) % 4
        return result

    def total_score(self) -> dict[str, int]:
        return dict(self.scores)

    @property
    def is_over(self) -> bool:
        """Match ends when either side reaches +/- game target."""
        for score in self.scores.values():
            if score >= GAME_TARGET or score <= -GAME_TARGET:
                return True
        return False

    @property
    def winner(self) -> str | None:
        """Return the winning partnership, or None if match is not over."""
        if not self.is_over:
            return None
        if self.scores["north_south"] >= GAME_TARGET:
            return "north_south"
        if self.scores["east_west"] >= GAME_TARGET:
            return "east_west"
        if self.scores["north_south"] <= -GAME_TARGET:
            return "east_west"
        if self.scores["east_west"] <= -GAME_TARGET:
            return "north_south"
        return None
