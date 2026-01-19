"""Deal and round helpers for Whist."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .cards import Card, Suit
from .deck import Deck
from .scoring import Scoreboard
from .trick import Trick


@dataclass
class Deal:
    """Represents a single 13-trick deal."""

    players: list[str]
    deck: Deck = field(default_factory=Deck)
    hands: dict[str, list[Card]] = field(init=False)
    scoreboard: Scoreboard = field(init=False)
    trump_card: Card | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        if len(self.players) != 4:
            raise ValueError("Whist expects four players")
        self.deck.shuffle()
        self.hands = self._deal_hands()
        self.scoreboard = Scoreboard(self.players)

    def _deal_hands(self) -> dict[str, list[Card]]:
        hands = {player: [] for player in self.players}
        last_card: Card | None = None
        for _ in range(13):
            for player in self.players:
                card = self.deck.deal(1)[0]
                hands[player].append(card)
                last_card = card
        self.trump_card = last_card
        if self.deck.remaining() != 0:
            raise ValueError("deck should be empty after dealing")
        return hands

    @property
    def trump_suit(self) -> Suit | None:
        return self.trump_card.suit if self.trump_card else None

    def record_trick(self, winner: str) -> None:
        self.scoreboard.record_trick(winner)

    def partnership_points(self) -> dict[str, int]:
        return self.scoreboard.partnership_points()

    def hand_for(self, player: str) -> Iterable[Card]:
        if player not in self.hands:
            raise ValueError("player must be part of the deal")
        return list(self.hands[player])

    def play_card(self, player: str, card: Card, trick: Trick) -> None:
        """Play a card into a trick, enforcing follow-suit when possible."""

        if player not in self.hands:
            raise ValueError("player must be part of the deal")
        hand = self.hands[player]
        if card not in hand:
            raise ValueError("card must be in the player's hand")
        lead_suit = trick.lead_suit()
        if lead_suit is not None and card.suit != lead_suit:
            if any(hand_card.suit == lead_suit for hand_card in hand):
                raise ValueError("must follow suit if possible")
        hand.remove(card)
        trick.add_play(player, card)
