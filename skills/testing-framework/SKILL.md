---
name: "testing-framework"
description: "Specialized skill for testing framework workflows and automation."
---

# Testing Framework

Generate production-ready tests from natural language descriptions or source code using AI.

## Overview

This skill transforms descriptions or source code into comprehensive test suites with:

- **Multiple Test Types** - Unit, Integration, E2E
- **Multiple Frameworks** - Vitest, Jest, Playwright
- **Complete Coverage** - Happy paths, edge cases, errors
- **Best Practices** - AAA pattern, mocking, assertions
- **Configuration** - Test configs with coverage
- **TypeScript** - Full type safety
- **Ready to Run** - Executable tests

## When to Use This Skill

- Writing tests for new functions or components
- Adding tests to existing code
- Creating E2E tests for user flows
- Learning testing patterns
- Improving test coverage
- Setting up testing infrastructure

## Quick Start

### Generate Unit Tests

```bash
python3 scripts/generate_tests.py "Tests for user authentication functions"
```

### Generate Tests from Source File

```bash
python3 scripts/generate_tests.py --file src/utils/format.ts
```

### Generate E2E Tests

```bash
python3 scripts/generate_tests.py "E2E tests for checkout flow" --type e2e --framework playwright
```

### Generate Test Configuration

```bash
python3 scripts/generate_tests.py --config --framework vitest
```

## Workflow

### Step 1: Choose Test Type

**Unit Tests** - Test individual functions/methods:
```
"Tests for calculateTotal function with tax and discounts"
```

**Integration Tests** - Test multiple components:
```
"Integration tests for user registration API endpoint"
```

**E2E Tests** - Test complete user flows:
```
"E2E tests for login, browse products, and checkout flow"
```

### Step 2: Generate Tests

Run the generator:

```bash
python3 scripts/generate_tests.py "<description>" [options]
```

**Options**:
- `--type unit` - Unit tests (default)
- `--type integration` - Integration tests
- `--type e2e` - E2E tests
- `--framework vitest` - Vitest (default for unit/integration)
- `--framework jest` - Jest
- `--framework playwright` - Playwright (for E2E)
- `--file <path>` - Generate tests for source file
- `--output-file <path>` - Output test file path
- `--coverage` - Include coverage configuration
- `--config` - Generate test configuration file

### Step 3: Review and Run

1. Review generated tests
2. Adjust assertions if needed
3. Run tests:
   ```bash
   vitest run
   # or
   npm test
   ```

## Examples

### Example 1: Unit Tests for Utility Function

**Description**:
```
"Tests for formatCurrency function that formats numbers as currency"
```

**Command**:
```bash
python3 scripts/generate_tests.py "Tests for formatCurrency function" --output-file utils/format.test.ts
```

**Generated** (excerpt):
```typescript
import { describe, it, expect } from 'vitest';
import { formatCurrency } from './format';

describe('formatCurrency', () => {
  it('should format positive numbers correctly', () => {
    expect(formatCurrency(1234.56)).toBe('$1,234.56');
  });

  it('should handle zero', () => {
    expect(formatCurrency(0)).toBe('$0.00');
  });

  it('should handle negative numbers', () => {
    expect(formatCurrency(-100)).toBe('-$100.00');
  });

  it('should round to 2 decimal places', () => {
    expect(formatCurrency(10.999)).toBe('$11.00');
  });
});
```

### Example 2: Tests from Source File

**Source File** (`src/utils/validate.ts`):
```typescript
export function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}
```

**Command**:
```bash
python3 scripts/generate_tests.py --file src/utils/validate.ts
```

**Generated**:
```typescript
import { describe, it, expect } from 'vitest';
import { validateEmail } from './validate';

describe('validateEmail', () => {
  it('should accept valid email', () => {
    expect(validateEmail('user@example.com')).toBe(true);
  });

  it('should reject email without @', () => {
    expect(validateEmail('userexample.com')).toBe(false);
  });

  it('should reject email without domain', () => {
    expect(validateEmail('user@')).toBe(false);
  });

  it('should reject empty string', () => {
    expect(validateEmail('')).toBe(false);
  });
});
```

### Example 3: Integration Tests for API

**Description**:
```
"Integration tests for POST /api/posts endpoint with authentication and validation"
```

**Command**:
```bash
python3 scripts/generate_tests.py "Integration tests for POST /api/posts" --type integration
```

**Generated** (excerpt):
```typescript
import { describe, it, expect, beforeAll, afterAll } from 'vitest';
import request from 'supertest';
import { app } from '../app';

describe('POST /api/posts', () => {
  let authToken: string;

  beforeAll(async () => {
    authToken = await createTestUser();
  });

  afterAll(async () => {
    await cleanupTestData();
  });

  it('should create post with valid data', async () => {
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

  it('should return 401 without authentication', async () => {
    const response = await request(app)
      .post('/api/posts')
      .send({ title: 'Test', content: 'Test' });

    expect(response.status).toBe(401);
  });
});
```

