"""Deck operations for Whist."""

from __future__ import annotations

import random
from collections.abc import Iterable

from .cards import Card, Rank, Suit


class Deck:
    """Represents a standard 52-card deck."""

    def __init__(self, cards: Iterable[Card] | None = None) -> None:
        self._cards = list(cards) if cards is not None else self._standard_cards()

    @staticmethod
    def _standard_cards() -> list[Card]:
        return [Card(rank=rank, suit=suit) for suit in Suit for rank in Rank]

    def shuffle(self, rng: random.Random | None = None) -> None:
        """Shuffle the deck in place."""

        (rng or random).shuffle(self._cards)

    def deal(self, count: int) -> list[Card]:
        """Deal a number of cards from the top of the deck."""

        if count < 0:
            raise ValueError("count must be non-negative")
        if count > len(self._cards):
            raise ValueError("not enough cards remaining to deal")
        hand = self._cards[:count]
        self._cards = self._cards[count:]
        return hand

    def remaining(self) -> int:
        return len(self._cards)

    def __len__(self) -> int:
        return len(self._cards)
