"use client";

import { GameState, Card, BidInfo } from "@/lib/types";
import PlayerHand from "./PlayerHand";
import OpponentHand from "./OpponentHand";
import TrickArea from "./TrickArea";
import ScorePanel from "./ScorePanel";
import TrumpIndicator from "./TrumpIndicator";
import TrickHistory from "./TrickHistory";
import BiddingPanel from "./BiddingPanel";
import KittyExchange from "./KittyExchange";

interface Props {
  state: GameState;
  onPlayCard: (card: Card) => void;
  onBid: (bid: BidInfo | null) => void;
  onExchangeKitty: (trumpSuit: string | null, direction: string, discards: Card[]) => void;
}

export default function GameBoard({ state, onPlayCard, onBid, onExchangeKitty }: Props) {
  const { players, seat, expected_player, your_hand, legal_moves, current_trick, trick_counts, phase } = state;
  const myIndex = players.indexOf(seat);
  const isMyTurn = phase === "playing" && expected_player === seat && !state.is_complete;

  const partnerIndex = (myIndex + 2) % 4;
  const leftIndex = (myIndex + 1) % 4;
  const rightIndex = (myIndex + 3) % 4;

  const partner = players[partnerIndex];
  const left = players[leftIndex];
  const right = players[rightIndex];

  const cardsInTrick = current_trick.map((p) => p.player);
  function cardCount(playerName: string): number {
    const inCurrentTrick = cardsInTrick.includes(playerName) ? 1 : 0;
    return 12 - (state.tricks_played || 0) - inCurrentTrick;
  }

  // Bidding phase
  if (phase === "bidding") {
    return (
      <div className="min-h-screen bg-green-900 text-white flex flex-col items-center justify-center p-4">
        <div className="mb-6">
          <BiddingPanel state={state} onBid={onBid} />
        </div>
        <div className="mt-4">
          <h3 className="text-center text-green-300 text-sm mb-2">Your Hand</h3>
          <PlayerHand cards={your_hand} legalMoves={[]} isMyTurn={false} onPlay={() => {}} />
        </div>
      </div>
    );
  }

  // Kitty exchange phase
  if (phase === "kitty") {
    return (
      <div className="min-h-screen bg-green-900 text-white flex flex-col items-center justify-center p-4">
        <KittyExchange state={state} onExchange={onExchangeKitty} />
      </div>
    );
  }

  // Playing / Complete phase
  return (
    <div className="min-h-screen bg-green-900 text-white flex">
      <div className="flex-1 flex flex-col items-center justify-between p-4">
        <div className="flex-shrink-0">
          <OpponentHand
            name={partner}
            cardCount={cardCount(partner)}
            isCurrentPlayer={expected_player === partner}
            trickCount={trick_counts[partner] || 0}
            position="top"
          />
        </div>

        <div className="flex items-center justify-center gap-8 flex-1">
          <div className="flex-shrink-0">
            <OpponentHand
              name={left}
              cardCount={cardCount(left)}
              isCurrentPlayer={expected_player === left}
              trickCount={trick_counts[left] || 0}
              position="left"
            />
          </div>

          <TrickArea plays={current_trick} players={players} seat={seat} />

          <div className="flex-shrink-0">
            <OpponentHand
              name={right}
              cardCount={cardCount(right)}
              isCurrentPlayer={expected_player === right}
              trickCount={trick_counts[right] || 0}
              position="right"
            />
          </div>
        </div>

        <div className="flex-shrink-0 pb-4">
          {isMyTurn && (
            <p className="text-center text-yellow-300 font-semibold mb-2 animate-pulse">
              Your turn! Select a card to play.
            </p>
          )}
          <PlayerHand
            cards={your_hand}
            legalMoves={legal_moves}
            isMyTurn={isMyTurn}
            onPlay={onPlayCard}
          />
        </div>
      </div>

      <div className="w-64 bg-green-950 p-4 space-y-4 overflow-y-auto">
        <TrumpIndicator
          trumpSuit={state.trump_suit}
          direction={state.direction}
          bidWinner={state.bid_winner}
          winningBid={state.winning_bid}
        />
        <ScorePanel state={state} />
        <TrickHistory tricks={state.completed_tricks} />
      </div>
    </div>
  );
}
