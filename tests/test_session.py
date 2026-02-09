"""Tests for Match (session.py) — Bid Whist."""

import random

import pytest

from whist.bidding import Bid, BidType
from whist.cards import Direction, Suit
from whist.scoring import GAME_TARGET
from whist.session import Match


def _play_deal(match, rng_seed=0):
    """Helper: start a game in the match, bid, exchange, play out, record it."""
    game = match.start_game()
    di = game.dealer_index
    players = game.players
    order = [(di + 1 + i) % 4 for i in range(4)]
    bidder = players[order[0]]

    for i, idx in enumerate(order):
        p = players[idx]
        if i == 0:
            game.place_bid(p, Bid(3, BidType.UPTOWN))
        else:
            game.place_bid(p, None)

    hand = list(game.round.deal.hand_for(bidder))
    kitty = list(game.round.deal.kitty)
    game.set_trump_and_exchange(bidder, Suit.HEARTS, Direction.UPTOWN, (hand + kitty)[:6])
    game.play_out(random.Random(rng_seed))
    return match.record_game(game)


class TestMatch:
    PLAYERS = ["N", "E", "S", "W"]

    def test_creation(self):
        match = Match(self.PLAYERS)
        assert match.total_score() == {"north_south": 0, "east_west": 0}
        assert match.games == []

    def test_requires_four_players(self):
        with pytest.raises(ValueError, match="four players"):
            Match(["A", "B"])

    def test_start_game(self):
        match = Match(self.PLAYERS)
        game = match.start_game()
        assert game in match.games

    def test_dealer_rotates(self):
        match = Match(self.PLAYERS)
        g1 = match.start_game()
        assert g1.dealer_index == 0
        _play_deal(match)  # this starts a new game internally, so use record on g1
        # Actually, _play_deal starts a new game. Let's test differently:
        match2 = Match(self.PLAYERS)
        _play_deal(match2, rng_seed=1)
        g2 = match2.start_game()
        assert g2.dealer_index == 1  # rotated after first deal

    def test_score_accumulates(self):
        match = Match(self.PLAYERS)
        result = _play_deal(match, rng_seed=42)
        assert "north_south" in result
        assert "east_west" in result
        total = match.total_score()
        assert total["north_south"] == result["north_south"]
        assert total["east_west"] == result["east_west"]

    def test_record_unknown_game_raises(self):
        from whist.match import Game

        match = Match(self.PLAYERS)
        other_game = Game(self.PLAYERS, dealer_index=0)
        with pytest.raises(ValueError, match="part of this match"):
            match.record_game(other_game)

    def test_is_over_not_initially(self):
        match = Match(self.PLAYERS)
        assert not match.is_over

    def test_winner_none_when_not_over(self):
        match = Match(self.PLAYERS)
        assert match.winner is None

    def test_is_over_at_positive_target(self):
        match = Match(self.PLAYERS)
        match.scores["north_south"] = GAME_TARGET
        assert match.is_over
        assert match.winner == "north_south"

    def test_is_over_at_negative_target(self):
        match = Match(self.PLAYERS)
        match.scores["east_west"] = -GAME_TARGET
        assert match.is_over
        assert match.winner == "north_south"  # opponents win

    def test_multiple_deals(self):
        match = Match(self.PLAYERS)
        for i in range(3):
            _play_deal(match, rng_seed=i)
        assert len(match.games) == 3
        total = match.total_score()
        assert isinstance(total["north_south"], int)
        assert isinstance(total["east_west"], int)
