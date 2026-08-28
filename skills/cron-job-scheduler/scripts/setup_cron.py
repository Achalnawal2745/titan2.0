#!/usr/bin/env python3
"""Cron Job Scheduler Setup"""
import os, subprocess

def main():
    print("⏰ Setting up cron job scheduler...")
    subprocess.run(['npm', 'install', 'node-cron'], check=True)
    
    config = """// lib/cron.ts
import cron from 'node-cron';

export function scheduleJob(schedule: string, task: () => void) {
  return cron.schedule(schedule, task);
}

// Example: Run every day at midnight
// scheduleJob('0 0 * * *', () => console.log('Daily task'));
"""
    os.makedirs('lib', exist_ok=True)
    with open('lib/cron.ts', 'w') as f:
        f.write(config)
    
    print("✅ Cron scheduler setup complete!")

if __name__ == '__main__':
    main()
