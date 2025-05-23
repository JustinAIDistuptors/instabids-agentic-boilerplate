"""
Windsurf Agents - AI-Driven Multi-Agent System for InstaBids
Built with Google ADK 1.0.0+ and Supabase
"""
import asyncio
import sys

# Windows Proactor loop initialization (Critical for Windows support)
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

__version__ = "0.1.0"
