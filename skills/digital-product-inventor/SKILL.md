---
name: digital-product-inventor
description: "Systematic framework for inventing, designing, pricing, and building digital product offers from an existing archive of tools, agents, doctrines, and skills. Use when turning a tool or capability into a sellable product, designing a new digital offer from scratch, going vertical into a new industry with an existing capability, building a product line from an AI agent stack, or creating a launch-ready product with a landing page, pricing strategy, and implementation plan. Combines deep client/market analysis, product architecture design, pricing strategy, landing page generation, and Google Drive delivery into one unified workflow."
---

# Digital Product Inventor

Turn your archive of tools, agents, and doctrines into launch-ready digital products — with vertical scalability across industries.

## When to Use

- You have a tool, agent, skill, or workflow and want to sell it
- You want to go vertical (same capability, new industry)
- You need a product offer with pricing, landing page, and build plan
- You want to systematically mine your archive for product ideas

## The 6-Phase Workflow

### Phase 1 — Archive Audit (What do you have?)

Read all relevant context about the user's existing tools, skills, agents, and doctrines. Build a structured inventory. See `references/archive-audit.md` for the full audit protocol and scoring rubric.

Key output: A ranked list of "productizable assets" — things you own that others would pay for.

### Phase 2 — Market Signal Scan (Is there demand?)

For each candidate asset, run a rapid market scan:
- Search Reddit, Discord, and community forums for people asking for this
- Check if anyone is already selling it and at what price
- Identify the gap between what exists and what the asset can do

Key output: A "signal score" (1–10) for each candidate. Only proceed with assets scoring 6+.

See `references/market-signal-scan.md` for search patterns and scoring criteria.

### Phase 3 — Product Architecture (What exactly is the product?)

Design the product using the 3-layer model:
1. **Core Transformation** — What problem does it solve? What is the before/after?
2. **Delivery Mechanism** — How is it delivered? (service, digital download, SaaS, agent, course)
3. **Expansion Path** — What does the buyer buy next?

Apply the Two-Tier Rule: every product line should have a $99–$599 entry product and a $999–$4,999 expansion product. One-time pricing only. No subscriptions.

See `references/product-architecture.md` for the full 3-layer model and Two-Tier Rule examples.

### Phase 4 — Pricing & Positioning (What does it cost and why?)

Use the Pricing Triangle to set price:
- **Floor**: What does it cost you to deliver?
- **Ceiling**: What is the buyer's perceived value?
- **Anchor**: What do competitors charge?

Price slightly above market average. State the price plainly — no quote requests when a price is listed.

See `references/pricing-strategy.md` for the full Pricing Triangle, market research method, and objection-handling scripts.

### Phase 5 — Landing Page & Marketing Brief

Build the landing page using the Dark Luxury Concierge design system (or adapt to vertical):
- Hero with primary transformation message
- Problem section (3 pain points, specific and emotional)
- Process section (4 steps, numbered, concrete)
- Pricing card (animated, one-time price, no subscription)
- Social proof (real quotes, not generic testimonials)
- CTA (direct booking link, not mailto)

Generate the marketing brief covering: target personas, messaging hierarchy, campaign channels, and 90-day success metrics.

See `references/landing-page-spec.md` for the full design system, section structure, and copy formulas.
See `references/marketing-brief-template.md` for the brief structure.

### Phase 6 — Implementation Build Plan

Produce a phased build plan with:
- Week 1: Core deliverable (the thing you sell)
- Week 2: Delivery infrastructure (booking, payment, onboarding)
- Week 3: Marketing activation (3 communities, content proof)
- Month 2: Paid amplification (only after 3 paid clients)

Include a 90-day revenue target and the routing rule for which AI model to use for each task type.

See `references/build-plan-template.md` for the full plan structure.

## Vertical Scaling

To go vertical with an existing product into a new industry:
1. Re-run Phase 2 (market scan) for the new vertical
2. Re-run Phase 3 (product architecture) — the core transformation changes, the delivery mechanism usually stays the same
3. Re-run Phase 4 (pricing) — different verticals have different price ceilings
4. Re-run Phase 5 (landing page) — swap industry-specific language and pain points
5. Keep Phase 6 (build plan) mostly the same

See `references/vertical-scaling-playbook.md` for industry-specific templates: legal, healthcare, real estate, e-commerce, coaching, and SaaS.

## Key Rules

- **One-time pricing only.** No subscriptions. No "request a quote" when a price is listed.
- **Two-tier structure always.** Entry product + expansion product. Never a single offer.
- **Price above average.** Slightly above market, not cheap, not inaccessible.
- **Mermaid diagrams: no quotes in node labels.** Use plain text only — quoted strings break the parser.
- **Landing page CTAs: no mailto.** Always a Calendly, Cal.com, or Typeform link.
- **Model routing:** Gemini 2.5 Pro for UI/React components. Claude Sonnet for strategy and writing. GPT-5.2 Codex for bulk automated pipelines.

## Deliverables Checklist

- [ ] Archive audit with ranked productizable assets
- [ ] Market signal scores for top 3 candidates
- [ ] Product architecture doc (3-layer model)
- [ ] Pricing strategy with Pricing Triangle
- [ ] Landing page (live, deployed)
- [ ] Marketing brief (Google Drive)
- [ ] 90-day implementation build plan (Google Drive)

## Related Skills

`get-to-know-a-client`, `openclaw-monetization-launcher`, `brainstorming`, `writing-plans`, `skill-creator`, `vertical-expansion-blueprint`
