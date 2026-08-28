#!/usr/bin/env python3
"""
Analytics Dashboard Setup Script

Automates setup of analytics tracking and dashboard for web applications.
Supports multiple analytics providers and generates dashboard components.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def detect_project_type(project_dir):
    """Detect the project type based on files present."""
    project_path = Path(project_dir)
    
    if (project_path / "package.json").exists():
        with open(project_path / "package.json") as f:
            package = json.load(f)
            deps = {**package.get("dependencies", {}), **package.get("devDependencies", {})}
            
            if "next" in deps:
                return "nextjs"
            elif "react" in deps:
                return "react"
            elif "express" in deps:
                return "express"
    
    if (project_path / "requirements.txt").exists() or (project_path / "pyproject.toml").exists():
        return "python"
    
    return "unknown"

def install_dependencies(project_type, provider):
    """Install required analytics dependencies."""
    print(f"\n📦 Installing {provider} dependencies...")
    
    if project_type in ["nextjs", "react"]:
        packages = {
            "posthog": ["posthog-js"],
            "mixpanel": ["mixpanel-browser"],
            "amplitude": ["@amplitude/analytics-browser"],
            "segment": ["@segment/analytics-next"]
        }
        
        if provider in packages:
            cmd = ["npm", "install", *packages[provider]]
            subprocess.run(cmd, check=True)
            print(f"✅ Installed {provider} packages")
    
    elif project_type == "python":
        packages = {
            "posthog": ["posthog"],
            "mixpanel": ["mixpanel"],
            "amplitude": ["amplitude-analytics"],
            "segment": ["analytics-python"]
        }
        
        if provider in packages:
            cmd = ["pip3", "install", *packages[provider]]
            subprocess.run(cmd, check=True)
            print(f"✅ Installed {provider} packages")

def create_analytics_config(project_dir, project_type, provider, api_key):
    """Create analytics configuration file."""
    project_path = Path(project_dir)
    
    if project_type == "nextjs":
        config_path = project_path / "lib" / "analytics.ts"
        config_path.parent.mkdir(exist_ok=True)
        
        config_content = f"""// Analytics Configuration
import posthog from 'posthog-js'

export const initAnalytics = () => {{
  if (typeof window !== 'undefined') {{
    posthog.init('{api_key}', {{
      api_host: 'https://app.posthog.com',
      loaded: (posthog) => {{
        if (process.env.NODE_ENV === 'development') posthog.opt_out_capturing()
      }}
    }})
  }}
}}

export const trackEvent = (eventName: string, properties?: Record<string, any>) => {{
  posthog.capture(eventName, properties)
}}

export const identifyUser = (userId: string, traits?: Record<string, any>) => {{
  posthog.identify(userId, traits)
}}
"""
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Created analytics config at {config_path}")
    
    elif project_type == "python":
        config_path = project_path / "analytics.py"
        
        config_content = f"""# Analytics Configuration
from posthog import Posthog

posthog = Posthog(
    project_api_key='{api_key}',
    host='https://app.posthog.com'
)

def track_event(user_id: str, event_name: str, properties: dict = None):
    \"\"\"Track an analytics event.\"\"\"
    posthog.capture(user_id, event_name, properties or {{}})

def identify_user(user_id: str, traits: dict = None):
    \"\"\"Identify a user with traits.\"\"\"
    posthog.identify(user_id, traits or {{}})
"""
        
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"✅ Created analytics config at {config_path}")

def create_dashboard_component(project_dir, project_type):
    """Create analytics dashboard component."""
    project_path = Path(project_dir)
    
    if project_type == "nextjs":
        dashboard_path = project_path / "components" / "AnalyticsDashboard.tsx"
        dashboard_path.parent.mkdir(exist_ok=True)
        
        dashboard_content = """import { useState, useEffect } from 'react'

interface AnalyticsData {
  totalEvents: number
  uniqueUsers: number
  topEvents: Array<{ name: string; count: number }>
}

export default function AnalyticsDashboard() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('/api/analytics')
      const data = await response.json()
      setData(data)
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) return <div>Loading analytics...</div>

  return (
    <div className="analytics-dashboard">
      <h2>Analytics Dashboard</h2>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <h3>Total Events</h3>
          <p className="metric-value">{data?.totalEvents || 0}</p>
        </div>
        
        <div className="metric-card">
          <h3>Unique Users</h3>
          <p className="metric-value">{data?.uniqueUsers || 0}</p>
        </div>
      </div>

      <div className="top-events">
        <h3>Top Events</h3>
        <ul>
          {data?.topEvents.map((event, i) => (
            <li key={i}>
              {event.name}: {event.count}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}
"""
        
        with open(dashboard_path, 'w') as f:
            f.write(dashboard_content)
        
        print(f"✅ Created dashboard component at {dashboard_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: setup_analytics.py <project_dir> [provider] [api_key]")
        print("Providers: posthog (default), mixpanel, amplitude, segment")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    provider = sys.argv[2] if len(sys.argv) > 2 else "posthog"
    api_key = sys.argv[3] if len(sys.argv) > 3 else "YOUR_API_KEY"
    
    print(f"🔍 Detecting project type in {project_dir}...")
    project_type = detect_project_type(project_dir)
    print(f"✅ Detected project type: {project_type}")
    
    if project_type == "unknown":
        print("❌ Could not detect project type")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies(project_type, provider)
    
    # Create analytics config
    create_analytics_config(project_dir, project_type, provider, api_key)
    
    # Create dashboard component
    create_dashboard_component(project_dir, project_type)
    
    print("\n✅ Analytics setup complete!")
    print(f"\nNext steps:")
    print(f"1. Replace 'YOUR_API_KEY' with your actual {provider} API key")
    print(f"2. Initialize analytics in your app entry point")
    print(f"3. Start tracking events with trackEvent()")
    print(f"4. View analytics in your {provider} dashboard")

if __name__ == "__main__":
    main()
