import { test, expect } from '@playwright/test';

/**
 * Playwright E2E Test Template
 * 
 * This template shows common patterns for E2E testing with Playwright.
 * 
 * Test structure:
 * - test: Individual test case
 * - expect: Assertion
 * - page: Browser page object
 * 
 * Patterns:
 * - Page navigation
 * - Element interactions
 * - Waiting for elements
 * - Taking screenshots
 * - Testing user flows
 */

// ============================================
// BASIC NAVIGATION
// ============================================

test('should load homepage', async ({ page }) => {
  await page.goto('/');
  
  await expect(page).toHaveTitle(/Home/);
  await expect(page.locator('h1')).toContainText('Welcome');
});

// ============================================
// FORM INTERACTIONS
// ============================================

test('should submit login form', async ({ page }) => {
  await page.goto('/login');
  
  // Fill form
  await page.fill('input[name="email"]', 'user@example.com');
  await page.fill('input[name="password"]', 'password123');
  
  // Submit
  await page.click('button[type="submit"]');
  
  // Wait for navigation
  await page.waitForURL('/dashboard');
  
  // Verify success
  await expect(page.locator('.welcome-message')).toBeVisible();
});

// ============================================
// BUTTON CLICKS
// ============================================

test('should create new post', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Click create button
  await page.click('button:has-text("New Post")');
  
  // Wait for modal
  await expect(page.locator('.modal')).toBeVisible();
  
  // Fill form
  await page.fill('input[name="title"]', 'My Test Post');
  await page.fill('textarea[name="content"]', 'This is test content');
  
  // Submit
  await page.click('button:has-text("Create")');
  
  // Verify post appears
  await expect(page.locator('text=My Test Post')).toBeVisible();
});

// ============================================
// WAITING FOR ELEMENTS
// ============================================

test('should wait for data to load', async ({ page }) => {
  await page.goto('/posts');
  
  // Wait for loading to finish
  await page.waitForSelector('.loading', { state: 'hidden' });
  
  // Verify data loaded
  await expect(page.locator('.post-item')).toHaveCount(10);
});

// ============================================
// DROPDOWN & SELECT
// ============================================

test('should select from dropdown', async ({ page }) => {
  await page.goto('/settings');
  
  // Select option
  await page.selectOption('select[name="role"]', 'admin');
  
  // Verify selection
  await expect(page.locator('select[name="role"]')).toHaveValue('admin');
});

// ============================================
// CHECKBOX & RADIO
// ============================================

test('should toggle checkbox', async ({ page }) => {
  await page.goto('/settings');
  
  // Check checkbox
  await page.check('input[name="notifications"]');
  await expect(page.locator('input[name="notifications"]')).toBeChecked();
  
  // Uncheck checkbox
  await page.uncheck('input[name="notifications"]');
  await expect(page.locator('input[name="notifications"]')).not.toBeChecked();
});

// ============================================
// FILE UPLOAD
// ============================================

test('should upload file', async ({ page }) => {
  await page.goto('/upload');
  
  // Upload file
  await page.setInputFiles('input[type="file"]', './test-image.png');
  
  // Submit
  await page.click('button:has-text("Upload")');
  
  // Verify success
  await expect(page.locator('.success-message')).toBeVisible();
});

// ============================================
// KEYBOARD INTERACTIONS
// ============================================

test('should use keyboard shortcuts', async ({ page }) => {
  await page.goto('/editor');
  
  // Focus editor
  await page.click('textarea');
  
  // Type text
  await page.keyboard.type('Hello World');
  
  // Use shortcut (Ctrl+S to save)
  await page.keyboard.press('Control+S');
  
  // Verify saved
  await expect(page.locator('.saved-indicator')).toBeVisible();
});

// ============================================
// HOVER & TOOLTIPS
// ============================================

test('should show tooltip on hover', async ({ page }) => {
  await page.goto('/dashboard');
  
  // Hover over element
  await page.hover('.info-icon');
  
  // Verify tooltip appears
  await expect(page.locator('.tooltip')).toBeVisible();
});

