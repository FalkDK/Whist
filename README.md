# Whist

WhistGameApp focuses on the core mechanics of the classic trick-taking game.

## Phase 1: Core card primitives

The first phase introduces the foundational card and deck models so that later
phases can focus on game rules, trick resolution, and scoring.

```python
from whist import Deck

deck = Deck()
deck.shuffle()
hand = deck.deal(13)
```

## Phase 2: Trick resolution and scoring

Phase two introduces trick resolution and basic Whist scoring for the two
partnerships.

```python
from whist import Deal, Rank, Suit, Trick

players = ["North", "East", "South", "West"]
deal = Deal(players)
trick = Trick()

trick.add_play("North", deal.hand_for("North").pop())
trick.add_play("East", deal.hand_for("East").pop())
trick.add_play("South", deal.hand_for("South").pop())
trick.add_play("West", deal.hand_for("West").pop())

winner = trick.winner(trump=Suit.SPADES)
if winner:
    deal.record_trick(winner)

print(deal.partnership_points())
```

## Phase 3: Deal play validation

Phase three introduces basic play validation so that players must follow suit
when possible.

```python
from whist import Deal, Suit, Trick

players = ["North", "East", "South", "West"]
deal = Deal(players)
trick = Trick()

card = deal.hand_for("North")[0]
deal.play_card("North", card, trick)
```
