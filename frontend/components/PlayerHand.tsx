"use client";

import { Card } from "@/lib/types";
import { cardDisplay, cardKey, cardsEqual, suitColor } from "@/lib/cards";

interface Props {
  cards: Card[];
  legalMoves: Card[];
  isMyTurn: boolean;
  onPlay: (card: Card) => void;
}

export default function PlayerHand({ cards, legalMoves, isMyTurn, onPlay }: Props) {
  const sortedCards = [...cards].sort((a, b) => {
    const suitOrder = ["spades", "hearts", "diamonds", "clubs"];
    const rankOrder = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"];
    const sd = suitOrder.indexOf(a.suit) - suitOrder.indexOf(b.suit);
    if (sd !== 0) return sd;
    return rankOrder.indexOf(a.rank) - rankOrder.indexOf(b.rank);
  });

  function isLegal(card: Card): boolean {
    return legalMoves.some((m) => cardsEqual(m, card));
  }

  return (
    <div className="flex justify-center gap-1 flex-wrap">
      {sortedCards.map((card) => {
        const legal = isMyTurn && isLegal(card);
        const playable = isMyTurn && legal;
        return (
          <button
            key={cardKey(card)}
            onClick={() => playable && onPlay(card)}
            disabled={!playable}
            className={`
              relative w-14 h-20 rounded-lg border-2 flex flex-col items-center justify-center
              text-lg font-bold transition-all select-none
              ${suitColor(card.suit)}
              ${playable
                ? "bg-white border-yellow-400 hover:border-yellow-300 hover:-translate-y-2 cursor-pointer shadow-lg"
                : isMyTurn && !legal
                  ? "bg-gray-200 border-gray-300 opacity-50 cursor-not-allowed"
                  : "bg-white border-gray-300 cursor-default"
              }
            `}
          >
            <span className="text-xs leading-none">{card.rank}</span>
            <span className="text-xl leading-none">{cardDisplay(card).slice(-1)}</span>
          </button>
        );
      })}
    </div>
  );
}
