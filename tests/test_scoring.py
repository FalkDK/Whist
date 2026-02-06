"""Tests for scoring helpers."""

import pytest

from whist.scoring import Scoreboard, tricks_to_points


class TestTricksToPoints:
    def test_zero_tricks(self):
        assert tricks_to_points(0) == 0

    def test_six_tricks_gives_zero_points(self):
        assert tricks_to_points(6) == 0

    def test_seven_tricks_gives_one_point(self):
        assert tricks_to_points(7) == 1

    def test_thirteen_tricks_gives_seven_points(self):
        assert tricks_to_points(13) == 7

    def test_negative_tricks_raises(self):
        with pytest.raises(ValueError, match="non-negative"):
            tricks_to_points(-1)


class TestScoreboard:
    PLAYERS = ["North", "East", "South", "West"]

    def test_initial_trick_counts_are_zero(self):
        sb = Scoreboard(self.PLAYERS)
        assert all(count == 0 for count in sb.trick_counts.values())

    def test_record_trick(self):
        sb = Scoreboard(self.PLAYERS)
        sb.record_trick("North")
        assert sb.trick_counts["North"] == 1

    def test_record_trick_unknown_player_raises(self):
        sb = Scoreboard(self.PLAYERS)
        with pytest.raises(ValueError, match="registered player"):
            sb.record_trick("Unknown")

    def test_partnership_tricks(self):
        sb = Scoreboard(self.PLAYERS)
        for _ in range(5):
            sb.record_trick("North")
        for _ in range(3):
            sb.record_trick("South")
        for _ in range(3):
            sb.record_trick("East")
        for _ in range(2):
            sb.record_trick("West")
        tricks = sb.partnership_tricks()
        assert tricks["north_south"] == 8
        assert tricks["east_west"] == 5

    def test_partnership_points(self):
        sb = Scoreboard(self.PLAYERS)
        for _ in range(5):
            sb.record_trick("North")
        for _ in range(3):
            sb.record_trick("South")
        for _ in range(3):
            sb.record_trick("East")
        for _ in range(2):
            sb.record_trick("West")
        points = sb.partnership_points()
        assert points["north_south"] == 2  # 8 - 6
        assert points["east_west"] == 0    # 5 - 6 = 0 (clamped)

    def test_requires_four_players(self):
        with pytest.raises(ValueError, match="four players"):
            Scoreboard(["A", "B", "C"])
