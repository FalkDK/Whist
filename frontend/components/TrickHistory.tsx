"use client";

import { TrickResult } from "@/lib/types";
import { cardDisplay } from "@/lib/cards";

interface Props {
  tricks: TrickResult[];
}

export default function TrickHistory({ tricks }: Props) {
  if (tricks.length === 0) return null;

  return (
    <div className="bg-green-800 rounded-lg p-4 text-sm max-h-60 overflow-y-auto">
      <h3 className="font-semibold text-green-200 mb-2">Trick History</h3>
      <div className="space-y-1">
        {tricks.map((trick, i) => (
          <div key={i} className="text-xs text-green-100">
            <span className="text-green-300 font-mono">{i + 1}.</span>{" "}
            <span className="font-semibold">{trick.winner}</span>:{" "}
            {trick.plays.map((p) => `${p.player} ${cardDisplay(p.card)}`).join(", ")}
          </div>
        ))}
      </div>
    </div>
  );
}
