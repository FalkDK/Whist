"""WebSocket endpoint for real-time gameplay."""

from __future__ import annotations

import asyncio

from fastapi import WebSocket, WebSocketDisconnect

from whist import Card, Rank, Suit

from .auth import ws_authenticate
from .game_manager import ActiveGame, GameManager, _serialize_card


async def broadcast(active: ActiveGame, message: dict) -> None:
    """Send a message to all connected human subscribers."""
    disconnected: list[str] = []
    for username, ws in active.subscribers.items():
        try:
            await ws.send_json(message)
        except Exception:
            disconnected.append(username)
    for username in disconnected:
        active.subscribers.pop(username, None)


async def send_personal_states(active: ActiveGame) -> None:
    """Send each human subscriber their personal game state view."""
    for username, ws in list(active.subscribers.items()):
        try:
            state = active.build_state_for(username)
            await ws.send_json({"type": "game_state", "data": state.model_dump()})
        except Exception:
            active.subscribers.pop(username, None)


async def handle_bot_plays(active: ActiveGame) -> None:
    """Auto-play consecutive bots with delays for animation."""
    bot_plays = active.auto_play_bots()
    for seat, card, trick_winner in bot_plays:
        await asyncio.sleep(0.6)
        display_name = active._display_name(seat)
        await broadcast(active, {
            "type": "card_played",
            "data": {
                "player": display_name,
                "card": _serialize_card(card).model_dump(),
                "trick_winner": active._display_name(trick_winner) if trick_winner else None,
            },
        })
        if trick_winner:
            await broadcast(active, {
                "type": "trick_complete",
                "data": {"winner": active._display_name(trick_winner)},
            })
        await send_personal_states(active)

    if active.current_game.is_complete():
        scores = active.current_game.score()
        counts = active.current_game.trick_counts()
        display_counts = {active._display_name(k): v for k, v in counts.items()}
        await broadcast(active, {
            "type": "game_over",
            "data": {"scores": scores, "trick_counts": display_counts},
        })


async def game_websocket(
    websocket: WebSocket,
    game_id: str,
    game_manager: GameManager,
) -> None:
    username = await ws_authenticate(websocket)
    await websocket.accept()

    active = game_manager.get_game(game_id)
    if active is None:
        await websocket.send_json({"type": "error", "data": {"message": "Game not found"}})
        await websocket.close()
        return

    seat = active.seat_for(username)
    if seat is None:
        await websocket.send_json({"type": "error", "data": {"message": "Not a player in this game"}})
        await websocket.close()
        return

    active.subscribers[username] = websocket

    # Send initial state
    state = active.build_state_for(username)
    await websocket.send_json({"type": "game_state", "data": state.model_dump()})

    # If the first player is a bot, auto-play them now
    async with active.lock:
        if active.current_game.expected_player() in active.bot_seats:
            await handle_bot_plays(active)

    try:
        while True:
            raw = await websocket.receive_json()
            msg_type = raw.get("type")

            if msg_type == "play_card":
                async with active.lock:
                    expected = active.current_game.expected_player()
                    if expected != seat:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": "Not your turn"},
                        })
                        continue

                    card_data = raw["data"]["card"]
                    try:
                        card = Card(rank=Rank(card_data["rank"]), suit=Suit(card_data["suit"]))
                    except (KeyError, ValueError):
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": "Invalid card"},
                        })
                        continue

                    try:
                        trick_winner = active.play_card(seat, card)
                    except ValueError as exc:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": str(exc)},
                        })
                        continue

                    display_name = active._display_name(seat)
                    await broadcast(active, {
                        "type": "card_played",
                        "data": {
                            "player": display_name,
                            "card": _serialize_card(card).model_dump(),
                            "trick_winner": active._display_name(trick_winner) if trick_winner else None,
                        },
                    })

                    if trick_winner:
                        await broadcast(active, {
                            "type": "trick_complete",
                            "data": {"winner": active._display_name(trick_winner)},
                        })

                    if active.current_game.is_complete():
                        scores = active.current_game.score()
                        counts = active.current_game.trick_counts()
                        display_counts = {active._display_name(k): v for k, v in counts.items()}
                        await broadcast(active, {
                            "type": "game_over",
                            "data": {"scores": scores, "trick_counts": display_counts},
                        })
                    else:
                        await send_personal_states(active)
                        await handle_bot_plays(active)

            elif msg_type == "request_state":
                state = active.build_state_for(username)
                await websocket.send_json({"type": "game_state", "data": state.model_dump()})

    except WebSocketDisconnect:
        active.subscribers.pop(username, None)
