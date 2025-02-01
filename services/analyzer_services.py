from dotenv import load_dotenv
import openai
import os

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
    location: str = "Global",
    max_competitors: int = 3,
) -> str:
    print(f"Analyzing competitors for: {company_name_or_website}")
    print(f"Location: {location}")
    print(f"Max Competitors: {max_competitors}")
    if company_name_or_website.startswith("http") or company_name_or_website.startswith("www"):
        log_thought("Analyzing given website...")
        company_data = extract_company_info(company_name_or_website)
        external_data = search_external_data(company_name_or_website)
        report = generate_competitor_analysis("Provided Website", company_data, external_data)
        print(report)
        return report
    else:
        log_thought("Finding competitor brands...")
        print(f"Searching for competitors of: {company_name_or_website}")
        competitor_urls = get_search_results(company_name_or_website, location)
        print(f"Found {len(competitor_urls)} competitors")
        competitor_names = []

        for url in competitor_urls:
            log_thought(f"Extracting data from: {url}")
            page_text = extract_company_info(url).get("description", "")
            if page_text:
                competitor_names.extend(extract_competitor_names(client, page_text))

        competitor_names = clean_competitor_names(competitor_names)[:max_competitors]  # Get top N competitors
        log_thought(f"Identified Competitor Brands: {competitor_names}")

        combined_report = ""
        for competitor in competitor_names:
            log_thought(f"Finding website for {competitor}...")
            competitor_website = get_company_website(competitor)
            if competitor_website:
                competitor_data = extract_company_info(competitor_website)
                external_data = search_external_data(competitor)
                report = generate_competitor_analysis(client, competitor, competitor_data, external_data)
                print(f"\nCompetitor Analysis Report for {competitor}:")
                print(report)
                combined_report += report
            else:
                log_thought(f"No website found for {competitor}")

        return combined_report
