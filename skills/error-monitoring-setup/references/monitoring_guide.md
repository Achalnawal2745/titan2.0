# Error Monitoring Best Practices

## Why Error Monitoring?

Error monitoring helps you:
- **Catch bugs** before users report them
- **Fix issues faster** with detailed error context
- **Improve reliability** by tracking error trends
- **Understand impact** of errors on users
- **Prioritize fixes** based on frequency and severity

---

## Sentry Overview

**Sentry** is the industry-standard error monitoring platform.

**Features**:
- Real-time error tracking
- Performance monitoring
- Session replay
- Release tracking
- User feedback
- Source map support
- Integrations (Slack, GitHub, etc.)

**Pricing**:
- Free tier: 5,000 errors/month
- Team: $26/month (50,000 errors)
- Business: $80/month (500,000 errors)

---

## Setup Process

### 1. Create Sentry Account
1. Go to [sentry.io](https://sentry.io)
2. Sign up for free account
3. Create new project
4. Select your platform (Next.js, React, Node.js, Python)
5. Copy your DSN

### 2. Install Sentry
```bash
# Next.js
npm install --save @sentry/nextjs

# React
npm install --save @sentry/react

# Node.js
npm install --save @sentry/node

# Python
pip install sentry-sdk
```

### 3. Configure Sentry
Use the setup script:
```bash
python3 /home/ubuntu/skills/error-monitoring-setup/scripts/setup_sentry.py /path/to/project <your-dsn>
```

### 4. Test Error Tracking
```javascript
// Throw a test error
throw new Error("Test error - Sentry is working!");
```

### 5. Check Sentry Dashboard
- Go to Sentry dashboard
- Verify error appears
- Check stack trace and context

---

## Configuration Options

### Sample Rates

**Traces Sample Rate** (Performance Monitoring):
```javascript
tracesSampleRate: 1.0  // 100% of transactions
tracesSampleRate: 0.1  // 10% of transactions (recommended for production)
```

**Replays Sample Rate** (Session Replay):
```javascript
replaysSessionSampleRate: 0.1   // 10% of sessions
replaysOnErrorSampleRate: 1.0   // 100% of sessions with errors
```

### Environment

```javascript
environment: process.env.NODE_ENV  // "development", "staging", "production"
```

### Release Tracking

```javascript
release: "my-app@1.0.0"
```

### User Context

```javascript
Sentry.setUser({
  id: user.id,
  email: user.email,
  username: user.username
});
```

### Custom Tags

```javascript
Sentry.setTag("page_locale", "en-us");
Sentry.setTag("feature_flag", "new-ui");
```

### Custom Context

```javascript
Sentry.setContext("character", {
  name: "Mighty Fighter",
  age: 19,
  attack_type: "melee"
});
```

---

## Error Handling Patterns

### Next.js

**API Route Error Handling**:
```javascript
import * as Sentry from "@sentry/nextjs";

export default async function handler(req, res) {
  try {
    // Your code here
  } catch (error) {
    Sentry.captureException(error);
    res.status(500).json({ error: "Internal server error" });
  }
}
```

**Page Error Boundary**:
```javascript
// pages/_error.js
import * as Sentry from "@sentry/nextjs";
import NextErrorComponent from "next/error";

const CustomErrorComponent = (props) => {
  return <NextErrorComponent statusCode={props.statusCode} />;
};

CustomErrorComponent.getInitialProps = async (contextData) => {
  await Sentry.captureUnderscoreErrorException(contextData);
  return NextErrorComponent.getInitialProps(contextData);
};

export default CustomErrorComponent;
```

### React

**Error Boundary**:
```javascript
import * as Sentry from "@sentry/react";

const myFallback = <div>An error has occurred</div>;

<Sentry.ErrorBoundary fallback={myFallback} showDialog>
  <App />
</Sentry.ErrorBoundary>
```

### Node.js

**Express Error Handler**:
```javascript
const Sentry = require("@sentry/node");

// Error handling middleware
app.use(Sentry.Handlers.errorHandler());

app.use((err, req, res, next) => {
  res.status(500).send("Internal Server Error");
});
```

### Python

**Flask Integration**:
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-dsn",
    integrations=[FlaskIntegration()],
)
```

**Django Integration**:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-dsn",
    integrations=[DjangoIntegration()],
)
```

---

## Performance Monitoring

### Enable Tracing

```javascript
Sentry.init({
  dsn: "your-dsn",
  tracesSampleRate: 0.1,  // 10% of transactions
});
```

### Custom Transactions

```javascript
const transaction = Sentry.startTransaction({
  op: "task",
  name: "Process User Data"
});

// Do work...

transaction.finish();
```

### Spans

```javascript
const span = transaction.startChild({
  op: "http",
  description: "GET /api/users"
});

// Make API call...

span.finish();
```

---

## Session Replay

### Enable Replay

```javascript
Sentry.init({
  dsn: "your-dsn",
  integrations: [
    new Sentry.Replay({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
});
```

### Privacy Options

