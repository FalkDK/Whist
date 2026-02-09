import { Card, Suit } from "./types";

const SUIT_SYMBOLS: Record<string, string> = {
  spades: "\u2660",
  hearts: "\u2665",
  diamonds: "\u2666",
  clubs: "\u2663",
  joker: "\u2605",
};

const SUIT_COLORS: Record<string, string> = {
  spades: "text-gray-900",
  clubs: "text-gray-900",
  hearts: "text-red-600",
  diamonds: "text-red-600",
  joker: "text-purple-700",
};

export function suitSymbol(suit: Suit): string {
  return SUIT_SYMBOLS[suit] || "\u2605";
}

export function suitColor(suit: Suit): string {
  return SUIT_COLORS[suit] || "text-purple-700";
}

export function isJoker(card: Card): boolean {
  return card.suit === "joker" || card.rank === "Big Joker" || card.rank === "Little Joker";
}

export function cardDisplay(card: Card): string {
  if (isJoker(card)) {
    return card.rank === "Big Joker" ? "BJ\u2605" : "LJ\u2605";
  }
  return `${card.rank}${SUIT_SYMBOLS[card.suit] || ""}`;
}

export function cardKey(card: Card): string {
  return `${card.rank}-${card.suit}`;
}

export function cardsEqual(a: Card, b: Card): boolean {
  return a.rank === b.rank && a.suit === b.suit;
}
