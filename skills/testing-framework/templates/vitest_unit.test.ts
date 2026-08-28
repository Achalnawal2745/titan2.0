import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

/**
 * Vitest Unit Test Template
 * 
 * This template shows common patterns for unit testing with Vitest.
 * 
 * Test structure:
 * - describe: Group related tests
 * - it/test: Individual test case
 * - expect: Assertion
 * 
 * Patterns:
 * - AAA: Arrange, Act, Assert
 * - Mocking: vi.fn(), vi.mock()
 * - Setup/Teardown: beforeEach, afterEach
 */

// ============================================
// BASIC TESTS
// ============================================

describe('Calculator', () => {
  it('should add two numbers correctly', () => {
    // Arrange
    const a = 2;
    const b = 3;
    
    // Act
    const result = add(a, b);
    
    // Assert
    expect(result).toBe(5);
  });

  it('should handle negative numbers', () => {
    expect(add(-1, -2)).toBe(-3);
    expect(add(-1, 2)).toBe(1);
  });

  it('should handle zero', () => {
    expect(add(0, 5)).toBe(5);
    expect(add(5, 0)).toBe(5);
  });
});

// ============================================
// TESTING WITH SETUP/TEARDOWN
// ============================================

describe('UserService', () => {
  let userService: UserService;
  let mockDb: any;

  beforeEach(() => {
    // Setup before each test
    mockDb = {
      findUser: vi.fn(),
      createUser: vi.fn(),
    };
    userService = new UserService(mockDb);
  });

  afterEach(() => {
    // Cleanup after each test
    vi.clearAllMocks();
  });

  it('should create a new user', async () => {
    // Arrange
    const userData = { name: 'John', email: 'john@example.com' };
    mockDb.createUser.mockResolvedValue({ id: '123', ...userData });

    // Act
    const user = await userService.createUser(userData);

    // Assert
    expect(user).toEqual({ id: '123', name: 'John', email: 'john@example.com' });
    expect(mockDb.createUser).toHaveBeenCalledWith(userData);
    expect(mockDb.createUser).toHaveBeenCalledTimes(1);
  });

  it('should throw error if user already exists', async () => {
    // Arrange
    mockDb.createUser.mockRejectedValue(new Error('User exists'));

    // Act & Assert
    await expect(
      userService.createUser({ name: 'John', email: 'john@example.com' })
    ).rejects.toThrow('User exists');
  });
});

// ============================================
// MOCKING MODULES
// ============================================

// Mock external module
vi.mock('~/lib/db', () => ({
  db: {
    user: {
      findMany: vi.fn(),
      create: vi.fn(),
    },
  },
}));

import { db } from '~/lib/db';

describe('UserRepository', () => {
  it('should fetch all users', async () => {
    // Arrange
    const mockUsers = [
      { id: '1', name: 'Alice' },
      { id: '2', name: 'Bob' },
    ];
    vi.mocked(db.user.findMany).mockResolvedValue(mockUsers);

    // Act
    const users = await fetchAllUsers();

    // Assert
    expect(users).toEqual(mockUsers);
    expect(db.user.findMany).toHaveBeenCalled();
  });
});

// ============================================
// TESTING ASYNC CODE
// ============================================

describe('Async Operations', () => {
  it('should resolve with data', async () => {
    const data = await fetchData();
    expect(data).toBeDefined();
  });

  it('should reject with error', async () => {
    await expect(fetchDataThatFails()).rejects.toThrow('Network error');
  });

  it('should handle timeout', async () => {
    const promise = fetchWithTimeout(100);
    await expect(promise).rejects.toThrow('Timeout');
  });
});

// ============================================
// TESTING ERROR HANDLING
// ============================================

describe('Error Handling', () => {
  it('should throw error for invalid input', () => {
    expect(() => divide(10, 0)).toThrow('Division by zero');
  });

  it('should return error object', () => {
    const result = validateEmail('invalid');
    expect(result.success).toBe(false);
    expect(result.error).toBeDefined();
  });
});

// ============================================
// TESTING WITH MATCHERS
// ============================================

describe('Matchers', () => {
  it('should use equality matchers', () => {
    expect(2 + 2).toBe(4); // Strict equality
    expect({ name: 'John' }).toEqual({ name: 'John' }); // Deep equality
    expect([1, 2, 3]).toStrictEqual([1, 2, 3]); // Strict deep equality
  });

  it('should use truthiness matchers', () => {
    expect(true).toBeTruthy();
    expect(false).toBeFalsy();
    expect(null).toBeNull();
    expect(undefined).toBeUndefined();
    expect('hello').toBeDefined();
  });

  it('should use number matchers', () => {
    expect(10).toBeGreaterThan(5);
    expect(10).toBeGreaterThanOrEqual(10);
    expect(5).toBeLessThan(10);
    expect(5).toBeLessThanOrEqual(5);
    expect(0.1 + 0.2).toBeCloseTo(0.3); // Floating point
  });

  it('should use string matchers', () => {
    expect('hello world').toContain('world');
    expect('hello').toMatch(/^hel/);
  });

  it('should use array matchers', () => {
    expect([1, 2, 3]).toContain(2);
    expect([1, 2, 3]).toHaveLength(3);
  });

  it('should use object matchers', () => {
    expect({ name: 'John', age: 30 }).toHaveProperty('name');
    expect({ name: 'John', age: 30 }).toMatchObject({ name: 'John' });
  });
});

// ============================================
// TESTING CALLBACKS & TIMERS
// ============================================

describe('Timers', () => {
  it('should execute callback after delay', () => {
    vi.useFakeTimers();
    
    const callback = vi.fn();
    setTimeout(callback, 1000);
    
    expect(callback).not.toHaveBeenCalled();
    
    vi.advanceTimersByTime(1000);
    
    expect(callback).toHaveBeenCalled();
    
    vi.useRealTimers();
  });
});

// ============================================
// TESTING SPIES
// ============================================

describe('Spies', () => {
  it('should spy on method calls', () => {
    const obj = {
      method: (x: number) => x * 2,
    };
    
    const spy = vi.spyOn(obj, 'method');
    
    obj.method(5);
    
    expect(spy).toHaveBeenCalledWith(5);
    expect(spy).toHaveReturnedWith(10);
  });
});

// ============================================
// SNAPSHOT TESTING
// ============================================

describe('Snapshots', () => {
  it('should match snapshot', () => {
    const data = {
      id: '123',
      name: 'John',
      createdAt: new Date('2024-01-01'),
    };
    
    expect(data).toMatchSnapshot();
  });
});

// ============================================
// PARAMETERIZED TESTS
// ============================================

describe.each([
  { a: 1, b: 1, expected: 2 },
  { a: 2, b: 2, expected: 4 },
  { a: 3, b: 3, expected: 6 },
])('add($a, $b)', ({ a, b, expected }) => {
  it(`should return ${expected}`, () => {
    expect(add(a, b)).toBe(expected);
  });
});
