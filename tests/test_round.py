"""Tests for round management — Bid Whist."""

import random

import pytest

from whist.bidding import Bid, BidType
from whist.cards import Direction, Suit
from whist.round import Phase, Round, TRICKS_PER_DEAL


def _setup_round_to_playing(players, dealer_index=0, rng_seed=42):
    """Helper: create a round, complete bidding and kitty, return it in PLAYING phase."""
    r = Round(players, dealer_index=dealer_index)
    # Left of dealer bids 3 uptown, everyone else passes
    order = [(dealer_index + 1 + i) % 4 for i in range(4)]
    bidder = players[order[0]]
    for i, idx in enumerate(order):
        p = players[idx]
        if i == 0:
            r.place_bid(p, Bid(3, BidType.UPTOWN))
        else:
            r.place_bid(p, None)
    # Exchange kitty
    hand = list(r.deal.hand_for(bidder))
    kitty = list(r.deal.kitty)
    discards = (hand + kitty)[:6]
    r.set_trump_and_exchange(bidder, Suit.HEARTS, Direction.UPTOWN, discards)
    return r


class TestRoundBidding:
    PLAYERS = ["N", "E", "S", "W"]

    def test_starts_in_bidding_phase(self):
        r = Round(self.PLAYERS)
        assert r.phase == Phase.BIDDING

    def test_bidding_advances_to_kitty(self):
        r = Round(self.PLAYERS, dealer_index=0)
        r.place_bid("E", Bid(3, BidType.UPTOWN))
        r.place_bid("S", None)
        r.place_bid("W", None)
        r.place_bid("N", None)
        assert r.phase == Phase.KITTY
        assert r.bid_winner == "E"


class TestRoundKitty:
    PLAYERS = ["N", "E", "S", "W"]

    def test_kitty_exchange_to_playing(self):
        r = Round(self.PLAYERS, dealer_index=0)
        r.place_bid("E", Bid(3, BidType.UPTOWN))
        r.place_bid("S", None)
        r.place_bid("W", None)
        r.place_bid("N", None)
        hand = list(r.deal.hand_for("E"))
        kitty = list(r.deal.kitty)
        r.set_trump_and_exchange("E", Suit.SPADES, Direction.UPTOWN, (hand + kitty)[:6])
        assert r.phase == Phase.PLAYING
        assert r.trump == Suit.SPADES

    def test_wrong_player_cannot_exchange(self):
        r = Round(self.PLAYERS, dealer_index=0)
        r.place_bid("E", Bid(3, BidType.UPTOWN))
        r.place_bid("S", None)
        r.place_bid("W", None)
        r.place_bid("N", None)
        with pytest.raises(ValueError, match="bid winner"):
            r.set_trump_and_exchange("N", Suit.SPADES, Direction.UPTOWN, [])


class TestRoundPlaying:
    PLAYERS = ["N", "E", "S", "W"]

    def test_play_out_completes(self):
        r = _setup_round_to_playing(self.PLAYERS)
        r.play_out(random.Random(42))
        assert r.is_complete()
        assert r.phase == Phase.COMPLETE
        assert len(r.completed_tricks) == TRICKS_PER_DEAL

    def test_trick_counts_sum_to_13(self):
        r = _setup_round_to_playing(self.PLAYERS)
        r.play_out(random.Random(42))
        # 12 tricks + 1 kitty bonus = 13 total books
        assert sum(r.trick_counts().values()) == 13

    def test_play_out_of_turn_raises(self):
        r = _setup_round_to_playing(self.PLAYERS)
        expected = r.expected_player()
        other = [p for p in self.PLAYERS if p != expected][0]
        card = list(r.deal.hand_for(other))[0]
        with pytest.raises(ValueError, match="turn order"):
            r.play(other, card)

    def test_score_returns_bid_whist_scoring(self):
        r = _setup_round_to_playing(self.PLAYERS)
        r.play_out(random.Random(42))
        score = r.score()
        assert "north_south" in score
        assert "east_west" in score

    def test_state_snapshot(self):
        r = _setup_round_to_playing(self.PLAYERS)
        state = r.state()
        assert state["phase"] == "playing"
        assert state["trump"] == Suit.HEARTS
        assert state["bid_winner"] is not None

    def test_trick_history(self):
        r = _setup_round_to_playing(self.PLAYERS)
        r.play_out(random.Random(42))
        history = r.trick_history()
        assert len(history) == TRICKS_PER_DEAL

    def test_display_history(self):
        r = _setup_round_to_playing(self.PLAYERS)
        r.play_out(random.Random(42))
        display = r.display_history()
        assert len(display) == TRICKS_PER_DEAL
        assert display[0].startswith("1.")
