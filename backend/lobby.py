"""Lobby for creating and joining games before they start."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from .game_manager import ActiveGame, GameManager
from .models import LobbyGameSchema


@dataclass
class LobbyEntry:
    game_id: str
    host: str
    human_players: list[str]
    bot_count: int
    status: str = "waiting"  # waiting | in_progress | complete

    @property
    def needed_humans(self) -> int:
        return 4 - self.bot_count

    @property
    def is_full(self) -> bool:
        return len(self.human_players) >= self.needed_humans

    def to_schema(self) -> LobbyGameSchema:
        return LobbyGameSchema(
            game_id=self.game_id,
            host=self.host,
            players=list(self.human_players),
            bot_count=self.bot_count,
            needed=self.needed_humans - len(self.human_players),
            status=self.status,
        )


class LobbyManager:
    def __init__(self, game_manager: GameManager) -> None:
        self._entries: dict[str, LobbyEntry] = {}
        self._game_manager = game_manager

    def create(self, host: str, bot_count: int) -> LobbyEntry:
        if bot_count < 0 or bot_count > 3:
            raise ValueError("bot_count must be 0-3")
        game_id = uuid.uuid4().hex[:8]
        entry = LobbyEntry(
            game_id=game_id,
            host=host,
            human_players=[host],
            bot_count=bot_count,
        )
        self._entries[game_id] = entry
        if entry.is_full:
            self._start(entry)
        return entry

    def join(self, game_id: str, username: str) -> LobbyEntry:
        entry = self._entries.get(game_id)
        if entry is None:
            raise ValueError("Game not found")
        if entry.status != "waiting":
            raise ValueError("Game already started")
        if username in entry.human_players:
            raise ValueError("Already joined this game")
        if entry.is_full:
            raise ValueError("Game is full")
        entry.human_players.append(username)
        if entry.is_full:
            self._start(entry)
        return entry

    def get(self, game_id: str) -> LobbyEntry | None:
        return self._entries.get(game_id)

    def list_entries(self) -> list[LobbyEntry]:
        return list(self._entries.values())

    def _start(self, entry: LobbyEntry) -> ActiveGame:
        entry.status = "in_progress"
        active = self._game_manager.create_game(
            host_username=entry.host,
            human_usernames=entry.human_players,
            bot_count=entry.bot_count,
            game_id=entry.game_id,
        )
        return active
