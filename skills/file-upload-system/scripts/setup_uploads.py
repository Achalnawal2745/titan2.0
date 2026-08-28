#!/usr/bin/env python3
"""S3/R2 File Upload System Setup"""
import os, subprocess

def main():
    print("🔧 Setting up file upload system...")
    subprocess.run(['npm', 'install', '@aws-sdk/client-s3', '@aws-sdk/s3-request-presigner'], check=True)
    
    config = """// lib/s3.ts
import { S3Client } from '@aws-sdk/client-s3';

export const s3 = new S3Client({
  region: process.env.AWS_REGION!,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID!,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY!,
  },
});
"""
    os.makedirs('lib', exist_ok=True)
    with open('lib/s3.ts', 'w') as f:
        f.write(config)
    
    print("✅ File upload system setup complete!")

if __name__ == '__main__':
    main()
