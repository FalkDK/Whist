"""Tests for deal handling (game.py)."""

import pytest

from whist.cards import Card, Rank, Suit
from whist.game import Deal
from whist.trick import Trick


class TestDeal:
    PLAYERS = ["North", "East", "South", "West"]

    def test_deals_13_cards_to_each_player(self):
        deal = Deal(self.PLAYERS)
        for player in self.PLAYERS:
            assert len(list(deal.hand_for(player))) == 13

    def test_all_52_cards_distributed(self):
        deal = Deal(self.PLAYERS)
        all_cards = []
        for player in self.PLAYERS:
            all_cards.extend(deal.hand_for(player))
        assert len(all_cards) == 52
        assert len(set(all_cards)) == 52

    def test_trump_suit_set_from_last_card(self):
        deal = Deal(self.PLAYERS)
        assert deal.trump_suit is not None
        assert isinstance(deal.trump_suit, Suit)
        assert deal.trump_card is not None
        assert deal.trump_card.suit == deal.trump_suit

    def test_requires_four_players(self):
        with pytest.raises(ValueError, match="four players"):
            Deal(["A", "B", "C"])

    def test_hand_for_unknown_player_raises(self):
        deal = Deal(self.PLAYERS)
        with pytest.raises(ValueError, match="part of the deal"):
            deal.hand_for("Unknown")

    def test_play_card_removes_from_hand(self):
        deal = Deal(self.PLAYERS)
        hand = list(deal.hand_for("North"))
        card = hand[0]
        trick = Trick()
        deal.play_card("North", card, trick)
        assert card not in list(deal.hand_for("North"))

    def test_play_card_adds_to_trick(self):
        deal = Deal(self.PLAYERS)
        card = list(deal.hand_for("North"))[0]
        trick = Trick()
        deal.play_card("North", card, trick)
        assert len(trick.plays) == 1

    def test_play_card_must_follow_suit(self):
        deal = Deal(self.PLAYERS)
        trick = Trick()
        # Find a card in North's hand, play it as lead
        north_hand = list(deal.hand_for("North"))
        lead_card = north_hand[0]
        deal.play_card("North", lead_card, trick)
        lead_suit = lead_card.suit

        # East must follow suit if they can
        east_hand = list(deal.hand_for("East"))
        suited = [c for c in east_hand if c.suit == lead_suit]
        off_suit = [c for c in east_hand if c.suit != lead_suit]

        if suited and off_suit:
            with pytest.raises(ValueError, match="follow suit"):
                deal.play_card("East", off_suit[0], trick)

    def test_play_card_not_in_hand_raises(self):
        deal = Deal(self.PLAYERS)
        trick = Trick()
        # Create a card not in North's hand
        north_hand = set(deal.hand_for("North"))
        fake_card = None
        for rank in Rank:
            for suit in Suit:
                c = Card(rank, suit)
                if c not in north_hand:
                    fake_card = c
                    break
            if fake_card:
                break
        with pytest.raises(ValueError, match="in the player's hand"):
            deal.play_card("North", fake_card, trick)

    def test_legal_moves_returns_all_when_leading(self):
        deal = Deal(self.PLAYERS)
        trick = Trick()
        legal = deal.legal_moves("North", trick)
        assert len(legal) == 13

    def test_legal_moves_filters_by_suit(self):
        deal = Deal(self.PLAYERS)
        trick = Trick()
        north_hand = list(deal.hand_for("North"))
        deal.play_card("North", north_hand[0], trick)
        lead_suit = north_hand[0].suit

        east_hand = list(deal.hand_for("East"))
        suited = [c for c in east_hand if c.suit == lead_suit]
        legal = deal.legal_moves("East", trick)

        if suited:
            assert all(c.suit == lead_suit for c in legal)
        else:
            assert len(legal) == len(east_hand)

    def test_record_trick_and_partnership_points(self):
        deal = Deal(self.PLAYERS)
        for _ in range(7):
            deal.record_trick("North")
        for _ in range(6):
            deal.record_trick("East")
        points = deal.partnership_points()
        assert points["north_south"] == 1
        assert points["east_west"] == 0

    def test_trick_counts(self):
        deal = Deal(self.PLAYERS)
        deal.record_trick("North")
        deal.record_trick("North")
        deal.record_trick("East")
        counts = deal.trick_counts()
        assert counts["North"] == 2
        assert counts["East"] == 1
        assert counts["South"] == 0
        assert counts["West"] == 0
