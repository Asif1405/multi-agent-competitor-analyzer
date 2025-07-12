import openai
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI

from config.config import settings
from utils.agent_utils import (
    log_thought,
    get_search_results,
    clean_competitor_names,
    extract_company_info,
    extract_competitor_names,
    search_external_data,
    get_company_website,
    generate_competitor_analysis,
)
from .state import CompetitorAnalysisState


class CompetitorAnalysisNodes:
    """LangGraph nodes for competitor analysis workflow."""
    
    def __init__(self):
        if settings.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            self.llm = ChatOpenAI(
                model="gpt-4o",
                api_key=settings.OPENAI_API_KEY,
                temperature=0.1
            )
        else:
            self.openai_client = None
            self.llm = None
    
    def input_classifier_node(self, state: CompetitorAnalysisState) -> Dict[str, Any]:
        """Classifies input and determines the workflow path."""
        log_thought("🔍 Classifying input type...")
        
        company_name_or_website = state["company_name_or_website"]
        is_website = company_name_or_website.startswith(("http://", "https://", "www."))
        
        updates = {
            "is_website_input": is_website,
            "target_company": company_name_or_website,
            "next_step": "website_analysis" if is_website else "competitor_search"
        }
        
        log_thought(f"✅ Input classified as: {'Website' if is_website else 'Company Name'}")
        return updates
    
    def competitor_search_node(self, state: CompetitorAnalysisState) -> Dict[str, Any]:
        """Searches for competitors based on company name and location."""
        log_thought("🔎 Searching for competitors...")
        
        company_name = state["company_name_or_website"]
        location = state.get("location", "global")
        
        if not location:
            return {
                "error_message": "Location is required for competitor search",
                "next_step": "error"
            }
        
        # Get search results
        search_urls = get_search_results(company_name, location)
        competitor_names = []
        
        # Extract competitor names from search results
        for url in search_urls:
            page_data = extract_company_info(url)
            if page_text := page_data.get("description", ""):
                if self.openai_client:
                    names = extract_competitor_names(self.openai_client, page_text)
                    competitor_names.extend(names)
                else:
                    # Fallback to simple text extraction if no API key
                    competitor_names.extend(page_text.split()[:10])
        
        cleaned_names = clean_competitor_names(competitor_names)
        
        updates = {
            "search_urls": search_urls,
            "competitor_names": cleaned_names,
            "next_step": "competitor_selection"
        }
        
        log_thought(f"✅ Found {len(cleaned_names)} competitors")
        return updates
    
    def competitor_selection_node(self, state: CompetitorAnalysisState) -> Dict[str, Any]:
        """Handles competitor selection logic."""
        log_thought("🎯 Processing competitor selection...")
        
        selected_competitor = state.get("selected_competitor")
        
        if not selected_competitor:
            return {
                "error_message": "Please select a competitor from the available options",
                "next_step": "error"
            }
        
        # Find website for selected competitor
        website = get_company_website(selected_competitor)
        
        if not website:
            return {
                "error_message": f"Could not find website for {selected_competitor}",
                "next_step": "error"
            }
        
        updates = {
            "target_company": selected_competitor,
            "company_website": website,
            "next_step": "data_collection"
        }
        
        log_thought(f"✅ Selected competitor: {selected_competitor}")
        return updates
    
    def website_analysis_node(self, state: CompetitorAnalysisState) -> Dict[str, Any]:
        """Directly analyzes a provided website."""
        log_thought("🌐 Analyzing provided website...")
        
        website_url = state["company_name_or_website"]
        
        updates = {
            "target_company": website_url,
            "company_website": website_url,
            "next_step": "data_collection"
        }
        
        log_thought(f"✅ Website ready for analysis: {website_url}")
        return updates
    
    def data_collection_node(self, state: CompetitorAnalysisState) -> Dict[str, Any]:
        """Collects company data and external market data."""
        log_thought("📊 Collecting company and market data...")
        
        target_company = state["target_company"]
        website = state["company_website"]
        
        # Collect company data
        company_data = extract_company_info(website) if website else {}
        
        # Collect external data
        external_data = search_external_data(target_company)
        
        updates = {
            "company_data": company_data,
            "external_data": external_data,
            "next_step": "analysis_generation"
        }
        
        log_thought("✅ Data collection completed")
        return updates
    
    def analysis_generation_node(self, state: CompetitorAnalysisState) -> Dict[str, Any]:
        """Generates the final competitor analysis report."""
        log_thought("📝 Generating competitor analysis report...")
        
        target_company = state["target_company"]
        company_data = state.get("company_data", {})
        external_data = state.get("external_data", {})
        
        # Generate analysis report
        if self.openai_client:
            analysis_report = generate_competitor_analysis(
                self.openai_client,
                target_company,
                company_data,
                external_data
            )
        else:
            analysis_report = f"Mock analysis report for {target_company} (OpenAI API key not configured)"
        
        updates = {
            "analysis_report": analysis_report,
            "workflow_completed": True,
            "next_step": "end"
        }
        
        log_thought("✅ Analysis report generated successfully")
        return updates
    
    def error_node(self, state: CompetitorAnalysisState) -> Dict[str, Any]:
        """Handles errors in the workflow."""
        error_message = state.get("error_message", "An unknown error occurred")
        log_thought(f"❌ Error: {error_message}")
        
        return {
            "workflow_completed": True,
            "next_step": "end"
        }
    
    def should_continue(self, state: CompetitorAnalysisState) -> str:
        """Determines the next step in the workflow."""
        if state.get("workflow_completed", False):
            return "end"
        
        next_step = state.get("next_step", "error")
        log_thought(f"➡️ Next step: {next_step}")
        return next_step
