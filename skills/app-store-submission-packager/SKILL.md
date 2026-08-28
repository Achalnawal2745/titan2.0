---
name: "app-store-submission-packager"
description: "Specialized skill for app store submission packager workflows and automation."
---

# App Store Submission Packager

Generate production-ready documentation packages for submitting mobile apps to Apple App Store and Google Play Store.

## When to Use This Skill

Use this skill when:
- Preparing a mobile app for App Store or Google Play submission
- User requests "submission checklist", "app store guide", or "submission documentation"
- App is production-ready and needs submission materials
- Creating TestFlight installation and testing guides
- Generating marketing copy, privacy policies, or support pages for app stores

## What This Skill Provides

A complete submission package with 6-8 comprehensive documents:

1. **Master Submission Guide** - Step-by-step walkthrough of entire process
2. **Submission Checklist** - Track progress through all requirements
3. **Marketing Copy** - Ready-to-paste text for app store listings
4. **Privacy Policy Template** - GDPR/CCPA compliant policy
5. **Support Page Template** - FAQ and troubleshooting guide
6. **Screenshot Guide** - Specifications and capture instructions
7. **TestFlight Guide** - Physical device testing instructions
8. **Testing Checklist** - Printable feature verification checklist

## Core Workflow

### Phase 1: Gather App Information

Collect essential details about the app:

**Required Information:**
- App name and subtitle
- Bundle ID (iOS) / Package name (Android)
- Version and build numbers
- Developer account details (Apple ID, Team ID)
- Backend URL (if applicable)
- Build download links (Expo, EAS, or direct .ipa/.aab)

**App Details:**
- Primary category (e.g., Games → Card, Productivity, Social)
- Target audience and age rating
- Key features (3-5 main features)
- Unique selling points
- Gameplay or app flow description

**Technical Details:**
- Minimum iOS/Android version
- Device support (iPhone, iPad, Android phones/tablets)
- Required permissions (notifications, camera, location, etc.)
- External services used (push notifications, analytics, etc.)

### Phase 2: Generate Core Documentation

Create the foundation documents in this order:

#### 2.1: Submission Checklist

Comprehensive checklist covering:
- Apple Developer / Google Play Console account requirements
- Build file preparation and download
- App information fields (name, category, age rating)
- Marketing materials (description, keywords, promotional text)
- Visual assets (screenshots, app icon, preview videos)
- Legal requirements (privacy policy, support URL)
- Demo account for reviewers
- Export compliance and data privacy declarations
- Final review and submission steps

**Structure:**
- Organized by submission phase (preparation, screenshots, forms, upload, review)
- Checkboxes for each item
- Estimated time for each phase
- Quick reference tables for key information

#### 2.2: Marketing Copy

Ready-to-paste text for app store forms:

**App Description** (4000 characters max for iOS, 4000 for Android)
- Opening hook highlighting main value proposition
- Key features section with bullet points
- How it works / gameplay explanation
- Target audience section
- Closing call-to-action

**Keywords** (100 characters for iOS, 50 for Android)
- Primary keywords (app type, main features)
- Secondary keywords (related terms, use cases)
- Comma-separated, no spaces after commas

**Promotional Text** (170 characters for iOS)
- Compelling one-liner for app store listing

**What's New** (4000 characters)
- Version-specific release notes

**Review Notes**
- Instructions for Apple/Google reviewers
- Demo account credentials
- Testing instructions
- Backend information

**Privacy Practices**
- Data collection declarations
- Tracking usage statements

#### 2.3: Privacy Policy Template

GDPR/CCPA compliant privacy policy covering:
- Introduction and scope
- Information collected (account data, usage data, device info)
- How information is used
- Data storage and security measures
- Data sharing and third-party services
- User rights (access, correction, deletion)
- Children's privacy (if applicable)
- International data transfers
- Contact information
- Changes to policy

**Format:** Markdown with clear sections, ready to publish as webpage

#### 2.4: Support Page Template

Comprehensive support page with:
- How to use the app (getting started guide)
- Frequently asked questions
- Troubleshooting common issues
- Contact information
- System requirements
- Feature requests and bug reporting

