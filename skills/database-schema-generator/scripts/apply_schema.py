#!/usr/bin/env python3
"""
Apply SQL schema to Supabase database via MCP.

Usage:
    python3 apply_schema.py <schema_file> --project-id <project_id>

Options:
    --project-id: Supabase project ID (required)
    --dry-run: Show what would be executed without running
    --confirm: Skip confirmation prompt

Examples:
    python3 apply_schema.py schema.sql --project-id abc123
    python3 apply_schema.py schema.sql --project-id abc123 --dry-run
    python3 apply_schema.py schema.sql --project-id abc123 --confirm
"""

import sys
import os
import json
import subprocess
import argparse
from pathlib import Path

def run_mcp_command(tool_name, server, input_data):
    """Run MCP CLI command."""
    cmd = [
        'manus-mcp-cli',
        'tool',
        'call',
        tool_name,
        '--server',
        server,
        '--input',
        json.dumps(input_data)
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"MCP command failed: {result.stderr}")
    
    return result.stdout

def execute_sql(project_id, sql_content, dry_run=False):
    """Execute SQL on Supabase via MCP."""
    
    if dry_run:
        print("\n🔍 DRY RUN - SQL that would be executed:")
        print("=" * 80)
        print(sql_content)
        print("=" * 80)
        return {"success": True, "dry_run": True}
    
    try:
        # Use Supabase MCP to execute SQL
        result = run_mcp_command(
            'execute_sql',
            'supabase',
            {
                'project_id': project_id,
                'sql': sql_content
            }
        )
        
        return json.loads(result)
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def confirm_execution(schema_file, project_id):
    """Ask user to confirm execution."""
    print("\n⚠️  You are about to execute SQL on your Supabase database:")
    print(f"   File: {schema_file}")
    print(f"   Project ID: {project_id}")
    print("\nThis will modify your database schema.")
    
    response = input("\nProceed? (yes/no): ").strip().lower()
    return response in ['yes', 'y']

def main():
    parser = argparse.ArgumentParser(
        description='Apply SQL schema to Supabase database'
    )
    parser.add_argument('schema_file', type=str, help='Path to SQL schema file')
    parser.add_argument('--project-id', type=str, required=True,
                       help='Supabase project ID')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be executed without running')
    parser.add_argument('--confirm', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    schema_file = Path(args.schema_file)
    
    if not schema_file.exists():
        print(f"❌ Error: File not found: {schema_file}")
        sys.exit(1)
    
    print(f"📁 Reading schema: {schema_file}")
    sql_content = schema_file.read_text()
    
    # Validate before applying
    print("🔍 Validating schema...")
    validate_result = subprocess.run(
        ['python3', str(Path(__file__).parent / 'validate_schema.py'), str(schema_file)],
        capture_output=True,
        text=True
    )
    
    if validate_result.returncode != 0:
        print("❌ Schema validation failed. Please fix errors first.")
        print(validate_result.stdout)
        sys.exit(1)
    
    print("✅ Schema validation passed")
    
    # Confirm execution (unless --confirm flag)
    if not args.confirm and not args.dry_run:
        if not confirm_execution(schema_file, args.project_id):
            print("❌ Execution cancelled by user")
            sys.exit(0)
    
    # Execute SQL
    print(f"\n🚀 {'[DRY RUN] ' if args.dry_run else ''}Applying schema to Supabase...")
    
    result = execute_sql(args.project_id, sql_content, dry_run=args.dry_run)
    
    if result.get('success'):
        if args.dry_run:
            print("\n✅ Dry run complete - no changes made")
        else:
            print("\n✅ Schema applied successfully!")
            print("\n📝 Next steps:")
            print("   1. Verify tables in Supabase dashboard")
            print("   2. Test RLS policies")
            print("   3. Add seed data if needed")
    else:
        print(f"\n❌ Error applying schema: {result.get('error', 'Unknown error')}")
        sys.exit(1)

if __name__ == '__main__':
    main()
