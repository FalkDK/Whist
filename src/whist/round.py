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
        if self.trump is None:
            self.trump = self.deal.trump_suit
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

        if self.is_complete():
            raise ValueError("round is already complete")
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

    def play_trick(self, plays: dict[str, Card]) -> str:
        """Play a full trick from an ordered mapping of player to card."""

        winner: str | None = None
        for _ in range(len(self.players)):
            player = self.expected_player()
            if player not in plays:
                raise ValueError("plays must include the next player in order")
            winner = self.play(player, plays[player])
        if winner is None:
            raise ValueError("trick did not complete with a winner")
        return winner

    def is_complete(self) -> bool:
        return len(self.completed_tricks) >= TRICKS_PER_DEAL

    def score(self) -> dict[str, int]:
        return self.deal.partnership_points()

    def state(self) -> dict[str, object]:
        """Return a snapshot of round progress for UI or logging."""

        return {
            "leader": self._leader,
            "next_player": self.expected_player(),
            "tricks_played": len(self.completed_tricks),
            "tricks_remaining": TRICKS_PER_DEAL - len(self.completed_tricks),
            "trump": self.trump,
        }
