"""Tests for card primitives."""

import pytest

from whist.cards import BIG_JOKER, LITTLE_JOKER, Card, Direction, Rank, Suit


class TestSuit:
    def test_suits_have_five_members(self):
        assert len(Suit) == 5

    def test_standard_suit_values(self):
        assert Suit.CLUBS.value == "clubs"
        assert Suit.SPADES.value == "spades"
        assert Suit.JOKER.value == "joker"


class TestRank:
    def test_ordered_returns_thirteen(self):
        assert len(Rank.ordered()) == 13

    def test_uptown_strength(self):
        assert Rank.strength(Rank.TWO) < Rank.strength(Rank.ACE)

    def test_downtown_strength(self):
        assert Rank.strength(Rank.ACE, downtown=True) < Rank.strength(Rank.TWO, downtown=True)
        assert Rank.strength(Rank.QUEEN, downtown=True) < Rank.strength(Rank.KING, downtown=True)

    def test_joker_strength_always_highest(self):
        assert Rank.strength(Rank.BIG_JOKER) > Rank.strength(Rank.ACE)
        assert Rank.strength(Rank.BIG_JOKER) > Rank.strength(Rank.LITTLE_JOKER)
        assert Rank.strength(Rank.BIG_JOKER, downtown=True) > Rank.strength(Rank.KING, downtown=True)


class TestCard:
    def test_immutable(self):
        card = Card(rank=Rank.ACE, suit=Suit.SPADES)
        with pytest.raises(AttributeError):
            card.rank = Rank.KING

    def test_label(self):
        assert Card(Rank.ACE, Suit.SPADES).label() == "AS"

    def test_joker_label(self):
        assert BIG_JOKER.label() == "BJ"
        assert LITTLE_JOKER.label() == "LJ"

    def test_joker_display(self):
        assert BIG_JOKER.display() == "Big Joker"

    def test_is_joker(self):
        assert BIG_JOKER.is_joker
        assert not Card(Rank.ACE, Suit.SPADES).is_joker

    def test_equality(self):
        assert Card(Rank.FIVE, Suit.CLUBS) == Card(Rank.FIVE, Suit.CLUBS)

    def test_hashable(self):
        assert len({BIG_JOKER, BIG_JOKER}) == 1


class TestDirection:
    def test_values(self):
        assert Direction.UPTOWN.value == "uptown"
        assert Direction.DOWNTOWN.value == "downtown"
