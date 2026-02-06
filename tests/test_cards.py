"""Tests for card primitives."""

import pytest

from whist.cards import Card, Rank, Suit


class TestSuit:
    def test_suits_have_four_members(self):
        assert len(Suit) == 4

    def test_suit_values(self):
        assert Suit.CLUBS.value == "clubs"
        assert Suit.DIAMONDS.value == "diamonds"
        assert Suit.HEARTS.value == "hearts"
        assert Suit.SPADES.value == "spades"


class TestRank:
    def test_ranks_have_thirteen_members(self):
        assert len(Rank) == 13

    def test_ordered_returns_all_ranks_low_to_high(self):
        ordered = Rank.ordered()
        assert len(ordered) == 13
        assert ordered[0] == Rank.TWO
        assert ordered[-1] == Rank.ACE

    def test_strength_increases_from_two_to_ace(self):
        assert Rank.strength(Rank.TWO) < Rank.strength(Rank.ACE)
        assert Rank.strength(Rank.JACK) < Rank.strength(Rank.QUEEN)
        assert Rank.strength(Rank.QUEEN) < Rank.strength(Rank.KING)
        assert Rank.strength(Rank.KING) < Rank.strength(Rank.ACE)

    def test_short_name(self):
        assert Rank.short_name(Rank.ACE) == "A"
        assert Rank.short_name(Rank.TEN) == "10"
        assert Rank.short_name(Rank.TWO) == "2"


class TestCard:
    def test_card_is_immutable(self):
        card = Card(rank=Rank.ACE, suit=Suit.SPADES)
        with pytest.raises(AttributeError):
            card.rank = Rank.KING

    def test_label(self):
        card = Card(rank=Rank.ACE, suit=Suit.SPADES)
        assert card.label() == "AS"

    def test_display(self):
        card = Card(rank=Rank.QUEEN, suit=Suit.HEARTS)
        assert card.display() == "Q of hearts"

    def test_equality(self):
        a = Card(rank=Rank.FIVE, suit=Suit.CLUBS)
        b = Card(rank=Rank.FIVE, suit=Suit.CLUBS)
        assert a == b

    def test_inequality(self):
        a = Card(rank=Rank.FIVE, suit=Suit.CLUBS)
        b = Card(rank=Rank.SIX, suit=Suit.CLUBS)
        assert a != b

    def test_card_is_hashable(self):
        card = Card(rank=Rank.ACE, suit=Suit.SPADES)
        assert isinstance(hash(card), int)
        s = {card, card}
        assert len(s) == 1