### Example 4: E2E Tests for User Flow

**Description**:
```
"E2E tests for complete checkout flow: login, add to cart, checkout, payment"
```

**Command**:
```bash
python3 scripts/generate_tests.py "E2E checkout flow" --type e2e --framework playwright
```

**Generated** (excerpt):
```typescript
import { test, expect } from '@playwright/test';

test('complete checkout flow', async ({ page }) => {
  // Login
  await page.goto('/login');
  await page.fill('input[name="email"]', 'user@example.com');
  await page.fill('input[name="password"]', 'password');
  await page.click('button[type="submit"]');

  // Browse and add to cart
  await page.goto('/products');
  await page.click('.product:first-child .add-to-cart');
  await expect(page.locator('.cart-badge')).toContainText('1');

  // Checkout
  await page.click('.cart-icon');
  await page.click('button:has-text("Checkout")');

  // Payment
  await page.fill('input[name="cardNumber"]', '4242424242424242');
  await page.click('button:has-text("Pay")');

  // Verify success
  await expect(page.locator('.success-message')).toBeVisible();
});
```

## Test Types Comparison

### Unit Tests

**Best for**: Individual functions, utilities, business logic

**Pros**:
- Fast execution
- Easy to debug
- High coverage
- Isolated

**Cons**:
- Doesn't test integration
- Requires mocking

**Example**:
```typescript
it('should calculate discount', () => {
  expect(calculateDiscount(100, 0.1)).toBe(90);
});
```

### Integration Tests

**Best for**: API endpoints, database operations, multiple components

**Pros**:
- Tests real interactions
- Catches integration bugs
- More realistic

**Cons**:
- Slower than unit tests
- More setup required
- Harder to debug

**Example**:
```typescript
it('should create user in database', async () => {
  const user = await createUser({ email: 'test@example.com' });
  expect(user.id).toBeDefined();
});
```

### E2E Tests

**Best for**: Critical user journeys, complete workflows

**Pros**:
- Tests like real users
- Catches UI bugs
- High confidence

**Cons**:
- Slowest execution
- Most brittle
- Hardest to maintain

**Example**:
```typescript
test('user can complete purchase', async ({ page }) => {
  await page.goto('/products');
  await page.click('.buy-button');
  await expect(page).toHaveURL('/success');
});
```

## Framework Comparison

### Vitest

**Best for**: Modern TypeScript projects, Vite-based apps

**Pros**:
- Fast (uses Vite)
- Great TypeScript support
- Jest-compatible API
- Built-in coverage

**Cons**:
- Newer (less mature)
- Smaller ecosystem

### Jest

**Best for**: React projects, established codebases

**Pros**:
- Mature ecosystem
- Widely adopted
- Great documentation
- Many plugins

**Cons**:
- Slower than Vitest
- More configuration

### Playwright

**Best for**: E2E testing, cross-browser testing

**Pros**:
- Fast and reliable
- Cross-browser support
- Great debugging tools
- Auto-wait

**Cons**:
- E2E only
- Requires browser setup

## Common Patterns

### AAA Pattern

**Arrange, Act, Assert** - The foundation of good tests:

```typescript
it('should add items to cart', () => {
  // Arrange - Setup
  const cart = new Cart();
  const item = { id: '1', price: 10 };
  
  // Act - Execute
  cart.add(item);
  
  // Assert - Verify
  expect(cart.items).toHaveLength(1);
  expect(cart.total).toBe(10);
});
```

### Mocking

Mock external dependencies:

```typescript
// Mock function
const mockFn = vi.fn().mockReturnValue(42);

// Mock module
vi.mock('~/lib/db', () => ({
  db: {
    user: {
      findMany: vi.fn(),
    },
  },
}));

// Use mock
await fetchUsers();
expect(db.user.findMany).toHaveBeenCalled();
```

### Setup/Teardown

Run code before/after tests:

```typescript
describe('UserService', () => {
  let service: UserService;

  beforeEach(() => {
    service = new UserService();
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it('should create user', () => {
    // Test uses fresh service
  });
});
```

## Templates

### Vitest Unit Test Template

Use `templates/vitest_unit.test.ts` for unit test patterns:
- Basic tests
- Mocking
- Async tests
- Error handling
- Setup/teardown

### Playwright E2E Template

Use `templates/playwright_e2e.test.ts` for E2E patterns:
- Navigation
- Form interactions
- Button clicks
- Waiting for elements
- Complete user flows

## Best Practices

The generator follows these best practices automatically:

