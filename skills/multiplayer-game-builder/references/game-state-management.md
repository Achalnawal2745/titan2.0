# Game State Management Patterns

## 1. Immutable State Updates

**Never mutate the game state directly.** Always create a new game state object with the updated values. This makes debugging easier and prevents unexpected side effects.

**Bad (Mutation)**:
```javascript
game.currentPlayer = nextPlayer;
game.currentTrick.push(card);
return game;
```

**Good (Immutable)**:
```javascript
const newTrick = [...game.currentTrick, card];
return { ...game, currentTrick: newTrick, currentPlayer: nextPlayer };
```

## 2. Single Source of Truth

The **server is the single source of truth** for game state. The client should only render the state it receives from the server.

## 3. Input Validation

Validate all player inputs on the server before updating the game state.

- Is it the player's turn?
- Does the player have the card they're trying to play?
- Is the bid valid?
- Is the move legal according to the game rules?

## 4. Game State Structure

Design a clear and predictable game state structure.

```json
{
  "players": [
    { "id": 0, "hand": [...], "userId": "..." },
    { "id": 1, "hand": [...], "userId": "..." },
    { "id": 2, "hand": [...], "userId": "..." },
    { "id": 3, "hand": [...], "userId": "..." }
  ],
  "scores": { "A": 0, "B": 0 },
  "deck": [],
  "nest": [],
  "bidding": {
    "highestBid": 185000,
    "highestBidder": 1,
    "passes": 2,
    "biddingEnded": false,
    "trumpSuit": null
  },
  "tricks": [
    { "cards": [...], "winner": 0 }
  ],
  "currentTrick": [
    { "card": {...}, "player": 1 },
    { "card": {...}, "player": 2 }
  ],
  "currentPlayer": 3,
  "declarer": 1,
  "round": 1
}
```

## 5. Game Logic as Pure Functions

Write game logic as pure functions that take the current game state and an action, and return the new game state.

```javascript
function playCard(game, card, player) {
  // ... validation
  const newGameState = { ... };
  return newGameState;
}
```

This makes the logic easy to test and reason about.
