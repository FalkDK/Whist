"""Scoring helpers for Whist."""

from __future__ import annotations

from dataclasses import dataclass, field


def tricks_to_points(tricks_won: int) -> int:
    """Whist awards one point for each trick above six."""

    if tricks_won < 0:
        raise ValueError("tricks_won must be non-negative")
    return max(0, tricks_won - 6)


@dataclass
class Scoreboard:
    """Tracks trick totals for the two Whist partnerships."""

    players: list[str]
    trick_counts: dict[str, int] = field(init=False)

    def __post_init__(self) -> None:
        if len(self.players) != 4:
            raise ValueError("Whist expects four players")
        self.trick_counts = {player: 0 for player in self.players}

    def record_trick(self, winner: str) -> None:
        if winner not in self.trick_counts:
            raise ValueError("winner must be a registered player")
        self.trick_counts[winner] += 1

    def partnership_tricks(self) -> dict[str, int]:
        north_south = self.trick_counts[self.players[0]] + self.trick_counts[
            self.players[2]
        ]
        east_west = self.trick_counts[self.players[1]] + self.trick_counts[
            self.players[3]
        ]
        return {"north_south": north_south, "east_west": east_west}

    def partnership_points(self) -> dict[str, int]:
        tricks = self.partnership_tricks()
        return {
            "north_south": tricks_to_points(tricks["north_south"]),
            "east_west": tricks_to_points(tricks["east_west"]),
        }
