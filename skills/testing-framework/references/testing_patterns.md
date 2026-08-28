# Testing Patterns & Best Practices

Comprehensive guide to testing patterns for unit, integration, and E2E tests.

## Table of Contents

1. [Testing Pyramid](#testing-pyramid)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [E2E Testing](#e2e-testing)
5. [Test Organization](#test-organization)
6. [Mocking Strategies](#mocking-strategies)
7. [Assertions](#assertions)
8. [Coverage Goals](#coverage-goals)

---

## Testing Pyramid

### The Ideal Distribution

```
        /\
       /E2E\      10% - Slow, expensive, brittle
      /------\
     /  INT   \   20% - Medium speed, moderate cost
    /----------\
   /    UNIT    \ 70% - Fast, cheap, reliable
  /--------------\
```

**Unit Tests (70%)**:
- Test individual functions/methods
- Fast execution (milliseconds)
- No external dependencies
- Easy to maintain

**Integration Tests (20%)**:
- Test multiple components together
- Medium execution (seconds)
- Real database/APIs (or test instances)
- Moderate maintenance

**E2E Tests (10%)**:
- Test complete user flows
- Slow execution (minutes)
- Full application stack
- Higher maintenance

---

## Unit Testing

### What to Test

✅ **Do test**:
- Pure functions
- Business logic
- Utility functions
- Data transformations
- Edge cases
- Error handling

❌ **Don't test**:
- Third-party libraries
- Framework internals
- Trivial getters/setters

### AAA Pattern

**Arrange, Act, Assert** - The foundation of good tests:

```typescript
it('should calculate total price with tax', () => {
  // Arrange - Set up test data
  const items = [
    { price: 10, quantity: 2 },
    { price: 5, quantity: 1 },
  ];
  const taxRate = 0.1;
  
  // Act - Execute the function
  const total = calculateTotal(items, taxRate);
  
  // Assert - Verify the result
  expect(total).toBe(27.5); // (10*2 + 5*1) * 1.1
});
```

### Test Naming

Use descriptive names that explain:
1. What is being tested
2. Under what conditions
3. What the expected result is

```typescript
// ✅ Good
it('should return null when user is not found')
it('should throw error when email is invalid')
it('should calculate discount for premium users')

// ❌ Bad
it('works')
it('test user')
it('should pass')
```

### Testing Edge Cases

Always test boundary conditions:

```typescript
describe('validateAge', () => {
  it('should accept valid age', () => {
    expect(validateAge(25)).toBe(true);
  });

  it('should reject negative age', () => {
    expect(validateAge(-1)).toBe(false);
  });

  it('should reject zero', () => {
    expect(validateAge(0)).toBe(false);
  });

  it('should accept minimum valid age', () => {
    expect(validateAge(1)).toBe(true);
  });

  it('should accept maximum valid age', () => {
    expect(validateAge(120)).toBe(true);
  });

  it('should reject age over maximum', () => {
    expect(validateAge(121)).toBe(false);
  });

  it('should handle non-integer values', () => {
    expect(validateAge(25.5)).toBe(true);
  });
});
```

### Testing Async Code

```typescript
// Using async/await
it('should fetch user data', async () => {
  const user = await fetchUser('123');
  expect(user.id).toBe('123');
});

// Testing promises
it('should resolve with data', () => {
  return fetchUser('123').then(user => {
    expect(user.id).toBe('123');
  });
});

// Testing rejections
it('should reject when user not found', async () => {
  await expect(fetchUser('invalid')).rejects.toThrow('User not found');
});
```

### Testing Error Handling

```typescript
describe('Error Handling', () => {
  it('should throw error for invalid input', () => {
    expect(() => divide(10, 0)).toThrow('Division by zero');
  });

  it('should throw specific error type', () => {
    expect(() => parseJSON('invalid')).toThrow(SyntaxError);
  });

  it('should return error object', () => {
    const result = validateEmail('invalid');
    expect(result.success).toBe(false);
    expect(result.error).toBe('Invalid email format');
  });
});
```

---

## Integration Testing

### What to Test

✅ **Do test**:
- API endpoints
- Database operations
- Multiple components working together
- Data flow between layers
- Authentication/authorization

### Testing API Endpoints

```typescript
describe('POST /api/posts', () => {
  let authToken: string;

  beforeAll(async () => {
    // Setup: Create test user and get auth token
    authToken = await createTestUser();
  });

  afterAll(async () => {
    // Teardown: Clean up test data
    await cleanupTestData();
  });

  it('should create new post', async () => {
    const response = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        title: 'Test Post',
        content: 'Test content',
      });

    expect(response.status).toBe(201);
    expect(response.body).toMatchObject({
      title: 'Test Post',
      content: 'Test content',
    });
  });

  it('should return 401 without auth', async () => {
    const response = await request(app)
      .post('/api/posts')
      .send({
        title: 'Test Post',
        content: 'Test content',
      });

    expect(response.status).toBe(401);
  });

  it('should return 400 for invalid data', async () => {
    const response = await request(app)
      .post('/api/posts')
      .set('Authorization', `Bearer ${authToken}`)
      .send({
        title: '', // Invalid: empty title
      });

    expect(response.status).toBe(400);
    expect(response.body.error).toBeDefined();
  });
});
```

### Testing Database Operations

```typescript
describe('UserRepository', () => {
  let db: Database;

  beforeAll(async () => {
    // Setup test database
    db = await createTestDatabase();
  });

  afterAll(async () => {
    // Cleanup
    await db.close();
  });

  beforeEach(async () => {
    // Clear data before each test
    await db.clear();
  });

  it('should create user', async () => {
    const user = await db.user.create({
      email: 'test@example.com',
      name: 'Test User',
    });

    expect(user.id).toBeDefined();
    expect(user.email).toBe('test@example.com');
  });

  it('should find user by email', async () => {
    await db.user.create({
      email: 'test@example.com',
      name: 'Test User',
    });

    const user = await db.user.findByEmail('test@example.com');

    expect(user).toBeDefined();
    expect(user.name).toBe('Test User');
  });

  it('should return null for non-existent user', async () => {
    const user = await db.user.findByEmail('nonexistent@example.com');
    expect(user).toBeNull();
  });
});
```

---

## E2E Testing

### What to Test

✅ **Do test**:
- Critical user journeys
- Happy paths
- Common error scenarios
- Cross-browser compatibility

❌ **Don't test**:
- Every possible combination
- Unit-level logic
- Third-party integrations (unless critical)

### Page Object Pattern

Organize E2E tests with page objects:

```typescript
// pages/LoginPage.ts
export class LoginPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.page.fill('input[name="email"]', email);
    await this.page.fill('input[name="password"]', password);
    await this.page.click('button[type="submit"]');
  }

  async getErrorMessage() {
    return await this.page.locator('.error-message').textContent();
  }
}

// tests/login.test.ts
test('should login successfully', async ({ page }) => {
  const loginPage = new LoginPage(page);
  
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password123');
  
  await expect(page).toHaveURL('/dashboard');
});
```

### Testing User Flows

```typescript
test('complete purchase flow', async ({ page }) => {
  // 1. Login
  await page.goto('/login');
  await page.fill('input[name="email"]', 'user@example.com');
  await page.fill('input[name="password"]', 'password');
  await page.click('button[type="submit"]');
  
  // 2. Browse products
  await page.goto('/products');
  await expect(page.locator('.product-grid')).toBeVisible();
  
  // 3. Add to cart
  await page.click('.product:first-child .add-to-cart');
  await expect(page.locator('.cart-badge')).toContainText('1');
  
  // 4. Checkout
  await page.click('.cart-icon');
  await page.click('button:has-text("Checkout")');
  
  // 5. Fill payment
  await page.fill('input[name="cardNumber"]', '4242424242424242');
  await page.click('button:has-text("Pay")');
  
  // 6. Verify success
  await expect(page.locator('.success-message')).toBeVisible();
});
```

---

## Test Organization

### File Structure

```
src/
├── components/
│   ├── Button.tsx
│   └── Button.test.tsx          # Co-located with component
├── utils/
│   ├── format.ts
│   └── format.test.ts           # Co-located with utility
tests/
├── integration/
│   ├── api/
│   │   ├── posts.test.ts
│   │   └── users.test.ts
│   └── database/
│       └── queries.test.ts
└── e2e/
    ├── auth.test.ts
    ├── checkout.test.ts
    └── dashboard.test.ts
```

### Test Suites

Group related tests with `describe`:

```typescript
describe('UserService', () => {
  describe('createUser', () => {
    it('should create user with valid data', () => {});
    it('should reject duplicate email', () => {});
    it('should validate email format', () => {});
  });

  describe('updateUser', () => {
    it('should update user profile', () => {});
    it('should reject invalid data', () => {});
  });

  describe('deleteUser', () => {
    it('should soft delete user', () => {});
    it('should cascade delete related data', () => {});
  });
});
```

---

## Mocking Strategies

### When to Mock

✅ **Mock**:
- External APIs
- Databases (in unit tests)
- File system operations
- Time/dates
- Random number generation

❌ **Don't mock**:
- Code you're testing
- Simple utilities
- Constants

### Mocking Functions

```typescript
// Create mock function
const mockFn = vi.fn();

// Mock implementation
mockFn.mockImplementation((x) => x * 2);

// Mock return value
mockFn.mockReturnValue(42);

// Mock resolved promise
mockFn.mockResolvedValue({ id: '123' });

// Mock rejected promise
mockFn.mockRejectedValue(new Error('Failed'));

// Verify calls
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledWith('arg');
expect(mockFn).toHaveBeenCalledTimes(2);
```

### Mocking Modules

```typescript
// Mock entire module
vi.mock('~/lib/db', () => ({
  db: {
    user: {
      findMany: vi.fn(),
      create: vi.fn(),
    },
  },
}));

// Mock specific exports
vi.mock('~/lib/auth', () => ({
  getSession: vi.fn(),
  requireAuth: vi.fn(),
}));

// Partial mock (keep some real implementations)
vi.mock('~/lib/utils', async () => {
  const actual = await vi.importActual('~/lib/utils');
  return {
    ...actual,
    fetchData: vi.fn(), // Only mock this one
  };
});
```

### Mocking Time

```typescript
// Use fake timers
vi.useFakeTimers();

// Set specific date
vi.setSystemTime(new Date('2024-01-01'));

// Advance time
vi.advanceTimersByTime(1000); // 1 second

// Run all timers
vi.runAllTimers();

// Restore real timers
vi.useRealTimers();
```

---

## Assertions

### Common Matchers

```typescript
// Equality
expect(value).toBe(expected);           // ===
expect(value).toEqual(expected);        // Deep equality
expect(value).toStrictEqual(expected);  // Strict deep equality

// Truthiness
expect(value).toBeTruthy();
expect(value).toBeFalsy();
expect(value).toBeNull();
expect(value).toBeUndefined();
expect(value).toBeDefined();

// Numbers
expect(value).toBeGreaterThan(3);
expect(value).toBeGreaterThanOrEqual(3);
expect(value).toBeLessThan(5);
expect(value).toBeLessThanOrEqual(5);
expect(value).toBeCloseTo(0.3); // Floating point

// Strings
expect(string).toContain('substring');
expect(string).toMatch(/regex/);
expect(string).toHaveLength(10);

// Arrays
expect(array).toContain(item);
expect(array).toHaveLength(3);
expect(array).toEqual(expect.arrayContaining([1, 2]));

// Objects
expect(object).toHaveProperty('key');
expect(object).toMatchObject({ key: 'value' });

// Functions
expect(fn).toThrow();
expect(fn).toThrow('Error message');
expect(fn).toThrow(ErrorType);

// Promises
await expect(promise).resolves.toBe(value);
await expect(promise).rejects.toThrow();

// Mocks
expect(mockFn).toHaveBeenCalled();
expect(mockFn).toHaveBeenCalledWith(arg);
expect(mockFn).toHaveBeenCalledTimes(2);
expect(mockFn).toHaveReturnedWith(value);
```

---

## Coverage Goals

### Target Coverage

- **Statements**: 80%+
- **Branches**: 75%+
- **Functions**: 80%+
- **Lines**: 80%+

### What to Cover

**High Priority** (aim for 100%):
- Business logic
- Utility functions
- Data transformations
- Validation logic
- Error handling

**Medium Priority** (aim for 80%):
- API endpoints
- Database queries
- UI components

**Low Priority** (can skip):
- Configuration files
- Type definitions
- Simple getters/setters
- Third-party wrappers

### Measuring Coverage

```bash
# Vitest
vitest --coverage

# Jest
jest --coverage

# View HTML report
open coverage/index.html
```

---

## Best Practices

1. ✅ Write tests before fixing bugs (TDD)
2. ✅ Keep tests simple and focused
3. ✅ Use descriptive test names
4. ✅ Follow AAA pattern
5. ✅ Test edge cases
6. ✅ Mock external dependencies
7. ✅ Keep tests fast
8. ✅ Make tests independent
9. ✅ Use setup/teardown properly
10. ✅ Maintain tests like production code

---

## Common Mistakes

1. ❌ Testing implementation details
2. ❌ Not testing edge cases
3. ❌ Slow tests (not using mocks)
4. ❌ Flaky tests (timing issues)
5. ❌ Tests that depend on each other
6. ❌ Not cleaning up after tests
7. ❌ Too many E2E tests
8. ❌ Vague test names
9. ❌ Testing third-party code
10. ❌ Ignoring failing tests

---

## Further Reading

- [Vitest Documentation](https://vitest.dev/)
- [Playwright Documentation](https://playwright.dev/)
- [Testing Library](https://testing-library.com/)
- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
