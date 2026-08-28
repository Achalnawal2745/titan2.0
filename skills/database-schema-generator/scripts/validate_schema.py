#!/usr/bin/env python3
"""
Validate SQL schema syntax and structure.

Usage:
    python3 validate_schema.py <schema_file>

Examples:
    python3 validate_schema.py schema.sql
    python3 validate_schema.py migrations/001_initial.sql
"""

import sys
import re
from pathlib import Path

def validate_sql_syntax(sql_content):
    """Basic SQL syntax validation."""
    errors = []
    warnings = []
    
    # Check for common syntax errors
    if not sql_content.strip():
        errors.append("Empty SQL file")
        return errors, warnings
    
    # Check for balanced parentheses
    if sql_content.count('(') != sql_content.count(')'):
        errors.append("Unbalanced parentheses")
    
    # Check for semicolons at end of statements
    statements = [s.strip() for s in sql_content.split(';') if s.strip()]
    for i, stmt in enumerate(statements[:-1]):  # All but last should have semicolon
        if not stmt.endswith(';') and stmt:
            warnings.append(f"Statement {i+1} might be missing semicolon")
    
    # Check for CREATE TABLE statements
    if 'CREATE TABLE' not in sql_content.upper():
        warnings.append("No CREATE TABLE statements found")
    
    return errors, warnings

def validate_best_practices(sql_content):
    """Check for database best practices."""
    recommendations = []
    
    # Check for timestamps
    if 'created_at' not in sql_content.lower():
        recommendations.append("Consider adding created_at timestamp columns")
    
    # Check for UUIDs
    if 'uuid' not in sql_content.lower() and 'gen_random_uuid' not in sql_content.lower():
        recommendations.append("Consider using UUIDs for primary keys")
    
    # Check for indexes
    if 'CREATE INDEX' not in sql_content.upper() and 'INDEX' not in sql_content.upper():
        recommendations.append("Consider adding indexes for performance")
    
    # Check for foreign keys
    if 'REFERENCES' not in sql_content.upper() and 'FOREIGN KEY' not in sql_content.upper():
        recommendations.append("Consider adding foreign key constraints for relationships")
    
    # Check for RLS (Supabase)
    if 'ALTER TABLE' in sql_content.upper() and 'ENABLE ROW LEVEL SECURITY' not in sql_content.upper():
        recommendations.append("Consider enabling Row Level Security (RLS) for Supabase")
    
    return recommendations

def analyze_schema_structure(sql_content):
    """Analyze schema structure."""
    analysis = {
        'tables': [],
        'indexes': [],
        'constraints': [],
        'rls_policies': []
    }
    
    # Extract table names
    table_pattern = r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?(\w+)'
    analysis['tables'] = re.findall(table_pattern, sql_content, re.IGNORECASE)
    
    # Extract index names
    index_pattern = r'CREATE\s+(?:UNIQUE\s+)?INDEX\s+(?:IF NOT EXISTS\s+)?(\w+)'
    analysis['indexes'] = re.findall(index_pattern, sql_content, re.IGNORECASE)
    
    # Check for RLS
    if 'ENABLE ROW LEVEL SECURITY' in sql_content.upper():
        analysis['rls_policies'].append('RLS enabled')
    
    return analysis

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 validate_schema.py <schema_file>")
        sys.exit(1)
    
    schema_file = Path(sys.argv[1])
    
    if not schema_file.exists():
        print(f"❌ Error: File not found: {schema_file}")
        sys.exit(1)
    
    print(f"🔍 Validating schema: {schema_file}")
    print("=" * 80)
    
    # Read SQL file
    sql_content = schema_file.read_text()
    
    # Validate syntax
    errors, warnings = validate_sql_syntax(sql_content)
    
    # Check best practices
    recommendations = validate_best_practices(sql_content)
    
    # Analyze structure
    analysis = analyze_schema_structure(sql_content)
    
    # Display results
    print("\n📊 SCHEMA ANALYSIS")
    print("-" * 80)
    print(f"Tables: {len(analysis['tables'])}")
    if analysis['tables']:
        for table in analysis['tables']:
            print(f"  • {table}")
    
    print(f"\nIndexes: {len(analysis['indexes'])}")
    if analysis['indexes']:
        for index in analysis['indexes']:
            print(f"  • {index}")
    
    print(f"\nRLS Policies: {len(analysis['rls_policies'])}")
    if analysis['rls_policies']:
        for policy in analysis['rls_policies']:
            print(f"  • {policy}")
    
    # Display errors
    if errors:
        print("\n❌ ERRORS")
        print("-" * 80)
        for error in errors:
            print(f"  • {error}")
    
    # Display warnings
    if warnings:
        print("\n⚠️  WARNINGS")
        print("-" * 80)
        for warning in warnings:
            print(f"  • {warning}")
    
    # Display recommendations
    if recommendations:
        print("\n💡 RECOMMENDATIONS")
        print("-" * 80)
        for rec in recommendations:
            print(f"  • {rec}")
    
    # Final verdict
    print("\n" + "=" * 80)
    if errors:
        print("❌ Validation FAILED - Please fix errors above")
        sys.exit(1)
    elif warnings:
        print("⚠️  Validation PASSED with warnings")
        sys.exit(0)
    else:
        print("✅ Validation PASSED - Schema looks good!")
        sys.exit(0)

if __name__ == '__main__':
    main()
