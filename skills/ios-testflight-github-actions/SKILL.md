---
name: "ios-testflight-github-actions"
description: "Specialized skill for ios testflight github actions workflows and automation."
---

# iOS TestFlight GitHub Actions Automation

Automate iOS TestFlight deployments using GitHub Actions with the official Apple-Actions/upload-testflight-build action.

## When to Use This Skill

Use this skill when:
- Setting up CI/CD for iOS mobile apps
- Automating TestFlight uploads after manual first upload
- User requests "automate TestFlight", "GitHub Actions iOS", or "CI/CD for mobile app"
- Configuring deployment pipeline for React Native, Expo, Flutter, or native iOS apps
- Transitioning from manual uploads to automated deployments

## Prerequisites

**Before using this skill, user MUST complete one-time manual setup:**

1. ✅ Apple Developer account ($99/year)
2. ✅ App created in App Store Connect
3. ✅ App Store Connect API key generated
4. ✅ .p8 private key file downloaded
5. ✅ First build uploaded successfully via Transporter

**If prerequisites are NOT met:** Direct user to complete manual setup first using the TestFlight installation guide.

## What This Skill Provides

Complete GitHub Actions automation setup including:

1. **GitHub Actions workflow file** - `.github/workflows/deploy-testflight.yml`
2. **Setup instructions** - Step-by-step guide for adding secrets
3. **Build configuration** - Expo EAS or Xcode build integration
4. **Deployment triggers** - Manual, tag-based, or branch-based
5. **Testing guide** - How to verify the automation works
6. **Troubleshooting** - Common issues and solutions

## Core Workflow

### Phase 1: Verify Prerequisites

Before starting automation setup, verify user has completed manual setup:

**Questions to ask:**
- "Have you successfully uploaded your first build to TestFlight manually?"
- "Do you have your App Store Connect API key (.p8 file)?"
- "Do you have the Key ID and Issuer ID from App Store Connect?"

**If NO to any:** Stop and direct user to complete manual setup first.

**If YES to all:** Proceed with automation setup.

### Phase 2: Gather Project Information

Collect essential details about the project:

**Required Information:**
- Project type (Expo, React Native, Flutter, native iOS)
- Repository location (GitHub repo URL or name)
- Build method (Expo EAS, Xcode, fastlane)
- Bundle ID / App ID
- Deployment trigger preference (manual, on tag, on push to main)

**For Expo projects:**
- EAS project ID
- Expo account credentials (if needed)

**For native iOS projects:**
- Xcode project/workspace path
- Scheme name
- Build configuration (Release, Production, etc.)

### Phase 3: Create GitHub Actions Workflow

Generate `.github/workflows/deploy-testflight.yml` based on project type.

#### 3.1: Expo Projects

Use the Expo workflow template from `templates/expo-testflight-workflow.yml`:

**Key steps:**
1. Checkout code
2. Setup Node.js
3. Install dependencies
4. Build with EAS (`eas build --platform ios --profile production`)
5. Download .ipa artifact
6. Upload to TestFlight using Apple-Actions

**Trigger options:**
- Manual: `workflow_dispatch`
- On tag: `push: tags: ['v*']`
- On main branch: `push: branches: ['main']`

#### 3.2: Native iOS / React Native Projects

Use the native iOS workflow template from `templates/native-ios-testflight-workflow.yml`:

**Key steps:**
1. Checkout code
2. Setup Xcode
3. Install dependencies (CocoaPods, npm)
4. Build and archive with xcodebuild
5. Export .ipa
6. Upload to TestFlight using Apple-Actions

**Build command example:**
```bash
xcodebuild archive \
  -workspace MyApp.xcworkspace \
  -scheme MyApp \
  -configuration Release \
  -archivePath build/MyApp.xcarchive
```

#### 3.3: Configure Apple-Actions

All workflows use the official `apple-actions/upload-testflight-build@v3` action:

```yaml
- name: Upload to TestFlight
  uses: apple-actions/upload-testflight-build@v3
  with:
    app-path: path/to/app.ipa
    issuer-id: ${{ secrets.APPSTORE_ISSUER_ID }}
    api-key-id: ${{ secrets.APPSTORE_API_KEY_ID }}
    api-private-key: ${{ secrets.APPSTORE_API_PRIVATE_KEY }}
```

