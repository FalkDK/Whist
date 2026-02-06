"""FastAPI application entry point."""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .game_manager import GameManager
from .lobby import LobbyManager
from .routes import auth_routes, lobby_routes, game_routes
from .ws import game_websocket

app = FastAPI(title="Whist Game Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Singletons
game_manager = GameManager()
lobby_manager = LobbyManager(game_manager)

# Wire managers into route modules
lobby_routes.set_lobby_manager(lobby_manager)
game_routes.set_game_manager(game_manager)

# REST routes
app.include_router(auth_routes.router, prefix="/api")
app.include_router(lobby_routes.router, prefix="/api/lobby")
app.include_router(game_routes.router, prefix="/api/game")


@app.websocket("/ws/game/{game_id}")
async def ws_endpoint(websocket: WebSocket, game_id: str) -> None:
    await game_websocket(websocket, game_id, game_manager)
