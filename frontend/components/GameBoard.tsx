"use client";

import { GameState, Card } from "@/lib/types";
import PlayerHand from "./PlayerHand";
import OpponentHand from "./OpponentHand";
import TrickArea from "./TrickArea";
import ScorePanel from "./ScorePanel";
import TrumpIndicator from "./TrumpIndicator";
import TrickHistory from "./TrickHistory";

interface Props {
  state: GameState;
  onPlayCard: (card: Card) => void;
}

export default function GameBoard({ state, onPlayCard }: Props) {
  const { players, seat, expected_player, your_hand, legal_moves, current_trick, trick_counts } = state;
  const myIndex = players.indexOf(seat);
  const isMyTurn = expected_player === seat && !state.is_complete;

  // Relative positions: me=bottom, partner=top, left opponent, right opponent
  const partnerIndex = (myIndex + 2) % 4;
  const leftIndex = (myIndex + 1) % 4;
  const rightIndex = (myIndex + 3) % 4;

  const partner = players[partnerIndex];
  const left = players[leftIndex];
  const right = players[rightIndex];

  // Card counts: 13 - tricks_played approximation
  // Each player starts with 13 cards, plays 1 per trick + cards in current trick
  const cardsInTrick = current_trick.map((p) => p.player);
  function cardCount(playerName: string): number {
    const played = trick_counts[playerName] || 0;
    // Each player has played `tricks_played` cards in completed tricks
    // plus potentially one in the current trick
    const inCurrentTrick = cardsInTrick.includes(playerName) ? 1 : 0;
    return 13 - state.tricks_played - inCurrentTrick;
  }

  return (
    <div className="min-h-screen bg-green-900 text-white flex">
      {/* Main play area */}
      <div className="flex-1 flex flex-col items-center justify-between p-4">
        {/* Top opponent (partner) */}
        <div className="flex-shrink-0">
          <OpponentHand
            name={partner}
            cardCount={cardCount(partner)}
            isCurrentPlayer={expected_player === partner}
            trickCount={trick_counts[partner] || 0}
            position="top"
          />
        </div>

        {/* Middle row: left opponent, trick area, right opponent */}
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

        {/* Bottom: my hand */}
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

      {/* Right sidebar */}
      <div className="w-64 bg-green-950 p-4 space-y-4 overflow-y-auto">
        <TrumpIndicator trumpSuit={state.trump_suit} trumpCard={state.trump_card} />
        <ScorePanel state={state} />
        <TrickHistory tricks={state.completed_tricks} />
      </div>
    </div>
  );
}
