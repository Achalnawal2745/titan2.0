# Checkpoint Guidelines

Best practices for creating informative, useful checkpoints.

## Checkpoint Timing

**When to Create Checkpoints:**
- After completing a feature or set of related features
- Before risky operations (major refactors, dependency upgrades)
- At logical milestones (MVP complete, beta ready)
- Before deployment to production

**When NOT to Create Checkpoints:**
- During active development of a single feature
- After every small change
- Before testing is complete

## Checkpoint Description Structure

### Title (Required)

Concise summary of what changed:
- ✅ "Add bulk CSV import and onboarding wizard"
- ✅ "Fix authentication bug in production"
- ❌ "Updates" (too vague)
- ❌ "Checkpoint 5" (not descriptive)

### Body (Recommended)

Use this structure for comprehensive checkpoints:

```markdown
## Features Added

### 1. [Feature Name]
- Key capability 1
- Key capability 2
- Added to [location]

### 2. [Feature Name]
- Key capability 1
- Key capability 2

## Bug Fixes

- Fixed [issue] that caused [problem]
- Resolved [error] in [component]

## Technical Details

**Database Changes:**
- Added [table/field] for [purpose]
- Migration: [migration file]

**New Dependencies:**
- [package]: [purpose]

**New Components/Files:**
- [path/to/file]: [purpose]

## Testing

- [X] tests passing
- [Y] tests failing (list reasons)

## Next Steps

- [Action item 1]
- [Action item 2]
```

## Examples

### Good Checkpoint: Feature Addition

```
Title: Platform completion: bulk rep code CSV import, onboarding wizard, and enhanced recording endpoint

## Features Added

### 1. Bulk Rep Code CSV Import
- Admin endpoint for bulk importing rep codes from CSV
- BulkRepCodeImport component with file upload
- Papa Parse integration for CSV parsing
- Detailed import results with error reporting
- CSV template download functionality
- Added to Admin page

### 2. Onboarding Wizard
- 5-step interactive onboarding flow for new users
- Database field: onboardingCompleted
- Auto-triggers on first login
- Progress indicators and skip option
- Navigates to Practice page after completion

## Technical Details

**Database Changes:**
- Added onboardingCompleted field to users table (migration 0012)

**New Components:**
- client/src/components/BulkRepCodeImport.tsx
- client/src/components/OnboardingWizard.tsx

**Dependencies:**
- Added papaparse for CSV parsing

## Testing
- 52 tests passing (no regressions)
- 3 tests failing (pre-existing external API issues)

## Next Steps
- Test bulk CSV import with real data
- Test onboarding wizard with new user account
- Deploy to production
```

### Good Checkpoint: Bug Fix

```
Title: Fix recording callback endpoint indentation error

Fixed critical indentation error (line 142) that prevented the Twilio recording callback endpoint from registering. The endpoint was returning HTML instead of processing webhooks, blocking automatic phone call recording and transcription.

**Changes:**
- server/_core/index.ts: Fixed indentation on line 142

**Testing:**
- Verified locally: endpoint returns 404 "Session not found" (correct behavior)
- Verified in production after deployment

**Impact:**
- Recording callbacks now work correctly
- Automatic transcription enabled
```

## Common Mistakes

**Too Vague:**
```
Title: Updates
Description: Made some changes
```

**Too Detailed:**
```
Title: Update line 42 in file.ts to change variable name from x to y
Description: [500 lines of code diff]
```

**Missing Context:**
```
Title: Add feature
Description: Added the feature we discussed
```
(Future you won't remember what "the feature" was)

## Webdev-Specific Guidelines

**Before Creating Checkpoint:**
1. Run `pnpm test` to verify no regressions
2. Check `webdev_check_status` for health
3. Verify feature works in dev server
4. Update todo.md to mark completed items
5. Move large media files to S3 (use `manus-upload-file`)

**Deployment Note:**
Include in description if checkpoint requires:
- Database migrations
- Environment variable changes
- External service configuration
- Manual testing steps after deployment
