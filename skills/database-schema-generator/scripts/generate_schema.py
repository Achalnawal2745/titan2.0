#!/usr/bin/env python3
"""
Generate database schemas from natural language descriptions.

Usage:
    python3 generate_schema.py "<description>" [options]

Options:
    --output-format: sql, supabase, migration, types (default: sql)
    --include-rls: Include Row Level Security policies (default: true)
    --include-seed: Include seed data (default: false)
    --output-file: Output file path (default: stdout)

Examples:
    python3 generate_schema.py "A blog with users, posts, and comments"
    python3 generate_schema.py "E-commerce with products, orders, and customers" --output-format migration
    python3 generate_schema.py "Task management app" --include-seed --output-file schema.sql
"""

import sys
import os
import json
import argparse
from openai import OpenAI

# Initialize OpenAI client (API key from environment)
client = OpenAI()

SYSTEM_PROMPT = """You are an expert database architect specializing in PostgreSQL and Supabase.

Your task is to generate complete, production-ready database schemas from natural language descriptions.

Guidelines:
1. Use PostgreSQL best practices
2. Include proper data types, constraints, and indexes
3. Add foreign keys for relationships
4. Use UUIDs for primary keys (gen_random_uuid())
5. Include created_at and updated_at timestamps
6. Add soft delete support (deleted_at) where appropriate
7. Use snake_case for table and column names
8. Add helpful comments
9. Include Row Level Security (RLS) policies for Supabase
10. Consider performance with appropriate indexes

Common patterns to include:
- users table with auth integration
- Proper foreign key constraints with ON DELETE CASCADE/SET NULL
- Indexes on foreign keys and frequently queried columns
- Check constraints for data validation
- Unique constraints where needed

Output format: Clean, executable SQL that can be run directly in Supabase SQL Editor."""

def generate_schema_sql(description, include_rls=True, include_seed=False):
    """Generate SQL schema from description using LLM."""
    
    user_prompt = f"""Generate a complete PostgreSQL/Supabase database schema for:

{description}

Requirements:
- Include all necessary tables with proper relationships
- Add appropriate indexes
- Include timestamps (created_at, updated_at)
- Use UUIDs for primary keys
- Add foreign key constraints
{"- Include Row Level Security (RLS) policies" if include_rls else ""}
{"- Include realistic seed data (INSERT statements)" if include_seed else ""}

Return ONLY the SQL code, no explanations."""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=4000
    )
    
    return response.choices[0].message.content.strip()

def generate_migration(description, include_rls=True):
    """Generate migration file format."""
    
    schema_sql = generate_schema_sql(description, include_rls=include_rls, include_seed=False)
    
    migration_template = f"""-- Migration: {description}
-- Created: {import_datetime_now()}

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
{schema_sql}

-- Add indexes (if not already in schema)
-- CREATE INDEX idx_table_column ON table(column);

-- Grant permissions
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;
"""
    
    return migration_template

def import_datetime_now():
    """Import and return current datetime."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_typescript_types(schema_sql):
    """Generate TypeScript types from SQL schema."""
    
    type_prompt = f"""Given this SQL schema, generate TypeScript types for each table.

{schema_sql}

Requirements:
- Export each type
- Use proper TypeScript types (string, number, boolean, Date, etc.)
- Make optional fields nullable (| null)
- Include JSDoc comments
- Use PascalCase for type names

Return ONLY the TypeScript code, no explanations."""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are a TypeScript expert. Generate clean, type-safe TypeScript types."},
            {"role": "user", "content": type_prompt}
        ],
        temperature=0.2,
        max_tokens=2000
    )
    
    return response.choices[0].message.content.strip()

def format_output(schema_sql, output_format, description, include_rls):
    """Format output based on requested format."""
    
    if output_format == "sql":
        return schema_sql
    
    elif output_format == "supabase":
        # Add Supabase-specific header
        header = """-- Supabase SQL Editor
-- Paste this into the Supabase SQL Editor and run

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

"""
        return header + schema_sql
    
    elif output_format == "migration":
        return generate_migration(description, include_rls)
    
    elif output_format == "types":
        return generate_typescript_types(schema_sql)
    
    else:
        return schema_sql

def main():
    parser = argparse.ArgumentParser(
        description='Generate database schemas from natural language descriptions'
    )
    parser.add_argument('description', type=str, help='Natural language description of the database')
    parser.add_argument('--output-format', type=str, default='sql',
                       choices=['sql', 'supabase', 'migration', 'types'],
                       help='Output format')
    parser.add_argument('--include-rls', action='store_true', default=True,
                       help='Include Row Level Security policies')
    parser.add_argument('--no-rls', action='store_false', dest='include_rls',
                       help='Exclude Row Level Security policies')
    parser.add_argument('--include-seed', action='store_true', default=False,
                       help='Include seed data')
    parser.add_argument('--output-file', type=str, default=None,
                       help='Output file path (default: stdout)')
    
    args = parser.parse_args()
    
    print(f"🔨 Generating schema for: {args.description}", file=sys.stderr)
    print(f"📋 Format: {args.output_format}", file=sys.stderr)
    
    try:
        # Generate base schema
        schema_sql = generate_schema_sql(
            args.description,
            include_rls=args.include_rls,
            include_seed=args.include_seed
        )
        
        # Format output
        output = format_output(
            schema_sql,
            args.output_format,
            args.description,
            args.include_rls
        )
        
        # Write output
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(output)
            print(f"✅ Schema written to: {args.output_file}", file=sys.stderr)
        else:
            print("\n" + "="*80, file=sys.stderr)
            print(output)
            print("="*80, file=sys.stderr)
        
        print("✅ Schema generation complete!", file=sys.stderr)
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
