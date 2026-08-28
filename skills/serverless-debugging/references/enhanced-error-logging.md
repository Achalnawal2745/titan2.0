# Enhanced Error Logging for Serverless

## The Problem

Generic error messages hide the actual problem:
```json
{"error": "An error occurred with our connection to Stripe. Request was retried 1 times."}
```

This tells you:
- ❌ Something failed
- ❌ It's related to Stripe
- ❌ It retried once

But NOT:
- ❌ What the actual Stripe error was
- ❌ What error type/code Stripe returned
- ❌ What request parameters caused the error
- ❌ Where in the code it failed

**Result:** Debugging blind, guessing at solutions.

## Anti-Pattern: Generic Error Messages

```javascript
// ❌ DON'T: Hide error details
try {
  const session = await stripe.checkout.sessions.create({...});
  res.json({ sessionId: session.id });
} catch (error) {
  console.error('Stripe error:', error);
  res.status(500).json({ 
    error: 'An error occurred with our connection to Stripe.' 
  });
}
```

**Problems:**
- Actual Stripe error hidden from logs
- Client gets generic message
- No way to diagnose root cause
- Can't distinguish between different error types

## Pattern: Comprehensive Error Logging

### Basic Pattern

```javascript
try {
  const session = await stripe.checkout.sessions.create({...});
  res.json({ sessionId: session.id, url: session.url });
} catch (error) {
  // Log FULL error details to console
  console.error('Stripe checkout error:', {
    message: error.message,
    type: error.type,
    code: error.code,
    statusCode: error.statusCode,
    param: error.param,
    raw: error.raw,
    stack: error.stack,
    requestParams: {
      priceId: req.body.priceId,
      successUrl: req.body.successUrl,
      cancelUrl: req.body.cancelUrl
    }
  });
  
  // Return detailed error to client (for debugging)
  res.status(500).json({ 
    error: error.message,
    type: error.type,
    code: error.code,
    param: error.param
  });
}
```

**Benefits:**
- ✅ See exact Stripe error type and code
- ✅ Know which parameter caused the error
- ✅ Full stack trace for debugging
- ✅ Request context included
- ✅ Client gets actionable error info

### Pattern: Supabase Errors

```javascript
try {
  const { data, error } = await supabase
    .from('users')
    .insert({ email, name });
  
  if (error) throw error;
  
  res.json({ success: true, data });
} catch (error) {
  console.error('Supabase insert error:', {
    message: error.message,
    code: error.code,
    details: error.details,
    hint: error.hint,
    table: 'users',
    operation: 'insert',
    requestData: { email, name }
  });
  
  res.status(500).json({
    error: error.message,
    code: error.code,
    hint: error.hint
  });
}
```

### Pattern: SendGrid Errors

```javascript
try {
  await sgMail.send({
    to: email,
    from: 'noreply@example.com',
    subject: 'Welcome',
    text: 'Welcome to our app!'
  });
  
  res.json({ success: true });
} catch (error) {
  console.error('SendGrid send error:', {
    message: error.message,
    code: error.code,
    response: error.response?.body,
    statusCode: error.response?.statusCode,
    headers: error.response?.headers,
    emailData: {
      to: email,
      from: 'noreply@example.com',
      subject: 'Welcome'
    }
  });
  
  res.status(500).json({
    error: error.message,
    code: error.code,
    statusCode: error.response?.statusCode
  });
}
```

### Pattern: Async Operation Errors

```javascript
async function processPayment(sessionId) {
  try {
    console.log('Starting payment processing:', { sessionId });
    
    const session = await stripe.checkout.sessions.retrieve(sessionId);
    console.log('Session retrieved:', {
      id: session.id,
      status: session.payment_status,
      amount: session.amount_total
    });
    
    const { data, error } = await supabase
      .from('payments')
      .insert({
        session_id: sessionId,
        amount: session.amount_total,
        status: session.payment_status
      });
    
    if (error) {
      console.error('Database insert failed:', {
        error: error.message,
        code: error.code,
        sessionId,
        amount: session.amount_total
      });
      throw error;
    }
    
    console.log('Payment processed successfully:', { sessionId, paymentId: data.id });
    return data;
  } catch (error) {
    console.error('Payment processing failed:', {
      message: error.message,
      type: error.type,
      code: error.code,
      sessionId,
      stack: error.stack
    });
    throw error;
  }
}
```

