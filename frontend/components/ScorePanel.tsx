"use client";

import { GameState } from "@/lib/types";

interface Props {
  state: GameState;
}

export default function ScorePanel({ state }: Props) {
  const { partnership_scores, tricks_played, tricks_remaining } = state;

  return (
    <div className="bg-green-800 rounded-lg p-4 text-sm space-y-2">
      <h3 className="font-semibold text-green-200">Score</h3>
      <div className="flex justify-between">
        <span>N/S ({state.players[0]}, {state.players[2]})</span>
        <span className="font-bold">{partnership_scores.north_south} pts</span>
      </div>
      <div className="flex justify-between">
        <span>E/W ({state.players[1]}, {state.players[3]})</span>
        <span className="font-bold">{partnership_scores.east_west} pts</span>
      </div>
      <hr className="border-green-600" />
      <div className="flex justify-between text-xs text-green-300">
        <span>Tricks played: {tricks_played}</span>
        <span>Remaining: {tricks_remaining}</span>
      </div>
    </div>
  );
}
