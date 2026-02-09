"use client";

import { Play } from "@/lib/types";
import { suitColor, suitSymbol, isJoker } from "@/lib/cards";

interface Props {
  plays: Play[];
  players: string[];
  seat: string;
}

export default function TrickArea({ plays, players, seat }: Props) {
  const myIndex = players.indexOf(seat);
  const positions = ["bottom", "left", "top", "right"];
  const seatToPosition: Record<string, string> = {};
  for (let i = 0; i < 4; i++) {
    seatToPosition[players[(myIndex + i) % 4]] = positions[i];
  }

  const positionStyles: Record<string, string> = {
    bottom: "bottom-0 left-1/2 -translate-x-1/2",
    top: "top-0 left-1/2 -translate-x-1/2",
    left: "left-0 top-1/2 -translate-y-1/2",
    right: "right-0 top-1/2 -translate-y-1/2",
  };

  return (
    <div className="relative w-56 h-44">
      {plays.map((play) => {
        const pos = seatToPosition[play.player] || "bottom";
        return (
          <div
            key={play.player}
            className={`absolute ${positionStyles[pos]} transition-all duration-300`}
          >
            <div
              className={`w-14 h-20 rounded-lg border-2 border-gray-300 bg-white flex flex-col items-center justify-center font-bold ${suitColor(play.card.suit)}`}
            >
              <span className="text-xs">
                {isJoker(play.card) ? (play.card.rank === "Big Joker" ? "BJ" : "LJ") : play.card.rank}
              </span>
              <span className="text-xl">
                {isJoker(play.card) ? "\u2605" : suitSymbol(play.card.suit)}
              </span>
            </div>
            <span className="block text-center text-xs text-green-200 mt-0.5">
              {play.player}
            </span>
          </div>
        );
      })}
      {plays.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center text-green-400 text-sm">
          Play area
        </div>
      )}
    </div>
  );
}
