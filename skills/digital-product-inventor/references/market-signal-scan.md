# Market Signal Scan

## Purpose

Validate demand for a productizable asset before investing in building the product. The goal is to find evidence that real people are actively seeking what you have — not just that they "might" want it.

## Search Protocol

For each candidate asset, run searches across these channels in order:

### 1. Reddit (Highest Signal)

Search patterns:
- `"how do I [capability]" site:reddit.com`
- `"anyone know how to [capability]" site:reddit.com`
- `"looking for [tool/service type]" site:reddit.com`
- `"will pay for [capability]" site:reddit.com`

Target subreddits by category:
| Asset Category | Primary Subreddits |
|---|---|
| AI tools/agents | r/ClaudeCode, r/AI_Agents, r/LocalLLaMA, r/ChatGPT |
| Automation | r/n8n, r/zapier, r/nocode, r/selfhosted |
| Business tools | r/entrepreneur, r/smallbusiness, r/SaaS |
| Developer tools | r/webdev, r/programming, r/devops |
| Productivity | r/productivity, r/Notion, r/ObsidianMD |

### 2. Discord Communities

Search the Discord servers for the tool or ecosystem your asset is built on. Look for:
- #help or #support channels (people stuck = demand)
- #marketplace or #services channels (people already paying)
- Pinned messages about common problems

### 3. Twitter/X

Search: `"[tool name] install" OR "[tool name] setup" OR "[tool name] help"`
Filter by "Latest" to see recent demand.

### 4. Existing Sellers

Search: `"[capability] service" OR "[capability] setup" site:gumroad.com OR site:fiverr.com OR site:upwork.com`

This tells you: (a) whether a market exists, and (b) what the going rate is.

## Signal Scoring Rubric

After completing the search, assign a signal score (1–10):

| Score | Meaning |
|---|---|
| 1–3 | No evidence of demand. People don't know they need this yet. |
| 4–5 | Weak signal. A few posts, but no urgency or willingness to pay. |
| 6–7 | Moderate signal. Multiple posts, some urgency, some willingness to pay. |
| 8–9 | Strong signal. Many posts, clear urgency, documented willingness to pay. |
| 10 | Explosive signal. Active threads, people already paying, no dominant provider. |

**Proceed to Phase 3 only if signal score is 6 or higher.**

## Competitive Gap Analysis

For each competitor found, document:
- What they offer
- What they charge
- What they don't offer (the gap)
- What their reviews/complaints say

The gap between what competitors offer and what your asset can do is your positioning statement.

## Output Format

```
Asset: [name]
Signal Score: [1-10]
Evidence: [2-3 specific posts or threads with URLs]
Competitors: [list with prices]
Gap: [what you can do that they can't]
Recommended Entry Price: $[amount]
Recommended Expansion Price: $[amount]
```
