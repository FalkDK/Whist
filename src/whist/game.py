"""Deal and round helpers for Bid Whist."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from .cards import Card, Direction, Suit
from .deck import Deck
from .scoring import Scoreboard
from .trick import Trick

CARDS_PER_HAND = 12
KITTY_SIZE = 6


@dataclass
class Deal:
    """Represents a single Bid Whist deal (12 cards each + 6-card kitty)."""

    players: list[str]
    deck: Deck = field(default_factory=lambda: Deck(jokers=True))
    hands: dict[str, list[Card]] = field(init=False)
    kitty: list[Card] = field(init=False)
    scoreboard: Scoreboard = field(init=False)
    trump_suit: Suit | None = field(init=False, default=None)
    direction: Direction = field(init=False, default=Direction.UPTOWN)
    _kitty_exchanged: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        if len(self.players) != 4:
            raise ValueError("Bid Whist expects four players")
        self.deck.shuffle()
        self.hands, self.kitty = self._deal_hands()
        self.scoreboard = Scoreboard(self.players)

    def _deal_hands(self) -> tuple[dict[str, list[Card]], list[Card]]:
        hands: dict[str, list[Card]] = {player: [] for player in self.players}
        kitty: list[Card] = []
        # Deal 12 cards to each player, 6 to kitty
        # Kitty cards dealt in the middle of the deal
        for i in range(CARDS_PER_HAND):
            for player in self.players:
                hands[player].append(self.deck.deal(1)[0])
            # Deal one kitty card after rounds 2 and 8 (3 cards each time)
            if i == 2:
                kitty.extend(self.deck.deal(3))
            elif i == 8:
                kitty.extend(self.deck.deal(3))
        assert self.deck.remaining() == 0
        return hands, kitty

    def set_trump(self, suit: Suit | None, direction: Direction) -> None:
        """Set the trump suit and direction after bidding."""
        self.trump_suit = suit
        self.direction = direction

    def exchange_kitty(self, player: str, discards: list[Card]) -> None:
        """Bid winner picks up kitty and discards cards back."""
        if self._kitty_exchanged:
            raise ValueError("kitty already exchanged")
        if player not in self.hands:
            raise ValueError("player must be part of the deal")
        if len(discards) != KITTY_SIZE:
            raise ValueError(f"must discard exactly {KITTY_SIZE} cards")

        # Add kitty to player's hand
        self.hands[player].extend(self.kitty)

        # Validate and remove discards
        for card in discards:
            if card not in self.hands[player]:
                raise ValueError(f"cannot discard {card} - not in hand")
            self.hands[player].remove(card)

        # Discarded kitty goes to winner of first trick
        self.kitty = list(discards)
        self._kitty_exchanged = True

    def record_trick(self, winner: str, is_first_trick: bool = False) -> None:
        self.scoreboard.record_trick(winner)
        if is_first_trick:
            # First trick winner also gets the kitty (counts as a bonus book)
            self.scoreboard.record_trick(winner)

    def partnership_points(self) -> dict[str, int]:
        return self.scoreboard.partnership_points()

    def trick_counts(self) -> dict[str, int]:
        return dict(self.scoreboard.trick_counts)

    def hand_for(self, player: str) -> Iterable[Card]:
        if player not in self.hands:
            raise ValueError("player must be part of the deal")
        return list(self.hands[player])

    def play_card(self, player: str, card: Card, trick: Trick) -> None:
        """Play a card into a trick, enforcing follow-suit when possible.

        Jokers are special: in trump games they belong to the trump suit.
        In no-trump, they belong to no suit and can be played anytime,
        but cannot win (handled in Trick.winner).
        """
        if player not in self.hands:
            raise ValueError("player must be part of the deal")
        hand = self.hands[player]
        if card not in hand:
            raise ValueError("card must be in the player's hand")

        lead_suit = trick.lead_suit()
        if lead_suit is not None and not card.is_joker:
            if card.suit != lead_suit:
                # Check if player has any cards of the led suit (non-joker)
                has_suit = any(
                    c.suit == lead_suit and not c.is_joker for c in hand
                )
                if has_suit:
                    raise ValueError("must follow suit if possible")

        hand.remove(card)
        trick.add_play(player, card)

    def legal_moves(self, player: str, trick: Trick) -> list[Card]:
        """Return the legal cards a player may play for the given trick."""
        if player not in self.hands:
            raise ValueError("player must be part of the deal")
        hand = list(self.hands[player])
        lead_suit = trick.lead_suit()
        if lead_suit is None:
            return hand
        # Must follow lead suit if possible (jokers are always playable)
        suited = [c for c in hand if c.suit == lead_suit and not c.is_joker]
        if suited:
            # Can play suited cards or jokers
            jokers = [c for c in hand if c.is_joker]
            return suited + jokers
        return hand
