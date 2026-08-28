# Test-Driven Development (TDD) Workflow for Games

Follow this cycle for every piece of game logic:

**1. Write a Failing Test**
- Create a new test file (e.g., `test/deck.test.js`)
- Write a test case that describes the desired behavior
- The test should fail because the implementation doesn't exist yet

**2. Run the Test**
- Run the test to verify it fails as expected
- This confirms the test is working correctly

**3. Write the Minimal Code**
- Write the simplest possible code to make the test pass
- Don't add any extra features or optimizations yet

**4. Run the Tests Again**
- Run all tests to verify they all pass
- This confirms the new code works and didn't break anything

**5. Refactor (Optional)**
- Clean up the code, improve readability, remove duplication
- Run tests again to ensure refactoring didn't break anything

**6. Commit**
- Commit the changes with a clear message

## Example: Deck Creation

**1. Write Failing Test (`test/deck.test.js`)**
```javascript
it("should create a deck of 55 cards", () => {
  const deck = createDeck();
  assert.strictEqual(deck.length, 55);
});
```

**2. Run Test (Fails)**
`ReferenceError: createDeck is not defined`

**3. Write Minimal Code (`game-logic/deck.js`)**
```javascript
function createDeck() {
  return Array(55).fill({});
}
module.exports = { createDeck };
```

**4. Run Test (Passes)**
`✔ should create a deck of 55 cards`

**5. Refactor**
- Implement the actual card creation logic
- Add more tests for card types, suits, ranks

**6. Commit**
`feat: implement deck creation with 55 cards`
