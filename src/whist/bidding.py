"""Bidding round for Bid Whist."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .cards import Direction, Suit


class BidType(str, Enum):
    """The three bid suffixes in Bid Whist."""

    UPTOWN = "uptown"
    DOWNTOWN = "downtown"
    NO_TRUMP = "no_trump"


# Ranking within same number: uptown < downtown < no_trump
_BID_TYPE_RANK = {BidType.UPTOWN: 0, BidType.DOWNTOWN: 1, BidType.NO_TRUMP: 2}


@dataclass(frozen=True)
class Bid:
    """A single bid: number (3-7) + type (uptown/downtown/no_trump)."""

    number: int
    bid_type: BidType

    def __post_init__(self) -> None:
        if self.number < 3 or self.number > 7:
            raise ValueError("bid number must be 3-7")

    @property
    def strength(self) -> int:
        """Comparable strength: higher = stronger bid."""
        return self.number * 10 + _BID_TYPE_RANK[self.bid_type]

    def outranks(self, other: "Bid") -> bool:
        return self.strength > other.strength

    @property
    def direction(self) -> Direction:
        """Card ranking direction implied by this bid."""
        if self.bid_type == BidType.DOWNTOWN:
            return Direction.DOWNTOWN
        return Direction.UPTOWN

    @property
    def has_trump(self) -> bool:
        return self.bid_type != BidType.NO_TRUMP

    @property
    def is_boston(self) -> bool:
        return self.number == 7


@dataclass
class BiddingRound:
    """Manages one round of bidding.  Each player bids once or passes.

    Players bid starting left of the dealer.  If the first three pass
    the dealer is forced to bid (minimum 3).
    """

    players: list[str]
    dealer_index: int
    bids: dict[str, Bid | None] = field(init=False)
    _order: list[str] = field(init=False)
    _next: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        if len(self.players) != 4:
            raise ValueError("Bid Whist expects four players")
        # Bidding starts left of dealer
        start = (self.dealer_index + 1) % 4
        self._order = [self.players[(start + i) % 4] for i in range(4)]
        self.bids = {}

    @property
    def is_complete(self) -> bool:
        return self._next >= 4

    @property
    def expected_bidder(self) -> str | None:
        if self.is_complete:
            return None
        return self._order[self._next]

    def place_bid(self, player: str, bid: Bid | None) -> None:
        """Place a bid or pass (bid=None).

        The dealer (last bidder) must bid if everyone else passed.
        """
        if self.is_complete:
            raise ValueError("bidding is already complete")
        if player != self.expected_bidder:
            raise ValueError("not this player's turn to bid")

        is_last = self._next == 3  # dealer
        if bid is None and is_last and not self._highest_bid():
            raise ValueError("dealer must bid when all others pass")

        if bid is not None:
            current_best = self._highest_bid()
            if current_best is not None and not bid.outranks(current_best):
                raise ValueError("bid must outrank the current highest bid")

        self.bids[player] = bid
        self._next += 1

    def _highest_bid(self) -> Bid | None:
        best: Bid | None = None
        for b in self.bids.values():
            if b is not None and (best is None or b.outranks(best)):
                best = b
        return best

    @property
    def winning_bid(self) -> Bid | None:
        if not self.is_complete:
            return None
        return self._highest_bid()

    @property
    def winner(self) -> str | None:
        """Player who won the bidding."""
        if not self.is_complete:
            return None
        best = self._highest_bid()
        if best is None:
            return None
        for player, bid in self.bids.items():
            if bid is not None and bid.strength == best.strength:
                return player
        return None
