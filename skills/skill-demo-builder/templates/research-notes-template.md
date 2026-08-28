# Research Notes - [API/Service Name]

**Date**: [Date]  
**Purpose**: [Why researching this]  
**Decision**: ✅ Use / ❌ Don't Use

---

## API Overview

**Name**: [API name]  
**Documentation**: [URL]  
**Base URL**: [Base URL]  
**Version**: [Version]

**Description**: [What the API does]

---

## Authentication

**Method**: [API Key / OAuth / JWT / None]

**Setup**:
```bash
[How to get credentials]
```

**Usage**:
```bash
[How to authenticate in requests]
```

**Notes**: [Any special considerations]

---

## Rate Limits

**Limits**:
- [Limit 1]: [value]
- [Limit 2]: [value]

**Quotas**:
- [Quota 1]: [value]
- [Quota 2]: [value]

**Strategies**:
- [How to handle rate limits]

---

## Key Endpoints

### Endpoint 1: [Name]

**URL**: `[method] [endpoint]`

**Purpose**: [What it does]

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| [param1] | [type] | ✅/❌ | [description] |
| [param2] | [type] | ✅/❌ | [description] |

**Example Request**:
```bash
curl -X [METHOD] '[URL]' \
  -H '[header]' \
  -d '[data]'
```

**Example Response**:
```json
{
  "[field]": "[value]"
}
```

**Notes**: [Any gotchas or tips]

---

### Endpoint 2: [Name]

**URL**: `[method] [endpoint]`

**Purpose**: [What it does]

**Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| [param1] | [type] | ✅/❌ | [description] |
| [param2] | [type] | ✅/❌ | [description] |

**Example Request**:
```bash
curl -X [METHOD] '[URL]' \
  -H '[header]' \
  -d '[data]'
```

**Example Response**:
```json
{
  "[field]": "[value]"
}
```

**Notes**: [Any gotchas or tips]

---

## Data Models

### Model 1: [Name]

```json
{
  "[field1]": "[type]",
  "[field2]": "[type]",
  "[field3]": {
    "[nested]": "[type]"
  }
}
```

**Field Descriptions**:
- `[field1]`: [Description]
- `[field2]`: [Description]
- `[field3]`: [Description]

---

### Model 2: [Name]

```json
{
  "[field1]": "[type]",
  "[field2]": "[type]"
}
```

**Field Descriptions**:
- `[field1]`: [Description]
- `[field2]`: [Description]

---

## Error Handling

**Common Errors**:

| Status Code | Error | Cause | Solution |
|-------------|-------|-------|----------|
| [code] | [error] | [cause] | [solution] |
| [code] | [error] | [cause] | [solution] |

**Error Response Format**:
```json
{
  "error": {
    "code": "[code]",
    "message": "[message]"
  }
}
```

---

## Pagination

**Method**: [Cursor / Offset / Page Number]

**Parameters**:
- `[param1]`: [Description]
- `[param2]`: [Description]

**Example**:
```bash
[pagination example]
```

**Notes**: [How to handle pagination]

---

## Gotchas & Tips

### Gotcha 1: [Issue]

**Problem**: [Description]

**Solution**: [How to handle]

**Example**: [Code example if applicable]

---

### Gotcha 2: [Issue]

**Problem**: [Description]

**Solution**: [How to handle]

**Example**: [Code example if applicable]

---

## Use Cases for Demo

### Use Case 1: [Name]

**Description**: [What this demonstrates]

**Endpoints Used**:
- [Endpoint 1]
- [Endpoint 2]

**Complexity**: [Simple / Medium / Complex]

**Value**: [Why this is a good demo]

---

### Use Case 2: [Name]

**Description**: [What this demonstrates]

**Endpoints Used**:
- [Endpoint 1]
- [Endpoint 2]

**Complexity**: [Simple / Medium / Complex]

**Value**: [Why this is a good demo]

---

## Decision

**Use this API?** ✅ Yes / ❌ No

**Rationale**:
- [Reason 1]
- [Reason 2]
- [Reason 3]

**For Demo Example**: [Which example will use this]

---

## Resources

**Documentation**:
- [Link 1] - [Description]
- [Link 2] - [Description]

**Examples**:
- [Link 1] - [Description]
- [Link 2] - [Description]

**Community**:
- [Link 1] - [Description]
- [Link 2] - [Description]

---

## Notes

[Any additional notes or observations]
