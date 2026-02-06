"use client";

import { useEffect, useRef, useState, useCallback } from "react";

interface UseWebSocketReturn {
  lastMessage: unknown | null;
  sendMessage: (data: unknown) => void;
  readyState: number;
}

export function useWebSocket(url: string | null): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const [lastMessage, setLastMessage] = useState<unknown | null>(null);
  const [readyState, setReadyState] = useState<number>(WebSocket.CLOSED);
  const reconnectAttempts = useRef(0);
  const urlRef = useRef(url);
  urlRef.current = url;

  const connect = useCallback(() => {
    if (!urlRef.current) return;
    const ws = new WebSocket(urlRef.current);
    wsRef.current = ws;

    ws.onopen = () => {
      setReadyState(WebSocket.OPEN);
      reconnectAttempts.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setLastMessage(data);
      } catch {
        // ignore non-JSON
      }
    };

    ws.onclose = () => {
      setReadyState(WebSocket.CLOSED);
      // Reconnect with exponential backoff
      if (reconnectAttempts.current < 5) {
        const delay = Math.min(1000 * 2 ** reconnectAttempts.current, 16000);
        reconnectAttempts.current += 1;
        setTimeout(connect, delay);
      }
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    connect();
    return () => {
      wsRef.current?.close();
    };
  }, [url, connect]);

  const sendMessage = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  return { lastMessage, sendMessage, readyState };
}
