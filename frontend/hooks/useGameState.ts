"use client";

import { useEffect, useReducer, useCallback } from "react";
import { GameState, Card, BidInfo } from "@/lib/types";
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
  placeBid: (bid: BidInfo | null) => void;
  exchangeKitty: (trumpSuit: string | null, direction: string, discards: Card[]) => void;
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
    } else if (
      msg.type === "card_played" ||
      msg.type === "trick_complete" ||
      msg.type === "bot_play" ||
      msg.type === "bid_placed" ||
      msg.type === "kitty_exchanged"
    ) {
      sendMessage({ type: "request_state", data: {} });
    } else if (msg.type === "game_over") {
      sendMessage({ type: "request_state", data: {} });
    }
  }, [lastMessage, sendMessage]);

  const placeBid = useCallback(
    (bid: BidInfo | null) => {
      sendMessage({
        type: "place_bid",
        data: { bid },
      });
    },
    [sendMessage],
  );

  const exchangeKitty = useCallback(
    (trumpSuit: string | null, direction: string, discards: Card[]) => {
      sendMessage({
        type: "exchange_kitty",
        data: {
          trump_suit: trumpSuit,
          direction,
          discards: discards.map((c) => ({ rank: c.rank, suit: c.suit })),
        },
      });
    },
    [sendMessage],
  );

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
    placeBid,
    exchangeKitty,
    playCard,
    requestResync,
    connected: readyState === WebSocket.OPEN,
  };
}
