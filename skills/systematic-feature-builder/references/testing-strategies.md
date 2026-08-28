# Testing Strategies

Comprehensive testing approaches for different project types.

## General Testing Principles

Test at three levels before creating checkpoint:

1. **Unit Tests** - Individual functions and components
2. **Integration Tests** - Features working together
3. **Manual Verification** - User-facing behavior

## Webdev Projects

### Backend Testing

**tRPC Endpoints:**
```typescript
// server/feature.test.ts
import { describe, it, expect } from 'vitest';
import { createCaller } from './_core/trpc';

describe('Feature Tests', () => {
  it('should handle valid input', async () => {
    const caller = createCaller({ user: mockUser });
    const result = await caller.feature.endpoint({ input });
    expect(result).toMatchObject({ expected });
  });
});
```

**Database Operations:**
- Test CRUD operations
- Verify schema constraints
- Check foreign key relationships

**Run Tests:**
```bash
pnpm test
```

### Frontend Testing

**Component Behavior:**
- Form submissions
- State management
- Error handling
- Loading states

**Manual Checks:**
- UI renders correctly
- Responsive design works
- Accessibility (keyboard navigation, screen readers)
- Cross-browser compatibility

**Browser DevTools:**
- Check console for errors
- Verify network requests
- Test different viewport sizes

### End-to-End Testing

**Critical User Flows:**
1. User authentication
2. Primary feature workflows
3. Data persistence
4. Error recovery

**Verification Checklist:**
- [ ] Feature works in development
- [ ] Feature works after server restart
- [ ] Feature works in production (after deployment)
- [ ] No console errors
- [ ] No broken UI elements
- [ ] Mobile responsive

## Python Projects

### Unit Tests

```python
import pytest

def test_function():
    result = my_function(input)
    assert result == expected
```

**Run Tests:**
```bash
pytest tests/
```

### Integration Tests

Test external dependencies:
- API calls
- Database connections
- File I/O operations

## Data Analysis Projects

### Validation Checks

- Data integrity (no nulls where unexpected)
- Statistical sanity checks
- Visualization accuracy
- Reproducibility

### Output Verification

- Results match expected patterns
- Edge cases handled
- Performance acceptable for dataset size

## Common Testing Pitfalls

**Don't Skip:**
- Error cases
- Edge cases (empty inputs, large datasets)
- Permission checks
- Concurrent operations

**Always Test:**
- After dependency updates
- After schema changes
- After configuration changes
- Before creating checkpoint
