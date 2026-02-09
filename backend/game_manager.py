"""Manages active game instances and bridges the whist engine with the network layer."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field

from fastapi import WebSocket

from whist import Bid, BidType, Card, Direction, Game, Match, Phase, Rank, Suit

from .bot import BotPlayer
from .models import (
    BidSchema,
    CardSchema,
    GameStateSchema,
    PlaySchema,
    TrickSchema,
)

SEAT_NAMES = ["North", "East", "South", "West"]


def _serialize_card(card: Card) -> CardSchema:
    return CardSchema(rank=card.rank.value, suit=card.suit.value, label=card.label())


def _deserialize_card(data: dict) -> Card:
    return Card(rank=Rank(data["rank"]), suit=Suit(data["suit"]))


def _serialize_bid(bid: Bid) -> BidSchema:
    return BidSchema(number=bid.number, bid_type=bid.bid_type.value)


@dataclass
class ActiveGame:
    """Wraps a whist Match/Game with multiplayer metadata."""

    game_id: str
    seat_names: list[str]
    username_to_seat: dict[str, str] = field(default_factory=dict)
    seat_to_username: dict[str, str] = field(default_factory=dict)
    bot_seats: set[str] = field(default_factory=set)
    bots: dict[str, BotPlayer] = field(default_factory=dict)
    match: Match = field(init=False)
    current_game: Game = field(init=False)
    subscribers: dict[str, WebSocket] = field(default_factory=dict)
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    host: str = ""

    def __post_init__(self) -> None:
        self.match = Match(self.seat_names)
        self.current_game = self.match.start_game()

    @property
    def human_seats(self) -> set[str]:
        return set(self.seat_names) - self.bot_seats

    def seat_for(self, username: str) -> str | None:
        return self.username_to_seat.get(username)

    def build_state_for(self, username: str) -> GameStateSchema:
        seat = self.username_to_seat[username]
        game = self.current_game
        rnd = game.round
        deal = rnd.deal
        phase = rnd.phase

        hand = [_serialize_card(c) for c in deal.hand_for(seat)]

        state = GameStateSchema(
            game_id=self.game_id,
            phase=phase.value,
            players=[self._display_name(s) for s in self.seat_names],
            seat=self._display_name(seat),
            your_hand=hand,
            is_complete=game.is_complete(),
        )

        # Bid info (available from KITTY phase onward)
        if rnd.bid_winner:
            state.bid_winner = self._display_name(rnd.bid_winner)
        if rnd.winning_bid:
            state.winning_bid = _serialize_bid(rnd.winning_bid)

        if phase == Phase.BIDDING:
            bidder = rnd.expected_bidder()
            state.expected_bidder = self._display_name(bidder) if bidder else None
            bids: dict[str, BidSchema | None] = {}
            for player, bid in rnd.bidding.bids.items():
                display = self._display_name(player)
                bids[display] = _serialize_bid(bid) if bid else None
            state.bids = bids

        elif phase == Phase.KITTY:
            # Only the bid winner sees the kitty
            if seat == rnd.bid_winner:
                state.kitty = [_serialize_card(c) for c in deal.kitty]

        elif phase in (Phase.PLAYING, Phase.COMPLETE):
            state.trump_suit = rnd.trump.value if rnd.trump else None
            state.direction = rnd.direction.value if rnd.direction else None

            expected = game.expected_player()
            state.expected_player = self._display_name(expected)

            if expected == seat and not game.is_complete():
                state.legal_moves = [
                    _serialize_card(c) for c in deal.legal_moves(seat, rnd.current_trick)
                ]

            state.current_trick = [
                PlaySchema(player=self._display_name(p), card=_serialize_card(c))
                for p, c in rnd.current_trick.plays
            ]

            state.tricks_played = len(rnd.completed_tricks)
            state.tricks_remaining = 12 - len(rnd.completed_tricks)
            state.trick_counts = {
                self._display_name(k): v for k, v in deal.trick_counts().items()
            }
            state.partnership_scores = deal.partnership_points()

            completed = []
            for trick in rnd.completed_tricks:
                plays = [
                    PlaySchema(player=self._display_name(p), card=_serialize_card(c))
                    for p, c in trick.plays
                ]
                winner = trick.winner(rnd.trump, rnd.direction)
                completed.append(
                    TrickSchema(
                        plays=plays,
                        winner=self._display_name(winner) if winner else None,
                    )
                )
            state.completed_tricks = completed

        return state

    # --- Bidding ---

    def place_bid(self, seat: str, bid: Bid | None) -> None:
        self.current_game.place_bid(seat, bid)

    # --- Kitty exchange ---

    def set_trump_and_exchange(
        self, seat: str, trump_suit: Suit | None, direction: Direction, discards: list[Card]
    ) -> None:
        self.current_game.set_trump_and_exchange(seat, trump_suit, direction, discards)

    # --- Play ---

    def play_card(self, seat: str, card: Card) -> str | None:
        return self.current_game.play(seat, card)

    def auto_play_bot_bids(self) -> list[tuple[str, Bid | None]]:
        """Auto-bid for consecutive bot seats."""
        results: list[tuple[str, Bid | None]] = []
        while self.current_game.phase == Phase.BIDDING:
            expected = self.current_game.expected_bidder()
            if expected is None or expected not in self.bot_seats:
                break
            bot = self.bots[expected]
            bid = bot.choose_bid(self.current_game)
            try:
                self.current_game.place_bid(expected, bid)
            except ValueError:
                # Dealer forced to bid — place minimum
                bid = Bid(3, BidType.UPTOWN)
                self.current_game.place_bid(expected, bid)
            results.append((expected, bid))
        return results

    def auto_play_bot_kitty(self) -> tuple[str, Suit | None, Direction] | None:
        """Auto-exchange kitty if bid winner is a bot."""
        if self.current_game.phase != Phase.KITTY:
            return None
        bid_winner = self.current_game.bid_winner
        if bid_winner not in self.bot_seats:
            return None
        bot = self.bots[bid_winner]
        trump, direction, discards = bot.choose_trump_and_discards(self.current_game)
        self.current_game.set_trump_and_exchange(bid_winner, trump, direction, discards)
        return (bid_winner, trump, direction)

    def auto_play_bot_cards(self) -> list[tuple[str, Card, str | None]]:
        """Play for all consecutive bot seats."""
        results: list[tuple[str, Card, str | None]] = []
        while not self.current_game.is_complete():
            if self.current_game.phase != Phase.PLAYING:
                break
            expected = self.current_game.expected_player()
            if expected not in self.bot_seats:
                break
            bot = self.bots[expected]
            card = bot.choose_card(self.current_game)
            winner = self.current_game.play(expected, card)
            results.append((expected, card, winner))
        return results

    def _display_name(self, seat: str) -> str:
        if seat in self.seat_to_username:
            return self.seat_to_username[seat]
        return seat


class GameManager:
    """Central registry of all active games."""

    def __init__(self) -> None:
        self._games: dict[str, ActiveGame] = {}

    def create_game(
        self,
        host_username: str,
        human_usernames: list[str],
        bot_count: int,
        game_id: str | None = None,
    ) -> ActiveGame:
        if game_id is None:
            game_id = uuid.uuid4().hex[:8]
        active = ActiveGame(game_id=game_id, seat_names=list(SEAT_NAMES), host=host_username)

        for i, username in enumerate(human_usernames):
            seat = SEAT_NAMES[i]
            active.username_to_seat[username] = seat
            active.seat_to_username[seat] = username

        bot_index = 0
        for i in range(len(human_usernames), 4):
            seat = SEAT_NAMES[i]
            bot_name = f"Bot-{bot_index + 1}"
            active.bot_seats.add(seat)
            active.bots[seat] = BotPlayer(seat, seed=bot_index)
            active.seat_to_username[seat] = bot_name
            bot_index += 1

        self._games[game_id] = active
        return active

    def get_game(self, game_id: str) -> ActiveGame | None:
        return self._games.get(game_id)

    def list_games(self) -> list[ActiveGame]:
        return list(self._games.values())
