---
name: "github-workflow-automation"
description: "Specialized skill for github workflow automation workflows and automation."
---

# github-workflow-automation

**Automate Git commits, pull requests, releases, and CI/CD workflows**

---

## Overview

Automate GitHub workflows including intelligent auto-commits, CI/CD pipelines, automated releases, and pull request management. Saves time on repetitive Git operations and ensures consistent workflow practices.

**Time Saved**: ~20 minutes per workflow setup  
**Complexity**: Medium  
**Prerequisites**: Git, GitHub CLI (gh), Node.js

---

## When to Use

- Automating Git commits and pushes
- Setting up CI/CD pipelines
- Creating automated releases
- Managing pull requests programmatically
- Standardizing team workflows

---

## Features

1. **Auto-Commit** - Intelligent commit message generation and push
2. **CI/CD Templates** - Ready-to-use GitHub Actions workflows
3. **Release Automation** - Automated versioning and releases
4. **Workflow Patterns** - Best practices and common patterns

---

## Quick Start

### 1. Auto-Commit and Push

```bash
python3 /home/ubuntu/skills/github-workflow-automation/scripts/auto_commit.py /path/to/repo
```

### 2. Auto-Commit with Custom Message

```bash
python3 /home/ubuntu/skills/github-workflow-automation/scripts/auto_commit.py /path/to/repo "Add new feature"
```

### 3. Set Up CI/CD Workflow

```bash
# Copy template to project
cp /home/ubuntu/skills/github-workflow-automation/templates/ci-cd.yml /path/to/repo/.github/workflows/ci-cd.yml
```

---

## How It Works

### Auto-Commit Script

**Phase 1: Detection**
- Checks for git repository
- Detects changed files
- Analyzes file types

**Phase 2: Message Generation**
- Generates intelligent commit message based on changes
- Or uses custom message if provided

**Phase 3: Commit and Push**
- Stages all changes (`git add .`)
- Commits with generated/custom message
- Pushes to current branch

---

## Usage Examples

### Example 1: Auto-Commit After Making Changes

```bash
# Made changes to multiple files
python3 /home/ubuntu/skills/github-workflow-automation/scripts/auto_commit.py ~/my-project

# Output:
# 📁 Repository: /home/ubuntu/my-project
# 📝 Changes detected:
#  M src/index.js
#  M src/styles.css
# 💬 Commit message: Update JavaScript/TypeScript code
# 📦 Staging changes...
# 💾 Committing...
# ✅ Committed successfully
# 🌿 Current branch: main
# 🚀 Pushing to origin/main...
# ✅ Pushed successfully!
# 🎉 All done!
```

### Example 2: Custom Commit Message

```bash
python3 /home/ubuntu/skills/github-workflow-automation/scripts/auto_commit.py ~/my-project "Fix critical bug in authentication"

# Output:
# 📁 Repository: /home/ubuntu/my-project
# 📝 Changes detected:
#  M src/auth.js
# 💬 Commit message: Fix critical bug in authentication
# 📦 Staging changes...
# 💾 Committing...
# ✅ Committed successfully
# 🌿 Current branch: main
# 🚀 Pushing to origin/main...
# ✅ Pushed successfully!
# 🎉 All done!
```

### Example 3: Set Up CI/CD Pipeline

```bash
# Create workflows directory
mkdir -p ~/my-project/.github/workflows

# Copy CI/CD template
cp /home/ubuntu/skills/github-workflow-automation/templates/ci-cd.yml ~/my-project/.github/workflows/ci-cd.yml

# Commit and push
python3 /home/ubuntu/skills/github-workflow-automation/scripts/auto_commit.py ~/my-project "Add CI/CD workflow"
```

---

## Intelligent Commit Messages

The auto-commit script generates context-aware commit messages:

| File Types Changed | Generated Message |
|--------------------|-------------------|
| Only .md files | "Update documentation" |
| .py files | "Update Python code" |
| .js or .ts files | "Update JavaScript/TypeScript code" |
| .json files | "Update configuration" |
| .css or .scss files | "Update styles" |
| Single file | "Update {filename}" |
| Multiple files | "Update {count} files" |

---

## CI/CD Workflow Template

### Features
- ✅ Runs on push to main/develop
- ✅ Runs on pull requests
- ✅ Linting
- ✅ Testing
- ✅ Building
- ✅ Automatic deployment to production

### Customization

Edit `.github/workflows/ci-cd.yml`:

