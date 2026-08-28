# Common Game Patterns

## 1. Turn-Based Play

```javascript
function advanceTurn(game) {
  const nextPlayer = (game.currentPlayer + 1) % 4;
  return { ...game, currentPlayer: nextPlayer };
}
```

## 2. Bidding Systems

```javascript
function placeBid(game, bid, player) {
  // ... validation
  if (bid === "pass") {
    // ... handle pass
  } else {
    // ... handle bid
  }
  return newGameState;
}
```

## 3. Trick-Taking

```javascript
function determineTrickWinner(trick, trumpSuit) {
  // ... logic to find winner
  return winningPlayer;
}
```

## 4. Scoring Systems

```javascript
function scoreRound(game) {
  // ... logic to calculate scores
  const newScores = { ... };
  return { ...game, scores: newScores };
}
```

## 5. Round Management

```javascript
function nextRound(game) {
  const newGame = createGame();
  newGame.scores = game.scores; // Carry over scores
  newGame.round = game.round + 1;
  return dealCards(newGame);
}
```
