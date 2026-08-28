# [System Name] Architecture

**Date**: [Date]  
**System Name**: [Full system name]  
**Inspiration/Context**: [What inspired this design]

---

## Executive Summary

[2-3 paragraph overview of what this system does and why it matters]

**Core Principles**:
1. [Principle 1]
2. [Principle 2]
3. [Principle 3]
4. [Principle 4]
5. [Principle 5]

---

## System Overview

### [Component] Levels/Layers

[Description of the hierarchy or layering]

```
Level 0: [Description]
Level 1: [Description]
Level 2: [Description]
Level N: [Description]
```

**Current Implementation**: [What exists now]  
**Future Expansion**: [What will be added later]

### [Component] Types

**1. [Type 1]** ([Lifecycle description])
- [Example 1]
- [Example 2]

**2. [Type 2]** ([Lifecycle description])
- [Example 1]
- [Example 2]

---

## Core Protocol

[Description of how components interact]

### [Component] Identity

```json
{
  "field1": "value",
  "field2": "value"
}
```

### [Component] Authorities

What the component can do without asking permission:

```json
{
  "authorities": [
    "Authority 1",
    "Authority 2"
  ]
}
```

### [Component] Constraints

Hard limits the component cannot cross:

```json
{
  "constraints": [
    "Constraint 1",
    "Constraint 2"
  ]
}
```

### [Component] Lifecycle

**1. [Stage 1]**
- [Step 1]
- [Step 2]

**2. [Stage 2]**
- [Step 1]
- [Step 2]

---

## Data Model

### [Table 1] Table

```sql
CREATE TABLE [table_name] (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  [field1] [type] [constraints],
  [field2] [type] [constraints],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX [index_name] ON [table_name]([field]);
```

### [Table 2] Table

[Continue for all tables]

---

## [Key Algorithm/Protocol]

### When to [Action 1]

[Description of conditions]

1. **[Condition 1]** - [Description]
2. **[Condition 2]** - [Description]

### When to [Action 2]

[Description of conditions]

### [Algorithm] Process

**Step 1: [Step Name]**
```python
def step_one():
    # Pseudocode or actual code
    pass
```

**Step 2: [Step Name]**
```python
def step_two():
    # Pseudocode or actual code
    pass
```

---

## MVP Design

### Minimum Viable [System]

**Level 0: [Component]**
- [Description]

**Level 1: [Components]**
1. [Component 1]
2. [Component 2]

**Level 2: [Components]**
[Description]

---

## Interface Design

### [Interface 1]

**Requirements**: [What this interface must provide]

**Views**:

**1. [View Name]** ([Description])

[Description of what this view shows]

**Features**:
- [Feature 1]
- [Feature 2]

---

## Snap-On Expansion Protocol

### Adding a New [Component]

**Step 1: Define [Component]**

```json
{
  "definition": "..."
}
```

**Step 2: Register [Component]**

```sql
INSERT INTO [table] (...) VALUES (...);
```

**Step 3: [Component] Appears in [Interface]**

[Description of automatic integration]

---

## Implementation Phases

### Phase 1: [Phase Name] (Weeks X-Y)

**Goal**: [What this phase achieves]

**Deliverables**:
1. [Deliverable 1]
2. [Deliverable 2]

**Success Criteria**: [How you know this phase is complete]

### Phase 2: [Phase Name] (Weeks X-Y)

[Continue for all phases]

---

## Technical Stack

### Backend
- **[Technology]**: [Purpose]
- **[Technology]**: [Purpose]

### Frontend
- **[Technology]**: [Purpose]
- **[Technology]**: [Purpose]

### Integration
- **[Technology]**: [Purpose]

---

## Success Metrics

### Technical Metrics
- **[Metric]**: [Target]
- **[Metric]**: [Target]

### Business Metrics
- **[Metric]**: [Target]
- **[Metric]**: [Target]

### User Experience Metrics
- **[Metric]**: [Target]

---

## Risks and Mitigations

### Risk 1: [Risk Name]

**Risk**: [Description of the risk]

**Mitigation**:
- [Mitigation strategy 1]
- [Mitigation strategy 2]

### Risk 2: [Risk Name]

[Continue for all major risks]

---

## Conclusion

[Summary paragraph]

**Key Innovations**:
1. [Innovation 1]
2. [Innovation 2]

**Next Steps**:
1. [Next step 1]
2. [Next step 2]

[Closing statement]
