"""Tests for deck operations."""

import random

import pytest

from whist.cards import BIG_JOKER, LITTLE_JOKER, Rank, Suit
from whist.deck import Deck


class TestDeck:
    def test_standard_deck_has_52_cards(self):
        assert len(Deck()) == 52

    def test_joker_deck_has_54_cards(self):
        assert len(Deck(jokers=True)) == 54

    def test_joker_deck_contains_jokers(self):
        deck = Deck(jokers=True)
        cards = deck.deal(54)
        assert BIG_JOKER in cards
        assert LITTLE_JOKER in cards

    def test_standard_deck_no_jokers(self):
        deck = Deck()
        cards = deck.deal(52)
        assert BIG_JOKER not in cards

    def test_deal_removes_cards(self):
        deck = Deck()
        deck.deal(5)
        assert deck.remaining() == 47

    def test_deal_negative_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            Deck().deal(-1)

    def test_deal_too_many_raises(self):
        with pytest.raises(ValueError, match="not enough"):
            Deck().deal(53)

    def test_shuffle_deterministic(self):
        d1, d2 = Deck(jokers=True), Deck(jokers=True)
        d1.shuffle(random.Random(99))
        d2.shuffle(random.Random(99))
        assert d1.deal(54) == d2.deal(54)

    def test_no_joker_suits_in_standard_deck(self):
        deck = Deck()
        cards = deck.deal(52)
        assert all(c.suit != Suit.JOKER for c in cards)
        assert all(c.rank not in (Rank.BIG_JOKER, Rank.LITTLE_JOKER) for c in cards)
