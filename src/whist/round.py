"""Round helpers for sequential trick play."""

from __future__ import annotations

from dataclasses import dataclass, field

from .cards import Card, Suit
from .game import Deal
from .trick import Trick


TRICKS_PER_DEAL = 13


@dataclass
class Round:
    """Manages turn order and trick progression for a deal."""

    players: list[str]
    trump: Suit | None = None
    deal: Deal = field(init=False)
    current_trick: Trick = field(default_factory=Trick)
    completed_tricks: list[Trick] = field(default_factory=list)
    _leader: str = field(init=False)
    _next_index: int = field(init=False)

    def __post_init__(self) -> None:
        self.deal = Deal(self.players)
        self._set_leader(self.players[0])

    def _set_leader(self, leader: str) -> None:
        if leader not in self.players:
            raise ValueError("leader must be a player in the round")
        self._leader = leader
        self._next_index = self.players.index(leader)

    def expected_player(self) -> str:
        return self.players[self._next_index]

    def play(self, player: str, card: Card) -> str | None:
        """Play a card in order and advance to the next trick if complete."""

        if player != self.expected_player():
            raise ValueError("player must act in turn order")
        self.deal.play_card(player, card, self.current_trick)
        self._next_index = (self._next_index + 1) % len(self.players)
        if not self.current_trick.is_complete():
            return None
        winner = self.current_trick.winner(self.trump)
        if winner is None:
            raise ValueError("completed trick must have a winner")
        self.deal.record_trick(winner)
        self.completed_tricks.append(self.current_trick)
        self.current_trick = Trick()
        self._set_leader(winner)
        return winner

    def is_complete(self) -> bool:
        return len(self.completed_tricks) >= TRICKS_PER_DEAL

    def score(self) -> dict[str, int]:
        return self.deal.partnership_points()
