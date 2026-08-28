#!/usr/bin/env python3
"""Setup email system for web applications"""
import os, sys, json

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 setup_email.py <project_dir> <provider>")
        print("Providers: resend, sendgrid, mailgun, ses")
        sys.exit(1)
    
    project_dir, provider = sys.argv[1], sys.argv[2]
    
    print(f"📦 Installing {provider} dependencies...")
    if provider == "resend":
        os.system("npm install resend")
    elif provider == "sendgrid":
        os.system("npm install @sendgrid/mail")
    
    # Create email config
    env_vars = {
        "resend": "RESEND_API_KEY=re_...",
        "sendgrid": "SENDGRID_API_KEY=SG...",
        "mailgun": "MAILGUN_API_KEY=key-...",
        "ses": "AWS_ACCESS_KEY_ID=...\nAWS_SECRET_ACCESS_KEY=..."
    }
    
    with open(os.path.join(project_dir, ".env.local"), "a") as f:
        f.write(f"\n# {provider.upper()} Email\n{env_vars.get(provider, '')}\n")
    
    print(f"✅ Email system setup complete!")
    print(f"Next: Update API key in .env.local")

if __name__ == "__main__":
    main()
