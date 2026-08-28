# Archive Audit Protocol

## Purpose

Systematically inventory the user's existing tools, skills, agents, doctrines, and workflows to identify which assets are "productizable" — meaning someone outside the user's organization would pay for them.

## Step 1: Asset Collection

Ask the user (or infer from context) to enumerate their assets across these six categories:

| Category | Examples |
|---|---|
| **Skills** | Manus skills, prompt libraries, workflow templates |
| **Agents** | Named AI agents with specific roles or behaviors |
| **Tools** | Scripts, CLIs, automation pipelines, integrations |
| **Doctrines** | Frameworks, mental models, decision systems, playbooks |
| **Data** | Curated datasets, research archives, knowledge bases |
| **Infrastructure** | MCP servers, API integrations, deployment configs |

## Step 2: Productizability Scoring

Score each asset on five dimensions (1–10 each):

| Dimension | Question |
|---|---|
| **Pain Intensity** | How much does the target buyer suffer without this? |
| **Uniqueness** | How hard is this to replicate without the user's specific knowledge? |
| **Deliverability** | How easily can this be packaged and transferred to a buyer? |
| **Market Size** | How many people have this problem? |
| **Proof of Demand** | Is there documented evidence of people asking for this? |

**Total score = sum of five dimensions (max 50)**

Proceed to Phase 2 (Market Signal Scan) only for assets scoring 30+.

## Step 3: Asset Ranking Table

Produce a ranked table:

```
| Asset Name | Category | Pain | Unique | Deliver | Market | Demand | Total |
|---|---|---|---|---|---|---|---|
| [name] | [type] | /10 | /10 | /10 | /10 | /10 | /50 |
```

## Step 4: Top 3 Selection

Select the top 3 assets by total score. These become the candidates for Phase 2.

## Common Productizable Asset Patterns

These patterns consistently score 35+ and should be prioritized:

- **Installation/setup services** for complex tools (high pain, high deliverability)
- **Pre-configured agent bundles** for specific job roles (high uniqueness, high market size)
- **Workflow automation scripts** for repetitive business processes (high pain, high deliverability)
- **Decision frameworks** packaged as interactive tools or worksheets (high uniqueness)
- **Data pipelines** for specific industries (high pain, high uniqueness)
- **Training/onboarding systems** for AI tools (high demand, high deliverability)
