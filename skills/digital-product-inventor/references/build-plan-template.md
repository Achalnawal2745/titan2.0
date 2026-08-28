# Implementation Build Plan Template

## Structure

The build plan is organized into four time horizons. Each horizon has a clear goal, specific tasks, and a definition of done.

---

## Week 1 — Core Deliverable

**Goal:** Build the thing you sell. Nothing else.

The Week 1 deliverable is the minimum viable version of the product that a paying client could receive today. It does not need to be perfect. It needs to work and deliver the transformation.

| Task | Owner | Done When |
|---|---|---|
| [Core deliverable task 1] | You | [specific outcome] |
| [Core deliverable task 2] | You | [specific outcome] |
| [Core deliverable task 3] | You | [specific outcome] |

**Week 1 Definition of Done:** You could deliver this to a paying client right now and they would get the promised transformation.

---

## Week 2 — Delivery Infrastructure

**Goal:** Make it easy for clients to find you, book you, and pay you.

| Task | Tool | Done When |
|---|---|---|
| Replace mailto CTA with booking link | Calendly or Cal.com | CTA button opens real booking page |
| Add payment processing | Stripe or Gumroad | Client can pay without emailing you |
| Write onboarding email sequence | Gmail or ConvertKit | Client receives instructions automatically after booking |
| Add founder section to landing page | Webdev | Real photo + 2 sentences of credibility visible |

**Week 2 Definition of Done:** A stranger can find the landing page, understand the offer, book a session, and pay — without you being involved.

---

## Week 3 — Marketing Activation

**Goal:** Get the first 3 paying clients through organic channels.

| Channel | Post Format | Framing |
|---|---|---|
| [Community 1] | Problem-first post | "Anyone else struggle with [pain point]?" |
| [Community 2] | Value post | "I built [product] — here's what I learned" |
| [Community 3] | Direct offer | "Offering [service] — [price] — [CTA]" |
| Twitter/X | Thread | "What it actually takes to [outcome]" |

**Week 3 Definition of Done:** 3 posts published, at least 1 paid client booked.

---

## Month 2 — Paid Amplification

**Prerequisite:** At least 3 paid clients and at least 1 testimonial collected.

**Goal:** Scale what's working with a small paid budget.

| Action | Budget | Platform | Creative |
|---|---|---|---|
| Paid post promotion | $5–10/day | Reddit | Static image: pricing card + headline |
| Retargeting | $3–5/day | Twitter/X | Quote from real testimonial |

**Month 2 Definition of Done:** Cost per acquisition (CPA) is below 20% of entry tier price.

---

## 90-Day Revenue Target

| Month | Clients (Entry) | Clients (Expansion) | Revenue |
|---|---|---|---|
| Month 1 | [X] | 0 | $[amount] |
| Month 2 | [X] | [X] | $[amount] |
| Month 3 | [X] | [X] | $[amount] |
| **Total** | | | **$[amount]** |

---

## AI Model Routing Rule

Apply this routing rule to all development and content work:

| Task Type | Model | Reason |
|---|---|---|
| React components, landing page UI | Gemini 2.5 Pro | #1 WebDev Arena, 54% cheaper than Claude |
| Strategy, writing, client work | Claude Sonnet 4.5 | Best reasoning and instruction-following |
| Bulk automated code pipelines | GPT-5.2 Codex | 30% cheaper than Claude at scale |
| Simple extraction/formatting | GPT-5 mini | 12x cheaper than Claude for simple tasks |

---

## Known Pitfalls (Lessons from Open Claw Concierge)

**Mermaid diagrams:** Never use quotation marks inside node labels. The parser breaks silently. Use plain text only.

**Framer Motion:** Do not pass cubic-bezier arrays as `ease` inside variant definitions. Use string values ("easeOut", "easeInOut") or move the transition to the `transition` prop on the motion element.

**Landing page CTAs:** Never use `mailto:` as the CTA href. Always use a real booking URL. Mailto links kill conversion.

**Testimonials:** Never fabricate. Source real quotes from Reddit/Discord posts or wait for real client feedback. Fabricated testimonials are detectable and destroy trust.

**Pricing card:** The price must be visible without scrolling on mobile. Test on a 375px viewport before shipping.
