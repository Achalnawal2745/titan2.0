# Socket.IO Patterns for Multiplayer Games

## 1. Game State Management

**Store game state on the server**, never trust the client.

```javascript
// Server-side
const games = {}; // In-memory store

function getGame(gameId) {
  return games[gameId];
}

function updateGame(gameId, newGameState) {
  games[gameId] = newGameState;
}
```

## 2. Broadcasting vs. Emitting

- **`io.to(gameId).emit(...)`**: Broadcast to all players in the game
- **`socket.emit(...)`**: Emit to a single player

Use `io.to(gameId).emit` for public game state changes (e.g., card played, trick collected).

Use `socket.emit` for private information (e.g., sending a player their hand).

## 3. Per-Player Hand Updates

Never broadcast the entire game state with all hands. Send each player only their own hand.

```javascript
// Server-side
updatedGame.players.forEach((player, index) => {
  const playerSocket = findSocketForPlayer(player.userId);
  if (playerSocket) {
    playerSocket.emit("hand_updated", { hand: player.hand });
  }
});
```

## 4. Error Handling

Always wrap game logic in `try/catch` blocks and emit errors to the specific player who caused them.

```javascript
// Server-side
socket.on("play_card", (data) => {
  try {
    const updatedGame = playCard(game, data.card, data.player);
    // ... broadcast updates
  } catch (error) {
    socket.emit("error", { message: error.message });
  }
});
```

## 5. Turn-Based Play

Enforce turn-based play on the server.

```javascript
// Server-side
if (player !== game.currentPlayer) {
  throw new Error("It's not your turn!");
}
```

## 6. Automatic Actions

Use `setTimeout` to create delays for UX and automate actions.

```javascript
// Server-side
if (updatedGame.currentTrick.length === 4) {
  setTimeout(() => {
    const collectedGame = collectTrick(updatedGame);
    // ... broadcast trick collected
  }, 2000); // 2-second delay
}
```

## 7. Reconnection Handling

Store `userId` in the session and have players rejoin with their `userId`.

```javascript
// Client-side
socket.on("connect", () => {
  socket.emit("rejoin_game", { gameId, userId });
});

// Server-side
socket.on("rejoin_game", (data) => {
  // Find player in game state and re-associate socket
});
```
