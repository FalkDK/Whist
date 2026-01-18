"""Trick resolution for Whist."""

from __future__ import annotations

from dataclasses import dataclass, field

from .cards import Card, Rank, Suit


@dataclass
class Trick:
    """Collects card plays for a single trick and resolves the winner."""

    max_plays: int = 4
    plays: list[tuple[str, Card]] = field(default_factory=list)

    def lead_suit(self) -> Suit | None:
        return self.plays[0][1].suit if self.plays else None

    def add_play(self, player: str, card: Card) -> None:
        if len(self.plays) >= self.max_plays:
            raise ValueError("trick already has maximum plays")
        if any(existing_player == player for existing_player, _ in self.plays):
            raise ValueError("player has already played in this trick")
        self.plays.append((player, card))

    def is_complete(self) -> bool:
        return len(self.plays) == self.max_plays

    def winner(self, trump: Suit | None = None) -> str | None:
        if not self.plays:
            return None
        lead = self.lead_suit()
        assert lead is not None
        trump_plays = [play for play in self.plays if trump and play[1].suit == trump]
        candidate_plays = trump_plays if trump_plays else [
            play for play in self.plays if play[1].suit == lead
        ]
        winner_player, _ = max(
            candidate_plays,
            key=lambda play: Rank.strength(play[1].rank),
        )
        return winner_player
