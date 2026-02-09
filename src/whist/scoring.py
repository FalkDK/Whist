"""Scoring helpers for Bid Whist."""

from __future__ import annotations

from dataclasses import dataclass, field

from .bidding import Bid

BOOK = 6
GAME_TARGET = 7


def tricks_to_points(tricks_won: int) -> int:
    """Whist awards one point for each trick above the book (6)."""
    if tricks_won < 0:
        raise ValueError("tricks_won must be non-negative")
    return max(0, tricks_won - BOOK)


@dataclass
class Scoreboard:
    """Tracks trick totals for the two Bid Whist partnerships."""

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


def partnership_for_player(players: list[str], player: str) -> str:
    """Return 'north_south' or 'east_west' for the given player."""
    idx = players.index(player)
    return "north_south" if idx % 2 == 0 else "east_west"


def opponent_partnership(partnership: str) -> str:
    return "east_west" if partnership == "north_south" else "north_south"


def score_deal(
    bid: Bid,
    bid_winner: str,
    players: list[str],
    partnership_tricks: dict[str, int],
) -> dict[str, int]:
    """Score a completed Bid Whist deal.

    Returns points to add to each partnership's running total.
    Positive = gained, negative = set.

    Rules:
    - Bidding team made bid: scores tricks_above_book (actual, not just bid amount)
    - Bidding team set (failed): loses bid amount
    - Non-bidding team: scores their tricks_above_book only if bidding team was set
    """
    bidder_side = partnership_for_player(players, bid_winner)
    opp_side = opponent_partnership(bidder_side)

    bidder_tricks = partnership_tricks[bidder_side]
    opp_tricks = partnership_tricks[opp_side]
    bidder_books = tricks_to_points(bidder_tricks)

    result = {bidder_side: 0, opp_side: 0}

    if bidder_books >= bid.number:
        # Made the bid — score actual books taken
        result[bidder_side] = bidder_books
    else:
        # Set — lose the bid amount
        result[bidder_side] = -bid.number
        # Opponents score their own books
        result[opp_side] = tricks_to_points(opp_tricks)

    return result