**Format:** Markdown, ready to publish on GitHub Pages or website

### Phase 3: Create Visual Asset Guides

#### 3.1: Screenshot Guide

Detailed instructions for capturing and preparing screenshots:

**Required Sizes:**
- iOS: 6.7" (1290x2796), 6.5" (1242x2688), 5.5" (1242x2208)
- iPad: 12.9" (2048x2732)
- Android: Multiple density buckets

**Screens to Capture:**
- Identify 6-10 key screens that showcase app features
- Provide specific guidance for each screen
- Include captions and ordering recommendations

**Technical Instructions:**
- How to capture using iOS Simulator / Android Emulator
- How to capture on physical devices
- Editing and resizing guidelines
- File naming conventions
- Upload instructions

#### 3.2: App Icon Specifications

Document icon requirements:
- iOS: 1024x1024 PNG, no transparency, no rounded corners
- Android: Adaptive icon layers (foreground, background, monochrome)
- Verify existing icon meets requirements

### Phase 4: TestFlight & Physical Device Testing

#### 4.1: TestFlight Installation Guide

Step-by-step guide for iOS testing:

**Upload Process:**
1. Download Transporter app
2. Download .ipa build
3. Sign in and upload build
4. Wait for processing (15-60 minutes)

**TestFlight Setup:**
1. Install TestFlight app on iPhone/iPad
2. Add internal testers in App Store Connect
3. Install app from TestFlight
4. Grant permissions

**Testing Instructions:**
- Create test accounts (4+ for multiplayer apps)
- Test all core features
- Verify push notifications on real device
- Test offline behavior
- Check different device sizes

#### 4.2: Physical Device Testing Checklist

Comprehensive testing checklist covering:

**Functional Tests:**
- Authentication (login, register, logout)
- Core features (all primary user flows)
- Navigation and UI interactions
- Data persistence
- Error handling

**Device-Specific Tests:**
- Push notifications (critical!)
- Haptic feedback
- Camera/photo access (if applicable)
- Location services (if applicable)
- Offline functionality

**Performance Tests:**
- Loading times
- Animation smoothness
- Memory usage
- Battery consumption
- Network error recovery

**Multi-Device Tests:**
- Small screens (iPhone SE)
- Standard screens (iPhone 14)
- Large screens (iPhone 15 Pro Max)
- Tablets (iPad)
- Different iOS versions

**Format:** Printable checklist with checkboxes and space for notes

### Phase 5: Create Master Guide

Comprehensive guide tying everything together:

**Structure:**
1. Overview and quick start
2. What's included in the package
3. Step-by-step submission process
   - Phase 1: Preparation (2-3 hours)
   - Phase 2: Screenshots (2-3 hours)
   - Phase 3: App Store Connect forms (1-2 hours)
   - Phase 4: Build upload (30 minutes)
   - Phase 5: Final review and submission (15 minutes)
4. Review timeline expectations
5. Common rejection reasons and solutions
6. Post-submission checklist
7. Success metrics and next steps

**Key Features:**
- Timeline estimates for each phase
- Quick reference tables
- Links to all other documents
- Troubleshooting section
- Additional resources

### Phase 6: Package and Deliver

Create a README for the documentation package:

**Package README Contents:**
- Overview of all included documents
- Quick start guide (which document to read first)
- Build information and download links
- App status summary (health score, issues resolved)
- Pre-submission checklist
- Timeline summary
- Required URLs to create
- Common questions

**Delivery:**
1. Save all documents to `/docs/` directory in project
2. Create checkpoint with descriptive message
3. Deliver checkpoint to user with brief summary
4. Highlight 2-3 next steps (e.g., create support website, take screenshots, upload to TestFlight)

## Document Quality Standards

### Writing Style

- Use clear, actionable language
- Write in second person ("you")
- Use imperative mood for instructions ("Click Submit", not "You should click Submit")
- Break complex steps into numbered sub-steps
- Provide context for why each step matters

### Structure

- Use consistent heading hierarchy
- Include table of contents for long documents (500+ lines)
- Use tables for specifications and comparisons
- Use blockquotes for important warnings or notes
- Include estimated time for each major section

