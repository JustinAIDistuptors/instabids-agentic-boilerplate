"""
Main entry point for InstaBids Windsurf AI Agents
Demonstrates how to run agents in development mode
"""
import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from windsurf_agents.utils.ports import get_adk_ports


def main():
    """
    Main entry point for running InstaBids agents
    """
    print("🚀 InstaBids Windsurf AI Agents - Starting up...")
    
    # Check environment
    required_env_vars = [
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY", 
        "SUPABASE_SERVICE_KEY",
        "GOOGLE_API_KEY"
    ]
    
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Copy .env.template to .env and fill in your values")
        sys.exit(1)
    
    # Get available ports
    ports = get_adk_ports()
    print(f"\n📍 Available ports:")
    print(f"   - ADK Web UI: http://localhost:{ports['adk_web']}")
    print(f"   - API Server: http://localhost:{ports['api_server']}")
    print(f"   - Live Gateway: http://localhost:{ports['live_gateway']}")
    
    # Instructions for running
    print("\n📚 To start the development environment:")
    print(f"   1. Run ADK Web UI: poetry run adk web --port {ports['adk_web']}")
    print(f"   2. Run API Server: poetry run adk api_server --port {ports['api_server']}")
    print("\n💡 The ADK Web UI will show all registered agents from .adk/components.json")
    print("   You can interact with agents and test their capabilities there.")
    
    print("\n✅ Environment check complete! Ready to run agents.")


if __name__ == "__main__":
    main()
