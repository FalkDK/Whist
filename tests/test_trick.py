"""Tests for trick resolution."""

import pytest

from whist.cards import BIG_JOKER, LITTLE_JOKER, Card, Direction, Rank, Suit
from whist.trick import Trick


class TestTrick:
    def test_initially_empty(self):
        trick = Trick()
        assert trick.lead_suit() is None
        assert not trick.is_complete()

    def test_lead_suit_from_first_non_joker(self):
        trick = Trick()
        trick.add_play("N", BIG_JOKER)
        trick.add_play("E", Card(Rank.ACE, Suit.HEARTS))
        assert trick.lead_suit() == Suit.HEARTS

    def test_lead_suit_all_jokers(self):
        trick = Trick()
        trick.add_play("N", BIG_JOKER)
        trick.add_play("E", LITTLE_JOKER)
        assert trick.lead_suit() is None

    def test_winner_no_trump_highest_lead_suit(self):
        trick = Trick()
        trick.add_play("N", Card(Rank.TWO, Suit.CLUBS))
        trick.add_play("E", Card(Rank.ACE, Suit.CLUBS))
        trick.add_play("S", Card(Rank.KING, Suit.CLUBS))
        trick.add_play("W", Card(Rank.QUEEN, Suit.CLUBS))
        assert trick.winner(trump=None) == "E"

    def test_winner_trump_beats_lead(self):
        trick = Trick()
        trick.add_play("N", Card(Rank.ACE, Suit.CLUBS))
        trick.add_play("E", Card(Rank.TWO, Suit.SPADES))
        trick.add_play("S", Card(Rank.KING, Suit.CLUBS))
        trick.add_play("W", Card(Rank.QUEEN, Suit.CLUBS))
        assert trick.winner(trump=Suit.SPADES) == "E"

    def test_winner_joker_beats_all_in_trump_game(self):
        trick = Trick()
        trick.add_play("N", Card(Rank.ACE, Suit.SPADES))
        trick.add_play("E", LITTLE_JOKER)
        trick.add_play("S", Card(Rank.KING, Suit.SPADES))
        trick.add_play("W", BIG_JOKER)
        assert trick.winner(trump=Suit.SPADES) == "W"

    def test_winner_joker_weakest_in_no_trump(self):
        trick = Trick()
        trick.add_play("N", BIG_JOKER)
        trick.add_play("E", Card(Rank.TWO, Suit.CLUBS))
        trick.add_play("S", Card(Rank.THREE, Suit.CLUBS))
        trick.add_play("W", Card(Rank.FOUR, Suit.CLUBS))
        assert trick.winner(trump=None) == "W"

    def test_winner_downtown_ranking(self):
        trick = Trick()
        trick.add_play("N", Card(Rank.KING, Suit.HEARTS))
        trick.add_play("E", Card(Rank.QUEEN, Suit.HEARTS))
        trick.add_play("S", Card(Rank.ACE, Suit.HEARTS))
        trick.add_play("W", Card(Rank.JACK, Suit.HEARTS))
        # Downtown: K > Q > J > ... > 2 > A (A is weakest)
        assert trick.winner(trump=None, direction=Direction.DOWNTOWN) == "N"

    def test_winner_off_suit_loses(self):
        trick = Trick()
        trick.add_play("N", Card(Rank.TWO, Suit.CLUBS))
        trick.add_play("E", Card(Rank.ACE, Suit.HEARTS))
        trick.add_play("S", Card(Rank.THREE, Suit.CLUBS))
        trick.add_play("W", Card(Rank.FOUR, Suit.CLUBS))
        assert trick.winner(trump=None) == "W"

    def test_duplicate_player_raises(self):
        trick = Trick()
        trick.add_play("N", Card(Rank.TWO, Suit.CLUBS))
        with pytest.raises(ValueError, match="already played"):
            trick.add_play("N", Card(Rank.THREE, Suit.CLUBS))

    def test_summary(self):
        trick = Trick()
        trick.add_play("N", Card(Rank.ACE, Suit.SPADES))
        trick.add_play("E", BIG_JOKER)
        result = trick.summary()
        assert result == [("N", "AS"), ("E", "BJ")]
