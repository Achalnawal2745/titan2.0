#!/usr/bin/env python3
"""Build full-stack application using skill orchestration"""

import sys
import json
from pathlib import Path

# Add lib to path
sys.path.insert(0, "/tmp/manus-skills-v2")

from lib.skill_registry import SkillRegistry
from lib.skill_composer import SkillComposer

def build_app(description: str, features: list = None):
    """Build app using orchestrated skills
    
    Args:
        description: Natural language description of the app
        features: Optional list of features (payments, uploads, email, etc.)
    """
    
    print("=" * 60)
    print("FULL-STACK BUILDER - Meta-Skill Orchestration")
    print("=" * 60)
    print()
    
    # Initialize registry and composer
    registry = SkillRegistry()
    composer = SkillComposer(registry)
    
    # Define base workflow
    workflow_skills = [
        "brainstorming",
        "database-schema-generator",
        "api-endpoint-builder",
        "user-authentication-system",
        "testing-framework",
        "deployment-automation",
        "error-monitoring-setup"
    ]
    
    # Add optional skills based on features
    if features:
        if "payments" in features:
            workflow_skills.insert(-2, "payment-integration")
        if "uploads" in features or "files" in features:
            workflow_skills.insert(-2, "file-upload-system")
        if "email" in features:
            workflow_skills.insert(-2, "email-system-builder")
        if "analytics" in features:
            workflow_skills.insert(-2, "analytics-dashboard")
    
    print(f"Building: {description}")
    print()
    
    # Compose workflow
    print("Composing workflow...")
    workflow = composer.compose_workflow(workflow_skills)
    
    if not workflow["valid"]:
        print("❌ Workflow validation failed:")
        for error in workflow["errors"]:
            print(f"  - {error}")
        return
    
    print(f"✓ Workflow valid with {len(workflow['skills'])} skills")
    print()
    
    # Show workflow order
    print("Execution order:")
    for i, skill_name in enumerate(workflow['dependencies'], 1):
        skill = registry.get_skill(skill_name)
        time_saved = skill.get("time_saved", "unknown") if skill else "unknown"
        print(f"  {i}. {skill_name} (saves {time_saved})")
    print()
    
    # Calculate total time saved
    total_saved = 0
    for skill_name in workflow['dependencies']:
        skill = registry.get_skill(skill_name)
        if skill and skill.get("time_saved") != "unknown":
            time_str = skill.get("time_saved", "0")
            if "hour" in time_str:
                hours = float(time_str.split()[0])
                total_saved += hours
            elif "minute" in time_str:
                minutes = float(time_str.split()[0])
                total_saved += minutes / 60
    
    print(f"Total time saved: ~{total_saved:.1f} hours")
    print()
    
    # Execute workflow (placeholder)
    print("Executing workflow...")
    context = {
        "description": description,
        "features": features or []
    }
    results = composer.execute_workflow(workflow, context)
    
    print(f"✓ Executed {len(results['executed'])} skills successfully")
    print()
    
    print("=" * 60)
    print("BUILD COMPLETE")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  1. Review generated code and schemas")
    print("  2. Run tests to verify functionality")
    print("  3. Deploy to staging environment")
    print("  4. Monitor for errors and performance")

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: build_app.py 'app description' [feature1,feature2,...]")
        print()
        print("Example:")
        print("  build_app.py 'SaaS app with user management' payments,email")
        sys.exit(1)
    
    description = sys.argv[1]
    features = sys.argv[2].split(",") if len(sys.argv) > 2 else None
    
    build_app(description, features)

if __name__ == "__main__":
    main()
