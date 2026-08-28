# GitHub Actions Setup for TestFlight Automation

This document provides step-by-step instructions for setting up automated TestFlight deployments using GitHub Actions.

## Overview

This automation allows you to deploy iOS builds to TestFlight with a single button click or automatically on git push/tag. After the initial setup (15-30 minutes), future deployments require no manual intervention.

## Prerequisites

Before proceeding, ensure you have completed:

- [ ] Apple Developer account ($99/year)
- [ ] App created in App Store Connect
- [ ] App Store Connect API key generated
- [ ] .p8 private key file downloaded
- [ ] First build uploaded successfully via Transporter
- [ ] GitHub repository for your project

## Step 1: Add GitHub Secrets

GitHub secrets store sensitive information securely. You'll need to add three secrets for App Store Connect authentication.

### 1.1: Navigate to Repository Settings

1. Go to your GitHub repository
2. Click **Settings** (top menu)
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

### 1.2: Add APPSTORE_ISSUER_ID

1. Name: `APPSTORE_ISSUER_ID`
2. Value: Your Issuer ID from App Store Connect
   - Go to [App Store Connect](https://appstoreconnect.apple.com)
   - Click **Users and Access** → **Keys** tab
   - Copy the **Issuer ID** at the top of the page
3. Click **Add secret**

### 1.3: Add APPSTORE_API_KEY_ID

1. Name: `APPSTORE_API_KEY_ID`
2. Value: Your API Key ID
   - In App Store Connect → **Users and Access** → **Keys**
   - Find your API key in the list
   - Copy the **Key ID** (e.g., `ABC123DEFG`)
3. Click **Add secret**

### 1.4: Add APPSTORE_API_PRIVATE_KEY

1. Name: `APPSTORE_API_PRIVATE_KEY`
2. Value: Complete content of your .p8 file
   - Open your `AuthKey_XXXXX.p8` file in a text editor
   - Copy **everything** including the `-----BEGIN PRIVATE KEY-----` and `-----END PRIVATE KEY-----` lines
   - Paste the entire content
3. Click **Add secret**

### 1.5: Verify Secrets

After adding all three secrets, you should see:
- `APPSTORE_ISSUER_ID`
- `APPSTORE_API_KEY_ID`
- `APPSTORE_API_PRIVATE_KEY`

**Note:** For Expo projects, also add `EXPO_TOKEN` if using EAS build service.

## Step 2: Add Workflow File

The workflow file defines the automation process.

### 2.1: Create Workflow Directory

In your project root, create the directory structure:
```bash
mkdir -p .github/workflows
```

### 2.2: Add Workflow File

Copy the appropriate workflow file to `.github/workflows/deploy-testflight.yml`:
- **Expo projects:** Use `expo-testflight-workflow.yml`
- **React Native projects:** Use `react-native-testflight-workflow.yml`
- **Native iOS projects:** Use `native-ios-testflight-workflow.yml`

### 2.3: Customize Workflow

Edit the workflow file to match your project:

**For Expo projects:**
- Update `expo-version` if needed
- Verify `--profile production` matches your EAS profile

**For Native iOS / React Native projects:**
- Replace `YourApp` with your actual app name
- Update workspace path: `ios/YourApp.xcworkspace`
- Update scheme name: `-scheme YourApp`
- Verify `ExportOptions.plist` path

### 2.4: Commit and Push

```bash
git add .github/workflows/deploy-testflight.yml
git commit -m "Add GitHub Actions workflow for TestFlight deployment"
git push origin main
```

## Step 3: Test the Automation

### 3.1: Manual Trigger (Recommended First Test)

1. Go to your GitHub repository
2. Click **Actions** tab (top menu)
3. In the left sidebar, click **Deploy to TestFlight**
4. Click **Run workflow** button (right side)
5. Select the branch (usually `main`)
6. Click **Run workflow** (green button)

### 3.2: Monitor Progress

1. The workflow run appears in the list
2. Click on it to see real-time logs
3. Each step shows progress with ✓ or ✗
4. Typical duration:
   - Expo: 15-30 minutes
   - Native iOS: 10-20 minutes

### 3.3: Verify in TestFlight

1. Go to [App Store Connect](https://appstoreconnect.apple.com)
2. Click **My Apps** → Your App
3. Click **TestFlight** tab
4. Build should appear within 5-15 minutes after upload
5. Status changes from "Processing" to "Ready to Test"

## Step 4: Configure Deployment Triggers

By default, the workflow uses manual trigger (`workflow_dispatch`). You can enable automatic triggers:

### 4.1: Trigger on Git Tags

Uncomment in workflow file:
```yaml
on:
  push:
    tags:
      - 'v*'
```

**Usage:**
```bash
git tag v1.0.1
git push origin v1.0.1
```

### 4.2: Trigger on Push to Main

Uncomment in workflow file:
```yaml
on:
  push:
    branches:
      - main
```

**Usage:** Every push to `main` triggers deployment automatically.

### 4.3: Trigger on Pull Request Merge

```yaml
on:
  pull_request:
    types: [closed]
    branches:
      - main
```

**Usage:** Deployment triggers when PR is merged to `main`.

## Troubleshooting

### Issue: "Invalid API Key"

**Solution:**
1. Verify all three secrets are added correctly
2. Check .p8 file content includes BEGIN/END lines
3. Ensure no extra spaces or line breaks
4. Regenerate API key in App Store Connect if needed

### Issue: "Build Not Found"

**Solution:**
1. Check `app-path` in workflow matches actual .ipa location
2. Add debug step: `ls -la build/` to list files
3. Verify build step completed successfully

### Issue: "Code Signing Failed"

**Solution:**
1. Update provisioning profiles in Apple Developer Portal
2. Ensure certificates are not expired
3. For Expo: Verify EAS credentials are configured
4. For native iOS: Check `ExportOptions.plist` configuration

### Issue: "Workflow Doesn't Trigger"

**Solution:**
1. Verify trigger configuration in `on:` section
2. Check branch name matches (e.g., `main` vs `master`)
3. Use manual trigger first to test
4. Check GitHub Actions is enabled in repository settings

## Next Steps

### Recommended Actions

1. **Test with manual trigger** - Verify everything works before enabling automatic triggers
2. **Document for team** - Share this guide with team members
3. **Set up notifications** - Configure Slack/email notifications for deployment status
4. **Monitor costs** - GitHub Actions free tier includes 2,000 minutes/month

### Advanced Configuration

- **Multi-environment deployments** - Deploy to staging and production
- **Automated version bumping** - Increment version number automatically
- **Changelog generation** - Generate release notes from git commits
- **Slack notifications** - Get notified when deployments complete

### Maintenance

- **Rotate API keys annually** - Update GitHub secrets when rotating
- **Update Xcode version** - Keep `xcode-version` current in workflow
- **Monitor workflow runs** - Check Actions tab regularly for failures
- **Review logs** - Investigate failed runs promptly

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review workflow logs in GitHub Actions tab
3. Verify all prerequisites are met
4. Test with manual trigger before automatic triggers

## Estimated Timeline

- **Initial setup:** 15-30 minutes
- **First deployment:** 20-40 minutes (includes build time)
- **Subsequent deployments:** 15-30 minutes (fully automated)

## Success Checklist

- [ ] All three GitHub secrets added
- [ ] Workflow file committed and pushed
- [ ] Manual trigger test successful
- [ ] Build appears in TestFlight
- [ ] Team members can trigger deployments
- [ ] Documentation shared with team
