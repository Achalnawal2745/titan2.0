# Landing Page Spec: Dark Luxury Concierge Design System

## Design Philosophy

The Dark Luxury Concierge system signals: premium, trustworthy, high-craft. It is not flashy. It is not corporate. It is the aesthetic of someone who knows exactly what they're doing and charges accordingly.

**Core design tokens:**
- Background: `oklch(0.14 0.008 260)` (deep charcoal, near-black)
- Surface: `oklch(0.19 0.008 260)` (elevated card surface)
- Gold primary: `oklch(0.72 0.12 75)` (warm gold, not yellow)
- Gold muted: `oklch(0.55 0.08 75)` (secondary gold)
- Text primary: `oklch(0.92 0.005 65)` (warm off-white)
- Text muted: `oklch(0.65 0.008 65)` (secondary text)

**Typography:**
- Display/headlines: Cormorant Garamond (serif, italic for taglines)
- Body: DM Sans (clean, readable, not Inter)
- Monospace/prices: DM Mono

**Load fonts via Google Fonts CDN:**
```html
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,600&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

## Section Structure (in order)

### 1. Navigation Bar
- Logo left, CTA button right ("Book a Session" or equivalent)
- Sticky, transparent with blur backdrop on scroll
- No hamburger menu — keep it minimal

### 2. Hero Section
- **Headline formula:** "[Outcome] — [timeframe]."
  - Example: "Your AI agent, installed and running — in one session."
- **Subheadline formula:** "[Specific mechanism] + [trust signal]."
  - Example: "Security-hardened, skill-loaded, and configured for your workflow."
- **CTA:** Single button — "Book Your Session" → Calendly/Cal.com link (never mailto)
- **Trust bar:** 3–4 logos or social proof numbers below the fold
- Background: generated hero image or dark gradient with subtle grain texture

### 3. Problem Section
- **Headline:** "The problem with [current state]"
- **3 pain points** — specific, emotional, not generic
  - Each pain point: bold label + 1–2 sentence description
  - Use real language from Reddit/Discord posts
- **Bridge:** "There's a better way." or "That's why [product] exists."

### 4. Process Section
- **Headline:** "How it works"
- **4 numbered steps** — concrete, not vague
  - Step format: Number + Bold title + 1 sentence description
  - Steps should tell a story: problem → diagnosis → execution → result
- Optional: timeline or visual connector between steps

### 5. Pricing Section
- **Headline:** "Simple, transparent pricing"
- **Pricing card component** (see task_b_pricing_card.tsx for implementation)
  - Tier toggle: Entry tier ↔ Expansion tier
  - Gold border pulse animation on hover
  - Price: large, centered, one-time only
  - Feature list: staggered reveal on enter
  - CTA: "Book Your Session" → booking link
  - Trust note below CTA: "Typically scheduled within 48 hours."
- **No subscription toggle.** No "most popular" badge unless there are 3+ tiers.

### 6. Social Proof Section
- **3–5 testimonials** — real quotes, not generic
  - Format: Quote + Name + Context (e.g., "Real estate agent, 12 years")
  - Source real quotes from Reddit/Discord/community posts when possible
  - Never fabricate testimonials

### 7. FAQ Section (optional but recommended)
- 4–6 questions that address the top objections
- Use the objection scripts from `pricing-strategy.md`
- Accordion component (shadcn/ui Accordion)

### 8. Final CTA Section
- Repeat the transformation statement
- Single CTA button
- Trust signals: "X clients served" or "Typically scheduled within 48 hours"

### 9. Footer
- Minimal: copyright, email link, social links
- No sitemap, no legal pages unless required

## Copy Formulas

**Hero headline variants:**
- "[Outcome] — [timeframe]."
- "The [adjective] way to [outcome]."
- "Finally, [outcome] — without [pain]."

**Problem section opener:**
- "Most [buyer persona] spend [time/money] trying to [task] and still end up with [bad outcome]."

**Process step verbs:** Audit, Configure, Harden, Deploy, Integrate, Activate, Optimize

**CTA button copy:** "Book Your Session", "Get Started Today", "Schedule Your Install", "Claim Your Spot"

## Technical Rules

- All CTAs must link to a real booking URL (Calendly, Cal.com, or Typeform). Never mailto.
- All Mermaid diagrams: no quotes in node labels. Plain text only.
- All colors in oklch format (Tailwind 4 requirement).
- Framer Motion easing: use string values ("easeOut", "easeInOut") not cubic-bezier arrays in variant definitions.
- Images: use CDN URLs from `manus-upload-file --webdev`. Never local paths.
- Fonts: load via Google Fonts CDN in index.html, not as local files.