// ============================================
// MULTIPLE PAGES/TABS
// ============================================

test('should open link in new tab', async ({ context, page }) => {
  await page.goto('/');
  
  // Click link that opens new tab
  const [newPage] = await Promise.all([
    context.waitForEvent('page'),
    page.click('a[target="_blank"]'),
  ]);
  
  // Verify new page
  await expect(newPage).toHaveURL(/external-site/);
});

// ============================================
// AUTHENTICATION STATE
// ============================================

test.describe('Authenticated tests', () => {
  test.use({
    storageState: 'auth.json', // Load saved auth state
  });

  test('should access protected page', async ({ page }) => {
    await page.goto('/dashboard');
    
    await expect(page.locator('.user-profile')).toBeVisible();
  });
});

// ============================================
// MOBILE VIEWPORT
// ============================================

test('should work on mobile', async ({ page }) => {
  // Set mobile viewport
  await page.setViewportSize({ width: 375, height: 667 });
  
  await page.goto('/');
  
  // Verify mobile menu
  await expect(page.locator('.mobile-menu')).toBeVisible();
});

// ============================================
// SCREENSHOTS
// ============================================

test('should take screenshot', async ({ page }) => {
  await page.goto('/');
  
  // Take full page screenshot
  await page.screenshot({ path: 'homepage.png', fullPage: true });
  
  // Take element screenshot
  await page.locator('.hero').screenshot({ path: 'hero.png' });
});

// ============================================
// ERROR HANDLING
// ============================================

test('should show error message for invalid input', async ({ page }) => {
  await page.goto('/login');
  
  // Submit empty form
  await page.click('button[type="submit"]');
  
  // Verify error message
  await expect(page.locator('.error-message')).toContainText('Email is required');
});

// ============================================
// NETWORK INTERCEPTION
// ============================================

test('should handle API errors', async ({ page }) => {
  // Intercept API call
  await page.route('**/api/posts', (route) => {
    route.fulfill({
      status: 500,
      body: JSON.stringify({ error: 'Server error' }),
    });
  });
  
  await page.goto('/posts');
  
  // Verify error handling
  await expect(page.locator('.error-banner')).toBeVisible();
});

// ============================================
// COMPLETE USER FLOW
// ============================================

test('should complete checkout flow', async ({ page }) => {
  // 1. Browse products
  await page.goto('/products');
  await expect(page.locator('.product-grid')).toBeVisible();
  
  // 2. Add to cart
  await page.click('.product-card:first-child button:has-text("Add to Cart")');
  await expect(page.locator('.cart-badge')).toContainText('1');
  
  // 3. Go to cart
  await page.click('.cart-icon');
  await expect(page).toHaveURL(/cart/);
  
  // 4. Proceed to checkout
  await page.click('button:has-text("Checkout")');
  await expect(page).toHaveURL(/checkout/);
  
  // 5. Fill shipping info
  await page.fill('input[name="name"]', 'John Doe');
  await page.fill('input[name="address"]', '123 Main St');
  await page.fill('input[name="city"]', 'New York');
  await page.fill('input[name="zip"]', '10001');
  
  // 6. Fill payment info
  await page.fill('input[name="cardNumber"]', '4242424242424242');
  await page.fill('input[name="expiry"]', '12/25');
  await page.fill('input[name="cvc"]', '123');
  
  // 7. Submit order
  await page.click('button:has-text("Place Order")');
  
  // 8. Verify success
  await expect(page).toHaveURL(/order-confirmation/);
  await expect(page.locator('.success-message')).toContainText('Order placed successfully');
});

// ============================================
// SETUP & TEARDOWN
// ============================================

test.beforeEach(async ({ page }) => {
  // Run before each test
  await page.goto('/');
});

test.afterEach(async ({ page }) => {
  // Run after each test
  await page.close();
});
