#!/usr/bin/env python3
"""
Generate a diagnostic health endpoint for serverless functions.

Usage:
    python generate_health_endpoint.py <service1> <service2> ...

Example:
    python generate_health_endpoint.py stripe supabase sendgrid

Output:
    Generates health endpoint code to stdout
"""

import sys

def generate_health_endpoint(services):
    """Generate health endpoint code for given services."""
    
    # Map service names to their environment variable patterns
    env_vars = {
        'stripe': ['STRIPE_SECRET_KEY'],
        'supabase': ['SUPABASE_URL', 'SUPABASE_ANON_KEY'],
        'sendgrid': ['SENDGRID_API_KEY'],
        'twilio': ['TWILIO_ACCOUNT_SID', 'TWILIO_AUTH_TOKEN'],
        'openai': ['OPENAI_API_KEY'],
        'anthropic': ['ANTHROPIC_API_KEY'],
        'vercel': ['VERCEL_TOKEN'],
        'github': ['GITHUB_TOKEN'],
        'aws': ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'],
        'google': ['GOOGLE_APPLICATION_CREDENTIALS']
    }
    
    code = []
    code.append("// Diagnostic health endpoint")
    code.append("app.get('/api/health', (req, res) => {")
    code.append("  const config = {")
    
    # Generate config checks
    for service in services:
        if service not in env_vars:
            print(f"Warning: Unknown service '{service}', skipping", file=sys.stderr)
            continue
        
        vars_list = env_vars[service]
        if len(vars_list) == 1:
            code.append(f"    {service}: !!process.env.{vars_list[0]},")
        else:
            checks = " && ".join([f"!!process.env.{var}" for var in vars_list])
            code.append(f"    {service}: {checks},")
    
    code.append("  };")
    code.append("")
    code.append("  // Show key prefixes for debugging (safe to log)")
    code.append("  const keyPrefixes = {")
    
    # Generate key prefix extraction
    for service in services:
        if service not in env_vars:
            continue
        
        vars_list = env_vars[service]
        primary_var = vars_list[0]
        
        code.append(f"    {service}: config.{service} ? process.env.{primary_var}.substring(0, 10) : 'none',")
    
    code.append("  };")
    code.append("")
    code.append("  res.json({")
    code.append("    status: 'ok',")
    code.append("    configured: config,")
    code.append("    keyPrefixes: keyPrefixes,")
    code.append("    timestamp: new Date().toISOString()")
    code.append("  });")
    code.append("});")
    
    return "\n".join(code)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_health_endpoint.py <service1> <service2> ...")
        print("\nSupported services:")
        print("  stripe, supabase, sendgrid, twilio, openai, anthropic,")
        print("  vercel, github, aws, google")
        sys.exit(1)
    
    services = sys.argv[1:]
    code = generate_health_endpoint(services)
    print(code)
    
    print("\n\n// Test with:", file=sys.stderr)
    print("// curl https://your-api.vercel.app/api/health", file=sys.stderr)

if __name__ == '__main__':
    main()
