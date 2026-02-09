"""Tests for deal handling (game.py) — Bid Whist."""

import pytest

from whist.cards import Card, Direction, Rank, Suit
from whist.game import CARDS_PER_HAND, KITTY_SIZE, Deal
from whist.trick import Trick


class TestDeal:
    PLAYERS = ["N", "E", "S", "W"]

    def test_deals_12_cards_each(self):
        deal = Deal(self.PLAYERS)
        for p in self.PLAYERS:
            assert len(list(deal.hand_for(p))) == CARDS_PER_HAND

    def test_kitty_has_6_cards(self):
        deal = Deal(self.PLAYERS)
        assert len(deal.kitty) == KITTY_SIZE

    def test_all_54_cards_distributed(self):
        deal = Deal(self.PLAYERS)
        all_cards = []
        for p in self.PLAYERS:
            all_cards.extend(deal.hand_for(p))
        all_cards.extend(deal.kitty)
        assert len(all_cards) == 54
        assert len(set(all_cards)) == 54

    def test_requires_four_players(self):
        with pytest.raises(ValueError):
            Deal(["A", "B"])

    def test_exchange_kitty(self):
        deal = Deal(self.PLAYERS)
        hand_before = list(deal.hand_for("N"))
        kitty = list(deal.kitty)
        merged = hand_before + kitty
        discards = merged[:6]
        deal.exchange_kitty("N", discards)
        assert len(list(deal.hand_for("N"))) == CARDS_PER_HAND

    def test_exchange_kitty_wrong_count_raises(self):
        deal = Deal(self.PLAYERS)
        with pytest.raises(ValueError, match="exactly"):
            deal.exchange_kitty("N", [])

    def test_exchange_kitty_twice_raises(self):
        deal = Deal(self.PLAYERS)
        hand = list(deal.hand_for("N"))
        kitty = list(deal.kitty)
        deal.exchange_kitty("N", (hand + kitty)[:6])
        with pytest.raises(ValueError, match="already exchanged"):
            deal.exchange_kitty("N", list(deal.hand_for("N"))[:6])

    def test_follow_suit_enforced(self):
        deal = Deal(self.PLAYERS)
        trick = Trick()
        hand_n = list(deal.hand_for("N"))
        lead = hand_n[0]
        deal.play_card("N", lead, trick)
        lead_suit = lead.suit

        hand_e = list(deal.hand_for("E"))
        suited = [c for c in hand_e if c.suit == lead_suit and not c.is_joker]
        off_suit = [c for c in hand_e if c.suit != lead_suit and not c.is_joker]

        if suited and off_suit:
            with pytest.raises(ValueError, match="follow suit"):
                deal.play_card("E", off_suit[0], trick)

    def test_legal_moves_all_when_leading(self):
        deal = Deal(self.PLAYERS)
        trick = Trick()
        assert len(deal.legal_moves("N", trick)) == CARDS_PER_HAND

    def test_record_trick_first_trick_bonus(self):
        deal = Deal(self.PLAYERS)
        deal.record_trick("N", is_first_trick=True)
        assert deal.trick_counts()["N"] == 2  # 1 trick + 1 kitty bonus

    def test_record_trick_normal(self):
        deal = Deal(self.PLAYERS)
        deal.record_trick("N", is_first_trick=False)
        assert deal.trick_counts()["N"] == 1
