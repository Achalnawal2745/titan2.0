# Lazy Initialization Patterns for Serverless

## The Problem

Module-level initialization in serverless functions can fail because:
- Environment variables may not be ready at cold start
- External services timeout during initialization
- Initialization errors aren't logged properly
- Cached instances retain old/invalid configurations

## Anti-Pattern: Module-Level Initialization

```javascript
// ❌ DON'T: Initialize at module load
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_KEY);

app.post('/api/endpoint', async (req, res) => {
  // Use stripe here
});
```

**Problems:**
- If `STRIPE_SECRET_KEY` is undefined, Stripe initializes with `undefined`
- No validation that environment variables exist
- No error logging for initialization failures
- Serverless cold start timing issues

## Pattern: Lazy Initialization

### Basic Pattern

```javascript
let stripeInstance = null;

function getStripe() {
  if (!stripeInstance) {
    const secretKey = process.env.STRIPE_SECRET_KEY;
    
    if (!secretKey) {
      throw new Error('STRIPE_SECRET_KEY environment variable is not set');
    }
    
    console.log(`Initializing Stripe with key: ${secretKey.substring(0, 10)}...`);
    
    try {
      const stripe = require('stripe');
      stripeInstance = stripe(secretKey);
      console.log('Stripe initialized successfully');
    } catch (error) {
      console.error('Failed to initialize Stripe:', error);
      throw error;
    }
  }
  
  return stripeInstance;
}

// Use in endpoint
app.post('/api/create-checkout', async (req, res) => {
  try {
    const stripe = getStripe(); // Initialize on first use
    const session = await stripe.checkout.sessions.create({...});
    res.json({ sessionId: session.id });
  } catch (error) {
    console.error('Checkout error:', error);
    res.status(500).json({ error: error.message });
  }
});
```

**Benefits:**
- ✅ Environment variables validated before use
- ✅ Initialization happens on first API call (env vars ready)
- ✅ Clear error messages if configuration missing
- ✅ Initialization errors logged with details

### Pattern: Supabase Client

```javascript
let supabaseInstance = null;

function getSupabase() {
  if (!supabaseInstance) {
    const url = process.env.SUPABASE_URL;
    const key = process.env.SUPABASE_ANON_KEY;
    
    if (!url || !key) {
      throw new Error('SUPABASE_URL and SUPABASE_ANON_KEY must be set');
    }
    
    console.log(`Initializing Supabase: ${url}`);
    
    try {
      const { createClient } = require('@supabase/supabase-js');
      supabaseInstance = createClient(url, key);
      console.log('Supabase client initialized');
    } catch (error) {
      console.error('Failed to initialize Supabase:', error);
      throw error;
    }
  }
  
  return supabaseInstance;
}
```

### Pattern: SendGrid Email

```javascript
let sendgridInstance = null;

function getSendGrid() {
  if (!sendgridInstance) {
    const apiKey = process.env.SENDGRID_API_KEY;
    
    if (!apiKey) {
      throw new Error('SENDGRID_API_KEY environment variable is not set');
    }
    
    console.log(`Initializing SendGrid with key: ${apiKey.substring(0, 10)}...`);
    
    try {
      const sgMail = require('@sendgrid/mail');
      sgMail.setApiKey(apiKey);
      sendgridInstance = sgMail;
      console.log('SendGrid initialized successfully');
    } catch (error) {
      console.error('Failed to initialize SendGrid:', error);
      throw error;
    }
  }
  
  return sendgridInstance;
}
```

### Pattern: Multiple Services

