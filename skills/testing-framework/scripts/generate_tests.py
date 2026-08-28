#!/usr/bin/env python3
"""
Generate tests for functions, APIs, and components.

Usage:
    python3 generate_tests.py "<description>" [options]
    python3 generate_tests.py --file <source_file> [options]

Options:
    --type: unit, integration, e2e (default: unit)
    --framework: vitest, jest, playwright (default: vitest)
    --file: Source file to generate tests for
    --output-file: Output test file path
    --coverage: Include coverage configuration

Examples:
    python3 generate_tests.py "Tests for user authentication functions"
    python3 generate_tests.py --file src/utils/format.ts --type unit
    python3 generate_tests.py "E2E tests for checkout flow" --type e2e --framework playwright
"""

import sys
import os
import json
import argparse
from pathlib import Path
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI()

SYSTEM_PROMPT = """You are an expert software tester specializing in automated testing.

Your task is to generate comprehensive, production-ready tests from descriptions or source code.

Guidelines:
1. Write clear, descriptive test names
2. Follow AAA pattern (Arrange, Act, Assert)
3. Test happy paths and edge cases
4. Include error scenarios
5. Use proper assertions
6. Mock external dependencies
7. Keep tests isolated and independent
8. Add helpful comments
9. Follow framework-specific best practices
10. Aim for high code coverage

Test types:
- Unit tests: Test individual functions/methods in isolation
- Integration tests: Test multiple components working together
- E2E tests: Test complete user flows through the UI

Output format: Clean, executable test code that can be run directly."""

def read_source_file(filepath):
    """Read source file to generate tests for."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {filepath}")
    return path.read_text()

def generate_unit_tests(description, framework='vitest', source_code=None):
    """Generate unit tests."""
    
    user_prompt = f"""Generate {framework} unit tests for:

{description}

{"Source code:\n" + source_code if source_code else ""}

Requirements:
- Use {framework} syntax
- Test all functions/methods
- Include happy path and edge cases
- Test error handling
- Mock external dependencies
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)

Return ONLY the test code, no explanations."""

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

def generate_integration_tests(description, framework='vitest'):
    """Generate integration tests."""
    
    user_prompt = f"""Generate {framework} integration tests for:

{description}

Requirements:
- Use {framework} syntax
- Test multiple components working together
- Test API endpoints with real database (or test database)
- Test data flow between components
- Include setup and teardown
- Use realistic test data
- Test error scenarios

Return ONLY the test code, no explanations."""

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

def generate_e2e_tests(description, framework='playwright'):
    """Generate E2E tests."""
    
    user_prompt = f"""Generate {framework} E2E tests for:

{description}

Requirements:
- Use {framework} syntax
- Test complete user flows
- Include page interactions (clicks, inputs, navigation)
- Add assertions for UI elements
- Test success and error scenarios
- Use page object pattern if complex
- Add helpful comments

Return ONLY the test code, no explanations."""

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

def generate_test_config(framework, include_coverage=True):
    """Generate test configuration file."""
    
    if framework == 'vitest':
        config = """import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
"""
        if include_coverage:
            config += """    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.test.ts',
        '**/*.spec.ts',
      ],
    },
"""
        config += """  },
});
"""
        return config
    
    elif framework == 'jest':
        config = """module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/src'],
  testMatch: ['**/__tests__/**/*.ts', '**/?(*.)+(spec|test).ts'],
"""
        if include_coverage:
            config += """  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
  ],
"""
        config += """};
"""
        return config
    
    elif framework == 'playwright':
        config = """import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
"""
        return config
    
    return ""

def infer_output_filename(description, test_type, source_file=None):
    """Infer output filename from description or source file."""
    if source_file:
        path = Path(source_file)
        return f"{path.stem}.test{path.suffix}"
    
    # Generate from description
    name = description.lower().replace(' ', '_')[:30]
    return f"{name}.test.ts"

def main():
    parser = argparse.ArgumentParser(
        description='Generate tests for functions, APIs, and components'
    )
    parser.add_argument('description', type=str, nargs='?', 
                       help='Natural language description of what to test')
    parser.add_argument('--type', type=str, default='unit',
                       choices=['unit', 'integration', 'e2e'],
                       help='Type of tests to generate')
    parser.add_argument('--framework', type=str, default='vitest',
                       choices=['vitest', 'jest', 'playwright'],
                       help='Testing framework')
    parser.add_argument('--file', type=str, dest='source_file',
                       help='Source file to generate tests for')
    parser.add_argument('--output-file', type=str,
                       help='Output test file path')
    parser.add_argument('--coverage', action='store_true', default=True,
                       help='Include coverage configuration')
    parser.add_argument('--config', action='store_true',
                       help='Generate test configuration file')
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.description and not args.source_file:
        print("Error: Either description or --file must be provided", file=sys.stderr)
        sys.exit(1)
    
    # Generate config if requested
    if args.config:
        config = generate_test_config(args.framework, args.coverage)
        config_filename = {
            'vitest': 'vitest.config.ts',
            'jest': 'jest.config.js',
            'playwright': 'playwright.config.ts',
        }[args.framework]
        
        Path(config_filename).write_text(config)
        print(f"✅ Generated config: {config_filename}", file=sys.stderr)
        return
    
    print(f"🔨 Generating {args.type} tests using {args.framework}", file=sys.stderr)
    
    try:
        # Read source file if provided
        source_code = None
        if args.source_file:
            source_code = read_source_file(args.source_file)
            print(f"📁 Reading source: {args.source_file}", file=sys.stderr)
        
        # Generate description if not provided
        description = args.description or f"Tests for {args.source_file}"
        
        # Generate tests based on type
        if args.type == 'unit':
            tests = generate_unit_tests(description, args.framework, source_code)
        elif args.type == 'integration':
            tests = generate_integration_tests(description, args.framework)
        elif args.type == 'e2e':
            tests = generate_e2e_tests(description, args.framework)
        
        # Determine output filename
        if args.output_file:
            output_file = args.output_file
        else:
            output_file = infer_output_filename(description, args.type, args.source_file)
        
        # Write tests
        Path(output_file).write_text(tests)
        
        print(f"\n✅ Generated tests: {output_file}", file=sys.stderr)
        print("\n📝 Next steps:", file=sys.stderr)
        print(f"   1. Review generated tests", file=sys.stderr)
        print(f"   2. Run tests: {args.framework} {output_file}", file=sys.stderr)
        print(f"   3. Adjust assertions if needed", file=sys.stderr)
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
