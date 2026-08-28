# Vertical Roleplay Platform Builder - Requirements Analysis

## Using Systematic Feature Builder Methodology

This analysis reviews the skill design to identify gaps, risks, and missing components before implementation.

---

## ✅ What's Well-Defined

### 1. Core Architecture Pattern (STRONG)
- 10 reusable components clearly identified
- 90/10 split (reusable vs custom) is measurable
- Pattern validated against existing FLEXX FIBER codebase

### 2. Configuration Schema (STRONG)
- TypeScript interface is comprehensive
- Covers all 10 components
- Includes optional features for flexibility

### 3. Example Verticals (STRONG)
- 3 diverse examples (sales, dating, therapy)
- Demonstrates pattern applicability
- Clear differentiation between verticals

---

## ⚠️ Gaps & Risks Identified

### Gap 1: Generator Script Implementation Details

**Issue:** The design shows *what* the generator should do, but not *how* it does it.

**Missing Details:**
- How does template interpolation work? (Handlebars? Mustache? Custom?)
- How are file paths resolved during generation?
- How does the script handle existing files (overwrite? merge? skip?)
- What happens if generation fails mid-way? (rollback? partial state?)

**Risk Level:** HIGH - Core functionality undefined

**Recommendation:**
- Choose template engine (Handlebars is standard for this use case)
- Define file generation strategy (copy base + inject config)
- Add rollback mechanism for failed generations
- Create detailed pseudocode before implementing

---

### Gap 2: Base Platform Template

**Issue:** The skill assumes a "base platform template" exists, but it's not defined.

**Missing Details:**
- Where does this base template come from?
- Is it a copy of the FLEXX FIBER codebase with placeholders?
- How do we maintain it as the FLEXX FIBER codebase evolves?
- What files are in the base vs what gets generated?

**Risk Level:** HIGH - Can't generate platforms without base template

**Recommendation:**
- Create `templates/base-platform/` directory in skill
- Copy FLEXX FIBER codebase and add `{{placeholders}}`
- Document which files are static vs generated
- Add version tracking to keep base template in sync

---

### Gap 3: Database Migration Strategy

**Issue:** Config defines personas/modes, but how do we seed the database?

**Missing Details:**
- Do personas/modes go in the database or just prompts?
- If database: How are they seeded during deployment?
- If prompts only: How does frontend know available options?
- What about user-created content (custom scripts)?

**Risk Level:** MEDIUM - Affects data architecture

**Recommendation:**
- Add `seed-database.ts` script to base template
- Seed personas/modes from config during first run
- Document seeding strategy in deployment guide

---

### Gap 4: Voice Provider Abstraction

**Issue:** Config allows multiple voice providers, but implementation isn't defined.

**Missing Details:**
- How does the platform switch between Hume/ElevenLabs/OpenAI?
- Is there a voice provider interface/adapter pattern?
- What if a provider doesn't support a required feature?
- How are provider-specific configs validated?

**Risk Level:** MEDIUM - Affects flexibility claim

**Recommendation:**
- Create `server/voice-provider-interface.ts` in base template
- Implement adapter pattern for each provider
- Add provider validation to config validator
- Document provider capabilities matrix

---

### Gap 5: Terminology Replacement Logic

**Issue:** Config allows terminology overrides, but replacement strategy is unclear.

**Missing Details:**
- Is this a simple find/replace across all files?
- How do we handle plurals (session → sessions)?
- What about case variations (Session, SESSION, session)?
- How do we avoid replacing unintended matches?

**Risk Level:** LOW - Can be solved with careful implementation

**Recommendation:**
- Use token-based replacement ({{terminology.session}})
- Add terminology tokens to base template
- Document terminology conventions
- Test with all 3 example configs

---

### Gap 6: Testing Strategy for Generated Platforms

**Issue:** How do we know a generated platform actually works?

**Missing Details:**
- Should the skill include automated tests for generated platforms?
- How do we validate that all 3 example configs generate working platforms?
- What's the acceptance criteria for "working"?
- How do we test without deploying to production?

**Risk Level:** MEDIUM - Quality assurance undefined

**Recommendation:**
- Add `scripts/test-generated-platform.sh` to skill
- Test checklist: TypeScript compiles, server starts, database migrates, frontend renders
- Run tests on all 3 example configs before skill delivery
- Document testing process in deployment guide

---

### Gap 7: Coaching Prompt Integration

**Issue:** Config defines coaching prompt, but integration point is unclear.

**Missing Details:**
- Where does the coaching prompt get used? (server/coaching-service.ts?)
- How is the transcript passed to the LLM?
- What LLM is used? (invokeLLM from template?)
- How are coaching results stored in the database?

**Risk Level:** LOW - Implementation detail, not architectural

**Recommendation:**
- Create `server/coaching-service.ts` in base template
- Use `invokeLLM` with config.coachingPrompt
- Document coaching flow in architecture reference
- Add coaching endpoint to practice-router.ts

---

### Gap 8: Feature Flags Implementation

**Issue:** Config includes optional features (phone, replay, streaks), but no implementation.

**Missing Details:**
- How do feature flags affect code generation?
- Are disabled features removed from generated code or just hidden?
- How do we avoid generating broken code if a feature is disabled?
- What's the dependency graph between features?