### Completeness

- Provide actual example text, not just templates
- Include character counts for text fields
- Specify exact dimensions for images
- List all required fields and permissions
- Include troubleshooting for common issues

### Accuracy

- Verify all URLs and links are correct
- Ensure version numbers match actual build
- Confirm bundle IDs and package names
- Check that all referenced files exist
- Validate that instructions match current platform requirements

## Platform-Specific Considerations

### iOS / App Store

**Key Requirements:**
- Apple Developer Program membership ($99/year)
- Privacy policy URL (required if collecting data)
- Support URL (always required)
- Demo account for reviewers (if login required)
- Export compliance declaration
- Age rating questionnaire
- App privacy declarations

**Common Pitfalls:**
- Incomplete demo account instructions
- Privacy policy doesn't match data collection
- Screenshots don't match actual app
- Missing support URL
- Incorrect export compliance answers

### Android / Google Play

**Key Requirements:**
- Google Play Console account ($25 one-time)
- Privacy policy URL (required if collecting data)
- Content rating questionnaire
- Target API level requirements
- App signing by Google Play
- Data safety declarations

**Common Pitfalls:**
- Incorrect content rating
- Missing data safety declarations
- Target API level too low
- Incomplete app signing setup

## Customization Guidelines

Adapt the documentation based on:

**App Type:**
- Games: Emphasize gameplay, age rating, in-app purchases
- Productivity: Highlight features, integrations, privacy
- Social: Focus on user safety, content moderation, privacy
- E-commerce: Payment processing, security, refund policy

**Complexity:**
- Simple apps: Shorter guides, fewer screenshots
- Complex apps: Detailed feature testing, more screenshots
- Multiplayer: Emphasize testing with multiple accounts
- Offline-capable: Test offline functionality thoroughly

**Audience:**
- First-time publishers: More detailed explanations, troubleshooting
- Experienced developers: Concise checklists, quick reference
- Teams: Assign responsibilities, parallel task execution

## Success Criteria

A complete submission package should:

- [ ] Include all 6-8 core documents
- [ ] Provide ready-to-paste text for all form fields
- [ ] Specify exact requirements for all visual assets
- [ ] Include step-by-step TestFlight instructions
- [ ] Provide comprehensive testing checklist
- [ ] Estimate time for each phase
- [ ] List common rejection reasons with solutions
- [ ] Include troubleshooting for common issues
- [ ] Reference all build files and download links
- [ ] Provide clear next steps after delivery

## Example Usage

**User request:** "Create a checklist of everything needed before submitting to the App Store"

**Agent response:**
1. Gather app information (name, bundle ID, version, build links)
2. Generate submission checklist
3. Create marketing copy with app description, keywords, promotional text
4. Write privacy policy template
5. Create support page template
6. Write screenshot guide with required sizes and screens
7. Create TestFlight installation guide
8. Generate testing checklist
9. Write master submission guide
10. Create package README
11. Save checkpoint and deliver to user

**Deliverables:** 8 comprehensive documents in `/docs/` directory, ready to use immediately.

## Tips for Effective Documentation

1. **Be specific with examples** - Don't just say "write app description", provide actual example text
2. **Include character counts** - Show how much space is used vs. available
3. **Provide exact dimensions** - Specify pixel dimensions for all images
4. **Estimate time** - Help users plan their submission timeline
5. **Anticipate questions** - Include FAQ and troubleshooting sections
6. **Link related docs** - Cross-reference between documents
7. **Use tables** - Organize specifications and requirements clearly
8. **Add checkboxes** - Make checklists actionable and trackable
9. **Highlight critical items** - Mark must-have vs. optional items
10. **Keep it current** - Reference latest platform requirements

## Common Mistakes to Avoid

- Creating generic templates without app-specific content
- Missing character counts on text fields
- Forgetting to include demo account credentials
- Not specifying exact screenshot dimensions
- Omitting TestFlight testing instructions
- Failing to mention push notification testing
- Not providing troubleshooting guidance
- Missing timeline estimates
- Forgetting to create package README
- Not linking to build download URLs
