"""WebSocket endpoint for real-time gameplay."""

from __future__ import annotations

import asyncio

from fastapi import WebSocket, WebSocketDisconnect

from whist import Bid, BidType, Card, Direction, Phase, Rank, Suit

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


async def handle_bot_bids(active: ActiveGame) -> None:
    """Auto-bid for consecutive bots with delays."""
    bot_bids = active.auto_play_bot_bids()
    for seat, bid in bot_bids:
        await asyncio.sleep(0.6)
        display_name = active._display_name(seat)
        bid_data = None
        if bid:
            bid_data = {"number": bid.number, "bid_type": bid.bid_type.value}
        await broadcast(active, {
            "type": "bid_placed",
            "data": {"player": display_name, "bid": bid_data},
        })
        await send_personal_states(active)


async def handle_bot_kitty(active: ActiveGame) -> None:
    """Auto-exchange kitty if bid winner is a bot."""
    result = active.auto_play_bot_kitty()
    if result:
        seat, trump, direction = result
        await asyncio.sleep(0.8)
        display_name = active._display_name(seat)
        await broadcast(active, {
            "type": "kitty_exchanged",
            "data": {
                "player": display_name,
                "trump_suit": trump.value if trump else None,
                "direction": direction.value,
            },
        })
        await send_personal_states(active)


async def handle_bot_plays(active: ActiveGame) -> None:
    """Auto-play consecutive bots with delays for animation."""
    bot_plays = active.auto_play_bot_cards()
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


async def auto_advance_bots(active: ActiveGame) -> None:
    """Run through all bot actions for the current phase."""
    phase = active.current_game.phase
    if phase == Phase.BIDDING:
        await handle_bot_bids(active)
        if active.current_game.phase == Phase.KITTY:
            await handle_bot_kitty(active)
            if active.current_game.phase == Phase.PLAYING:
                await handle_bot_plays(active)
    elif phase == Phase.KITTY:
        await handle_bot_kitty(active)
        if active.current_game.phase == Phase.PLAYING:
            await handle_bot_plays(active)
    elif phase == Phase.PLAYING:
        await handle_bot_plays(active)


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

    # Auto-advance bots from the current phase
    async with active.lock:
        await auto_advance_bots(active)

    try:
        while True:
            raw = await websocket.receive_json()
            msg_type = raw.get("type")

            if msg_type == "place_bid":
                async with active.lock:
                    if active.current_game.phase != Phase.BIDDING:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": "Not in bidding phase"},
                        })
                        continue

                    expected = active.current_game.expected_bidder()
                    if expected != seat:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": "Not your turn to bid"},
                        })
                        continue

                    bid_data = raw.get("data", {}).get("bid")
                    try:
                        if bid_data:
                            bid = Bid(bid_data["number"], BidType(bid_data["bid_type"]))
                        else:
                            bid = None
                        active.place_bid(seat, bid)
                    except ValueError as exc:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": str(exc)},
                        })
                        continue

                    display_name = active._display_name(seat)
                    bid_info = None
                    if bid:
                        bid_info = {"number": bid.number, "bid_type": bid.bid_type.value}
                    await broadcast(active, {
                        "type": "bid_placed",
                        "data": {"player": display_name, "bid": bid_info},
                    })
                    await send_personal_states(active)
                    await auto_advance_bots(active)

            elif msg_type == "exchange_kitty":
                async with active.lock:
                    if active.current_game.phase != Phase.KITTY:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": "Not in kitty exchange phase"},
                        })
                        continue

                    if active.current_game.bid_winner != seat:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": "Only the bid winner can exchange the kitty"},
                        })
                        continue

                    data = raw.get("data", {})
                    try:
                        trump_val = data.get("trump_suit")
                        trump_suit = Suit(trump_val) if trump_val else None
                        direction = Direction(data.get("direction", "uptown"))
                        discard_data = data.get("discards", [])
                        discards = [
                            Card(rank=Rank(d["rank"]), suit=Suit(d["suit"]))
                            for d in discard_data
                        ]
                        active.set_trump_and_exchange(seat, trump_suit, direction, discards)
                    except (KeyError, ValueError) as exc:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": str(exc)},
                        })
                        continue

                    display_name = active._display_name(seat)
                    await broadcast(active, {
                        "type": "kitty_exchanged",
                        "data": {
                            "player": display_name,
                            "trump_suit": trump_suit.value if trump_suit else None,
                            "direction": direction.value,
                        },
                    })
                    await send_personal_states(active)
                    await auto_advance_bots(active)

            elif msg_type == "play_card":
                async with active.lock:
                    if active.current_game.phase != Phase.PLAYING:
                        await websocket.send_json({
                            "type": "error",
                            "data": {"message": "Not in playing phase"},
                        })
                        continue

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
