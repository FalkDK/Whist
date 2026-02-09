"""Trick resolution for Bid Whist."""

from __future__ import annotations

from dataclasses import dataclass, field

from .cards import Card, Direction, Rank, Suit


@dataclass
class Trick:
    """Collects card plays for a single trick and resolves the winner."""

    max_plays: int = 4
    plays: list[tuple[str, Card]] = field(default_factory=list)

    def lead_suit(self) -> Suit | None:
        """Return the effective lead suit.

        If a joker is led, the lead suit is determined by the first
        non-joker card played.  If all plays are jokers, there is no
        effective lead suit.
        """
        for _, card in self.plays:
            if not card.is_joker:
                return card.suit
        return None

    def add_play(self, player: str, card: Card) -> None:
        if len(self.plays) >= self.max_plays:
            raise ValueError("trick already has maximum plays")
        if any(existing_player == player for existing_player, _ in self.plays):
            raise ValueError("player has already played in this trick")
        self.plays.append((player, card))

    def is_complete(self) -> bool:
        return len(self.plays) == self.max_plays

    def winner(
        self,
        trump: Suit | None = None,
        direction: Direction = Direction.UPTOWN,
    ) -> str | None:
        """Resolve the trick winner considering trump, direction, and jokers.

        In trump games: Jokers are the highest trumps (Little < Big).
        In no-trump games: Jokers are the weakest cards and cannot win.
        """
        if not self.plays:
            return None

        downtown = direction == Direction.DOWNTOWN
        lead = self.lead_suit()
        has_trump = trump is not None

        def card_strength(play: tuple[str, Card]) -> int:
            _, card = play
            if card.is_joker:
                if has_trump:
                    # Jokers are the strongest trumps
                    return 300 + Rank.strength(card.rank, downtown=False)
                else:
                    # In no-trump, jokers are weakest and cannot win
                    return -1
            if has_trump and card.suit == trump:
                return 200 + Rank.strength(card.rank, downtown=downtown)
            if lead is not None and card.suit == lead:
                return 100 + Rank.strength(card.rank, downtown=downtown)
            # Off-suit, non-trump
            return Rank.strength(card.rank, downtown=downtown)

        best_player, _ = max(self.plays, key=card_strength)
        return best_player

    def summary(self) -> list[tuple[str, str]]:
        """Return a list of (player, card_label) for the trick."""
        return [(player, card.label()) for player, card in self.plays]
