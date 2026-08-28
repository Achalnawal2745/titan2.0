# Analytics Patterns and Best Practices

Comprehensive guide to implementing analytics tracking and dashboards.

---

## Table of Contents

1. [Analytics Providers](#analytics-providers)
2. [Event Tracking Patterns](#event-tracking-patterns)
3. [Dashboard Design](#dashboard-design)
4. [Performance Optimization](#performance-optimization)
5. [Privacy and Compliance](#privacy-and-compliance)
6. [Common Pitfalls](#common-pitfalls)

---

## Analytics Providers

### PostHog (Recommended for Startups)

**Pros**:
- Open source
- Self-hostable
- Session replay included
- Feature flags built-in
- Generous free tier

**Best For**: Startups, product analytics, feature experimentation

**Setup**:
```typescript
import posthog from 'posthog-js'

posthog.init('YOUR_API_KEY', {
  api_host: 'https://app.posthog.com',
  autocapture: true, // Automatically track clicks
  capture_pageview: true, // Track page views
  session_recording: {
    enabled: true,
    maskAllInputs: true // Privacy
  }
})
```

---

### Mixpanel (Best for User Analytics)

**Pros**:
- Powerful user segmentation
- Funnel analysis
- Retention reports
- A/B testing

**Best For**: SaaS products, user behavior analysis

**Setup**:
```typescript
import mixpanel from 'mixpanel-browser'

mixpanel.init('YOUR_TOKEN', {
  debug: process.env.NODE_ENV === 'development',
  track_pageview: true,
  persistence: 'localStorage'
})
```

---

### Amplitude (Best for Product Teams)

**Pros**:
- Advanced cohort analysis
- Behavioral reports
- Predictive analytics
- Great free tier

**Best For**: Product-led growth, mobile apps

---

### Google Analytics 4 (Best for Marketing)

**Pros**:
- Free
- SEO integration
- Ad platform integration
- Industry standard

**Best For**: Marketing analytics, traffic analysis

---

## Event Tracking Patterns

### 1. Page View Tracking

**Pattern**: Track every page view automatically

```typescript
// Next.js App Router
import { usePathname } from 'next/navigation'
import { useEffect } from 'react'
import { trackEvent } from '@/lib/analytics'

export function usePageTracking() {
  const pathname = usePathname()
  
  useEffect(() => {
    trackEvent('page_view', {
      path: pathname,
      referrer: document.referrer,
      timestamp: new Date().toISOString()
    })
  }, [pathname])
}
```

---

### 2. User Action Tracking

**Pattern**: Track specific user actions

```typescript
// Button click
<button onClick={() => {
  trackEvent('button_clicked', {
    button_name: 'signup',
    location: 'homepage_hero'
  })
}}>
  Sign Up
</button>

// Form submission
const handleSubmit = async (data) => {
  trackEvent('form_submitted', {
    form_name: 'contact',
    fields: Object.keys(data)
  })
  
  await submitForm(data)
}
```

---

### 3. User Identification

**Pattern**: Identify users after login

```typescript
import { identifyUser } from '@/lib/analytics'

// After successful login
const handleLogin = async (user) => {
  // Identify user in analytics
  identifyUser(user.id, {
    email: user.email,
    name: user.name,
    plan: user.subscription_plan,
    signup_date: user.created_at
  })
}
```

---

### 4. Conversion Tracking

**Pattern**: Track key conversion events

```typescript
// Purchase completed
trackEvent('purchase_completed', {
  amount: total,
  currency: 'USD',
  items: cart.items.length,
  payment_method: 'stripe'
})

// Trial started
trackEvent('trial_started', {
  plan: 'pro',
  trial_days: 14
})

// Subscription upgraded
trackEvent('subscription_upgraded', {
  from_plan: 'basic',
  to_plan: 'pro',
  mrr_change: 20
})
```

---

### 5. Error Tracking

**Pattern**: Track errors and failures

```typescript
try {
  await riskyOperation()
} catch (error) {
  trackEvent('error_occurred', {
    error_type: error.name,
    error_message: error.message,
    location: 'checkout_page',
    user_action: 'submit_payment'
  })
  
  throw error
}
```

---

## Dashboard Design

### Key Metrics to Track

**Engagement Metrics**:
- Daily Active Users (DAU)
- Weekly Active Users (WAU)
- Monthly Active Users (MAU)
- DAU/MAU ratio (stickiness)
- Session duration
- Sessions per user

**Conversion Metrics**:
- Conversion rate
- Funnel drop-off points
- Time to conversion
- Revenue per user

**Retention Metrics**:
- Day 1, 7, 30 retention
- Churn rate
- Cohort analysis

**Product Metrics**:
- Feature adoption rate
- Feature usage frequency
- User flows
- A/B test results

---

### Dashboard Layout

**Top Section**: Key metrics (4-6 cards)
**Middle Section**: Charts (2-3 visualizations)
**Bottom Section**: Tables (top pages, events, users)

**Example Structure**:
```
┌─────────────────────────────────────────────┐
│  Total Users  │  Active Users │  Conversions │
├─────────────────────────────────────────────┤
│         User Growth Chart                    │
│         (Line chart over time)               │
├─────────────────────────────────────────────┤
│    Top Events    │    Top Pages              │
│   (Bar chart)    │   (Table)                 │
└─────────────────────────────────────────────┘
```

---

## Performance Optimization

### 1. Batch Events

**Don't**: Send every event immediately
```typescript
// ❌ Bad - sends request for each event
trackEvent('button_click', {})
trackEvent('scroll', {})
trackEvent('hover', {})
```

**Do**: Batch events together
```typescript
// ✅ Good - batches events
const eventQueue = []

function queueEvent(name, properties) {
  eventQueue.push({ name, properties })
  
  if (eventQueue.length >= 10) {
    flushEvents()
  }
}

function flushEvents() {
  if (eventQueue.length > 0) {
    posthog.capture_batch(eventQueue)
    eventQueue.length = 0
  }
}

// Flush on page unload
window.addEventListener('beforeunload', flushEvents)
```

---

### 2. Debounce High-Frequency Events

```typescript
import { debounce } from 'lodash'

// Debounce scroll tracking
const trackScroll = debounce(() => {
  trackEvent('page_scrolled', {
    depth: window.scrollY / document.body.scrollHeight
  })
}, 1000)

window.addEventListener('scroll', trackScroll)
```

---

### 3. Lazy Load Analytics

```typescript
// Load analytics script after page load
useEffect(() => {
  if (typeof window !== 'undefined') {
    // Wait for page to be interactive
    if (document.readyState === 'complete') {
      initAnalytics()
    } else {
      window.addEventListener('load', initAnalytics)
    }
  }
}, [])
```

---

## Privacy and Compliance

### GDPR Compliance

**Required**:
1. Cookie consent banner
2. Opt-out mechanism
3. Data deletion on request
4. Privacy policy

**Implementation**:
```typescript
// Check consent before tracking
function trackEvent(name, properties) {
  if (!hasUserConsent()) {
    return // Don't track without consent
  }
  
  posthog.capture(name, properties)
}

// Opt-out function
function optOutOfTracking() {
  posthog.opt_out_capturing()
  localStorage.setItem('analytics_opted_out', 'true')
}
```

---

### Data Anonymization

**Mask sensitive data**:
```typescript
trackEvent('form_submitted', {
  email: maskEmail(user.email), // user@example.com -> u***@e***.com
  ip_address: null, // Don't track IP
  user_agent: null // Don't track user agent
})
```

---

## Common Pitfalls

### 1. Tracking Too Much

**Problem**: Overwhelming data, slow performance

**Solution**: Track only actionable events
- Focus on key user actions
- Avoid tracking every mouse move
- Use sampling for high-volume events

---

### 2. Not Tracking Enough Context

**Problem**: Events without context are useless

**Solution**: Always include relevant properties
```typescript
// ❌ Bad
trackEvent('button_clicked')

// ✅ Good
trackEvent('button_clicked', {
  button_name: 'signup',
  location: 'homepage_hero',
  user_type: 'visitor',
  ab_test_variant: 'variant_b'
})
```

---

### 3. Blocking Page Load

**Problem**: Analytics slows down page load

**Solution**: Load asynchronously
```typescript
// ✅ Good - async loading
const script = document.createElement('script')
script.src = 'https://cdn.analytics.com/script.js'
script.async = true
document.head.appendChild(script)
```

---

### 4. Not Testing Analytics

**Problem**: Broken tracking goes unnoticed

**Solution**: Test in development
```typescript
if (process.env.NODE_ENV === 'development') {
  // Log events instead of sending
  console.log('Analytics Event:', name, properties)
} else {
  posthog.capture(name, properties)
}
```

---

## Quick Reference

### Essential Events to Track

1. **User Lifecycle**:
   - `user_signed_up`
   - `user_logged_in`
   - `user_logged_out`
   - `account_deleted`

2. **Engagement**:
   - `page_viewed`
   - `feature_used`
   - `content_shared`
   - `search_performed`

3. **Conversion**:
   - `trial_started`
   - `subscription_created`
   - `purchase_completed`
   - `upgrade_completed`

4. **Product**:
   - `onboarding_completed`
   - `settings_changed`
   - `export_completed`
   - `integration_connected`

---

## Resources

- [PostHog Documentation](https://posthog.com/docs)
- [Mixpanel Best Practices](https://mixpanel.com/blog/best-practices)
- [Amplitude Playbook](https://amplitude.com/blog)
- [Google Analytics 4 Guide](https://support.google.com/analytics)

---

*Last Updated: February 2026*
