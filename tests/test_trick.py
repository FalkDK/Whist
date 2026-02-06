"""Tests for trick resolution."""

import pytest

from whist.cards import Card, Rank, Suit
from whist.trick import Trick


class TestTrick:
    def test_initially_empty(self):
        trick = Trick()
        assert trick.plays == []
        assert trick.lead_suit() is None
        assert not trick.is_complete()

    def test_add_play(self):
        trick = Trick()
        card = Card(Rank.ACE, Suit.SPADES)
        trick.add_play("North", card)
        assert len(trick.plays) == 1
        assert trick.lead_suit() == Suit.SPADES

    def test_lead_suit_is_first_card(self):
        trick = Trick()
        trick.add_play("North", Card(Rank.ACE, Suit.HEARTS))
        trick.add_play("East", Card(Rank.KING, Suit.SPADES))
        assert trick.lead_suit() == Suit.HEARTS

    def test_is_complete_after_four_plays(self):
        trick = Trick()
        trick.add_play("North", Card(Rank.TWO, Suit.CLUBS))
        trick.add_play("East", Card(Rank.THREE, Suit.CLUBS))
        trick.add_play("South", Card(Rank.FOUR, Suit.CLUBS))
        trick.add_play("West", Card(Rank.FIVE, Suit.CLUBS))
        assert trick.is_complete()

    def test_cannot_exceed_max_plays(self):
        trick = Trick()
        trick.add_play("North", Card(Rank.TWO, Suit.CLUBS))
        trick.add_play("East", Card(Rank.THREE, Suit.CLUBS))
        trick.add_play("South", Card(Rank.FOUR, Suit.CLUBS))
        trick.add_play("West", Card(Rank.FIVE, Suit.CLUBS))
        with pytest.raises(ValueError, match="maximum plays"):
            trick.add_play("Extra", Card(Rank.SIX, Suit.CLUBS))

    def test_duplicate_player_raises(self):
        trick = Trick()
        trick.add_play("North", Card(Rank.TWO, Suit.CLUBS))
        with pytest.raises(ValueError, match="already played"):
            trick.add_play("North", Card(Rank.THREE, Suit.CLUBS))

    def test_winner_no_trump_highest_lead_suit_wins(self):
        trick = Trick()
        trick.add_play("North", Card(Rank.TWO, Suit.CLUBS))
        trick.add_play("East", Card(Rank.ACE, Suit.CLUBS))
        trick.add_play("South", Card(Rank.KING, Suit.CLUBS))
        trick.add_play("West", Card(Rank.QUEEN, Suit.CLUBS))
        assert trick.winner(trump=None) == "East"

    def test_winner_off_suit_cards_lose(self):
        trick = Trick()
        trick.add_play("North", Card(Rank.TWO, Suit.CLUBS))
        trick.add_play("East", Card(Rank.ACE, Suit.HEARTS))  # off-suit
        trick.add_play("South", Card(Rank.THREE, Suit.CLUBS))
        trick.add_play("West", Card(Rank.FOUR, Suit.CLUBS))
        assert trick.winner(trump=None) == "West"

    def test_winner_trump_beats_lead_suit(self):
        trick = Trick()
        trick.add_play("North", Card(Rank.ACE, Suit.CLUBS))
        trick.add_play("East", Card(Rank.TWO, Suit.SPADES))  # trump
        trick.add_play("South", Card(Rank.KING, Suit.CLUBS))
        trick.add_play("West", Card(Rank.QUEEN, Suit.CLUBS))
        assert trick.winner(trump=Suit.SPADES) == "East"

    def test_winner_highest_trump_wins(self):
        trick = Trick()
        trick.add_play("North", Card(Rank.ACE, Suit.CLUBS))
        trick.add_play("East", Card(Rank.TWO, Suit.SPADES))
        trick.add_play("South", Card(Rank.KING, Suit.SPADES))
        trick.add_play("West", Card(Rank.QUEEN, Suit.CLUBS))
        assert trick.winner(trump=Suit.SPADES) == "South"

    def test_winner_returns_none_when_empty(self):
        trick = Trick()
        assert trick.winner() is None

    def test_summary(self):
        trick = Trick()
        trick.add_play("North", Card(Rank.ACE, Suit.SPADES))
        trick.add_play("East", Card(Rank.KING, Suit.HEARTS))
        result = trick.summary()
        assert result == [("North", "AS"), ("East", "KH")]
