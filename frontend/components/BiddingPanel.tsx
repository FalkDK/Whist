"use client";

import { GameState, BidInfo, BidType } from "@/lib/types";
import { useState } from "react";

interface Props {
  state: GameState;
  onBid: (bid: BidInfo | null) => void;
}

const BID_TYPES: { label: string; value: BidType }[] = [
  { label: "Uptown", value: "uptown" },
  { label: "Downtown", value: "downtown" },
  { label: "No Trump", value: "no_trump" },
];

export default function BiddingPanel({ state, onBid }: Props) {
  const [selectedNumber, setSelectedNumber] = useState(3);
  const [selectedType, setSelectedType] = useState<BidType>("uptown");
  const isMyBid = state.expected_bidder === state.seat;

  const currentHighBid = state.winning_bid;

  function canBid(number: number, bidType: BidType): boolean {
    if (!currentHighBid) return true;
    const typeRank: Record<BidType, number> = { uptown: 0, downtown: 1, no_trump: 2 };
    const newStrength = number * 10 + typeRank[bidType];
    const curStrength = currentHighBid.number * 10 + typeRank[currentHighBid.bid_type];
    return newStrength > curStrength;
  }

  return (
    <div className="bg-green-800 rounded-xl p-6 max-w-md mx-auto">
      <h2 className="text-xl font-bold text-center mb-4 text-yellow-300">Bidding Round</h2>

      {/* Current bids */}
      <div className="mb-4 space-y-1">
        {Object.entries(state.bids).map(([player, bid]) => (
          <div key={player} className="flex justify-between text-sm">
            <span className="text-green-200">{player}</span>
            <span className="font-semibold">
              {bid ? `${bid.number} ${bid.bid_type.replace("_", " ")}` : "Pass"}
            </span>
          </div>
        ))}
      </div>

      {isMyBid ? (
        <div className="space-y-3">
          <p className="text-yellow-300 text-center font-semibold animate-pulse">Your turn to bid!</p>

          {/* Bid number selector */}
          <div className="flex gap-1 justify-center">
            {[3, 4, 5, 6, 7].map((n) => (
              <button
                key={n}
                onClick={() => setSelectedNumber(n)}
                className={`w-10 h-10 rounded-lg font-bold transition ${
                  selectedNumber === n
                    ? "bg-yellow-400 text-green-900"
                    : "bg-green-700 text-white hover:bg-green-600"
                }`}
              >
                {n}
              </button>
            ))}
          </div>

          {/* Bid type selector */}
          <div className="flex gap-2 justify-center">
            {BID_TYPES.map(({ label, value }) => (
              <button
                key={value}
                onClick={() => setSelectedType(value)}
                className={`px-3 py-2 rounded-lg text-sm font-semibold transition ${
                  selectedType === value
                    ? "bg-yellow-400 text-green-900"
                    : "bg-green-700 text-white hover:bg-green-600"
                }`}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Action buttons */}
          <div className="flex gap-3 justify-center mt-2">
            <button
              onClick={() => onBid({ number: selectedNumber, bid_type: selectedType })}
              disabled={!canBid(selectedNumber, selectedType)}
              className={`px-6 py-2 rounded-lg font-bold transition ${
                canBid(selectedNumber, selectedType)
                  ? "bg-yellow-500 text-green-900 hover:bg-yellow-400"
                  : "bg-gray-500 text-gray-300 cursor-not-allowed"
              }`}
            >
              Bid {selectedNumber} {selectedType.replace("_", " ")}
            </button>
            <button
              onClick={() => onBid(null)}
              className="px-6 py-2 rounded-lg font-bold bg-red-700 text-white hover:bg-red-600 transition"
            >
              Pass
            </button>
          </div>
        </div>
      ) : (
        <div className="text-center">
          <p className="text-green-300">
            Waiting for <span className="font-bold text-white">{state.expected_bidder}</span> to bid...
          </p>
        </div>
      )}
    </div>
  );
}
