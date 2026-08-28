#!/usr/bin/env python3
"""
Generate API endpoints from specifications.

Usage:
    python3 generate_endpoints.py "<description>" [options]

Options:
    --framework: nextjs, trpc, express (default: nextjs)
    --auth: Include authentication middleware (default: true)
    --validation: Include Zod validation (default: true)
    --output-dir: Output directory (default: current directory)

Examples:
    python3 generate_endpoints.py "CRUD endpoints for blog posts"
    python3 generate_endpoints.py "User management API" --framework trpc
    python3 generate_endpoints.py "Product catalog endpoints" --framework express --output-dir api/
"""

import sys
import os
import json
import argparse
from pathlib import Path
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

SYSTEM_PROMPT = """You are an expert backend developer specializing in API design.

Your task is to generate production-ready API endpoints from natural language descriptions.

Guidelines:
1. Follow RESTful principles for REST APIs
2. Use proper HTTP methods (GET, POST, PUT, PATCH, DELETE)
3. Include input validation (Zod schemas)
4. Add error handling
5. Include authentication/authorization checks
6. Use TypeScript for type safety
7. Follow framework-specific best practices
8. Add helpful comments
9. Include rate limiting considerations
10. Return proper HTTP status codes

Common patterns:
- CRUD operations (Create, Read, Update, Delete)
- Pagination for list endpoints
- Filtering and sorting
- Error responses with proper status codes
- Authentication middleware
- Input validation before processing

Output format: Clean, production-ready code that can be used directly."""

def generate_nextjs_endpoints(description, include_auth=True, include_validation=True):
    """Generate Next.js App Router API endpoints."""
    
    user_prompt = f"""Generate Next.js App Router API endpoints for:

{description}

Requirements:
- Use Next.js 14+ App Router (app/api/... structure)
- TypeScript
- Proper HTTP methods and status codes
{"- Include authentication checks using auth middleware" if include_auth else ""}
{"- Include Zod validation schemas" if include_validation else ""}
- Error handling with try/catch
- Proper response types
- RESTful design

Return ONLY the code files with clear file paths as comments, no explanations."""

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

def generate_trpc_endpoints(description, include_auth=True, include_validation=True):
    """Generate tRPC router endpoints."""
    
    user_prompt = f"""Generate tRPC router for:

{description}

Requirements:
- tRPC v10+ syntax
- TypeScript
- Proper procedure types (query, mutation)
{"- Include authentication using protectedProcedure" if include_auth else ""}
{"- Include Zod input validation" if include_validation else ""}
- Error handling with TRPCError
- Proper return types
- Type-safe design

Return ONLY the code with clear structure, no explanations."""

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

def generate_express_endpoints(description, include_auth=True, include_validation=True):
    """Generate Express.js router endpoints."""
    
    user_prompt = f"""Generate Express.js router for:

{description}

Requirements:
- Express.js router
- TypeScript
- Proper HTTP methods and status codes
{"- Include authentication middleware" if include_auth else ""}
{"- Include request validation (express-validator or Zod)" if include_validation else ""}
- Error handling middleware
- Async/await with try/catch
- RESTful design

Return ONLY the code with clear structure, no explanations."""

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

def parse_code_files(code_output):
    """Parse code output into separate files."""
    files = {}
    current_file = None
    current_content = []
    
    for line in code_output.split('\n'):
        # Check for file path comments
        if line.strip().startswith('// ') and ('/' in line or '.ts' in line or '.js' in line):
            # Save previous file
            if current_file:
                files[current_file] = '\n'.join(current_content)
            
            # Start new file
            current_file = line.strip().replace('// ', '').strip()
            current_content = []
        else:
            if current_file:
                current_content.append(line)
    
    # Save last file
    if current_file:
        files[current_file] = '\n'.join(current_content)
    
    # If no files detected, treat as single file
    if not files:
        files['api.ts'] = code_output
    
    return files

def write_files(files, output_dir):
    """Write generated files to disk."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    written_files = []
    
    for filepath, content in files.items():
        # Clean up filepath
        filepath = filepath.strip()
        if filepath.startswith('/'):
            filepath = filepath[1:]
        
        full_path = output_path / filepath
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        full_path.write_text(content)
        written_files.append(str(full_path))
    
    return written_files

def main():
    parser = argparse.ArgumentParser(
        description='Generate API endpoints from specifications'
    )
    parser.add_argument('description', type=str, help='Natural language description of the API')
    parser.add_argument('--framework', type=str, default='nextjs',
                       choices=['nextjs', 'trpc', 'express'],
                       help='Framework to generate for')
    parser.add_argument('--auth', action='store_true', default=True,
                       help='Include authentication middleware')
    parser.add_argument('--no-auth', action='store_false', dest='auth',
                       help='Exclude authentication middleware')
    parser.add_argument('--validation', action='store_true', default=True,
                       help='Include input validation')
    parser.add_argument('--no-validation', action='store_false', dest='validation',
                       help='Exclude input validation')
    parser.add_argument('--output-dir', type=str, default='.',
                       help='Output directory for generated files')
    
    args = parser.parse_args()
    
    print(f"🔨 Generating {args.framework} endpoints for: {args.description}", file=sys.stderr)
    print(f"📋 Auth: {args.auth}, Validation: {args.validation}", file=sys.stderr)
    
    try:
        # Generate endpoints based on framework
        if args.framework == 'nextjs':
            code = generate_nextjs_endpoints(
                args.description,
                include_auth=args.auth,
                include_validation=args.validation
            )
        elif args.framework == 'trpc':
            code = generate_trpc_endpoints(
                args.description,
                include_auth=args.auth,
                include_validation=args.validation
            )
        elif args.framework == 'express':
            code = generate_express_endpoints(
                args.description,
                include_auth=args.auth,
                include_validation=args.validation
            )
        
        # Parse into files
        files = parse_code_files(code)
        
        # Write files
        written_files = write_files(files, args.output_dir)
        
        print(f"\n✅ Generated {len(written_files)} file(s):", file=sys.stderr)
        for filepath in written_files:
            print(f"   • {filepath}", file=sys.stderr)
        
        print("\n📝 Next steps:", file=sys.stderr)
        print("   1. Review generated code", file=sys.stderr)
        print("   2. Adjust validation schemas if needed", file=sys.stderr)
        print("   3. Test endpoints", file=sys.stderr)
        print("   4. Deploy", file=sys.stderr)
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