```javascript
const services = {
  stripe: null,
  supabase: null,
  sendgrid: null
};

function getService(serviceName) {
  if (services[serviceName]) {
    return services[serviceName];
  }
  
  switch (serviceName) {
    case 'stripe':
      services.stripe = initializeStripe();
      return services.stripe;
    
    case 'supabase':
      services.supabase = initializeSupabase();
      return services.supabase;
    
    case 'sendgrid':
      services.sendgrid = initializeSendGrid();
      return services.sendgrid;
    
    default:
      throw new Error(`Unknown service: ${serviceName}`);
  }
}

function initializeStripe() {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error('STRIPE_SECRET_KEY not set');
  return require('stripe')(key);
}

function initializeSupabase() {
  const url = process.env.SUPABASE_URL;
  const key = process.env.SUPABASE_ANON_KEY;
  if (!url || !key) throw new Error('Supabase env vars not set');
  return require('@supabase/supabase-js').createClient(url, key);
}

function initializeSendGrid() {
  const key = process.env.SENDGRID_API_KEY;
  if (!key) throw new Error('SENDGRID_API_KEY not set');
  const sgMail = require('@sendgrid/mail');
  sgMail.setApiKey(key);
  return sgMail;
}
```

## Diagnostic Health Endpoint

Add a health check endpoint to verify configuration:

```javascript
app.get('/api/health', (req, res) => {
  const config = {
    stripe: !!process.env.STRIPE_SECRET_KEY,
    supabase: !!process.env.SUPABASE_URL && !!process.env.SUPABASE_ANON_KEY,
    sendgrid: !!process.env.SENDGRID_API_KEY
  };
  
  // Show key prefixes for debugging (safe to log)
  const keyPrefixes = {
    stripe: config.stripe ? process.env.STRIPE_SECRET_KEY.substring(0, 7) : 'none',
    supabase: config.supabase ? process.env.SUPABASE_URL.substring(0, 20) : 'none',
    sendgrid: config.sendgrid ? process.env.SENDGRID_API_KEY.substring(0, 10) : 'none'
  };
  
  res.json({ 
    status: 'ok',
    configured: config,
    keyPrefixes: keyPrefixes,
    timestamp: new Date().toISOString()
  });
});
```

**Usage:**
```bash
curl https://your-api.vercel.app/api/health
```

**Expected output:**
```json
{
  "status": "ok",
  "configured": {
    "stripe": true,
    "supabase": true,
    "sendgrid": true
  },
  "keyPrefixes": {
    "stripe": "sk_test",
    "supabase": "https://abc123.supa",
    "sendgrid": "SG.abc123"
  },
  "timestamp": "2026-02-13T22:00:00.000Z"
}
```

## When to Use Lazy Initialization

**Always use for:**
- External API clients (Stripe, SendGrid, Twilio)
- Database connections (Supabase, Prisma, MongoDB)
- Authentication services (Auth0, Firebase Auth)
- Any service requiring environment variables

**Don't need for:**
- Pure functions with no external dependencies
- Static configuration objects
- Utility libraries that don't require initialization

## Testing Lazy Initialization

```javascript
// Test that initialization fails with missing env vars
process.env.STRIPE_SECRET_KEY = undefined;
try {
  getStripe();
  console.error('Should have thrown error');
} catch (error) {
  console.log('✅ Correctly threw error for missing key');
}

// Test that initialization succeeds with valid env vars
process.env.STRIPE_SECRET_KEY = 'sk_test_12345';
try {
  const stripe = getStripe();
  console.log('✅ Successfully initialized Stripe');
} catch (error) {
  console.error('❌ Failed to initialize:', error);
}
```

## Real-World Example: Stripe Checkout Bug

**Symptom:** Stripe checkout returning generic error despite correct environment variables

**Root Cause:** Module-level initialization with undefined key

**Fix:** Lazy initialization with validation

**Before:**
```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
// If STRIPE_SECRET_KEY is undefined, stripe initializes with undefined
// All API calls fail with generic "connection error"
```

**After:**
```javascript
let stripeInstance = null;
function getStripe() {
  if (!stripeInstance) {
    const key = process.env.STRIPE_SECRET_KEY;
    if (!key) throw new Error('STRIPE_SECRET_KEY not set');
    stripeInstance = require('stripe')(key);
  }
  return stripeInstance;
}
// Clear error message if key missing
// Initialization happens after env vars loaded
```

## Key Takeaways

1. **Never initialize external services at module level** in serverless
2. **Always validate environment variables** before using them
3. **Log initialization success/failure** for debugging
4. **Add diagnostic endpoints** to verify configuration
5. **Test with missing env vars** to ensure proper error handling
