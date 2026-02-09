"""Deck operations for Whist."""

from __future__ import annotations

import random
from collections.abc import Iterable

from .cards import Card, Rank, Suit, BIG_JOKER, LITTLE_JOKER


class Deck:
    """Represents a standard 52 or 54-card deck."""

    def __init__(self, cards: Iterable[Card] | None = None, *, jokers: bool = False) -> None:
        self._cards = list(cards) if cards is not None else self._standard_cards(jokers=jokers)

    @staticmethod
    def _standard_cards(jokers: bool = False) -> list[Card]:
        suits = [s for s in Suit if s != Suit.JOKER]
        ranks = [r for r in Rank if r not in (Rank.BIG_JOKER, Rank.LITTLE_JOKER)]
        cards = [Card(rank=rank, suit=suit) for suit in suits for rank in ranks]
        if jokers:
            cards.extend([BIG_JOKER, LITTLE_JOKER])
        return cards

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
