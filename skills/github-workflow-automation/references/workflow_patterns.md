# GitHub Workflow Patterns and Best Practices

## Common Workflow Patterns

### 1. CI/CD Pipeline
**Use Case**: Continuous integration and deployment  
**Triggers**: Push to main/develop, pull requests  
**Steps**: Lint → Test → Build → Deploy

### 2. Release Automation
**Use Case**: Automated releases on version tags  
**Triggers**: Push tags (v*)  
**Steps**: Build → Create release → Upload artifacts

### 3. Code Quality Checks
**Use Case**: Enforce code standards  
**Triggers**: Pull requests  
**Steps**: Lint → Format check → Type check → Security scan

### 4. Automated Testing
**Use Case**: Run tests on every change  
**Triggers**: Push, pull request  
**Steps**: Unit tests → Integration tests → E2E tests

---

## Workflow Best Practices

### 1. Use Caching
```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

### 2. Matrix Testing
```yaml
strategy:
  matrix:
    node-version: [16, 18, 20]
    os: [ubuntu-latest, windows-latest, macos-latest]
```

### 3. Conditional Execution
```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

### 4. Secrets Management
```yaml
env:
  API_KEY: ${{ secrets.API_KEY }}
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
```

### 5. Job Dependencies
```yaml
jobs:
  test:
    runs-on: ubuntu-latest
  deploy:
    needs: test
    runs-on: ubuntu-latest
```

---

## Common Triggers

### Push
```yaml
on:
  push:
    branches: [main, develop]
    paths:
      - 'src/**'
      - 'package.json'
```

### Pull Request
```yaml
on:
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened]
```

### Schedule (Cron)
```yaml
on:
  schedule:
    - cron: '0 0 * * *'  # Daily at midnight
```

### Manual Trigger
```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Environment to deploy to'
        required: true
        default: 'staging'
```

---

## Useful Actions

### Checkout Code
```yaml
- uses: actions/checkout@v3
```

### Setup Node.js
```yaml
- uses: actions/setup-node@v3
  with:
    node-version: '18'
    cache: 'npm'
```

### Setup Python
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.11'
    cache: 'pip'
```

### Upload Artifacts
```yaml
- uses: actions/upload-artifact@v3
  with:
    name: build
    path: dist/
```

### Download Artifacts
```yaml
- uses: actions/download-artifact@v3
  with:
    name: build
```

---

## Environment Variables

### Set Environment Variable
```yaml
env:
  NODE_ENV: production
  API_URL: https://api.example.com
```

### Use Secrets
```yaml
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}
```

### GitHub Context Variables
```yaml
- name: Print branch
  run: echo "Branch: ${{ github.ref }}"

- name: Print commit
  run: echo "Commit: ${{ github.sha }}"
```

---

## Debugging Workflows

### Enable Debug Logging
Set repository secrets:
- `ACTIONS_STEP_DEBUG`: true
- `ACTIONS_RUNNER_DEBUG`: true

### Print Context
```yaml
- name: Dump GitHub context
  run: echo '${{ toJSON(github) }}'

- name: Dump job context
  run: echo '${{ toJSON(job) }}'
```

### SSH into Runner
```yaml
- name: Setup tmate session
  uses: mxschmitt/action-tmate@v3
```

---

## Performance Optimization

### 1. Use Concurrency
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### 2. Skip CI
Add to commit message:
```
[skip ci]
[ci skip]
```

### 3. Parallel Jobs
```yaml
jobs:
  test-unit:
    runs-on: ubuntu-latest
  test-integration:
    runs-on: ubuntu-latest
  test-e2e:
    runs-on: ubuntu-latest
```

### 4. Selective Triggers
```yaml
on:
  push:
    paths:
      - 'src/**'
      - '!**/*.md'
```

---

## Security Best Practices

### 1. Use GITHUB_TOKEN
```yaml
permissions:
  contents: read
  pull-requests: write
```

### 2. Pin Action Versions
```yaml
- uses: actions/checkout@v3.5.2  # Good
- uses: actions/checkout@v3      # Okay
- uses: actions/checkout@main    # Bad
```

### 3. Validate Inputs
```yaml
- name: Validate input
  run: |
    if [[ ! "${{ inputs.environment }}" =~ ^(staging|production)$ ]]; then
      echo "Invalid environment"
      exit 1
    fi
```

### 4. Limit Secret Exposure
```yaml
env:
  # Don't do this
  SECRET: ${{ secrets.API_KEY }}

# Do this instead
- name: Use secret
  run: |
    # Secret only available in this step
  env:
    SECRET: ${{ secrets.API_KEY }}
```

---

## Workflow Examples

### Full CI/CD Pipeline
```yaml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm test

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v3
        with:
          name: build
          path: dist/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/download-artifact@v3
        with:
          name: build
      - name: Deploy
        run: |
          # Deploy to production
        env:
          DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

---

## Troubleshooting

### Workflow Not Triggering
- Check trigger conditions
- Verify branch names
- Check path filters
- Ensure workflow file is in `.github/workflows/`

### Job Failing
- Check logs
- Enable debug logging
- Test commands locally
- Verify secrets are set

### Slow Workflows
- Use caching
- Run jobs in parallel
- Skip unnecessary steps
- Use smaller runners

---

## Quick Reference

```bash
# Create workflow directory
mkdir -p .github/workflows

# Create workflow file
touch .github/workflows/ci.yml

# Test workflow locally (using act)
act push

# View workflow runs
gh run list

# View workflow logs
gh run view <run-id>

# Re-run workflow
gh run rerun <run-id>
```

---

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Awesome Actions](https://github.com/sdras/awesome-actions)
