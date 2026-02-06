"use client";

import { useEffect, useReducer, useCallback } from "react";
import { GameState, Card } from "@/lib/types";
import { useWebSocket } from "./useWebSocket";
import { wsUrl } from "@/lib/api";

type Action =
  | { type: "SET_STATE"; data: GameState }
  | { type: "RESET" };

function reducer(state: GameState | null, action: Action): GameState | null {
  switch (action.type) {
    case "SET_STATE":
      return action.data;
    case "RESET":
      return null;
    default:
      return state;
  }
}

interface UseGameStateReturn {
  gameState: GameState | null;
  playCard: (card: Card) => void;
  requestResync: () => void;
  connected: boolean;
}

export function useGameState(gameId: string | null, token: string | null): UseGameStateReturn {
  const [gameState, dispatch] = useReducer(reducer, null);

  const url = gameId && token ? wsUrl(gameId, token) : null;
  const { lastMessage, sendMessage, readyState } = useWebSocket(url);

  useEffect(() => {
    if (!lastMessage) return;
    const msg = lastMessage as { type: string; data: unknown };

    if (msg.type === "game_state") {
      dispatch({ type: "SET_STATE", data: msg.data as GameState });
    } else if (msg.type === "card_played" || msg.type === "trick_complete" || msg.type === "bot_play") {
      // Request full state resync on any play event for simplicity
      sendMessage({ type: "request_state", data: {} });
    } else if (msg.type === "game_over") {
      sendMessage({ type: "request_state", data: {} });
    }
  }, [lastMessage, sendMessage]);

  const playCard = useCallback(
    (card: Card) => {
      sendMessage({
        type: "play_card",
        data: { card: { rank: card.rank, suit: card.suit } },
      });
    },
    [sendMessage],
  );

  const requestResync = useCallback(() => {
    sendMessage({ type: "request_state", data: {} });
  }, [sendMessage]);

  return {
    gameState,
    playCard,
    requestResync,
    connected: readyState === WebSocket.OPEN,
  };
}
