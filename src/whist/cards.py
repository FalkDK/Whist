"""Card primitives used by Whist."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Suit(str, Enum):
    """Standard playing card suits."""

    CLUBS = "clubs"
    DIAMONDS = "diamonds"
    HEARTS = "hearts"
    SPADES = "spades"
    JOKER = "joker"


class Rank(str, Enum):
    """Standard playing card ranks ordered low to high."""

    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"
    LITTLE_JOKER = "LJ"
    BIG_JOKER = "BJ"

    @classmethod
    def short_name(cls, rank: "Rank") -> str:
        return rank.value

    @classmethod
    def ordered(cls) -> list["Rank"]:
        """Standard uptown ordering (high wins)."""
        return [
            cls.TWO,
            cls.THREE,
            cls.FOUR,
            cls.FIVE,
            cls.SIX,
            cls.SEVEN,
            cls.EIGHT,
            cls.NINE,
            cls.TEN,
            cls.JACK,
            cls.QUEEN,
            cls.KING,
            cls.ACE,
        ]

    @classmethod
    def strength(cls, rank: "Rank", downtown: bool = False) -> int:
        """Return strength index. Higher = stronger.

        Uptown: 2 3 4 5 6 7 8 9 10 J Q K A  (A highest)
        Downtown: A 2 3 4 5 6 7 8 9 10 J Q K  (A lowest non-joker, K highest)
        Jokers are always strongest (little < big).
        """
        if rank == cls.BIG_JOKER:
            return 100
        if rank == cls.LITTLE_JOKER:
            return 99
        if downtown:
            downtown_order = [
                cls.ACE, cls.TWO, cls.THREE, cls.FOUR, cls.FIVE,
                cls.SIX, cls.SEVEN, cls.EIGHT, cls.NINE, cls.TEN,
                cls.JACK, cls.QUEEN, cls.KING,
            ]
            return downtown_order.index(rank)
        return cls.ordered().index(rank)


class Direction(str, Enum):
    """Bid direction controlling card rank ordering."""

    UPTOWN = "uptown"
    DOWNTOWN = "downtown"


@dataclass(frozen=True)
class Card:
    """Immutable playing card value."""

    rank: Rank
    suit: Suit

    @property
    def is_joker(self) -> bool:
        return self.rank in (Rank.BIG_JOKER, Rank.LITTLE_JOKER)

    def label(self) -> str:
        if self.is_joker:
            return self.rank.value
        return f"{self.rank.value}{self.suit.value[0].upper()}"

    def display(self) -> str:
        if self.is_joker:
            return "Big Joker" if self.rank == Rank.BIG_JOKER else "Little Joker"
        return f"{self.rank.value} of {self.suit.value}"


BIG_JOKER = Card(rank=Rank.BIG_JOKER, suit=Suit.JOKER)
LITTLE_JOKER = Card(rank=Rank.LITTLE_JOKER, suit=Suit.JOKER)
