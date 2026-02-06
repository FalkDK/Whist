"""Tests for the Game class (match.py)."""

import random

import pytest

from whist.cards import Suit
from whist.match import Game


class TestGame:
    PLAYERS = ["North", "East", "South", "West"]

    def test_creation(self):
        game = Game(self.PLAYERS, trump=Suit.SPADES)
        assert game.round.trump == Suit.SPADES
        assert not game.is_complete()

    def test_trump_defaults_from_deal(self):
        game = Game(self.PLAYERS)
        assert game.round.trump is not None

    def test_expected_player(self):
        game = Game(self.PLAYERS)
        assert game.expected_player() == "North"

    def test_play_card(self):
        game = Game(self.PLAYERS)
        player = game.expected_player()
        hand = list(game.round.deal.hand_for(player))
        game.play(player, hand[0])
        assert game.expected_player() != player

    def test_play_auto(self):
        rng = random.Random(42)
        game = Game(self.PLAYERS)
        game.play_auto(rng)
        assert game.expected_player() == "East"

    def test_play_out_and_score(self):
        rng = random.Random(42)
        game = Game(self.PLAYERS)
        game.play_out(rng)
        assert game.is_complete()
        score = game.score()
        assert "north_south" in score
        assert "east_west" in score

    def test_score_before_complete_raises(self):
        game = Game(self.PLAYERS)
        with pytest.raises(ValueError, match="not complete"):
            game.score()

    def test_play_trick(self):
        game = Game(self.PLAYERS)
        leader = game.expected_player()
        leader_hand = list(game.round.deal.hand_for(leader))
        lead_card = leader_hand[0]
        lead_suit = lead_card.suit
        plays = {leader: lead_card}
        order = self.PLAYERS[self.PLAYERS.index(leader) + 1:] + self.PLAYERS[:self.PLAYERS.index(leader)]
        for player in order:
            hand = list(game.round.deal.hand_for(player))
            suited = [c for c in hand if c.suit == lead_suit]
            plays[player] = suited[0] if suited else hand[0]
        winner = game.play_trick(plays)
        assert winner in self.PLAYERS

    def test_state(self):
        game = Game(self.PLAYERS)
        state = game.state()
        assert state["tricks_played"] == 0

    def test_trick_history(self):
        rng = random.Random(42)
        game = Game(self.PLAYERS)
        game.play_out(rng)
        history = game.trick_history()
        assert len(history) == 13

    def test_display_history(self):
        rng = random.Random(42)
        game = Game(self.PLAYERS)
        game.play_out(rng)
        display = game.display_history()
        assert len(display) == 13

    def test_trick_counts(self):
        rng = random.Random(42)
        game = Game(self.PLAYERS)
        game.play_out(rng)
        counts = game.trick_counts()
        assert sum(counts.values()) == 13
