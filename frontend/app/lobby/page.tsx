"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { apiGet, apiPost } from "@/lib/api";
import { LobbyGame } from "@/lib/types";

export default function LobbyPage() {
  const { token, displayName, logout, isAuthenticated } = useAuth();
  const router = useRouter();
  const [games, setGames] = useState<LobbyGame[]>([]);
  const [botCount, setBotCount] = useState(3);
  const [error, setError] = useState("");

  const fetchGames = useCallback(async () => {
    if (!token) return;
    try {
      const list = await apiGet<LobbyGame[]>("/api/lobby", token);
      setGames(list);
    } catch {
      // ignore fetch errors
    }
  }, [token]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push("/");
      return;
    }
    fetchGames();
    const interval = setInterval(fetchGames, 3000);
    return () => clearInterval(interval);
  }, [isAuthenticated, router, fetchGames]);

  async function handleCreate() {
    if (!token) return;
    setError("");
    try {
      const game = await apiPost<LobbyGame>("/api/lobby/create", { bot_count: botCount }, token);
      if (game.status === "in_progress") {
        router.push(`/game/${game.game_id}`);
      } else {
        fetchGames();
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create game");
    }
  }

  async function handleJoin(gameId: string) {
    if (!token) return;
    setError("");
    try {
      const game = await apiPost<LobbyGame>(`/api/lobby/${gameId}/join`, {}, token);
      if (game.status === "in_progress") {
        router.push(`/game/${game.game_id}`);
      } else {
        fetchGames();
      }
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to join game");
    }
  }

  return (
    <div className="min-h-screen bg-green-900 text-white p-8">
      <div className="max-w-2xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Whist Lobby</h1>
          <div className="flex items-center gap-4">
            <span className="text-green-200">Hi, {displayName}</span>
            <button
              onClick={logout}
              className="text-sm bg-green-800 px-3 py-1 rounded hover:bg-green-700 transition"
            >
              Logout
            </button>
          </div>
        </div>

        {/* Create game */}
        <div className="bg-green-800 rounded-xl p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">New Game</h2>
          <div className="flex items-center gap-4">
            <label className="text-sm">Bots:</label>
            <select
              value={botCount}
              onChange={(e) => setBotCount(Number(e.target.value))}
              className="bg-green-700 border border-green-600 rounded px-3 py-1 text-white"
            >
              <option value={3}>3 bots (solo)</option>
              <option value={2}>2 bots (need 1 more human)</option>
              <option value={1}>1 bot (need 2 more humans)</option>
              <option value={0}>0 bots (need 3 more humans)</option>
            </select>
            <button
              onClick={handleCreate}
              className="bg-yellow-600 text-white font-semibold px-6 py-2 rounded-lg hover:bg-yellow-500 transition"
            >
              Create Game
            </button>
          </div>
          {error && <p className="text-red-300 text-sm mt-2">{error}</p>}
        </div>

        {/* Game list */}
        <div className="bg-green-800 rounded-xl p-6">
          <h2 className="text-xl font-semibold mb-4">Games</h2>
          {games.length === 0 ? (
            <p className="text-green-300">No games yet. Create one above!</p>
          ) : (
            <div className="space-y-3">
              {games.map((game) => (
                <div
                  key={game.game_id}
                  className="flex items-center justify-between bg-green-700 rounded-lg p-4"
                >
                  <div>
                    <span className="font-medium">{game.host}&apos;s game</span>
                    <span className="text-green-300 text-sm ml-3">
                      {game.players.join(", ")} | {game.bot_count} bot{game.bot_count !== 1 ? "s" : ""}
                    </span>
                    <span className="text-xs ml-2 px-2 py-0.5 rounded bg-green-600">
                      {game.status === "waiting"
                        ? `Waiting (need ${game.needed} more)`
                        : game.status}
                    </span>
                  </div>
                  <div className="flex gap-2">
                    {game.status === "waiting" && (
                      <button
                        onClick={() => handleJoin(game.game_id)}
                        className="bg-yellow-600 text-white text-sm px-4 py-1 rounded hover:bg-yellow-500 transition"
                      >
                        Join
                      </button>
                    )}
                    {game.status === "in_progress" && (
                      <button
                        onClick={() => router.push(`/game/${game.game_id}`)}
                        className="bg-blue-600 text-white text-sm px-4 py-1 rounded hover:bg-blue-500 transition"
                      >
                        Play
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
