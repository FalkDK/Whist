"use client";

import { GameState, Card, Suit } from "@/lib/types";
import { cardKey, suitColor, suitSymbol, isJoker, cardsEqual } from "@/lib/cards";
import { useState } from "react";

interface Props {
  state: GameState;
  onExchange: (trumpSuit: string | null, direction: string, discards: Card[]) => void;
}

const SUITS: { label: string; value: Suit; symbol: string }[] = [
  { label: "Spades", value: "spades", symbol: "\u2660" },
  { label: "Hearts", value: "hearts", symbol: "\u2665" },
  { label: "Diamonds", value: "diamonds", symbol: "\u2666" },
  { label: "Clubs", value: "clubs", symbol: "\u2663" },
];

export default function KittyExchange({ state, onExchange }: Props) {
  const isBidWinner = state.bid_winner === state.seat;
  const isNoTrump = state.winning_bid?.bid_type === "no_trump";

  const [selectedTrump, setSelectedTrump] = useState<Suit>("spades");
  const [selectedDiscards, setSelectedDiscards] = useState<Card[]>([]);

  const direction = state.winning_bid?.bid_type === "downtown" ? "downtown" : "uptown";

  // Merge hand + kitty for the bid winner's view
  const allCards = [...state.your_hand, ...state.kitty];
  const sortedCards = [...allCards].sort((a, b) => {
    if (isJoker(a) && !isJoker(b)) return -1;
    if (!isJoker(a) && isJoker(b)) return 1;
    if (isJoker(a) && isJoker(b)) return a.rank === "Big Joker" ? -1 : 1;
    const suitOrder = ["spades", "hearts", "diamonds", "clubs"];
    const rankOrder = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"];
    const sd = suitOrder.indexOf(a.suit) - suitOrder.indexOf(b.suit);
    if (sd !== 0) return sd;
    return rankOrder.indexOf(a.rank) - rankOrder.indexOf(b.rank);
  });

  function toggleDiscard(card: Card) {
    const isSelected = selectedDiscards.some((d) => cardsEqual(d, card));
    if (isSelected) {
      setSelectedDiscards(selectedDiscards.filter((d) => !cardsEqual(d, card)));
    } else if (selectedDiscards.length < 6) {
      setSelectedDiscards([...selectedDiscards, card]);
    }
  }

  function handleSubmit() {
    const trumpSuit = isNoTrump ? null : selectedTrump;
    onExchange(trumpSuit, direction, selectedDiscards);
  }

  if (!isBidWinner) {
    return (
      <div className="bg-green-800 rounded-xl p-6 max-w-md mx-auto text-center">
        <h2 className="text-xl font-bold text-yellow-300 mb-3">Kitty Exchange</h2>
        <p className="text-green-300">
          Waiting for <span className="font-bold text-white">{state.bid_winner}</span> to choose trump and discard...
        </p>
        {state.winning_bid && (
          <p className="text-sm text-green-400 mt-2">
            Winning bid: {state.winning_bid.number} {state.winning_bid.bid_type.replace("_", " ")}
          </p>
        )}
      </div>
    );
  }

  return (
    <div className="bg-green-800 rounded-xl p-6 max-w-2xl mx-auto">
      <h2 className="text-xl font-bold text-center text-yellow-300 mb-2">You won the bid!</h2>
      {state.winning_bid && (
        <p className="text-center text-green-300 text-sm mb-4">
          Your bid: {state.winning_bid.number} {state.winning_bid.bid_type.replace("_", " ")}
        </p>
      )}

      {/* Trump suit selection */}
      {!isNoTrump && (
        <div className="mb-4">
          <h3 className="font-semibold text-green-200 mb-2 text-center">Choose Trump Suit</h3>
          <div className="flex gap-2 justify-center">
            {SUITS.map(({ label, value, symbol }) => (
              <button
                key={value}
                onClick={() => setSelectedTrump(value)}
                className={`px-4 py-2 rounded-lg font-semibold transition ${
                  selectedTrump === value
                    ? "bg-yellow-400 text-green-900"
                    : "bg-green-700 text-white hover:bg-green-600"
                }`}
              >
                {symbol} {label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Card selection for discards */}
      <div className="mb-4">
        <h3 className="font-semibold text-green-200 mb-2 text-center">
          Select 6 cards to discard ({selectedDiscards.length}/6)
        </h3>
        <div className="flex flex-wrap gap-1 justify-center">
          {sortedCards.map((card) => {
            const selected = selectedDiscards.some((d) => cardsEqual(d, card));
            return (
              <button
                key={cardKey(card)}
                onClick={() => toggleDiscard(card)}
                className={`
                  relative w-14 h-20 rounded-lg border-2 flex flex-col items-center justify-center
                  text-lg font-bold transition-all select-none
                  ${suitColor(card.suit)}
                  ${selected
                    ? "bg-red-100 border-red-500 ring-2 ring-red-400"
                    : "bg-white border-gray-300 hover:border-yellow-400 cursor-pointer"
                  }
                `}
              >
                <span className="text-xs leading-none">
                  {isJoker(card) ? (card.rank === "Big Joker" ? "BJ" : "LJ") : card.rank}
                </span>
                <span className="text-xl leading-none">
                  {isJoker(card) ? "\u2605" : suitSymbol(card.suit)}
                </span>
                {selected && (
                  <div className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-white text-xs flex items-center justify-center">
                    X
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      <div className="text-center">
        <button
          onClick={handleSubmit}
          disabled={selectedDiscards.length !== 6}
          className={`px-8 py-3 rounded-lg font-bold text-lg transition ${
            selectedDiscards.length === 6
              ? "bg-yellow-500 text-green-900 hover:bg-yellow-400"
              : "bg-gray-500 text-gray-300 cursor-not-allowed"
          }`}
        >
          Confirm Exchange
        </button>
      </div>
    </div>
  );
}
