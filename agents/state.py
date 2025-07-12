from typing import List, Dict, Optional, Any
from typing_extensions import TypedDict


class CompetitorAnalysisState(TypedDict):
    """State definition for the competitor analysis workflow."""
    
    # Input parameters
    company_name_or_website: str
    location: str
    selected_competitor: Optional[str]
    
    # Intermediate data
    is_website_input: bool
    search_urls: List[str]
    competitor_names: List[str]
    target_company: str
    company_website: Optional[str]
    
    # Company data
    company_data: Dict[str, str]
    external_data: Dict[str, str]
    
    # Output
    analysis_report: str
    error_message: Optional[str]
    
    # Workflow control
    next_step: str
    workflow_completed: bool