**Risk Level:** MEDIUM - Affects code generation complexity

**Recommendation:**
- Use conditional generation (if feature.enabled, include file)
- Document feature dependencies (e.g., sessionReplay requires phone OR web)
- Add feature validation to config validator
- Start with all features enabled, add conditional logic later

---

### Gap 9: Deployment Automation

**Issue:** Skill design mentions `deploy-vertical.sh`, but no details.

**Missing Details:**
- Does this script deploy to Manus? External hosting?
- How are environment variables set?
- How is the database provisioned?
- What about domain/SSL setup?

**Risk Level:** LOW - Nice-to-have, not core functionality

**Recommendation:**
- Focus on local development first (pnpm dev)
- Add Manus deployment instructions to deployment guide
- Defer automated deployment to v2 of skill
- Document manual deployment steps clearly

---

### Gap 10: Versioning & Updates

**Issue:** What happens when the base template needs updates?

**Missing Details:**
- How do we version generated platforms?
- If FLEXX FIBER adds a feature, how do existing verticals get it?
- Can we "re-generate" a platform without losing customizations?
- How do we track which version of the skill generated a platform?

**Risk Level:** LOW - Future maintenance concern

**Recommendation:**
- Add `metadata.generatedBy` field to track skill version
- Document "manual merge" process for updates
- Consider "diff-based updates" in future versions
- For now: regenerate from scratch if major updates needed

---

## 🎯 Revised Requirements

Based on gaps identified, here are the **must-haves** before building:

### Must-Have (Blocking)
1. ✅ Choose template engine (Handlebars)
2. ✅ Create base platform template with placeholders
3. ✅ Define file generation strategy
4. ✅ Implement config validator
5. ✅ Create 3 complete example configs
6. ✅ Add testing checklist for generated platforms

### Should-Have (Important)
7. ✅ Database seeding strategy
8. ✅ Voice provider abstraction
9. ✅ Coaching prompt integration
10. ✅ Feature flags logic

### Nice-to-Have (Defer to v2)
11. ⏸️ Automated deployment script
12. ⏸️ Version tracking & update mechanism
13. ⏸️ Advanced terminology replacement (plurals, case)

---

## 📊 Implementation Complexity Assessment

### Original Estimate: "15-20 minutes"
**Revised Estimate: 3-4 hours**

**Why the increase?**
- Base platform template creation (60-90 min)
- Generator script with Handlebars (45-60 min)
- 3 complete example configs (30-45 min)
- Config validator (15-20 min)
- Testing & validation (30-45 min)
- Documentation (20-30 min)

**This is still reasonable** for a production-quality skill that can generate $10k/vertical platforms.

---

## 🚀 Recommended Approach

### Phase 1: Foundation (90 min)
1. Create base platform template from FLEXX FIBER
2. Add {{placeholder}} tokens throughout
3. Document which files are static vs generated

### Phase 2: Generator (60 min)
4. Install Handlebars in skill scripts/
5. Implement generate-platform.js with rollback
6. Add config validator with detailed error messages

### Phase 3: Examples (45 min)
7. Create sales.json (from existing FLEXX FIBER)
8. Create dating.json (new vertical)
9. Create therapy.json (new vertical)

### Phase 4: Testing (45 min)
10. Generate all 3 platforms
11. Verify TypeScript compiles
12. Test server starts & database migrates
13. Manually test one feature per platform

### Phase 5: Documentation (30 min)
14. Write comprehensive SKILL.md
15. Create deployment guide
16. Add architecture reference
17. Document known limitations

**Total: 4 hours 30 minutes**

---

## ✅ Success Criteria (Revised)

Before delivering the skill, verify:

1. **Generator Works**
   - [ ] Generates complete platform from config
   - [ ] All 3 example configs generate successfully
   - [ ] Generated platforms have no TypeScript errors

2. **Platforms Function**
   - [ ] Server starts without errors
   - [ ] Database migrates successfully
   - [ ] Frontend renders practice page
   - [ ] Can start a practice session

3. **Documentation Complete**
   - [ ] SKILL.md explains usage clearly
   - [ ] All 3 example configs are documented
   - [ ] Deployment guide covers setup steps
   - [ ] Known limitations are listed

4. **Quality Standards**
   - [ ] Config validator catches invalid configs
   - [ ] Error messages are helpful
   - [ ] File structure is organized
   - [ ] Code follows best practices

---

## 🎓 Key Insights from Analysis

### Insight 1: This is a "Meta-Tool"
This skill doesn't just solve one problem - it creates tools that solve problems. That's why quality is critical.

### Insight 2: The Base Template is the Foundation
Without a solid base template, the generator is useless. This is the most important artifact.

### Insight 3: Testing is Non-Negotiable
We can't ship a generator that produces broken platforms. Must test all 3 examples end-to-end.

### Insight 4: Start Simple, Iterate
Don't try to solve versioning/updates/deployment automation in v1. Focus on core: config → working platform.

---

## 📋 Next Step: Implementation Planning

Now that requirements are clear and gaps are identified, proceed to Phase 2: Create detailed implementation plan with tasks, time estimates, and file paths.

**Ready to create the implementation plan?**
