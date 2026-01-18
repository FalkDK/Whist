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
