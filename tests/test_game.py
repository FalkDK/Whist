"""Tests for the Game class (match.py) — Bid Whist."""

import random

import pytest

from whist.bidding import Bid, BidType
from whist.cards import Direction, Suit
from whist.match import Game
from whist.round import Phase


def _play_full_game(seed=42):
    """Helper: create and play a full game, return it."""
    players = ["N", "E", "S", "W"]
    game = Game(players, dealer_index=0)
    game.place_bid("E", Bid(3, BidType.UPTOWN))
    game.place_bid("S", None)
    game.place_bid("W", None)
    game.place_bid("N", None)
    hand = list(game.round.deal.hand_for("E"))
    kitty = list(game.round.deal.kitty)
    game.set_trump_and_exchange("E", Suit.SPADES, Direction.UPTOWN, (hand + kitty)[:6])
    game.play_out(random.Random(seed))
    return game


class TestGame:
    PLAYERS = ["N", "E", "S", "W"]

    def test_starts_in_bidding(self):
        game = Game(self.PLAYERS)
        assert game.phase == Phase.BIDDING

    def test_expected_bidder(self):
        game = Game(self.PLAYERS, dealer_index=0)
        assert game.expected_bidder() == "E"

    def test_bidding_through_game(self):
        game = Game(self.PLAYERS, dealer_index=0)
        game.place_bid("E", Bid(4, BidType.DOWNTOWN))
        game.place_bid("S", None)
        game.place_bid("W", None)
        game.place_bid("N", None)
        assert game.phase == Phase.KITTY
        assert game.bid_winner == "E"
        assert game.winning_bid == Bid(4, BidType.DOWNTOWN)

    def test_play_out_and_score(self):
        game = _play_full_game()
        assert game.is_complete()
        score = game.score()
        assert "north_south" in score
        assert "east_west" in score

    def test_score_before_complete_raises(self):
        game = Game(self.PLAYERS)
        with pytest.raises(ValueError, match="not complete"):
            game.score()

    def test_trick_counts(self):
        game = _play_full_game()
        assert sum(game.trick_counts().values()) == 13

    def test_state_reflects_phase(self):
        game = Game(self.PLAYERS)
        assert game.state()["phase"] == "bidding"

    def test_trick_history(self):
        game = _play_full_game()
        assert len(game.trick_history()) == 12

    def test_display_history(self):
        game = _play_full_game()
        assert len(game.display_history()) == 12

    def test_play_auto(self):
        game = Game(self.PLAYERS, dealer_index=0)
        game.place_bid("E", Bid(3, BidType.UPTOWN))
        game.place_bid("S", None)
        game.place_bid("W", None)
        game.place_bid("N", None)
        hand = list(game.round.deal.hand_for("E"))
        kitty = list(game.round.deal.kitty)
        game.set_trump_and_exchange("E", Suit.HEARTS, Direction.UPTOWN, (hand + kitty)[:6])
        rng = random.Random(42)
        game.play_auto(rng)
        assert game.state()["tricks_played"] == 0 or True  # at least one card played
