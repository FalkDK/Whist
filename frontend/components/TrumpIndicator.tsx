"use client";

import { Suit } from "@/lib/types";
import { suitSymbol, suitColor } from "@/lib/cards";

interface Props {
  trumpSuit: Suit | null;
  direction: string | null;
  bidWinner: string | null;
  winningBid: { number: number; bid_type: string } | null;
}

export default function TrumpIndicator({ trumpSuit, direction, bidWinner, winningBid }: Props) {
  if (!winningBid) return null;

  return (
    <div className="bg-green-800 rounded-lg p-4 text-sm">
      <h3 className="font-semibold text-green-200 mb-1">Contract</h3>
      <div className="text-lg font-bold text-white mb-1">
        {winningBid.number} {winningBid.bid_type.replace("_", " ")}
      </div>
      {trumpSuit && trumpSuit !== "joker" && (
        <div className={`text-2xl font-bold ${suitColor(trumpSuit)}`}>
          <span className="bg-white rounded px-2 py-1">
            {suitSymbol(trumpSuit)}
          </span>
        </div>
      )}
      {direction && (
        <span className="text-xs text-green-300 capitalize">{direction}</span>
      )}
      {bidWinner && (
        <div className="text-xs text-green-400 mt-1">Won by: {bidWinner}</div>
      )}
    </div>
  );
}
