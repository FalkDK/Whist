"""High-level game loop for a single Bid Whist deal."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .bidding import Bid
from .cards import Card, Direction, Suit
from .round import Phase, Round


@dataclass
class Game:
    """Coordinates a single Bid Whist deal through bidding, kitty, and play."""

    players: list[str]
    dealer_index: int = 0
    round: Round = field(init=False)

    def __post_init__(self) -> None:
        self.round = Round(self.players, dealer_index=self.dealer_index)

    # --- Phase queries ---

    @property
    def phase(self) -> Phase:
        return self.round.phase

    # --- Bidding ---

    def expected_bidder(self) -> str | None:
        return self.round.expected_bidder()

    def place_bid(self, player: str, bid: Bid | None) -> None:
        self.round.place_bid(player, bid)

    @property
    def winning_bid(self) -> Bid | None:
        return self.round.winning_bid

    @property
    def bid_winner(self) -> str | None:
        return self.round.bid_winner

    # --- Kitty exchange ---

    def set_trump_and_exchange(
        self,
        player: str,
        trump_suit: Suit | None,
        direction: Direction,
        discards: list[Card],
    ) -> None:
        self.round.set_trump_and_exchange(player, trump_suit, direction, discards)

    # --- Play ---

    def expected_player(self) -> str:
        return self.round.expected_player()

    def play(self, player: str, card: Card) -> str | None:
        return self.round.play(player, card)

    def play_trick(self, plays: dict[str, Card]) -> str:
        return self.round.play_trick(plays)

    def play_auto(self, rng: random.Random | None = None) -> str | None:
        return self.round.play_auto(rng)

    def play_out(self, rng: random.Random | None = None) -> None:
        self.round.play_out(rng)

    def is_complete(self) -> bool:
        return self.round.is_complete()

    def score(self) -> dict[str, int]:
        if not self.is_complete():
            raise ValueError("game is not complete")
        return self.round.score()

    def trick_counts(self) -> dict[str, int]:
        return self.round.trick_counts()

    def state(self) -> dict[str, object]:
        return self.round.state()

    def trick_history(self) -> list[dict[str, object]]:
        return self.round.trick_history()

    def display_history(self) -> list[str]:
        return self.round.display_history()
