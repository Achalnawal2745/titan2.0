// ============================================
// PROMO CODE SYSTEM - HARDCODED IMPLEMENTATION
// ============================================
//
// Quick and simple promo code system using hardcoded codes.
// Perfect for: MVPs, small projects, limited code requirements
//
// To use:
// 1. Copy this code to your server file (e.g., server.js, index.js)
// 2. Update the DISCOUNT_CODES object with your codes
// 3. Use validateDiscountCode() in your checkout endpoint
//
// ============================================

const DISCOUNT_CODES = {
  // ===== FREE ACCESS CODES =====
  'FREE': { 
    type: 'free', 
    value: 0,
    description: 'Free access code'
  },
  'FRIEND': { 
    type: 'free', 
    value: 0,
    description: 'Friend referral'
  },
  'BETA': { 
    type: 'free', 
    value: 0,
    description: 'Beta tester access'
  },
  
  // ===== FIXED AMOUNT DISCOUNTS =====
  'SAVE10': { 
    type: 'amount', 
    value: 10,
    description: '$10 off'
  },
  'SAVE20': { 
    type: 'amount', 
    value: 20,
    description: '$20 off'
  },
  
  // ===== PERCENTAGE DISCOUNTS =====
  'HALF': { 
    type: 'percentage', 
    value: 50,
    description: '50% off'
  },
  'QUARTER': { 
    type: 'percentage', 
    value: 25,
    description: '25% off'
  },
};

/**
 * Validate a discount code
 * @param {string} code - The promo code to validate
 * @returns {object} Validation result
 */
function validateDiscountCode(code) {
  if (!code) {
    return { 
      valid: false, 
      error: 'Code is required' 
    };
  }

  const upperCode = code.toUpperCase().trim();
  const discount = DISCOUNT_CODES[upperCode];

  if (!discount) {
    return { 
      valid: false, 
      error: 'Invalid code' 
    };
  }

  return {
    valid: true,
    code: upperCode,
    type: discount.type,
    value: discount.value,
    description: discount.description
  };
}

/**
 * Calculate final price after discount
 * @param {number} originalPrice - Original price
 * @param {string} code - Promo code
 * @returns {object} Price calculation result
 */
function calculateDiscountedPrice(originalPrice, code) {
  const validation = validateDiscountCode(code);
  
  if (!validation.valid) {
    return {
      success: false,
      error: validation.error,
      originalPrice,
      finalPrice: originalPrice
    };
  }

  let finalPrice = originalPrice;

  if (validation.type === 'free') {
    finalPrice = 0;
  } else if (validation.type === 'amount') {
    finalPrice = Math.max(0, originalPrice - validation.value);
  } else if (validation.type === 'percentage') {
    finalPrice = originalPrice * (1 - validation.value / 100);
  }

  return {
    success: true,
    code: validation.code,
    type: validation.type,
    value: validation.value,
    originalPrice,
    finalPrice,
    discount: originalPrice - finalPrice
  };
}

// ============================================
// EXAMPLE USAGE IN EXPRESS.JS
// ============================================

/*
// Validate promo code endpoint
app.post('/api/validate-promo-code', (req, res) => {
  const { code } = req.body;
  const validation = validateDiscountCode(code);
  
  if (!validation.valid) {
    return res.status(400).json(validation);
  }
  
  res.json(validation);
});

// Create checkout with discount
app.post('/api/create-checkout', async (req, res) => {
  const { amount = 27, discountCode } = req.body;
  
  let finalAmount = amount;
  
  if (discountCode) {
    const result = calculateDiscountedPrice(amount, discountCode);
    if (result.success) {
      finalAmount = result.finalPrice;
    }
  }
  
  // Create Stripe checkout or handle payment
  // ... your payment logic here
  
  res.json({ 
    success: true, 
    originalAmount: amount,
    finalAmount,
    discountApplied: finalAmount < amount
  });
});
*/

// ============================================
// EXAMPLE USAGE IN NEXT.JS API ROUTES
// ============================================

/*
// app/api/validate-promo/route.ts
export async function POST(request: Request) {
  const { code } = await request.json();
  const validation = validateDiscountCode(code);
  
  if (!validation.valid) {
    return Response.json(validation, { status: 400 });
  }
  
  return Response.json(validation);
}

// app/api/checkout/route.ts
export async function POST(request: Request) {
  const { amount = 27, discountCode } = await request.json();
  
  let finalAmount = amount;
  
  if (discountCode) {
    const result = calculateDiscountedPrice(amount, discountCode);
    if (result.success) {
      finalAmount = result.finalPrice;
    }
  }
  
  // Create Stripe checkout or handle payment
  // ... your payment logic here
  
  return Response.json({ 
    success: true, 
    originalAmount: amount,
    finalAmount,
    discountApplied: finalAmount < amount
  });
}
*/

// ============================================
// EXPORT FOR MODULE USAGE
// ============================================

// CommonJS
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    DISCOUNT_CODES,
    validateDiscountCode,
    calculateDiscountedPrice
  };
}

// ES Modules
// export { DISCOUNT_CODES, validateDiscountCode, calculateDiscountedPrice };
