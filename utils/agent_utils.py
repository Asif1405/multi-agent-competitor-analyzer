from bs4 import BeautifulSoup
from googlesearch import search
import logging
import openai
import re
import requests
import time
from typing import List, Dict, Any


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


def log_thought(thought: str) -> None:
    """Logs the agent's thought process."""
    LOGGER.info(thought)
    print(thought)


def retry(
    func: callable,
    *args: List[Any],
    retries: int = 3,
    delay: int = 2,
    **kwargs: Dict[str, Any]
) -> any:
    """Retries a function in case of failure."""
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log_thought(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    log_thought("Max retries reached. Moving on.")
    return None


def get_search_results(
    product: str,
    location: str = "global"
) -> List[str]:
    """Finds competitor brand names for a product in a given location using Google Search."""
    log_thought(f"Searching for top competitors of {product} in {location}...")
    print(product, location, "product, location")
    if location.lower() == "global":
        query = f"top {product} brands"
    elif location is None or location.lower() == "":
        query = f"top {product} brands"
    else:
        query = f"top {product} brands in {location}"
    print(query)
    urls = []
    try:
        for url in search(query, num=3, stop=3, pause=1):
            print(url, "url")
            urls.append(url)
    except Exception as e:
        log_thought(f"Error searching Google: {e}")
    return urls


def clean_competitor_names(names: List[str]) -> List[str]:
    """Cleans and removes duplicate and irrelevant competitor names."""
    cleaned_names = list(set(names))  # Remove duplicates
    filtered_names = [
        name.strip() for name in cleaned_names if len(
            name.strip()) > 1 and not any(
            c in name for c in [
                "review",
                "comparison",
                "site"])]
    filtered_names = re.sub(
        r'[^a-zA-Z0-9\s]',
        '',
        ' '.join(filtered_names)).split()
    return filtered_names


def extract_competitor_names(
    client: openai.Client,
    text: str
) -> List[str]:
    """Uses GPT-4o to extract competitor brand names from web page content."""
    log_thought("Extracting competitor names from webpage content...")
    prompt = f"""
    Extract and list company names from the following text:
    {text}
    Only return company names, no extra text, symbols, separators, special characters, or numbers.
    Remove any duplicates and irrelevant names.
    Remove any name that is not related to product brands.
    Remove any name that is not a company or brand.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant extracting competitor names."},
                {"role": "user", "content": prompt}
            ]
        )
        return clean_competitor_names(
            response.choices[0].message.content.strip().split("\n"))
    except Exception as e:
        log_thought(f"OpenAI API error: {e}")
        return []


def get_company_website(company_name: str) -> str:
    """Finds the official website of a company using Google Search."""
    log_thought(f"Searching for official website of {company_name}...")
    query = f"{company_name} official website"
    return retry(lambda: next(search(query, num=1, stop=1, pause=2), None))


def extract_company_info(url: str) -> Dict[str, str]:
    """Scrapes key data from the competitor's website."""
    log_thought(f"Scraping website: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.text if soup.title else ""
        description = " ".join([p.text for p in soup.find_all("p")])[
            :2000]  # Limit text to 2000 chars
        return {"website": url, "title": title, "description": description}
    except Exception as e:
        log_thought(f"Error scraping {url}: {e}")
        return {}


def search_external_data(company_name: str) -> Dict[str, str]:
    """Searches for external market insights, customer reviews, and financial data."""
    log_thought(f"Searching for external data on {company_name}...")
    queries = [
        f"{company_name} customer reviews",
        f"{company_name} market analysis",
        f"{company_name} financial data",
        f"{company_name} third party evaluation"
    ]
    data = ""
    for query in queries:
        result = retry(
            lambda: extract_company_info(
                next(
                    search(
                        query,
                        num=3,
                        stop=3,
                        pause=2),
                    None)))
        if result:
            data += result.get("description", "") + "\n"
    return {"description": data}


def generate_competitor_analysis(
    client: openai.Client,
    company_name: str,
    company_data: Dict[str, str],
    external_data: Dict[str, str]
) -> str:
    """Generates a competitor analysis report using GPT-4o."""
    log_thought(f"Generating competitor analysis for: {company_name}...")
    prompt = f"""
    Analyze the following competitor:

    Company Name: {company_name}
    Website: {company_data['website']}
    Title: {company_data['title']}

    Description:
    {company_data['description']}

    Additional Market Insights:
    {external_data.get('description', '')}

    Provide an in-depth competitor analysis, including:
    - Company Overview
    - Strengths & Weaknesses
    - Market Position
    - Unique Selling Proposition (USP)
    - Online Presence & Branding
    - Marketing & Advertising Strategy
    - Key Products & Services
    - Customer Review Summary & Sentiment
    - Market and Financial Data
    - Third-Party Evaluation
    - Key Takeaways

    Please ensure the report is detailed, accurate, and well-structured.
    Provide actionable insights and recommendations for the user.
    Provide references and citations where necessary.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a business analyst. Generate a competitor analysis report."},
                {"role": "user", "content": prompt}
            ]
        )
        print("Done")
        return response.choices[0].message.content.strip()
    except Exception as e:
        log_thought(f"OpenAI API error: {e}")
        return ""
