"""
Supabase integration tools for AI agents
Following ADK 1.0.0 tool patterns with comprehensive docstrings
"""
from typing import Dict, Any, Optional
from google.adk.types import ToolContext
import os
from supabase import create_client, Client

# Initialize Supabase client
url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_SERVICE_KEY", "")  # Service key for RLS bypass
supabase: Client = create_client(url, key) if url and key else None


def save_project_to_supabase(
    tool_context: ToolContext,
    title: str,
    description: str,
    budget_range: Optional[str] = None,
    timeline: Optional[str] = None,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Saves a home improvement project to the Supabase database.
    
    This tool creates a new project entry with all the gathered information
    from the homeowner conversation.
    
    Args:
        tool_context (ToolContext): ADK tool context providing session state access.
        title (str): The project title/name.
        description (str): Detailed description of the project.
        budget_range (str, optional): Budget range like "$5000-$10000".
        timeline (str, optional): Project timeline like "2-3 weeks".
        category (str, optional): Project category like "repair" or "renovation".
    
    Returns:
        dict: Result dictionary with status and project_id if successful.
              Example: {"status": "success", "project_id": "uuid-here"}
              On error: {"status": "error", "message": "error details"}
    """
    if not supabase:
        return {"status": "error", "message": "Supabase client not initialized"}
    
    try:
        # Get user ID from session state
        user_id = tool_context.state.get("user:id")
        if not user_id:
            return {"status": "error", "message": "User ID not found in session"}
        
        # Prepare project data
        project_data = {
            "owner_id": user_id,
            "title": title,
            "description": description,
            "budget_range": budget_range,
            "timeline": timeline,
            "category": category,
            "status": "draft"
        }
        
        # Insert into database
        result = supabase.table("projects").insert(project_data).execute()
        
        if result.data:
            project_id = result.data[0]["id"]
            # Store in session state for reference
            tool_context.state["temp:current_project_id"] = project_id
            return {"status": "success", "project_id": project_id}
        else:
            return {"status": "error", "message": "Failed to create project"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_user_preferences(
    tool_context: ToolContext,
    preference_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Retrieves user preferences from Supabase to personalize interactions.
    
    This tool helps the agent remember user preferences across conversations,
    such as typical budget ranges, preferred contractors, or style preferences.
    
    Args:
        tool_context (ToolContext): ADK tool context providing session state access.
        preference_key (str, optional): Specific preference to retrieve. 
                                       If None, returns all preferences.
    
    Returns:
        dict: Dictionary containing preferences and status.
              Example: {"status": "success", "preferences": {"default_budget": "$10000-$15000"}}
              On error: {"status": "error", "message": "error details"}
    """
    if not supabase:
        return {"status": "error", "message": "Supabase client not initialized"}
    
    try:
        user_id = tool_context.state.get("user:id")
        if not user_id:
            return {"status": "error", "message": "User ID not found in session"}
        
        query = supabase.table("user_preferences").select("*").eq("user_id", user_id)
        
        if preference_key:
            query = query.eq("preference_key", preference_key)
        
        result = query.execute()
        
        if result.data:
            preferences = {item["preference_key"]: item["preference_value"] 
                         for item in result.data}
            return {"status": "success", "preferences": preferences}
        else:
            return {"status": "success", "preferences": {}}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}


def save_user_preference(
    tool_context: ToolContext,
    preference_key: str,
    preference_value: str,
    confidence: float = 0.8
) -> Dict[str, Any]:
    """
    Saves or updates a user preference for future personalization.
    
    When the agent learns something about the user (like their typical budget),
    this tool persists that information for future conversations.
    
    Args:
        tool_context (ToolContext): ADK tool context providing session state access.
        preference_key (str): The preference identifier (e.g., "default_budget").
        preference_value (str): The preference value (e.g., "$10000-$15000").
        confidence (float): Confidence score for this preference (0.0-1.0).
    
    Returns:
        dict: Result dictionary with status.
              Example: {"status": "success", "message": "Preference saved"}
              On error: {"status": "error", "message": "error details"}
    """
    if not supabase:
        return {"status": "error", "message": "Supabase client not initialized"}
    
    try:
        user_id = tool_context.state.get("user:id")
        if not user_id:
            return {"status": "error", "message": "User ID not found in session"}
        
        # Upsert preference
        preference_data = {
            "user_id": user_id,
            "preference_key": preference_key,
            "preference_value": preference_value,
            "confidence_score": confidence
        }
        
        result = supabase.table("user_preferences").upsert(
            preference_data,
            on_conflict="user_id,preference_key"
        ).execute()
        
        if result.data:
            # Cache in session state
            tool_context.state[f"user:pref_{preference_key}"] = preference_value
            return {"status": "success", "message": "Preference saved"}
        else:
            return {"status": "error", "message": "Failed to save preference"}
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