```yaml
# Change Node version
- uses: actions/setup-node@v3
  with:
    node-version: '20'  # Change here

# Add environment variables
env:
  DATABASE_URL: ${{ secrets.DATABASE_URL }}
  API_KEY: ${{ secrets.API_KEY }}

# Customize deployment
- name: Deploy to production
  run: |
    npm run deploy  # Your deploy command
```

---

## Release Workflow Template

### Features
- ✅ Triggers on version tags (v*)
- ✅ Creates GitHub release
- ✅ Builds artifacts
- ✅ Uploads build to release

### Usage

```bash
# Tag a release
git tag v1.0.0
git push --tags

# GitHub Actions will automatically:
# 1. Build the project
# 2. Create a release
# 3. Upload artifacts
```

---

## GitHub CLI Integration

### Create Pull Request

```bash
gh pr create --title "Add new feature" --body "Description of changes"
```

### Merge Pull Request

```bash
gh pr merge <pr-number> --squash
```

### Create Release

```bash
gh release create v1.0.0 --title "Version 1.0.0" --notes "Release notes"
```

### View Workflow Runs

```bash
gh run list
gh run view <run-id>
```

---

## Best Practices

### 1. Commit Messages
- Use present tense ("Add feature" not "Added feature")
- Be descriptive but concise
- Reference issues when applicable

### 2. Branch Strategy
- `main` - Production-ready code
- `develop` - Development branch
- `feature/*` - Feature branches
- `hotfix/*` - Urgent fixes

### 3. CI/CD
- Run tests on every push
- Deploy only from main branch
- Use caching for dependencies
- Set up notifications

### 4. Secrets Management
- Store sensitive data in GitHub Secrets
- Never commit secrets to repository
- Use environment-specific secrets

### 5. Workflow Organization
- One workflow per purpose
- Use descriptive names
- Document workflow purpose
- Keep workflows DRY

---

## Troubleshooting

### Auto-Commit Fails

**Problem**: "Not a git repository"
```bash
# Solution: Initialize git
cd /path/to/project
git init
git remote add origin <url>
```

**Problem**: "Failed to push"
```bash
# Solution: Pull first
git pull origin main --rebase
# Then run auto-commit again
```

### Workflow Not Running

**Problem**: Workflow file not detected
```bash
# Solution: Check file location
# Must be in .github/workflows/
# File must have .yml or .yaml extension
```

**Problem**: Workflow syntax error
```bash
# Solution: Validate YAML
# Use GitHub Actions validator or yamllint
```

### Permission Denied

**Problem**: "Permission denied" when pushing
```bash
# Solution: Check authentication
gh auth status
gh auth login
```

---

## Advanced Usage

### Conditional Workflows

```yaml
# Only run on specific paths
on:
  push:
    paths:
      - 'src/**'
      - '!**/*.md'
```

### Matrix Testing

```yaml
strategy:
  matrix:
    node-version: [16, 18, 20]
    os: [ubuntu-latest, windows-latest]
```

### Reusable Workflows

```yaml
# .github/workflows/reusable.yml
on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
```

---

## Files

### Scripts
- `scripts/auto_commit.py` - Intelligent auto-commit and push

### Templates
- `templates/ci-cd.yml` - Complete CI/CD pipeline
- `templates/release.yml` - Automated release workflow

### References
- `references/workflow_patterns.md` - Patterns and best practices

---

## Related Skills

- **deployment-automation** - Deploy after CI/CD passes
- **error-monitoring-setup** - Monitor deployed applications
- **testing-framework** - Generate tests for CI/CD

---

## Workflow

```
1. User makes changes to code
2. User runs auto_commit.py
3. Script detects changes and generates message
4. Script commits and pushes
5. GitHub Actions triggers CI/CD
6. Tests run automatically
7. If tests pass, deploy to production
```

---

## Success Criteria

✅ Changes committed automatically  
✅ Intelligent commit messages generated  
✅ CI/CD pipeline runs on push  
✅ Tests execute successfully  
✅ Deployment automated  

---

## Time Savings

**Manual Git Workflow**: ~5 minutes per commit
- Check status: 30 sec
- Stage files: 30 sec
- Write commit message: 2 min
- Commit: 30 sec
- Push: 30 sec
- Check CI/CD: 1 min

**With This Skill**: ~30 seconds
- Run auto_commit.py: 30 sec

**Savings**: ~4.5 minutes per commit  
**Daily Savings** (10 commits): ~45 minutes

---

## Future Enhancements

- Conventional commits support
- Automatic changelog generation
- Semantic versioning automation
- PR template generation
- Code review automation
- Merge conflict resolution
- Branch protection rules setup

---

**Created**: February 10, 2026  
**Status**: Production Ready  
**Tested**: GitHub, GitHub Actions, GitHub CLI
