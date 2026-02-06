"use client";

import { useParams, useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { useGameState } from "@/hooks/useGameState";
import GameBoard from "@/components/GameBoard";
import GameOverDialog from "@/components/GameOverDialog";
import { useEffect } from "react";

export default function GamePage() {
  const params = useParams();
  const gameId = params.id as string;
  const router = useRouter();
  const { token, isAuthenticated } = useAuth();
  const { gameState, playCard, connected } = useGameState(gameId, token);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/");
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) return null;

  if (!connected && !gameState) {
    return (
      <div className="min-h-screen bg-green-900 flex items-center justify-center text-white">
        <div className="text-center">
          <div className="text-xl mb-2">Connecting to game...</div>
          <div className="text-sm text-green-300">Game ID: {gameId}</div>
        </div>
      </div>
    );
  }

  if (!gameState) {
    return (
      <div className="min-h-screen bg-green-900 flex items-center justify-center text-white">
        <div className="text-xl">Loading game state...</div>
      </div>
    );
  }

  return (
    <>
      <GameBoard state={gameState} onPlayCard={playCard} />
      {gameState.is_complete && (
        <GameOverDialog
          state={gameState}
          onBackToLobby={() => router.push("/lobby")}
        />
      )}
    </>
  );
}
