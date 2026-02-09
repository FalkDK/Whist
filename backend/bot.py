"""Bot player logic for automated card/bid selection."""

from __future__ import annotations

import random

from whist import Bid, BidType, Card, Direction, Game, Suit


class BotPlayer:
    """Picks random legal actions for all game phases."""

    def __init__(self, name: str, seed: int | None = None) -> None:
        self.name = name
        self.rng = random.Random(seed)

    def choose_bid(self, game: Game) -> Bid | None:
        """Bots always pass unless forced to bid as dealer."""
        return None

    def choose_trump_and_discards(self, game: Game) -> tuple[Suit | None, Direction, list[Card]]:
        """Choose trump suit, direction, and cards to discard from kitty exchange.

        Strategy: pick the suit with the most cards as trump. Discard the
        weakest off-suit cards.
        """
        hand = list(game.round.deal.hand_for(self.name))
        kitty = list(game.round.deal.kitty)
        merged = hand + kitty

        bid = game.winning_bid
        # If no-trump bid, no trump suit
        if bid and not bid.has_trump:
            direction = Direction.UPTOWN
            non_jokers = [c for c in merged if not c.is_joker]
            non_jokers.sort(key=lambda c: c.rank.strength(downtown=False))
            discards = non_jokers[:6]
            return None, direction, discards

        direction = bid.direction if bid else Direction.UPTOWN
        downtown = direction == Direction.DOWNTOWN

        # Count cards per real suit
        suit_counts: dict[Suit, int] = {}
        for c in merged:
            if not c.is_joker:
                suit_counts.setdefault(c.suit, 0)
                suit_counts[c.suit] = suit_counts[c.suit] + 1

        # Pick the suit with the most cards
        trump = max(suit_counts, key=lambda s: suit_counts[s]) if suit_counts else Suit.SPADES

        # Discard weakest non-trump, non-joker cards
        off_suit = [c for c in merged if not c.is_joker and c.suit != trump]
        off_suit.sort(key=lambda c: c.rank.strength(downtown=downtown))
        discards = off_suit[:6]

        # If we don't have enough off-suit to discard, add weakest trump
        if len(discards) < 6:
            trump_cards = [c for c in merged if not c.is_joker and c.suit == trump]
            trump_cards.sort(key=lambda c: c.rank.strength(downtown=downtown))
            remaining = 6 - len(discards)
            discards.extend(trump_cards[:remaining])

        return trump, direction, discards

    def choose_card(self, game: Game) -> Card:
        legal = game.round.deal.legal_moves(self.name, game.round.current_trick)
        return self.rng.choice(list(legal))
