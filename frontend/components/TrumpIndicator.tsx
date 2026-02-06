"use client";

import { Card, Suit } from "@/lib/types";
import { suitSymbol, suitColor } from "@/lib/cards";

interface Props {
  trumpSuit: Suit | null;
  trumpCard: Card | null;
}

export default function TrumpIndicator({ trumpSuit, trumpCard }: Props) {
  if (!trumpSuit) return null;

  return (
    <div className="bg-green-800 rounded-lg p-4 text-sm">
      <h3 className="font-semibold text-green-200 mb-1">Trump</h3>
      <div className={`text-2xl font-bold ${suitColor(trumpSuit)}`}>
        <span className="bg-white rounded px-2 py-1">
          {trumpCard ? `${trumpCard.rank}${suitSymbol(trumpSuit)}` : suitSymbol(trumpSuit)}
        </span>
      </div>
      <span className="text-xs text-green-300 capitalize">{trumpSuit}</span>
    </div>
  );
}
