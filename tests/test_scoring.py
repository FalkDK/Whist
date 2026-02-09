"""Tests for scoring helpers."""

import pytest

from whist.bidding import Bid, BidType
from whist.scoring import Scoreboard, score_deal, tricks_to_points


class TestTricksToPoints:
    def test_six_tricks_gives_zero(self):
        assert tricks_to_points(6) == 0

    def test_seven_tricks_gives_one(self):
        assert tricks_to_points(7) == 1

    def test_thirteen_gives_seven(self):
        assert tricks_to_points(13) == 7

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            tricks_to_points(-1)


class TestScoreboard:
    PLAYERS = ["N", "E", "S", "W"]

    def test_initial_counts_zero(self):
        sb = Scoreboard(self.PLAYERS)
        assert all(v == 0 for v in sb.trick_counts.values())

    def test_record_and_partnership(self):
        sb = Scoreboard(self.PLAYERS)
        for _ in range(8):
            sb.record_trick("N")
        for _ in range(5):
            sb.record_trick("E")
        tricks = sb.partnership_tricks()
        assert tricks["north_south"] == 8
        assert tricks["east_west"] == 5

    def test_requires_four_players(self):
        with pytest.raises(ValueError):
            Scoreboard(["A", "B", "C"])


class TestScoreDeal:
    PLAYERS = ["N", "E", "S", "W"]

    def test_bid_made(self):
        bid = Bid(3, BidType.UPTOWN)
        # N/S won 10 tricks (4 points above book), E/W won 3
        result = score_deal(bid, "N", self.PLAYERS, {"north_south": 10, "east_west": 3})
        assert result["north_south"] == 4  # actual books taken
        assert result["east_west"] == 0

    def test_bid_set(self):
        bid = Bid(4, BidType.DOWNTOWN)
        # E bid 4 downtown, E/W only took 8 tricks (2 books, need 4)
        result = score_deal(bid, "E", self.PLAYERS, {"north_south": 5, "east_west": 8})
        assert result["east_west"] == -4  # set: lose bid amount
        assert result["north_south"] == 0  # opponents: max(0, 5-6) = 0

    def test_bid_set_opponents_score(self):
        bid = Bid(5, BidType.UPTOWN)
        # N bid 5, N/S only took 9 (3 books, need 5)
        # E/W took 4 (but that's tricks, not books)
        result = score_deal(bid, "N", self.PLAYERS, {"north_south": 9, "east_west": 4})
        assert result["north_south"] == -5
        assert result["east_west"] == 0  # max(0, 4-6) = 0
