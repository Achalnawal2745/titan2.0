#!/usr/bin/env python3
"""Full-text Search Setup"""
import os, subprocess

def main():
    print("🔍 Setting up search...")
    subprocess.run(['npm', 'install', 'algoliasearch'], check=True)
    
    config = """// lib/algolia.ts
import algoliasearch from 'algoliasearch';

export const searchClient = algoliasearch(
  process.env.NEXT_PUBLIC_ALGOLIA_APP_ID!,
  process.env.ALGOLIA_ADMIN_KEY!
);
"""
    os.makedirs('lib', exist_ok=True)
    with open('lib/algolia.ts', 'w') as f:
        f.write(config)
    
    print("✅ Search setup complete!")

if __name__ == '__main__':
    main()
