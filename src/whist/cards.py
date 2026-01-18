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

    @classmethod
    def ordered(cls) -> list["Rank"]:
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
    def strength(cls, rank: "Rank") -> int:
        return cls.ordered().index(rank)


@dataclass(frozen=True)
class Card:
    """Immutable playing card value."""

    rank: Rank
    suit: Suit

    def label(self) -> str:
        return f"{self.rank.value}{self.suit.value[0].upper()}"
