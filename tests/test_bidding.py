"""Tests for the bidding module."""

import pytest

from whist.bidding import Bid, BidType, BiddingRound
from whist.cards import Direction


class TestBid:
    def test_valid_bid(self):
        bid = Bid(3, BidType.UPTOWN)
        assert bid.number == 3
        assert bid.bid_type == BidType.UPTOWN

    def test_invalid_bid_number(self):
        with pytest.raises(ValueError, match="3-7"):
            Bid(2, BidType.UPTOWN)
        with pytest.raises(ValueError, match="3-7"):
            Bid(8, BidType.UPTOWN)

    def test_outranks_higher_number(self):
        assert Bid(4, BidType.UPTOWN).outranks(Bid(3, BidType.UPTOWN))

    def test_outranks_same_number_type_order(self):
        # uptown < downtown < no_trump
        assert Bid(3, BidType.DOWNTOWN).outranks(Bid(3, BidType.UPTOWN))
        assert Bid(3, BidType.NO_TRUMP).outranks(Bid(3, BidType.DOWNTOWN))

    def test_direction_uptown(self):
        assert Bid(3, BidType.UPTOWN).direction == Direction.UPTOWN

    def test_direction_downtown(self):
        assert Bid(3, BidType.DOWNTOWN).direction == Direction.DOWNTOWN

    def test_direction_no_trump(self):
        # No trump defaults to uptown direction
        assert Bid(3, BidType.NO_TRUMP).direction == Direction.UPTOWN

    def test_has_trump(self):
        assert Bid(3, BidType.UPTOWN).has_trump
        assert Bid(3, BidType.DOWNTOWN).has_trump
        assert not Bid(3, BidType.NO_TRUMP).has_trump

    def test_is_boston(self):
        assert Bid(7, BidType.UPTOWN).is_boston
        assert not Bid(6, BidType.UPTOWN).is_boston


class TestBiddingRound:
    PLAYERS = ["N", "E", "S", "W"]

    def test_bidding_starts_left_of_dealer(self):
        br = BiddingRound(self.PLAYERS, dealer_index=0)
        assert br.expected_bidder == "E"

    def test_bidding_order_wraps(self):
        br = BiddingRound(self.PLAYERS, dealer_index=2)
        assert br.expected_bidder == "W"

    def test_all_pass_except_one(self):
        br = BiddingRound(self.PLAYERS, dealer_index=0)
        br.place_bid("E", Bid(3, BidType.UPTOWN))
        br.place_bid("S", None)
        br.place_bid("W", None)
        br.place_bid("N", None)
        assert br.is_complete
        assert br.winner == "E"
        assert br.winning_bid == Bid(3, BidType.UPTOWN)

    def test_dealer_forced_to_bid_when_all_pass(self):
        br = BiddingRound(self.PLAYERS, dealer_index=0)
        br.place_bid("E", None)
        br.place_bid("S", None)
        br.place_bid("W", None)
        with pytest.raises(ValueError, match="dealer must bid"):
            br.place_bid("N", None)

    def test_bid_must_outrank(self):
        br = BiddingRound(self.PLAYERS, dealer_index=0)
        br.place_bid("E", Bid(4, BidType.UPTOWN))
        with pytest.raises(ValueError, match="outrank"):
            br.place_bid("S", Bid(3, BidType.NO_TRUMP))

    def test_wrong_player_raises(self):
        br = BiddingRound(self.PLAYERS, dealer_index=0)
        with pytest.raises(ValueError, match="not this player"):
            br.place_bid("S", Bid(3, BidType.UPTOWN))

    def test_requires_four_players(self):
        with pytest.raises(ValueError):
            BiddingRound(["A", "B"], dealer_index=0)