```javascript
new Sentry.Replay({
  maskAllText: true,        // Mask all text
  blockAllMedia: true,      // Block all images/videos
  maskAllInputs: true,      // Mask form inputs
})
```

---

## Alerts and Notifications

### Slack Integration
1. Go to Sentry Settings → Integrations
2. Add Slack integration
3. Configure alert rules
4. Choose channels for notifications

### Email Alerts
1. Go to Sentry Settings → Alerts
2. Create new alert rule
3. Set conditions (frequency, error type)
4. Add email recipients

### Custom Webhooks
1. Go to Sentry Settings → Integrations
2. Add Webhook integration
3. Configure webhook URL
4. Set event types to trigger

---

## Source Maps

### Next.js

Sentry automatically handles source maps with `@sentry/nextjs`.

### React/Node.js

**Upload Source Maps**:
```bash
# Install Sentry CLI
npm install --save-dev @sentry/cli

# Configure .sentryclirc
[auth]
token=your-auth-token

[defaults]
org=your-org
project=your-project

# Upload source maps
sentry-cli sourcemaps upload --release=1.0.0 ./build
```

---

## Best Practices

### 1. Set Appropriate Sample Rates
- **Development**: 100% (tracesSampleRate: 1.0)
- **Production**: 10-20% (tracesSampleRate: 0.1)

### 2. Use Environments
```javascript
environment: process.env.NODE_ENV
```

### 3. Track Releases
```javascript
release: "my-app@" + process.env.npm_package_version
```

### 4. Add User Context
```javascript
Sentry.setUser({ id: user.id, email: user.email });
```

### 5. Use Custom Tags
```javascript
Sentry.setTag("page", "checkout");
Sentry.setTag("feature", "payment");
```

### 6. Filter Sensitive Data
```javascript
beforeSend(event, hint) {
  // Don't send events with sensitive data
  if (event.request?.url?.includes("/api/auth")) {
    return null;
  }
  return event;
}
```

### 7. Ignore Known Errors
```javascript
ignoreErrors: [
  "ResizeObserver loop limit exceeded",
  "Non-Error promise rejection captured"
]
```

### 8. Set Up Alerts
- Create alert rules for critical errors
- Configure Slack notifications
- Set up email alerts for high-priority issues

### 9. Monitor Performance
- Enable performance monitoring
- Track slow transactions
- Identify bottlenecks

### 10. Review Regularly
- Check Sentry dashboard daily
- Triage new errors
- Track error trends
- Prioritize fixes

---

## Troubleshooting

### Errors Not Appearing

**Check DSN**:
```javascript
console.log(process.env.NEXT_PUBLIC_SENTRY_DSN);
```

**Verify Initialization**:
```javascript
console.log("Sentry initialized");
```

**Test Manually**:
```javascript
Sentry.captureMessage("Test message");
```

### Source Maps Not Working

**Check Upload**:
```bash
sentry-cli sourcemaps list --release=1.0.0
```

**Verify Release**:
```javascript
release: "my-app@1.0.0"  // Must match uploaded source maps
```

### Too Many Events

**Adjust Sample Rates**:
```javascript
tracesSampleRate: 0.1  // Reduce to 10%
```

**Filter Events**:
```javascript
beforeSend(event) {
  // Filter out low-priority events
  return event;
}
```

---

## Alternatives to Sentry

### LogRocket
- Session replay focus
- Performance monitoring
- User analytics
- Higher cost

### Rollbar
- Error tracking
- Deployment tracking
- Simpler than Sentry
- Good for smaller teams

### Bugsnag
- Error monitoring
- Release tracking
- Good mobile support
- Similar to Sentry

### New Relic
- Full observability platform
- APM + Error tracking
- Enterprise focus
- Higher cost

---

## Cost Optimization

### Free Tier (5,000 errors/month)
- Perfect for side projects
- Good for early startups
- Monitor usage carefully

### Reduce Event Volume
1. Lower sample rates
2. Filter non-critical errors
3. Ignore known issues
4. Use error grouping

### Upgrade Strategically
- Monitor error volume
- Upgrade when consistently hitting limits
- Consider annual billing (20% discount)

---

## Quick Reference

```bash
# Install Sentry
npm install --save @sentry/nextjs

# Setup Sentry
python3 setup_sentry.py /path/to/project <dsn>

# Test error
throw new Error("Test error");

# Capture message
Sentry.captureMessage("Something happened");

# Capture exception
Sentry.captureException(error);

# Set user
Sentry.setUser({ id: "123", email: "user@example.com" });

# Add tag
Sentry.setTag("page", "checkout");

# Add context
Sentry.setContext("order", { id: "123", total: 99.99 });
```

---

## Resources

- [Sentry Documentation](https://docs.sentry.io/)
- [Sentry Next.js Guide](https://docs.sentry.io/platforms/javascript/guides/nextjs/)
- [Sentry React Guide](https://docs.sentry.io/platforms/javascript/guides/react/)
- [Sentry Node.js Guide](https://docs.sentry.io/platforms/node/)
- [Sentry Python Guide](https://docs.sentry.io/platforms/python/)
