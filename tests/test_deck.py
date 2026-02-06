"""Tests for deck operations."""

import random

import pytest

from whist.cards import Card, Rank, Suit
from whist.deck import Deck


class TestDeck:
    def test_standard_deck_has_52_cards(self):
        deck = Deck()
        assert len(deck) == 52

    def test_remaining_matches_len(self):
        deck = Deck()
        assert deck.remaining() == len(deck) == 52

    def test_deal_removes_cards(self):
        deck = Deck()
        hand = deck.deal(5)
        assert len(hand) == 5
        assert deck.remaining() == 47

    def test_deal_returns_cards_from_top(self):
        cards = [Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS)]
        deck = Deck(cards)
        hand = deck.deal(1)
        assert hand == [Card(Rank.ACE, Suit.SPADES)]

    def test_deal_negative_count_raises(self):
        deck = Deck()
        with pytest.raises(ValueError, match="non-negative"):
            deck.deal(-1)

    def test_deal_more_than_remaining_raises(self):
        deck = Deck()
        with pytest.raises(ValueError, match="not enough cards"):
            deck.deal(53)

    def test_shuffle_changes_order(self):
        deck1 = Deck()
        deck2 = Deck()
        rng = random.Random(42)
        deck2.shuffle(rng)
        # Deal all cards from both and compare order
        hand1 = deck1.deal(52)
        hand2 = deck2.deal(52)
        assert hand1 != hand2

    def test_shuffle_with_seeded_rng_is_deterministic(self):
        deck1 = Deck()
        deck2 = Deck()
        deck1.shuffle(random.Random(99))
        deck2.shuffle(random.Random(99))
        assert deck1.deal(52) == deck2.deal(52)

    def test_custom_cards(self):
        cards = [Card(Rank.TWO, Suit.CLUBS), Card(Rank.THREE, Suit.DIAMONDS)]
        deck = Deck(cards)
        assert len(deck) == 2

    def test_deal_zero_cards(self):
        deck = Deck()
        hand = deck.deal(0)
        assert hand == []
        assert deck.remaining() == 52

    def test_all_52_cards_are_unique(self):
        deck = Deck()
        cards = deck.deal(52)
        assert len(set(cards)) == 52
