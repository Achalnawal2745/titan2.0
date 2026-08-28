---
name: "multiplayer-game-builder"
description: "Specialized skill for multiplayer game builder workflows and automation."
---

# Multiplayer Game Builder

Build multiplayer turn-based games from scratch using a proven workflow that combines template-based rapid development, Test-Driven Development (TDD), and real-time Socket.IO integration.

## When to Use This Skill

Use this skill when building:
- Card games (poker, rummy, bridge, hearts, spades)
- Board games (chess, checkers, monopoly)
- Turn-based strategy games
- Any game requiring real-time multiplayer with game state synchronization

## Core Principles

1. **Template-Based Rapid Development**: Find and adapt existing open-source templates to save 50%+ development time
2. **Test-Driven Development**: Write tests first, implement to pass tests, ensure high code quality
3. **Immutable State**: Never mutate game state, always return new objects
4. **Progressive Implementation**: Build in phases, test each before moving forward
5. **Comprehensive Documentation**: Maintain implementation plans and execution logs

## The Development Workflow

### Phase 1: Research & Planning (1-2 days)

**Research Game Rules**

Deeply understand and document the complete rules. Create a rulebook that covers:
- Deck/board composition
- Player count and teams
- Setup and dealing
- Turn structure
- Winning conditions
- Special rules and edge cases

**Find Similar Templates**

Use the `find_game_templates.py` script to search GitHub:
```bash
python /home/ubuntu/skills/multiplayer-game-builder/scripts/find_game_templates.py "hearts card game"
```

**Evaluate Templates**

Use criteria from `references/github-template-evaluation.md`:
- Core functionality (auth, lobby, rooms, real-time, database)
- Technical quality (code quality, tech stack, architecture)
- Project health (stars, activity, contributors)
- Ease of use (demo, documentation, setup)

**Create Implementation Plan**

Use `templates/implementation-plan-template.md` to structure the project.

### Phase 2: Core Game Logic (TDD) (1-2 weeks)

Follow strict Test-Driven Development. See `references/tdd-workflow.md` for detailed workflow.

**Setup Test Infrastructure**

Generate boilerplate test files:
```bash
python /home/ubuntu/skills/multiplayer-game-builder/scripts/generate_test_suite.py "my-game"
```

**TDD Cycle for Each Module**

For each game logic module (deck, bidding, playing, scoring):

1. Write a failing test
2. Run test to verify it fails
3. Write minimal code to pass
4. Run tests again to verify pass
5. Refactor if needed
6. Commit with clear message

**Example: Deck Creation**

```javascript
// test/deck.test.js
it("should create a deck of 52 cards", () => {
  const deck = createDeck();
  assert.strictEqual(deck.length, 52);
});

// game-logic/deck.js
function createDeck() {
  // Implementation here
}
```

**Validate Game State**

During development, validate game state structure:
```bash
python /home/ubuntu/skills/multiplayer-game-builder/scripts/validate_game_state.py "game_state.json"
```

**Key Modules to Implement**

- **Deck/Board**: Card/piece generation, shuffling
- **Dealing**: Distribute cards/pieces to players
- **Game Actions**: Bidding, playing, moving
- **Validation**: Turn order, legal moves, rule enforcement
- **Trick/Round Collection**: Determine winners
- **Scoring**: Calculate and track scores
- **Game Orchestration**: Coordinate all modules

### Phase 3: Real-Time Multiplayer (1 week)

Integrate game logic with Socket.IO. See `references/socketio-patterns.md` for patterns.

**Setup Socket Handlers**

Start with `templates/socket-handler-template.js`:

```javascript
const games = {}; // In-memory game store

module.exports = function(io, socket) {
  socket.on("create_game", (data, ack) => {
    const gameId = generateId();
    games[gameId] = createGame();
    ack({ gameId });
  });
  
  socket.on("join_game", (data, ack) => {
    // Join logic
  });
  
  socket.on("play_card", (data) => {
    try {
      const game = games[data.gameId];
      const updatedGame = playCard(game, data.card, data.player);
      games[data.gameId] = updatedGame;
      io.to(data.gameId).emit("card_played", updatedGame);
    } catch (error) {
      socket.emit("error", { message: error.message });
    }
  });
};
```

**Key Patterns**

- **Broadcasting**: Use `io.to(gameId).emit()` for public state changes
- **Private Data**: Use `socket.emit()` for player-specific data (hands)
- **Turn Validation**: Enforce turn-based play on server
- **Error Handling**: Wrap all logic in try/catch
- **Automatic Actions**: Use `setTimeout()` for delays (e.g., trick collection)

### Phase 4: User Interface (1 week)

Build client-side interface that connects to Socket.IO.

**UI Components**

- Game board/table
- Player hands
- Action controls (buttons for bidding, playing)
- Current game state display
- Score tracking

**Client-Side Socket Integration**

```javascript
const socket = io();

socket.emit("join_game", { gameId, userId });

socket.on("card_played", (data) => {
  renderGameState(data);
});

$("#play-card-btn").click(() => {
  socket.emit("play_card", { gameId, card, player });
});
```

**State Rendering**

Update UI in real-time as server broadcasts state changes.

### Phase 5: Polish & Production (1-2 weeks)

**Game-Over Condition**

Implement logic to end game and declare winner.

**Persistence (Optional)**

Integrate database (PostgreSQL, Redis) to save game state.

**UI/UX Polish**

- Card images instead of text
- Animations (card playing, trick collection)
- Sound effects
- Mobile responsive design

**Deployment**

Deploy to production server with proper monitoring.

## Best Practices

**Immutable State Management**

See `references/game-state-management.md` for patterns:

```javascript
// Bad: Mutation
game.currentPlayer = nextPlayer;

// Good: Immutable
return { ...game, currentPlayer: nextPlayer };
```

**Error Handling**

Always wrap game logic in try/catch and emit errors to specific players.

**Logging**

Use `templates/execution-log-template.md` to track:
- Tasks completed
- Architectural decisions
- Code snippets for critical components
- Lessons learned
- Test results

## Common Game Patterns

See `references/common-game-patterns.md` for reusable patterns:

- Turn-based play
- Bidding systems
- Trick-taking
- Scoring systems
- Round management

## Resources

**Scripts** (`scripts/`):
- `find_game_templates.py`: Search GitHub for similar games
- `generate_test_suite.py`: Create boilerplate test files
- `validate_game_state.py`: Validate game state structure

**Templates** (`templates/`):
- `implementation-plan-template.md`: Project planning structure
- `execution-log-template.md`: Track implementation progress
- `game-logic-template.js`: Starter code for game modules
- `socket-handler-template.js`: Socket.IO boilerplate
- `test-suite-template.js`: Test structure

**References** (`references/`):
- `tdd-workflow.md`: Detailed TDD process
- `socketio-patterns.md`: Real-time multiplayer patterns
- `game-state-management.md`: State management best practices
- `github-template-evaluation.md`: Template selection criteria
- `common-game-patterns.md`: Reusable game mechanics
