#!/usr/bin/env python3
"""
Database State Debugger for Serverless Functions

Queries database state to verify logic conditions and identify mismatches
between expected and actual data.

Usage:
    python database_debugger.py <table_name> <condition>
    
Example:
    python database_debugger.py wade_conversations "message_count >= 4 AND last_extraction_at = 0"
"""

import sys
import json
import subprocess

def execute_sql(project_id: str, query: str) -> dict:
    """Execute SQL query using Supabase MCP connector"""
    input_data = {
        "project_id": project_id,
        "query": query
    }
    
    result = subprocess.run(
        ['manus-mcp-cli', 'tool', 'call', 'execute_sql', '--server', 'supabase', 
         '--input', json.dumps(input_data)],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error executing query: {result.stderr}")
        return None
    
    return json.loads(result.stdout)

def analyze_table(project_id: str, table_name: str, condition: str = None):
    """Analyze table state and identify potential issues"""
    
    # Build query
    if condition:
        query = f"SELECT * FROM {table_name} WHERE {condition} LIMIT 10"
    else:
        query = f"SELECT * FROM {table_name} LIMIT 10"
    
    print(f"Executing query: {query}\n")
    
    result = execute_sql(project_id, query)
    
    if not result:
        return
    
    # Parse result (format varies by MCP implementation)
    try:
        # Extract data from MCP result
        data = result.get('data', [])
        
        print(f"Found {len(data)} rows:\n")
        print(json.dumps(data, indent=2))
        
        # Analyze for common issues
        if data:
            print("\n=== Analysis ===")
            
            # Check for NULL vs 0 issues
            for row in data:
                for key, value in row.items():
                    if value == 0:
                        print(f"⚠️  Column '{key}' has value 0 (check if code expects NULL)")
                    if value is None:
                        print(f"ℹ️  Column '{key}' is NULL")
            
            # Check for type issues
            for row in data:
                for key, value in row.items():
                    if isinstance(value, str) and value.isdigit():
                        print(f"⚠️  Column '{key}' is string '{value}' (check if code expects number)")
        
    except Exception as e:
        print(f"Error parsing result: {e}")
        print(f"Raw result: {result}")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    table_name = sys.argv[1]
    condition = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Get project ID from environment or prompt
    project_id = input("Enter Supabase project ID: ").strip()
    
    if not project_id:
        print("Error: Project ID required")
        sys.exit(1)
    
    analyze_table(project_id, table_name, condition)

if __name__ == "__main__":
    main()
