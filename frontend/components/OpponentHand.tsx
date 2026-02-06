"use client";

interface Props {
  name: string;
  cardCount: number;
  isCurrentPlayer: boolean;
  trickCount: number;
  position: "top" | "left" | "right";
}

export default function OpponentHand({ name, cardCount, isCurrentPlayer, trickCount, position }: Props) {
  const isHorizontal = position === "top";

  return (
    <div className={`flex flex-col items-center gap-1 ${isCurrentPlayer ? "animate-pulse" : ""}`}>
      <span className={`text-sm font-semibold ${isCurrentPlayer ? "text-yellow-300" : "text-green-200"}`}>
        {name} {isCurrentPlayer && "(thinking...)"}
      </span>
      <div className={`flex ${isHorizontal ? "flex-row" : "flex-col"} gap-0.5`}>
        {Array.from({ length: Math.min(cardCount, 13) }).map((_, i) => (
          <div
            key={i}
            className={`
              ${isHorizontal ? "w-6 h-9" : "w-9 h-6"}
              rounded-sm bg-blue-800 border border-blue-600
            `}
          />
        ))}
      </div>
      <span className="text-xs text-green-300">Tricks: {trickCount}</span>
    </div>
  );
}
