#!/usr/bin/env python3
"""Notification System Setup"""
import os, subprocess

def main():
    print("🔔 Setting up notifications...")
    subprocess.run(['npm', 'install', 'react-hot-toast'], check=True)
    
    config = """// lib/notifications.ts
import { toast } from 'react-hot-toast';

export const notify = {
  success: (msg: string) => toast.success(msg),
  error: (msg: string) => toast.error(msg),
  info: (msg: string) => toast(msg),
};
"""
    os.makedirs('lib', exist_ok=True)
    with open('lib/notifications.ts', 'w') as f:
        f.write(config)
    
    print("✅ Notifications setup complete!")

if __name__ == '__main__':
    main()
