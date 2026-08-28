---
name: "error-monitoring-setup"
description: "Specialized skill for error monitoring setup workflows and automation."
---

# error-monitoring-setup

**Automated Sentry and error tracking setup for production applications**

---

## Overview

Automate the setup of Sentry error monitoring for Next.js, React, Node.js, and Python applications. Detects project type, installs dependencies, and configures error tracking in minutes.

**Time Saved**: ~45 minutes per setup  
**Complexity**: Low  
**Prerequisites**: Node.js/Python, Sentry account

---

## When to Use

- Setting up error monitoring for new projects
- Adding Sentry to existing applications
- Standardizing error tracking across projects
- Deploying to production
- Improving application reliability

---

## Supported Platforms

1. **Next.js** - Full-stack React framework
2. **React** - Frontend applications
3. **Node.js** - Backend APIs and services
4. **Python** - Flask, Django, FastAPI

---

## Quick Start

### 1. Get Sentry DSN

1. Go to [sentry.io](https://sentry.io)
2. Create account (free tier available)
3. Create new project
4. Copy your DSN (looks like: `https://...@sentry.io/...`)

### 2. Run Setup Script

```bash
python3 /home/ubuntu/skills/error-monitoring-setup/scripts/setup_sentry.py /path/to/project <your-dsn>
```

### 3. Test Error Tracking

```javascript
// Throw a test error
throw new Error("Test error - Sentry is working!");
```

### 4. Check Sentry Dashboard

Visit your Sentry dashboard to see the error.

---

## How It Works

### Phase 1: Detection
- Scans project for `package.json`, `requirements.txt`, etc.
- Identifies: Next.js, React, Node.js, or Python

### Phase 2: Installation
- Installs appropriate Sentry package
- `@sentry/nextjs`, `@sentry/react`, `@sentry/node`, or `sentry-sdk`

### Phase 3: Configuration
- Creates Sentry config files
- Sets up error tracking
- Configures performance monitoring
- Enables session replay (where applicable)

---

## Usage Examples

### Example 1: Setup Sentry for Next.js

```bash
python3 /home/ubuntu/skills/error-monitoring-setup/scripts/setup_sentry.py ~/my-nextjs-app https://abc123@sentry.io/456

# Output:
# 📁 Project: /home/ubuntu/my-nextjs-app
# 🔑 DSN: https://abc123...
# ✅ Detected project type: nextjs
# 📦 Installing Sentry package for nextjs...
# ✅ Sentry package installed
# 📝 Creating Sentry configuration...
# ✅ Created Sentry config files
# ✅ Sentry setup complete!
```

### Example 2: Setup Sentry for React

```bash
python3 /home/ubuntu/skills/error-monitoring-setup/scripts/setup_sentry.py ~/my-react-app https://abc123@sentry.io/456

# Output:
# 📁 Project: /home/ubuntu/my-react-app
# 🔑 DSN: https://abc123...
# ✅ Detected project type: react
# 📦 Installing Sentry package for react...
# ✅ Sentry package installed
# 📝 Creating Sentry configuration...
# ✅ Created Sentry config file
# ✅ Sentry setup complete!
```

### Example 3: Setup Sentry for Python

```bash
python3 /home/ubuntu/skills/error-monitoring-setup/scripts/setup_sentry.py ~/my-python-app https://abc123@sentry.io/456

# Output:
# 📁 Project: /home/ubuntu/my-python-app
# 🔑 DSN: https://abc123...
# ✅ Detected project type: python
# 📦 Installing Sentry package for python...
# ✅ Sentry package installed
# 📝 Creating Sentry configuration...
# ✅ Created Sentry config file
# ✅ Sentry setup complete!
```

---

## Configuration Files Created

### Next.js
- `sentry.client.config.js` - Client-side error tracking
- `sentry.server.config.js` - Server-side error tracking
- `sentry.edge.config.js` - Edge runtime error tracking

### React
- `src/sentry.js` - Browser error tracking

### Node.js
- `sentry.js` - Server error tracking

### Python
- `sentry_config.py` - Application error tracking

---

## Features Enabled

### Error Tracking ✅
- Automatic error capture
- Stack traces
- Error grouping
- User context
- Custom tags

### Performance Monitoring ✅
- Transaction tracking
- Slow query detection
- API performance
- Page load times

### Session Replay ✅ (Next.js/React)
- Video-like replay of user sessions
- See what users saw when errors occurred
- Privacy controls (mask sensitive data)

---

## Integration Steps

### Next.js

**Automatic** - Sentry config files are automatically loaded.

Test:
```javascript
// pages/index.js
export default function Home() {
  return (
    <button onClick={() => {
      throw new Error("Test error");
    }}>
      Test Sentry
    </button>
  );
}
```

### React

Import in `src/index.js`:
```javascript
import './sentry';
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
```

### Node.js

Import at the top of your main file:
```javascript
const Sentry = require('./sentry');
const express = require('express');

const app = express();

// Your routes...

// Error handler (must be last)
app.use(Sentry.Handlers.errorHandler());

app.listen(3000);
```

### Python

Import in your main file:
```python
from sentry_config import *
from flask import Flask

app = Flask(__name__)

# Your routes...

if __name__ == '__main__':
    app.run()
```

---

## Advanced Configuration

### Custom Sample Rates

Edit config files to adjust:

```javascript
Sentry.init({
  dsn: "your-dsn",
  tracesSampleRate: 0.1,  // 10% of transactions (production)
  replaysSessionSampleRate: 0.1,  // 10% of sessions
  replaysOnErrorSampleRate: 1.0,  // 100% of error sessions
});
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
Sentry.setTag("page", "checkout");
Sentry.setTag("feature", "payment");
```

### Custom Context

```javascript
Sentry.setContext("order", {
  id: "123",
  total: 99.99,
  items: 3
});
```

---

## Testing Error Tracking

### Manual Test

```javascript
// Throw error
throw new Error("Test error - Sentry is working!");

// Or capture manually
Sentry.captureMessage("Test message");
Sentry.captureException(new Error("Test exception"));
```

### Check Dashboard

1. Go to Sentry dashboard
2. Navigate to Issues
3. Verify test error appears
4. Check stack trace and context

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
Sentry.captureMessage("Test");
```

**Check Network**:
- Open browser DevTools
- Check Network tab
- Look for requests to sentry.io

### Wrong Project Type Detected

Manually specify project type by editing config files.

### Package Installation Failed

```bash
# Next.js/React/Node.js
npm install --save @sentry/nextjs

# Python
pip install sentry-sdk
```

---

## Best Practices

### 1. Set Appropriate Sample Rates
- Development: 100% (tracesSampleRate: 1.0)
- Production: 10-20% (tracesSampleRate: 0.1)

### 2. Use Environments
```javascript
environment: process.env.NODE_ENV
```

### 3. Track Releases
```javascript
release: "my-app@1.0.0"
```

### 4. Add User Context
```javascript
Sentry.setUser({ id: user.id });
```

### 5. Filter Sensitive Data
```javascript
beforeSend(event) {
  // Remove sensitive data
  delete event.request?.cookies;
  return event;
}
```

### 6. Set Up Alerts
- Configure Slack notifications
- Set up email alerts
- Create alert rules

### 7. Review Regularly
- Check dashboard daily
- Triage new errors
- Track trends
- Prioritize fixes

---

## Sentry Pricing

### Free Tier
- 5,000 errors/month
- 10,000 performance units/month
- 500 replays/month
- Perfect for side projects

### Team ($26/month)
- 50,000 errors/month
- 100,000 performance units/month
- 5,000 replays/month
- Good for small teams

### Business ($80/month)
- 500,000 errors/month
- 1M performance units/month
- 50,000 replays/month
- For growing companies

---

## Files

### Scripts
- `scripts/setup_sentry.py` - Automated Sentry setup

### Templates
- `templates/sentry.client.config.js` - Next.js client config

### References
- `references/monitoring_guide.md` - Complete monitoring guide

---

## Related Skills

- **deployment-automation** - Deploy after setting up monitoring
- **github-workflow-automation** - Add Sentry to CI/CD
- **testing-framework** - Test error handling

---

## Workflow

```
1. User creates Sentry account
2. User gets DSN from Sentry dashboard
3. User runs setup script with project path and DSN
4. Script detects project type
5. Script installs Sentry package
6. Script creates config files
7. User tests error tracking
8. Errors appear in Sentry dashboard
```

---

## Success Criteria

✅ Sentry package installed  
✅ Config files created  
✅ Error tracking working  
✅ Errors appear in dashboard  
✅ Stack traces visible  

---

## Time Savings

**Manual Setup**: ~45 minutes
- Create Sentry account: 5 min
- Read documentation: 10 min
- Install package: 2 min
- Configure: 15 min
- Test: 5 min
- Troubleshoot: 8 min

**With This Skill**: ~5 minutes
- Get DSN: 2 min
- Run script: 1 min
- Test: 2 min

**Savings**: ~40 minutes per setup

---

## Future Enhancements

- Support for more platforms (Vue, Angular, Ruby, Go)
- Automatic source map upload
- Custom error boundaries
- Performance optimization suggestions
- Alert rule templates
- Integration with other monitoring tools

---

**Created**: February 10, 2026  
**Status**: Production Ready  
**Tested**: Next.js, React, Node.js, Python
