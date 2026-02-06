"""Bot player logic for automated card selection."""

from __future__ import annotations

import random

from whist import Card, Game


class BotPlayer:
    """Picks a random legal card."""

    def __init__(self, name: str, seed: int | None = None) -> None:
        self.name = name
        self.rng = random.Random(seed)

    def choose_card(self, game: Game) -> Card:
        legal = game.round.deal.legal_moves(self.name, game.round.current_trick)
        return self.rng.choice(list(legal))
