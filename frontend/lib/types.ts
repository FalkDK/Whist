export type Suit = "clubs" | "diamonds" | "hearts" | "spades" | "joker";
export type Rank =
  | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "10"
  | "J" | "Q" | "K" | "A" | "Little Joker" | "Big Joker";

export type Phase = "bidding" | "kitty" | "playing" | "complete";
export type BidType = "uptown" | "downtown" | "no_trump";

export interface Card {
  rank: Rank;
  suit: Suit;
  label: string;
}

export interface BidInfo {
  number: number;
  bid_type: BidType;
}

export interface Play {
  player: string;
  card: Card;
}

export interface TrickResult {
  plays: Play[];
  winner: string | null;
}

export interface GameState {
  game_id: string;
  phase: Phase;
  players: string[];
  seat: string;

  // Bidding
  expected_bidder: string | null;
  bids: Record<string, BidInfo | null>;
  bid_winner: string | null;
  winning_bid: BidInfo | null;

  // Kitty / Trump
  trump_suit: Suit | null;
  direction: string | null;
  kitty: Card[];

  // Hand
  your_hand: Card[];
  legal_moves: Card[];

  // Playing
  current_trick: Play[];
  expected_player: string | null;
  tricks_played: number;
  tricks_remaining: number;
  trick_counts: Record<string, number>;
  partnership_scores: { north_south: number; east_west: number };
  completed_tricks: TrickResult[];
  is_complete: boolean;
}

export interface LobbyGame {
  game_id: string;
  host: string;
  players: string[];
  bot_count: number;
  needed: number;
  status: string;
}