### Phase 4: Setup GitHub Secrets

Create comprehensive instructions for adding secrets to GitHub repository.

**Required Secrets:**

| Secret Name | Description | How to Get |
|------------|-------------|------------|
| `APPSTORE_ISSUER_ID` | App Store Connect Issuer ID | App Store Connect → Users and Access → Keys → Issuer ID |
| `APPSTORE_API_KEY_ID` | API Key ID | App Store Connect → Users and Access → Keys → Key ID |
| `APPSTORE_API_PRIVATE_KEY` | .p8 private key content | Copy entire content of AuthKey_XXXXX.p8 file |

**Step-by-step instructions:**
1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add each secret with exact name and value
4. Verify all three secrets are added

**For Expo projects, also add:**
- `EXPO_TOKEN` (if using EAS)

### Phase 5: Create Setup Documentation

Generate `docs/GITHUB_ACTIONS_SETUP.md` with:

**Contents:**
1. Overview of the automation
2. Prerequisites checklist
3. Step-by-step setup instructions
4. How to trigger deployments
5. How to monitor workflow runs
6. Troubleshooting common issues
7. Next steps and best practices

**Include:**
- Screenshots or ASCII diagrams of GitHub UI
- Example workflow run output
- Links to relevant documentation
- Estimated setup time (15-30 minutes)

### Phase 6: Test the Automation

Provide testing instructions:

**Manual Trigger Test:**
1. Go to GitHub → Actions tab
2. Select "Deploy to TestFlight" workflow
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow" button
6. Monitor progress in real-time
7. Verify build appears in TestFlight

**Tag-Based Trigger Test (if configured):**
1. Create and push a new tag: `git tag v1.0.1 && git push origin v1.0.1`
2. Workflow should trigger automatically
3. Monitor in Actions tab
4. Verify build in TestFlight

**Expected Timeline:**
- Expo builds: 15-30 minutes
- Native iOS builds: 10-20 minutes
- TestFlight processing: 5-15 minutes after upload

### Phase 7: Deliver and Document

**Deliverables:**
1. `.github/workflows/deploy-testflight.yml` - GitHub Actions workflow
2. `docs/GITHUB_ACTIONS_SETUP.md` - Setup instructions
3. `docs/DEPLOYMENT_GUIDE.md` - How to use the automation
4. `docs/TROUBLESHOOTING.md` - Common issues and solutions

**Commit and push files:**
```bash
git add .github/workflows/deploy-testflight.yml docs/
git commit -m "Add GitHub Actions automation for TestFlight deployments"
git push origin main
```

**Inform user:**
- Automation is ready to use
- Next steps: Add GitHub secrets
- How to trigger first automated deployment
- Where to monitor workflow runs

## Troubleshooting

### Common Issues

**Issue 1: "Invalid API Key"**
- **Cause:** Incorrect API key, Key ID, or Issuer ID
- **Solution:** Verify all three values in GitHub secrets match App Store Connect
- **Check:** .p8 file content copied completely including BEGIN/END lines

**Issue 2: "Build Not Found"**
- **Cause:** .ipa file path incorrect
- **Solution:** Check artifact download path and update `app-path` in workflow
- **Debug:** Add `ls -la` step to list files after build

**Issue 3: "Code Signing Failed"**
- **Cause:** Missing or expired provisioning profile
- **Solution:** Update provisioning profiles in Apple Developer Portal
- **Note:** Expo handles this automatically, native iOS requires manual management

**Issue 4: "Workflow Doesn't Trigger"**
- **Cause:** Incorrect trigger configuration or branch name
- **Solution:** Verify `on:` section matches your git workflow
- **Test:** Use `workflow_dispatch` for manual testing first

**Issue 5: "TestFlight Upload Times Out"**
- **Cause:** Large .ipa file or slow network
- **Solution:** Increase timeout in workflow (default 30 minutes)
- **Add:** `timeout-minutes: 60` to upload step

## Success Criteria

A successful automation setup should:

- [ ] GitHub Actions workflow file created and committed
- [ ] All required secrets added to GitHub repository
- [ ] Workflow successfully triggers (manual or automatic)
- [ ] Build completes without errors
- [ ] .ipa file uploads to TestFlight
- [ ] Build appears in TestFlight within 15 minutes
- [ ] Documentation created for team reference
- [ ] User can trigger deployments independently
