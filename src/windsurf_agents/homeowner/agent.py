"""
HomeownerAgent implementation using Google ADK 1.0.0
Assists homeowners in defining and scoping home improvement projects
"""
from typing import Dict, Any, Optional
from google import genai
from google.adk.agents import LlmAgent
from google.adk.types import ToolContext
from google.adk.events import Event

from ..tools.supabase_tools import (
    save_project_to_supabase,
    get_user_preferences,
    save_user_preference
)
from ..tools.vision_tools import analyze_project_image


class HomeownerAgent(LlmAgent):
    """
    AI agent that helps homeowners define home improvement projects through
    conversational interaction and intelligent preference learning.
    """
    
    def __init__(self):
        super().__init__(
            name="homeowner_assistant",
            model="gemini-2.0-flash-exp",  # Using experimental model for Live features
            description="Assists homeowners in defining and scoping home improvement projects",
            instructions="""You are a helpful home improvement assistant. Your role is to:
            1. Help homeowners clearly define their project requirements
            2. Ask clarifying questions to fill in missing details
            3. Remember user preferences across conversations
            4. Analyze uploaded images to understand project scope
            5. Generate comprehensive project summaries for contractors
            
            Always use prefixes for state management:
            - user: for user-specific persistent data
            - app: for application-wide settings
            - temp: for temporary session data
            
            Be conversational, helpful, and thorough in gathering project details.""",
            tools=[
                save_project_to_supabase,
                get_user_preferences,
                save_user_preference,
                analyze_project_image
            ],
            output_key="project_summary"
        )


# Export the agent instance (Critical: ADK looks for 'agent' variable)
agent = HomeownerAgent()
