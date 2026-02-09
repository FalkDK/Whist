"use client";

import { GameState } from "@/lib/types";

interface Props {
  state: GameState;
  onBackToLobby: () => void;
}

export default function GameOverDialog({ state, onBackToLobby }: Props) {
  const { partnership_scores, trick_counts, players } = state;
  const nsWon = partnership_scores.north_south > partnership_scores.east_west;
  const tied = partnership_scores.north_south === partnership_scores.east_west;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl p-8 w-full max-w-md text-gray-900">
        <h2 className="text-2xl font-bold text-center mb-4">Game Over!</h2>

        <div className="space-y-3 mb-6">
          <div className={`p-3 rounded-lg ${nsWon ? "bg-green-100 border-2 border-green-500" : "bg-gray-50"}`}>
            <div className="flex justify-between font-semibold">
              <span>North/South</span>
              <span>{partnership_scores.north_south} pts</span>
            </div>
            <div className="text-xs text-gray-500">
              {players[0]}, {players[2]}
            </div>
          </div>
          <div className={`p-3 rounded-lg ${!nsWon && !tied ? "bg-green-100 border-2 border-green-500" : "bg-gray-50"}`}>
            <div className="flex justify-between font-semibold">
              <span>East/West</span>
              <span>{partnership_scores.east_west} pts</span>
            </div>
            <div className="text-xs text-gray-500">
              {players[1]}, {players[3]}
            </div>
          </div>
        </div>

        <div className="mb-6">
          <h3 className="font-semibold mb-2">Tricks Won</h3>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {players.map((p) => (
              <div key={p} className="flex justify-between bg-gray-50 rounded px-3 py-1">
                <span>{p}</span>
                <span className="font-bold">{trick_counts[p] ?? 0}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="text-center text-lg font-bold mb-4">
          {tied ? "It's a tie!" : `${nsWon ? "North/South" : "East/West"} wins!`}
        </div>

        <button
          onClick={onBackToLobby}
          className="w-full bg-green-700 text-white font-semibold py-2 rounded-lg hover:bg-green-800 transition"
        >
          Back to Lobby
        </button>
      </div>
    </div>
  );
}