### 1. Descriptive Test Names

```typescript
// ✅ Good
it('should return null when user is not found')

// ❌ Bad
it('works')
```

### 2. Test Edge Cases

```typescript
// Test happy path
it('should accept valid input', () => {});

// Test edge cases
it('should handle empty string', () => {});
it('should handle negative numbers', () => {});
it('should handle null', () => {});
```

### 3. Mock External Dependencies

```typescript
// Mock API calls
vi.mock('~/lib/api');

// Mock database
vi.mock('~/lib/db');
```

### 4. Keep Tests Independent

```typescript
// ✅ Good - Each test is independent
it('test 1', () => {
  const data = createTestData();
  // Use data
});

it('test 2', () => {
  const data = createTestData();
  // Use data
});

// ❌ Bad - Tests depend on each other
let sharedData;
it('test 1', () => {
  sharedData = createTestData();
});
it('test 2', () => {
  // Uses sharedData from test 1
});
```

### 5. Use Proper Assertions

```typescript
// ✅ Specific assertions
expect(user.email).toBe('user@example.com');
expect(users).toHaveLength(5);

// ❌ Vague assertions
expect(user).toBeTruthy();
expect(users.length > 0).toBe(true);
```

## Configuration

### Generate Vitest Config

```bash
python3 scripts/generate_tests.py --config --framework vitest
```

**Generated** (`vitest.config.ts`):
```typescript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
    },
  },
});
```

### Generate Playwright Config

```bash
python3 scripts/generate_tests.py --config --framework playwright
```

**Generated** (`playwright.config.ts`):
```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  use: {
    baseURL: 'http://localhost:3000',
  },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
  },
});
```

## Coverage

### Run with Coverage

```bash
# Vitest
vitest --coverage

# Jest
jest --coverage
```

### Coverage Goals

- **Statements**: 80%+
- **Branches**: 75%+
- **Functions**: 80%+
- **Lines**: 80%+

### What to Cover

**High Priority** (aim for 100%):
- Business logic
- Utility functions
- Validation logic

**Medium Priority** (aim for 80%):
- API endpoints
- Components

**Low Priority** (can skip):
- Configuration files
- Type definitions

## Integration with Other Skills

### With api-endpoint-builder

1. Generate API endpoints
2. Generate integration tests for endpoints
3. Run tests
4. Deploy with confidence

### With database-schema-generator

1. Generate database schema
2. Generate tests for database queries
3. Test data integrity
4. Verify RLS policies

## Troubleshooting

### Issue: "Tests not running"

**Solution**: Ensure test framework is installed:
```bash
npm install -D vitest
# or
npm install -D jest
# or
npm install -D @playwright/test
```

### Issue: "Mocks not working"

**Solution**: Check mock syntax for your framework:
```typescript
// Vitest
vi.mock('module');

// Jest
jest.mock('module');
```

### Issue: "E2E tests failing"

**Solution**: Ensure dev server is running:
```bash
npm run dev
```

Or configure `webServer` in Playwright config.

## Advanced Usage

### Parameterized Tests

```typescript
describe.each([
  { input: 1, expected: 2 },
  { input: 2, expected: 4 },
  { input: 3, expected: 6 },
])('double($input)', ({ input, expected }) => {
  it(`should return ${expected}`, () => {
    expect(double(input)).toBe(expected);
  });
});
```

### Snapshot Testing

```typescript
it('should match snapshot', () => {
  const data = generateComplexData();
  expect(data).toMatchSnapshot();
});
```

### Custom Matchers

```typescript
expect.extend({
  toBeValidEmail(received) {
    const pass = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(received);
    return {
      pass,
      message: () => `Expected ${received} to be a valid email`,
    };
  },
});

expect('user@example.com').toBeValidEmail();
```

## Reference Files

- `references/testing_patterns.md` - Testing patterns and best practices
- `templates/vitest_unit.test.ts` - Vitest unit test template
- `templates/playwright_e2e.test.ts` - Playwright E2E test template

## Success Criteria

✅ Tests generate without errors  
✅ Tests compile and run  
✅ Tests cover happy paths and edge cases  
✅ Mocks work correctly  
✅ Assertions are specific and clear  
✅ Tests are independent  
✅ Coverage meets goals (80%+)  

## Time Savings

- **Manual test writing**: 1-2 hours
- **With this skill**: 5-10 minutes
- **Savings**: ~1.5 hours per test suite

## Next Steps

After generating your tests:

1. ✅ Review generated tests
2. ✅ Adjust assertions if needed
3. ✅ Run tests and verify they pass
4. ✅ Check coverage report
5. ✅ Add more edge cases if needed
6. ✅ Integrate into CI/CD pipeline
7. ✅ Deploy with confidence
