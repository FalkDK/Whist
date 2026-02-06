"""Tests for Match (session.py)."""

import random

import pytest

from whist.cards import Suit
from whist.session import Match


class TestMatch:
    PLAYERS = ["North", "East", "South", "West"]

    def test_creation(self):
        match = Match(self.PLAYERS)
        assert match.total_score() == {"north_south": 0, "east_west": 0}
        assert match.games == []

    def test_requires_four_players(self):
        with pytest.raises(ValueError, match="four players"):
            Match(["A", "B"])

    def test_start_game(self):
        match = Match(self.PLAYERS)
        game = match.start_game(trump=Suit.CLUBS)
        assert game in match.games
        assert game.round.trump == Suit.CLUBS

    def test_record_game(self):
        rng = random.Random(42)
        match = Match(self.PLAYERS)
        game = match.start_game(trump=Suit.CLUBS)
        game.play_out(rng)
        result = match.record_game(game)
        assert "north_south" in result
        assert "east_west" in result

    def test_record_unknown_game_raises(self):
        from whist.match import Game
        rng = random.Random(42)
        match = Match(self.PLAYERS)
        other_game = Game(self.PLAYERS, trump=Suit.HEARTS)
        other_game.play_out(rng)
        with pytest.raises(ValueError, match="part of this match"):
            match.record_game(other_game)

    def test_total_score_accumulates(self):
        rng = random.Random(42)
        match = Match(self.PLAYERS)

        for i in range(3):
            game = match.start_game()
            game.play_out(random.Random(i))
            match.record_game(game)

        total = match.total_score()
        assert total["north_south"] >= 0
        assert total["east_west"] >= 0

    def test_multiple_games_are_tracked(self):
        match = Match(self.PLAYERS)
        g1 = match.start_game()
        g2 = match.start_game()
        assert len(match.games) == 2
        assert g1 in match.games
        assert g2 in match.games
