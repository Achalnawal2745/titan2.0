#!/usr/bin/env python3
"""
Stripe Payment Integration Setup Script
Automates Stripe setup for checkout and subscriptions
"""

import os
import sys
import json
import subprocess

def detect_framework():
    """Detect project framework"""
    if os.path.exists('next.config.js') or os.path.exists('next.config.mjs'):
        return 'nextjs'
    elif os.path.exists('package.json'):
        return 'react'
    elif os.path.exists('requirements.txt'):
        return 'python'
    return 'unknown'

def install_dependencies(framework):
    """Install Stripe dependencies"""
    if framework in ['nextjs', 'react']:
        subprocess.run(['npm', 'install', 'stripe', '@stripe/stripe-js', '@stripe/react-stripe-js'], check=True)
    elif framework == 'python':
        subprocess.run(['pip', 'install', 'stripe'], check=True)

def create_stripe_config(framework):
    """Create Stripe configuration files"""
    if framework in ['nextjs', 'react']:
        config = """// lib/stripe.ts
import Stripe from 'stripe';

export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: '2023-10-16',
});

export const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY!);
"""
        os.makedirs('lib', exist_ok=True)
        with open('lib/stripe.ts', 'w') as f:
            f.write(config)
    
    # Create .env.local template
    env_template = """# Stripe Keys
STRIPE_SECRET_KEY=sk_test_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
"""
    with open('.env.local.example', 'w') as f:
        f.write(env_template)

def main():
    print("🔧 Setting up Stripe payment integration...")
    
    framework = detect_framework()
    print(f"✅ Detected framework: {framework}")
    
    print("📦 Installing dependencies...")
    install_dependencies(framework)
    
    print("⚙️  Creating configuration...")
    create_stripe_config(framework)
    
    print("✅ Stripe setup complete!")
    print("\nNext steps:")
    print("1. Copy .env.local.example to .env.local")
    print("2. Add your Stripe keys from dashboard.stripe.com")
    print("3. Use templates to create checkout/subscription flows")

if __name__ == '__main__':
    main()
