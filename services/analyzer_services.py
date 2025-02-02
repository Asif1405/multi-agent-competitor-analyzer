import openai
from dotenv import load_dotenv
import os
from typing import Optional

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

load_dotenv()

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_competitor_analysis_service(
    company_name_or_website: str,
    selected_competitor: Optional[str] = None
) -> str:
    """Generate analysis report for either direct URL or selected competitor"""
    if company_name_or_website.startswith(("http://", "https://", "www.")):
        log_thought("Analyzing given website...")
        company_data = extract_company_info(company_name_or_website)
        external_data = search_external_data(company_name_or_website)
        return generate_competitor_analysis(client, company_name_or_website, company_data, external_data)
    
    if not selected_competitor:
        return "Please select a competitor from the dropdown"
    
    log_thought(f"Generating report for {selected_competitor}")
    if website := get_company_website(selected_competitor):
        competitor_data = extract_company_info(website)
        external_data = search_external_data(selected_competitor)
        return generate_competitor_analysis(client, selected_competitor, competitor_data, external_data)
    
    return f"Could not find website for {selected_competitor}"

def update_competitor_dropdown(company_name: str, location: str) -> list:
    """Fetch and return competitors for dropdown based on product/location"""
    if company_name.startswith(("http://", "https://", "www.")):
        return []
    
    if not location:
        return []
    
    log_thought(f"Searching competitors for {company_name} in {location}")
    competitor_urls = get_search_results(company_name, location)
    competitor_names = []
    
    for url in competitor_urls:
        if page_text := extract_company_info(url).get("description", ""):
            competitor_names.extend(extract_competitor_names(client, page_text))
    
    return clean_competitor_names(competitor_names)
