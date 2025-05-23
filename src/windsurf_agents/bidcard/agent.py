"""
BidCardAgent implementation using Google ADK 1.0.0
Generates structured bid cards from project information
"""
from typing import Dict, Any, Optional, List
from google import genai
from google.adk.agents import LlmAgent
from google.adk.types import ToolContext
import json

from ..tools.supabase_tools import save_project_to_supabase
from ..tools.vision_tools import analyze_project_image


def generate_bid_card(
    tool_context: ToolContext,
    project_id: str,
    project_data: Dict[str, Any],
    image_analyses: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Generates a structured bid card from project information.
    
    This tool creates a comprehensive bid card that contractors can use
    to understand project scope and submit accurate bids.
    
    Args:
        tool_context (ToolContext): ADK tool context providing session state access.
        project_id (str): UUID of the project to generate bid card for.
        project_data (dict): Project information including title, description, etc.
        image_analyses (list, optional): Results from image analysis if available.
    
    Returns:
        dict: Generated bid card information.
              Example: {
                  "status": "success",
                  "bid_card": {
                      "category": "renovation",
                      "job_type": "kitchen remodel",
                      "budget_range": "$15000-$25000",
                      "timeline": "6-8 weeks",
                      "scope_details": {...},
                      "ai_confidence": 0.85
                  }
              }
    """
    try:
        # Categorize the project
        description = project_data.get("description", "").lower()
        
        # Simple keyword-based categorization (in production, use LLM)
        if any(word in description for word in ["repair", "fix", "broken"]):
            category = "repair"
        elif any(word in description for word in ["renovate", "remodel", "update"]):
            category = "renovation"
        elif any(word in description for word in ["new", "install", "build"]):
            category = "installation"
        else:
            category = "general"
        
        # Determine job type
        if "kitchen" in description:
            job_type = "kitchen work"
        elif "bathroom" in description:
            job_type = "bathroom work"
        elif "roof" in description:
            job_type = "roofing"
        elif "plumb" in description:
            job_type = "plumbing"
        else:
            job_type = "general contracting"
        
        # Calculate confidence based on available information
        confidence = 0.7  # Base confidence
        if project_data.get("budget_range"):
            confidence += 0.1
        if project_data.get("timeline"):
            confidence += 0.1
        if image_analyses:
            confidence += 0.1
        
        # Build the bid card
        bid_card = {
            "project_id": project_id,
            "category": category,
            "job_type": job_type,
            "budget_range": project_data.get("budget_range", "To be determined"),
            "timeline": project_data.get("timeline", "Flexible"),
            "group_bidding": False,  # Could be determined by project size
            "scope_json": {
                "title": project_data.get("title"),
                "description": project_data.get("description"),
                "special_requirements": [],
                "access_notes": ""
            },
            "photo_meta": image_analyses or [],
            "ai_confidence": round(confidence, 2),
            "status": "final" if confidence >= 0.8 else "draft"
        }
        
        # Store in session state
        tool_context.state["temp:current_bid_card"] = bid_card
        
        return {"status": "success", "bid_card": bid_card}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}


def save_bid_card_to_supabase(
    tool_context: ToolContext,
    bid_card: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Saves a generated bid card to the Supabase database.
    
    Args:
        tool_context (ToolContext): ADK tool context providing session state access.
        bid_card (dict): Complete bid card data to save.
    
    Returns:
        dict: Result of the save operation.
              Example: {"status": "success", "bid_card_id": "uuid-here"}
    """
    # Implementation would use Supabase client to save
    # For now, return mock success
    return {"status": "success", "bid_card_id": "mock-bid-card-id"}


class BidCardAgent(LlmAgent):
    """
    AI agent that generates structured bid cards from project information.
    These bid cards help contractors understand project scope and submit accurate bids.
    """
    
    def __init__(self):
        super().__init__(
            name="bid_card_generator",
            model="gemini-2.0-flash-exp",
            description="Generates structured bid cards from project information",
            instructions="""You are a bid card generation specialist. Your role is to:
            1. Analyze project information to categorize the work needed
            2. Extract key details that contractors need for accurate bidding
            3. Assess confidence in the categorization
            4. Generate structured bid cards with all relevant information
            5. Flag any missing information that would help contractors
            
            Consider factors like:
            - Project category (repair, renovation, installation)
            - Specific job type (kitchen, bathroom, roofing, etc.)
            - Budget constraints
            - Timeline requirements
            - Whether group bidding might be beneficial
            - Special requirements or challenges
            
            Always aim for high-confidence bid cards that give contractors
            clear understanding of the project scope.""",
            tools=[
                generate_bid_card,
                save_bid_card_to_supabase,
                analyze_project_image  # Can use vision analysis
            ],
            output_key="bid_card_summary"
        )


# Export the agent instance
agent = BidCardAgent()
