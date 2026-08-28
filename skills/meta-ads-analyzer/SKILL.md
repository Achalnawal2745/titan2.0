---
name: "meta-ads-analyzer"
description: "Specialized skill for meta ads analyzer workflows and automation."
---

# Meta Ads Analysis & Diagnosis Skill

## When to Use This Skill

Use this skill when you need to **analyze and diagnose Meta Ads campaign performance**, including:
- Interpreting campaign, ad set, or ad-level performance data
- Identifying root causes of performance issues
- Generating actionable optimization recommendations
- Understanding why Meta's system makes certain budget allocation decisions

## Result Recommendations (MANDATORY for Final Reports)

> **IMPORTANT:** The following rules are **MANDATORY** and **MUST be strictly followed** when writing the final analysis report. These are not optional guidelines—they define the required standards for all deliverables.

- **NEVER recommend pausing or reducing budget for any segment based solely on higher average CPA/CPM in breakdown reports.** Higher average cost does NOT mean poor performance—it often reflects the system capturing low *marginal* cost opportunities earlier. Removing segments may increase overall costs. Always frame changes as testable hypotheses, not directives.
- **ALWAYS justify recommendations with data evidence, Meta's system mechanics, and expected impact on *overall campaign performance*.**
- **EVERY insight must include data evidence and explanation.** Every recommendation must be actionable and verifiable.
- **USE QUALIFIED LANGUAGE.** Say "Estimated Reach of ~1,000" not "You reached 1,000 people." All metrics are estimates.
- **ALIGN WITH OFFICIAL RECOMMENDATIONS.** Check `get_recommendations` API first. If diverging, explicitly acknowledge and explain why.
- **Disambiguate clicks.** Never use the term "clicks" alone. Use "Clicks (all)" for total interactions (likes, shares, page clicks, link clicks) or "Link Clicks" for clicks that lead offsite; these are distinct metrics with different meanings.**

## Core Principles

- **Holistic First:** Evaluate at aggregate level before drilling down. The system optimizes for the whole, not the parts.
- **Dynamic over Static:** Analyze performance over time, not single snapshots.
- **Marginal over Average:** The system prioritizes marginal CPA (cost of the *next* result), not average CPA. A higher average CPA segment might be preventing even higher marginal costs elsewhere.

## Analysis Workflow

**Reference Documents:**
- `references/breakdown_effect.md` - The Breakdown Effect with examples (read this first)
- `references/core_concepts.md` - Ad Auction, Pacing, Learning Phase overview
- `references/learning_phase.md` - Learning phase mechanics
- `references/ad_relevance_diagnostics.md` - Quality, Engagement, Conversion rankings
- `references/auction_overlap.md` - Diagnosing auction overlap
- `references/pacing.md` - Budget and bid pacing
- `references/bid_strategies.md` - Spend-based, goal-based, manual bidding
- `references/ad_auctions.md` - How auction winners are determined
- `references/performance_fluctuations.md` - Normal vs. concerning fluctuations

### Step 1: Identify the Correct Evaluation Level

This is the most critical step to avoid the Breakdown Effect.

| Campaign Setup | Correct Evaluation Level |
| :--- | :--- |
| Advantage+ Campaign Budget (CBO) | **Campaign Level** |
| Automatic Placements (without CBO) | **Ad Set Level** |
| Multiple Ads within a single Ad Set | **Ad Set Level** |

### Step 2: Analyze with Meta-Specific Lens

Focus on these Meta-specific analytical angles:

1. **Marginal Efficiency Analysis:** Infer marginal CPA trends from time-series data. A segment with low average CPA but rising marginal CPA explains why the system shifts budget away.
2. **Ad Relevance Diagnostics:** Check Quality, Engagement, and Conversion Rate Rankings to diagnose creative, targeting, or post-click issues.
3. **Learning Phase Status:** Determine if ad sets are still in learning phase (~50 results needed to exit).

### Step 3: Synthesize Findings Through Breakdown Effect Lens

Interpret all findings through the **Breakdown Effect**. Explain *why* the system makes certain decisions.

> **Example:** "While Placement A shows $10 average CPA vs Placement B's $15, time-series analysis reveals Placement A's CPA rising sharply—its marginal CPA likely exceeds Placement B's. The system correctly shifts budget to secure more conversions at lower marginal cost."
