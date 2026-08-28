---
name: "brand-driven-ux-overhaul"
description: "Specialized skill for brand driven ux overhaul workflows and automation."
---

# Brand-Driven UX Overhaul

Systematic workflow for overhauling user experience driven by brand identity, user feedback, and design best practices.

## When to Use This Skill

- User requests interface redesign or rebranding
- Navigation feels cluttered or confusing
- Application lacks visual identity or brand consistency
- Need to simplify complex user flows
- Combining multiple UX improvements into cohesive overhaul

## Core Methodology: 4-Phase Workflow

### Phase 1: Collaborative Brainstorming

**Goal:** Understand user vision, pain points, and brand identity through structured dialogue.

**Process:**
1. Ask clarifying questions **one at a time** (never multiple questions)
2. Offer 4-5 concrete options (not open-ended questions)
3. Use analogies to clarify direction ("Think Nike Training Club meets cutting-edge AI")
4. Request brand assets early (logo, colors, fonts)
5. Confirm understanding before moving to planning

**Question Templates:** See `references/brainstorming-questions.md` for comprehensive question library covering:
- Pain point identification
- Brand identity & emotional tone
- Navigation structure
- Simplification strategies
- Color scheme & visual identity
- Layout structure

**Key Principles:**
- **One question at a time** - Avoid overwhelming user
- **Concrete options** - Give specific choices, not "what do you want?"
- **Clarify combinations** - "Option B with some E" → Ask for proportions
- **Gather assets** - Logo, colors, fonts needed before implementation

---

### Phase 2: Design System Foundation

**Goal:** Establish cohesive design system with colors, typography, spacing, and effects.

**Checklist:** See `references/design-system-checklist.md` for complete checklist covering:
- Color palette (background, foreground, primary, semantic colors)
- Typography (font families, loading strategy, type scale)
- Spacing system (base unit, scale, layout)
- Shadows & effects (card shadows, glow effects, backdrop blur)
- CSS variables implementation
- Accessibility requirements

**Key Files to Create/Update:**
- `client/src/index.css` - Global styles and CSS variables
- `client/src/lib/design-tokens.ts` - TypeScript color constants
- `client/index.html` - Font CDN links
- `tailwind.config.js` - Theme extensions

**Example Design Tokens:**
```typescript
export const colors = {
  background: '#0a1628', // Navy
  foreground: '#ffffff', // White
  primary: '#00d4ff', // Electric blue
  card: '#1a2942', // Card background
};
```

---

### Phase 3: Implementation Planning

**Goal:** Create detailed, step-by-step implementation plan with time estimates.

**Template:** Use `templates/implementation-plan-template.md` as starting point.

**Plan Structure:**
1. **Overview** - Design direction, key changes
2. **Task Breakdown** - 6-10 tasks, each 30-90 minutes
3. **Steps** - Break each task into 5-15 minute steps
4. **Code Snippets** - Include exact code for each step
5. **Verification** - How to test each step
6. **Checklists** - Before/during/after implementation

**Task Sizing Guidelines:**
- **Simple tasks** (30-45 min) - Single component, no dependencies
- **Medium tasks** (60-90 min) - Multiple components, some integration
- **Complex tasks** (90-120 min) - Major refactoring, cross-cutting changes

**Conservative Approach:**
- When refactoring complex pages, add new UI above/below existing UI first
- Test thoroughly before removing old UI
- Preserve all existing functionality
- Document rollback procedure

---

### Phase 4: Systematic Execution

**Goal:** Execute plan task-by-task with verification at each step.

**Workflow:**
1. Create `todo.md` with all tasks listed as `[ ]` items
2. Execute Task 1, mark complete `[x]` in `todo.md`
3. Run TypeScript compilation to verify
4. Execute Task 2, mark complete, verify
5. Repeat until all tasks complete
6. Final verification: TypeScript, server restart, status check
7. Create checkpoint with detailed description

**Verification After Each Task:**
- TypeScript compiles without errors
- Dev server running (restart if needed)
- Browser shows expected changes
- No console errors

**Final Verification:**
- All items in `todo.md` marked `[x]`
- TypeScript: No errors
- Dev server: Running cleanly
- Browser: All pages load correctly
- Checkpoint created

---

## Best Practices

### Brainstorming
- **One question at a time** - User can focus on single decision
- **Concrete options** - Easier to choose than open-ended
- **Use analogies** - "Energetic + tech-forward = Nike Training Club meets AI"
- **Request assets early** - Logo, colors, fonts needed for implementation

### Design System
- **Start with colors** - Foundation for all other decisions
- **Use CSS variables** - Enable theme switching, easier maintenance
- **Document tokens** - TypeScript file for type safety
- **Test accessibility** - Color contrast, keyboard navigation, screen readers

### Implementation
- **Conservative refactoring** - Add new, test, remove old
- **Update todo.md** - Mark tasks complete immediately after finishing
- **Verify frequently** - TypeScript after each task, not at end
- **Restart server** - Clear stale errors before final checkpoint

### Common Pitfalls
- **Skipping brainstorming** - Leads to misaligned design
- **Too many questions at once** - Overwhelms user
- **No brand assets** - Can't match exact branding
- **Aggressive refactoring** - Breaks existing functionality
- **Forgetting todo.md** - Lose track of progress

---

## Example Workflow

**Scenario:** Sales training dashboard needs FLEXX FIBER rebrand + simplified navigation

**Phase 1: Brainstorming (30 min)**
- Q1: Primary pain point? → "Cluttered interface + generic look"
- Q2: Which pages cluttered? → "Multiple areas"
- Q3: Brand feeling? → "Energetic + tech-forward"
- Q4: Navigation approach? → "Bottom tab bar"
- Q5: Color scheme? → [User provides logo image]
- Extract colors from logo: Navy (#0a1628) + Electric blue (#00d4ff)

**Phase 2: Design System (45 min)**
- Define color palette (navy bg, electric blue primary)
- Choose font (Inter from Google Fonts)
- Create design tokens file
- Update index.css with CSS variables
- Add card glow utilities

**Phase 3: Planning (30 min)**
- Task 1: Design System Foundation (45 min)
- Task 2: Bottom Tab Navigation (60 min)
- Task 3: One-Tap Quick Start (90 min)
- Task 4: Timeline History View (90 min)
- Task 5: Brand Header Component (45 min)
- Task 6: Responsive Polish (30 min)
- Total: 6 hours

**Phase 4: Execution (6 hours)**
- Create todo.md with 6 tasks
- Execute Task 1 → Mark [x] → Verify TypeScript
- Execute Task 2 → Mark [x] → Verify TypeScript
- ... repeat for all tasks
- Final verification: All [x], TypeScript OK, server running
- Create checkpoint: "FLEXX FIBER UX Overhaul Complete"

---

## Progressive Disclosure

**When to load references:**
- Load `references/brainstorming-questions.md` at start of Phase 1
- Load `references/design-system-checklist.md` at start of Phase 2
- Load `templates/implementation-plan-template.md` at start of Phase 3

**Keep in context:**
- Core 4-phase workflow (always)
- Current phase instructions (as needed)
- Relevant reference file (as needed)

---

## Success Criteria

- [ ] User vision clearly understood through brainstorming
- [ ] Brand assets collected (logo, colors, fonts)
- [ ] Design system established with CSS variables
- [ ] Implementation plan created with detailed steps
- [ ] All tasks executed and marked complete in todo.md
- [ ] TypeScript compiles without errors
- [ ] Dev server running cleanly
- [ ] All pages load correctly in browser
- [ ] Checkpoint created with detailed description
- [ ] User satisfied with final result
