# iOS TestFlight GitHub Actions Automation Skill

Automate iOS TestFlight deployments using GitHub Actions after initial manual setup.

## Quick Start

This skill helps you set up automated TestFlight uploads using GitHub Actions with the official Apple-Actions/upload-testflight-build action.

## What This Skill Provides

- GitHub Actions workflow templates for Expo, React Native, and native iOS projects
- Step-by-step setup documentation
- Troubleshooting guide
- ExportOptions.plist template for native iOS

## When to Use

Use this skill when:
- Setting up CI/CD for iOS mobile apps
- Automating TestFlight uploads after manual first upload
- Configuring deployment pipeline for React Native, Expo, Flutter, or native iOS apps

## Prerequisites

Before using this skill, you must complete one-time manual setup:
1. Apple Developer account ($99/year)
2. App created in App Store Connect
3. App Store Connect API key generated
4. .p8 private key file downloaded
5. First build uploaded successfully via Transporter

## Files Included

### templates/
- `expo-testflight-workflow.yml` - GitHub Actions workflow for Expo projects
- `native-ios-testflight-workflow.yml` - GitHub Actions workflow for native iOS projects
- `react-native-testflight-workflow.yml` - GitHub Actions workflow for React Native projects
- `GITHUB_ACTIONS_SETUP.md` - Complete setup instructions
- `ExportOptions.plist` - Xcode export configuration template

### references/
- `EXECUTION_LOG.md` - Detailed creation history and architectural decisions

## Usage

Read `SKILL.md` for complete instructions on using this skill.

## Integration

This skill integrates with:
- `app-store-submission-packager` - Generate App Store submission documentation
- `production-system-audit` - Audit before deployment
- `feature-verification` - Verify features before release

## Author

Created as part of the unified skill arsenal strategy.
