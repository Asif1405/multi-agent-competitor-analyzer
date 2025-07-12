from typing import Optional, List

from agents.workflow import CompetitorAnalysisWorkflow
from utils.agent_utils import log_thought


# Initialize the LangGraph workflow
workflow = CompetitorAnalysisWorkflow()


def generate_competitor_analysis_service(
    company_name_or_website: str,
    selected_competitor: Optional[str] = None
) -> str:
    """Generate analysis report using LangGraph workflow."""
    log_thought("🚀 Starting LangGraph-based competitor analysis...")
    
    try:
        # Run the LangGraph workflow
        final_state = workflow.run_analysis(
            company_name_or_website=company_name_or_website,
            location="global",  # Default location
            selected_competitor=selected_competitor
        )
        
        # Check for errors
        if final_state.get("error_message"):
            return final_state["error_message"]
        
        # Return the analysis report
        return final_state.get("analysis_report", "No analysis generated")
        
    except Exception as e:
        log_thought(f"❌ Error in LangGraph workflow: {e}")
        return f"Error generating analysis: {str(e)}"


def update_competitor_dropdown(
    company_name: str, 
    location: str
) -> List[str]:
    """Fetch and return competitors for dropdown using LangGraph workflow."""
    log_thought("🔍 Fetching competitors using LangGraph workflow...")
    
    try:
        # Use the workflow to get competitors
        competitors = workflow.get_competitors(
            company_name=company_name,
            location=location or "global"
        )
        
        log_thought(f"✅ Found {len(competitors)} competitors")
        return competitors
        
    except Exception as e:
        log_thought(f"❌ Error fetching competitors: {e}")
        return []
