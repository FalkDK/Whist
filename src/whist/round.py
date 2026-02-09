"""Round helpers for sequential trick play in Bid Whist."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum

from .bidding import Bid, BidType, BiddingRound
from .cards import Card, Direction, Suit
from .game import Deal
from .scoring import score_deal
from .trick import Trick

TRICKS_PER_DEAL = 12  # 12 cards per hand; 13th book is the kitty (first trick bonus)


class Phase(str, Enum):
    BIDDING = "bidding"
    KITTY = "kitty"
    PLAYING = "playing"
    COMPLETE = "complete"


@dataclass
class Round:
    """Manages bidding, kitty exchange, and trick play for a Bid Whist deal."""

    players: list[str]
    dealer_index: int = 0
    deal: Deal = field(init=False)
    bidding: BiddingRound = field(init=False)
    winning_bid: Bid | None = field(init=False, default=None)
    bid_winner: str | None = field(init=False, default=None)
    trump: Suit | None = field(init=False, default=None)
    direction: Direction = field(init=False, default=Direction.UPTOWN)
    phase: Phase = field(init=False, default=Phase.BIDDING)
    current_trick: Trick = field(default_factory=Trick)
    completed_tricks: list[Trick] = field(default_factory=list)
    _leader: str | None = field(init=False, default=None)
    _next_index: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        self.deal = Deal(self.players)
        self.bidding = BiddingRound(self.players, self.dealer_index)

    # --- Bidding phase ---

    def expected_bidder(self) -> str | None:
        if self.phase != Phase.BIDDING:
            return None
        return self.bidding.expected_bidder

    def place_bid(self, player: str, bid: Bid | None) -> None:
        """Place a bid or pass.  Advances to kitty phase when complete."""
        if self.phase != Phase.BIDDING:
            raise ValueError("not in bidding phase")
        self.bidding.place_bid(player, bid)
        if self.bidding.is_complete:
            self.winning_bid = self.bidding.winning_bid
            self.bid_winner = self.bidding.winner
            self.phase = Phase.KITTY

    # --- Kitty exchange phase ---

    def set_trump_and_exchange(
        self,
        player: str,
        trump_suit: Suit | None,
        direction: Direction,
        discards: list[Card],
    ) -> None:
        """Bid winner names trump, picks up kitty, discards 6 cards."""
        if self.phase != Phase.KITTY:
            raise ValueError("not in kitty exchange phase")
        if player != self.bid_winner:
            raise ValueError("only the bid winner can exchange the kitty")

        self.trump = trump_suit
        self.direction = direction
        self.deal.set_trump(trump_suit, direction)
        self.deal.exchange_kitty(player, discards)

        # Bid winner leads first trick
        self._set_leader(self.bid_winner)
        self.phase = Phase.PLAYING

    # --- Playing phase ---

    def _set_leader(self, leader: str) -> None:
        if leader not in self.players:
            raise ValueError("leader must be a player in the round")
        self._leader = leader
        self._next_index = self.players.index(leader)

    def expected_player(self) -> str:
        return self.players[self._next_index]

    def play(self, player: str, card: Card) -> str | None:
        """Play a card in order and advance to the next trick if complete."""
        if self.phase != Phase.PLAYING:
            raise ValueError("not in playing phase")
        if self.is_complete():
            raise ValueError("round is already complete")
        if player != self.expected_player():
            raise ValueError("player must act in turn order")

        self.deal.play_card(player, card, self.current_trick)
        self._next_index = (self._next_index + 1) % len(self.players)

        if not self.current_trick.is_complete():
            return None

        winner = self.current_trick.winner(self.trump, self.direction)
        if winner is None:
            raise ValueError("completed trick must have a winner")

        is_first = len(self.completed_tricks) == 0
        self.deal.record_trick(winner, is_first_trick=is_first)
        self.completed_tricks.append(self.current_trick)
        self.current_trick = Trick()

        if self.is_complete():
            self.phase = Phase.COMPLETE
        else:
            self._set_leader(winner)

        return winner

    def play_trick(self, plays: dict[str, Card]) -> str:
        """Play a full trick from an ordered mapping of player to card."""
        winner: str | None = None
        for _ in range(len(self.players)):
            player = self.expected_player()
            if player not in plays:
                raise ValueError("plays must include the next player in order")
            winner = self.play(player, plays[player])
        if winner is None:
            raise ValueError("trick did not complete with a winner")
        return winner

    def play_auto(self, rng: random.Random | None = None) -> str | None:
        """Play a legal card at random for the expected player."""
        player = self.expected_player()
        legal = self.deal.legal_moves(player, self.current_trick)
        if not legal:
            raise ValueError("no legal moves available")
        card = (rng or random).choice(legal)
        return self.play(player, card)

    def play_out(self, rng: random.Random | None = None) -> None:
        """Play out the remainder of the round automatically."""
        while not self.is_complete():
            self.play_auto(rng)

    def is_complete(self) -> bool:
        return len(self.completed_tricks) >= TRICKS_PER_DEAL

    def score(self) -> dict[str, int]:
        """Score this deal using Bid Whist rules."""
        if not self.is_complete() or self.winning_bid is None or self.bid_winner is None:
            raise ValueError("round is not complete")
        return score_deal(
            self.winning_bid,
            self.bid_winner,
            self.players,
            self.deal.scoreboard.partnership_tricks(),
        )

    def trick_counts(self) -> dict[str, int]:
        return self.deal.trick_counts()

    def state(self) -> dict[str, object]:
        """Return a snapshot of round progress for UI or logging."""
        base: dict[str, object] = {
            "phase": self.phase.value,
            "dealer": self.players[self.dealer_index],
            "trump": self.trump,
            "direction": self.direction.value if self.direction else None,
            "tricks_played": len(self.completed_tricks),
            "tricks_remaining": TRICKS_PER_DEAL - len(self.completed_tricks),
        }
        if self.phase == Phase.BIDDING:
            base["expected_bidder"] = self.expected_bidder()
            base["bids"] = {
                p: ({"number": b.number, "bid_type": b.bid_type.value} if b else None)
                for p, b in self.bidding.bids.items()
            }
        elif self.phase in (Phase.PLAYING, Phase.COMPLETE):
            base["leader"] = self._leader
            base["next_player"] = self.expected_player()
            base["bid_winner"] = self.bid_winner
            base["winning_bid"] = {
                "number": self.winning_bid.number,
                "bid_type": self.winning_bid.bid_type.value,
            } if self.winning_bid else None
        return base

    def trick_history(self) -> list[dict[str, object]]:
        """Return summaries of completed tricks."""
        return [
            {"winner": trick.winner(self.trump, self.direction), "plays": trick.summary()}
            for trick in self.completed_tricks
        ]

    def display_history(self) -> list[str]:
        """Return human-readable summaries for completed tricks."""
        return [
            f"{index + 1}. {winner}: "
            + ", ".join(f"{player} {card.display()}" for player, card in trick.plays)
            for index, trick in enumerate(self.completed_tricks)
            for winner in [trick.winner(self.trump, self.direction)]
        ]
