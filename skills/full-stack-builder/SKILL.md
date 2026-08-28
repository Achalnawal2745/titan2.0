---
name: "full-stack-builder"
description: "Specialized skill for full stack builder workflows and automation."
---

# Full Stack Builder

**Meta-Skill** that orchestrates multiple skills to build complete full-stack applications from concept to deployment.

## Overview

This meta-skill chains together 7+ individual skills to create a complete application workflow. It handles everything from requirements gathering to deployment, using the skill registry and composer to intelligently orchestrate the process.

## Skills Orchestrated

1. **brainstorming** - Explore requirements and design
2. **database-schema-generator** - Design database schema
3. **api-endpoint-builder** - Build backend API
4. **user-authentication-system** - Add authentication
5. **testing-framework** - Add comprehensive tests
6. **deployment-automation** - Deploy to production
7. **error-monitoring-setup** - Set up monitoring

## Optional Skills (Based on Requirements)

- **payment-integration** - If payments needed
- **file-upload-system** - If file uploads needed
- **email-system-builder** - If email notifications needed
- **analytics-dashboard** - If analytics needed

## Usage

### Command Line

```bash
python3 /tmp/manus-skills-v2/meta-skills/full-stack-builder/scripts/build_app.py "SaaS app with auth and payments"
```

### Programmatic

```python
from lib.skill_registry import SkillRegistry
from lib.skill_composer import SkillComposer

registry = SkillRegistry()
composer = SkillComposer(registry)

# Define workflow
workflow_skills = [
    "brainstorming",
    "database-schema-generator",
    "api-endpoint-builder",
    "user-authentication-system",
    "testing-framework",
    "deployment-automation"
]

# Compose and execute
workflow = composer.compose_workflow(workflow_skills)
results = composer.execute_workflow(workflow, {"description": "My SaaS App"})
```

## Workflow

1. **Requirements Phase** - Use brainstorming to understand needs
2. **Database Phase** - Generate schema based on requirements
3. **Backend Phase** - Build API endpoints
4. **Auth Phase** - Add authentication system
5. **Testing Phase** - Add comprehensive tests
6. **Deployment Phase** - Deploy to production
7. **Monitoring Phase** - Set up error monitoring

## Time Saved

**Total:** 30-35 hours per application

- Without meta-skill: 30-35 hours of manual work
- With meta-skill: 4-5 hours of guided work
- **Savings:** 85-90% time reduction

## Dependencies

- All orchestrated skills must be available
- Skill registry must be loaded
- Skill composer must be initialized

## Notes

- This is a **meta-skill** - it doesn't contain implementation code itself
- It orchestrates other skills using the skill registry and composer
- Can be customized by adding/removing skills from the workflow
- Automatically resolves dependencies between skills
