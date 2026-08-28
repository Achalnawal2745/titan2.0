#!/usr/bin/env python3
"""
Setup authentication system for web applications.
Supports multiple auth providers and frameworks.
"""

import os
import sys
import json
import subprocess

def detect_framework(project_dir):
    """Detect the web framework being used"""
    if os.path.exists(os.path.join(project_dir, "next.config.js")):
        return "nextjs"
    elif os.path.exists(os.path.join(project_dir, "package.json")):
        with open(os.path.join(project_dir, "package.json")) as f:
            pkg = json.load(f)
            if "react" in pkg.get("dependencies", {}):
                return "react"
            elif "express" in pkg.get("dependencies", {}):
                return "express"
    elif os.path.exists(os.path.join(project_dir, "requirements.txt")):
        with open(os.path.join(project_dir, "requirements.txt")) as f:
            if "flask" in f.read().lower():
                return "flask"
            elif "django" in f.read().lower():
                return "django"
    return "unknown"

def install_dependencies(framework, provider):
    """Install required authentication dependencies"""
    deps = {
        "nextjs": {
            "clerk": ["@clerk/nextjs"],
            "auth0": ["@auth0/nextjs-auth0"],
            "supabase": ["@supabase/auth-helpers-nextjs", "@supabase/supabase-js"],
            "nextauth": ["next-auth"]
        },
        "react": {
            "clerk": ["@clerk/clerk-react"],
            "auth0": ["@auth0/auth0-react"],
            "supabase": ["@supabase/supabase-js"]
        },
        "express": {
            "passport": ["passport", "express-session", "passport-local"],
            "auth0": ["express-openid-connect"]
        },
        "flask": {
            "flask-login": ["flask-login"],
            "authlib": ["authlib"]
        }
    }
    
    packages = deps.get(framework, {}).get(provider, [])
    if not packages:
        print(f"❌ No dependencies found for {framework} + {provider}")
        return False
    
    print(f"📦 Installing {', '.join(packages)}...")
    
    if framework in ["nextjs", "react", "express"]:
        cmd = ["npm", "install"] + packages
    else:
        cmd = ["pip3", "install"] + packages
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install dependencies")
        return False

def create_auth_config(project_dir, framework, provider, api_key):
    """Create authentication configuration file"""
    env_file = os.path.join(project_dir, ".env.local" if framework in ["nextjs", "react"] else ".env")
    
    env_vars = {
        "clerk": {
            "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY": api_key,
            "CLERK_SECRET_KEY": "sk_test_..."
        },
        "auth0": {
            "AUTH0_SECRET": "use [openssl rand -hex 32] to generate",
            "AUTH0_BASE_URL": "http://localhost:3000",
            "AUTH0_ISSUER_BASE_URL": f"https://{api_key}.auth0.com",
            "AUTH0_CLIENT_ID": "your_client_id",
            "AUTH0_CLIENT_SECRET": "your_client_secret"
        },
        "supabase": {
            "NEXT_PUBLIC_SUPABASE_URL": f"https://{api_key}.supabase.co",
            "NEXT_PUBLIC_SUPABASE_ANON_KEY": "your_anon_key"
        },
        "nextauth": {
            "NEXTAUTH_URL": "http://localhost:3000",
            "NEXTAUTH_SECRET": "use [openssl rand -base64 32] to generate"
        }
    }
    
    vars_to_add = env_vars.get(provider, {})
    
    with open(env_file, "a") as f:
        f.write(f"\n# {provider.upper()} Authentication\n")
        for key, value in vars_to_add.items():
            f.write(f"{key}={value}\n")
    
    print(f"✅ Created {env_file}")
    print(f"⚠️  Remember to update the placeholder values!")

def create_auth_provider(project_dir, framework, provider):
    """Create authentication provider component/module"""
    if framework == "nextjs":
        if provider == "clerk":
            provider_code = '''import { ClerkProvider } from '@clerk/nextjs'

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang="en">
        <body>{children}</body>
      </html>
    </ClerkProvider>
  )
}'''
        elif provider == "supabase":
            provider_code = '''import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { SessionContextProvider } from '@supabase/auth-helpers-react'

export default function AuthProvider({ children }) {
  const supabase = createClientComponentClient()
  
  return (
    <SessionContextProvider supabaseClient={supabase}>
      {children}
    </SessionContextProvider>
  )
}'''
        
        provider_file = os.path.join(project_dir, "app", "providers.tsx")
        os.makedirs(os.path.dirname(provider_file), exist_ok=True)
        with open(provider_file, "w") as f:
            f.write(provider_code)
        print(f"✅ Created {provider_file}")

def main():
    if len(sys.argv) < 4:
        print("Usage: python3 setup_auth.py <project_dir> <provider> <api_key>")
        print("\nProviders:")
        print("  - clerk")
        print("  - auth0")
        print("  - supabase")
        print("  - nextauth")
        print("  - passport (Express)")
        print("  - flask-login (Flask)")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    provider = sys.argv[2]
    api_key = sys.argv[3]
    
    if not os.path.exists(project_dir):
        print(f"❌ Project directory not found: {project_dir}")
        sys.exit(1)
    
    print(f"🔍 Detecting framework...")
    framework = detect_framework(project_dir)
    print(f"✅ Detected: {framework}")
    
    if framework == "unknown":
        print("❌ Could not detect framework")
        sys.exit(1)
    
    print(f"\n🚀 Setting up {provider} authentication for {framework}...")
    
    # Install dependencies
    if not install_dependencies(framework, provider):
        sys.exit(1)
    
    # Create config
    create_auth_config(project_dir, framework, provider, api_key)
    
    # Create provider
    create_auth_provider(project_dir, framework, provider)
    
    print(f"\n✅ Authentication setup complete!")
    print(f"\nNext steps:")
    print(f"1. Update environment variables in .env.local")
    print(f"2. Wrap your app with the auth provider")
    print(f"3. Add sign-in/sign-up components")
    print(f"4. Protect routes with authentication")

if __name__ == "__main__":
    main()
