export type Suit = "clubs" | "diamonds" | "hearts" | "spades";
export type Rank =
  | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "10"
  | "J" | "Q" | "K" | "A";

export interface Card {
  rank: Rank;
  suit: Suit;
  label: string;
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
  players: string[];
  trump_suit: Suit | null;
  trump_card: Card | null;
  your_hand: Card[];
  legal_moves: Card[];
  current_trick: Play[];
  expected_player: string;
  tricks_played: number;
  tricks_remaining: number;
  trick_counts: Record<string, number>;
  partnership_scores: { north_south: number; east_west: number };
  completed_tricks: TrickResult[];
  is_complete: boolean;
  seat: string;
}

export interface LobbyGame {
  game_id: string;
  host: string;
  players: string[];
  bot_count: number;
  needed: number;
  status: string;
}