## Structured Logging

For complex operations, use structured logging:

```javascript
const logger = {
  info: (message, context = {}) => {
    console.log(JSON.stringify({
      level: 'info',
      message,
      timestamp: new Date().toISOString(),
      ...context
    }));
  },
  
  error: (message, error, context = {}) => {
    console.error(JSON.stringify({
      level: 'error',
      message,
      error: {
        message: error.message,
        type: error.type,
        code: error.code,
        stack: error.stack
      },
      timestamp: new Date().toISOString(),
      ...context
    }));
  }
};

// Usage
try {
  logger.info('Creating checkout session', { priceId, userId });
  const session = await stripe.checkout.sessions.create({...});
  logger.info('Checkout session created', { sessionId: session.id, userId });
  res.json({ sessionId: session.id });
} catch (error) {
  logger.error('Checkout session creation failed', error, { priceId, userId });
  res.status(500).json({ error: error.message });
}
```

## Error Context Wrapper

Create a reusable error handler:

```javascript
function withErrorLogging(operation, context = {}) {
  return async (...args) => {
    try {
      console.log(`Starting ${operation}:`, context);
      const result = await args[0](...args.slice(1));
      console.log(`${operation} succeeded:`, context);
      return result;
    } catch (error) {
      console.error(`${operation} failed:`, {
        message: error.message,
        type: error.type,
        code: error.code,
        stack: error.stack,
        context
      });
      throw error;
    }
  };
}

// Usage
const createCheckoutWithLogging = withErrorLogging(
  'create-checkout-session',
  { priceId: req.body.priceId }
);

const session = await createCheckoutWithLogging(
  stripe.checkout.sessions.create,
  {
    mode: 'payment',
    line_items: [{ price: req.body.priceId, quantity: 1 }],
    success_url: req.body.successUrl,
    cancel_url: req.body.cancelUrl
  }
);
```

## Production vs. Development Logging

```javascript
const isDevelopment = process.env.NODE_ENV === 'development';

function logError(error, context = {}) {
  if (isDevelopment) {
    // Full details in development
    console.error('Error:', {
      message: error.message,
      type: error.type,
      code: error.code,
      stack: error.stack,
      raw: error.raw,
      context
    });
  } else {
    // Essential details in production
    console.error('Error:', {
      message: error.message,
      type: error.type,
      code: error.code,
      context
    });
  }
}

function sendErrorResponse(res, error) {
  if (isDevelopment) {
    // Detailed error in development
    res.status(500).json({
      error: error.message,
      type: error.type,
      code: error.code,
      stack: error.stack
    });
  } else {
    // Safe error in production
    res.status(500).json({
      error: error.message,
      code: error.code
    });
  }
}
```

## Real-World Example: Stripe Integration

**Before (generic error):**
```javascript
catch (error) {
  console.error('Stripe error:', error);
  res.status(500).json({ 
    error: 'An error occurred with our connection to Stripe.' 
  });
}
```

**Result:** Spent hours guessing what was wrong

**After (detailed error):**
```javascript
catch (error) {
  console.error('Stripe checkout error:', {
    message: error.message,
    type: error.type,
    code: error.code,
    param: error.param,
    requestParams: { priceId, successUrl, cancelUrl }
  });
  res.status(500).json({ 
    error: error.message,
    type: error.type,
    code: error.code
  });
}
```

**Result:** Immediately see "invalid_request_error: No such price: price_xyz"

## Key Takeaways

1. **Always log full error details** - message, type, code, stack
2. **Include request context** - what parameters caused the error
3. **Return actionable errors to client** - help them fix their request
4. **Use structured logging** for complex operations
5. **Different logging levels** for development vs. production
6. **Never hide errors** with generic messages
