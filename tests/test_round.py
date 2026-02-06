"""Tests for round management."""

import random

import pytest

from whist.cards import Suit
from whist.round import Round, TRICKS_PER_DEAL


class TestRound:
    PLAYERS = ["North", "East", "South", "West"]

    def test_initial_state(self):
        r = Round(self.PLAYERS, trump=Suit.HEARTS)
        assert r.trump == Suit.HEARTS
        assert not r.is_complete()
        assert r.expected_player() == "North"
        assert len(r.completed_tricks) == 0

    def test_trump_defaults_from_deal(self):
        r = Round(self.PLAYERS)
        assert r.trump is not None

    def test_play_advances_expected_player(self):
        r = Round(self.PLAYERS, trump=Suit.HEARTS)
        assert r.expected_player() == "North"
        card = list(r.deal.hand_for("North"))[0]
        r.play("North", card)
        assert r.expected_player() == "East"

    def test_play_out_of_turn_raises(self):
        r = Round(self.PLAYERS, trump=Suit.HEARTS)
        card = list(r.deal.hand_for("East"))[0]
        with pytest.raises(ValueError, match="turn order"):
            r.play("East", card)

    def test_play_auto_plays_legal_card(self):
        rng = random.Random(42)
        r = Round(self.PLAYERS, trump=Suit.HEARTS)
        player_before = r.expected_player()
        r.play_auto(rng)
        assert r.expected_player() != player_before

    def test_play_out_completes_round(self):
        rng = random.Random(42)
        r = Round(self.PLAYERS, trump=Suit.HEARTS)
        r.play_out(rng)
        assert r.is_complete()
        assert len(r.completed_tricks) == TRICKS_PER_DEAL

    def test_play_on_complete_round_raises(self):
        rng = random.Random(42)
        r = Round(self.PLAYERS, trump=Suit.HEARTS)
        r.play_out(rng)
        with pytest.raises(ValueError, match="already complete"):
            player = r.expected_player()
            card = list(r.deal.hand_for(player))[0] if list(r.deal.hand_for(player)) else None
            r.play(player, card)

    def test_score_after_completion(self):
        rng = random.Random(42)
        r = Round(self.PLAYERS, trump=Suit.HEARTS)
        r.play_out(rng)
        score = r.score()
        assert "north_south" in score
        assert "east_west" in score
        total_points = score["north_south"] + score["east_west"]
        # Total tricks = 13; points = tricks - 6 for each side; max total = 13 - 12 = 1
        # Actually total points can vary: e.g. 8-5 => 2+0=2, 7-6 => 1+0=1
        assert total_points >= 0

    def test_trick_counts_sum_to_13(self):
        rng = random.Random(42)
        r = Round(self.PLAYERS, trump=Suit.HEARTS)
        r.play_out(rng)
        counts = r.trick_counts()
        assert sum(counts.values()) == 13

    def test_play_trick_plays_full_trick(self):
        r = Round(self.PLAYERS, trump=Suit.HEARTS)
        # Build plays dict: leader plays first card, others follow suit
        leader = r.expected_player()
        leader_hand = list(r.deal.hand_for(leader))
        lead_card = leader_hand[0]
        lead_suit = lead_card.suit
        plays = {leader: lead_card}
        order = self.PLAYERS[self.PLAYERS.index(leader) + 1:] + self.PLAYERS[:self.PLAYERS.index(leader)]
        for player in order:
            hand = list(r.deal.hand_for(player))
            suited = [c for c in hand if c.suit == lead_suit]
            plays[player] = suited[0] if suited else hand[0]
        winner = r.play_trick(plays)
        assert winner in self.PLAYERS
        assert len(r.completed_tricks) == 1

    def test_state_snapshot(self):
        r = Round(self.PLAYERS, trump=Suit.HEARTS)
        state = r.state()
        assert state["leader"] == "North"
        assert state["next_player"] == "North"
        assert state["tricks_played"] == 0
        assert state["tricks_remaining"] == 13
        assert state["trump"] == Suit.HEARTS

    def test_trick_history_after_play_out(self):
        rng = random.Random(42)
        r = Round(self.PLAYERS, trump=Suit.HEARTS)
        r.play_out(rng)
        history = r.trick_history()
        assert len(history) == 13
        for entry in history:
            assert "winner" in entry
            assert "plays" in entry
            assert len(entry["plays"]) == 4

    def test_display_history(self):
        rng = random.Random(42)
        r = Round(self.PLAYERS, trump=Suit.HEARTS)
        r.play_out(rng)
        display = r.display_history()
        assert len(display) == 13
        assert display[0].startswith("1.")
