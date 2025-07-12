from bs4 import BeautifulSoup
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
    """Finds competitor brand names for a product in a given location using Serper API."""
    log_thought(f"Searching for top competitors of {product} in {location}...")
    
    if location.lower() == "global":
        query = f"top {product} brands competitors"
    elif location is None or location.lower() == "":
        query = f"top {product} brands competitors"
    else:
        query = f"top {product} brands competitors in {location}"
    
    log_thought(f"Search query: {query}")
    
    try:
        # Import here to avoid circular imports
        from utils.serper_search import search_tool
        
        # Use Serper API for reliable search results
        search_results = search_tool.search(query)
        urls = [result["url"] for result in search_results if result.get("url")]
        
        log_thought(f"✅ Found {len(urls)} competitor URLs")
        return urls[:3]  # Limit to top 3 results
        
    except Exception as e:
        log_thought(f"Search failed: {e}")
        # Return mock competitor data based on common industry knowledge
        mock_competitors = {
            "tesla": ["BMW", "Mercedes-Benz", "Audi", "Volkswagen", "Ford"],
            "apple": ["Samsung", "Google", "Microsoft", "Amazon", "Meta"],
            "microsoft": ["Google", "Apple", "Amazon", "Oracle", "IBM"],
            "amazon": ["Google", "Microsoft", "Apple", "Walmart", "eBay"],
            "google": ["Microsoft", "Apple", "Amazon", "Meta", "Oracle"],
            "netflix": ["Disney", "Amazon Prime", "Hulu", "HBO Max", "Spotify"],
            "spotify": ["Apple Music", "YouTube Music", "Amazon Music", "Pandora", "Tidal"],
            "uber": ["Lyft", "Taxi", "DoorDash", "Grubhub", "Postmates"],
            "airbnb": ["Hotels.com", "Booking.com", "Expedia", "VRBO", "Marriott"]
        }
        
        product_lower = product.lower()
        mock_urls = []
        
        # Check if we have mock data for this product
        for key, competitors in mock_competitors.items():
            if key in product_lower:
                for comp in competitors[:3]:
                    mock_urls.append(f"https://www.{comp.lower().replace(' ', '').replace('-', '')}.com")
                break
        
        if not mock_urls:
            # Generic mock URLs
            mock_urls = [
                f"https://www.competitor1-{product.lower()}.com",
                f"https://www.competitor2-{product.lower()}.com",
                f"https://www.competitor3-{product.lower()}.com"
            ]
        
        urls = mock_urls[:3]
        log_thought(f"Using mock competitor URLs: {urls}")
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
    
    # If no client available, use mock extraction
    if not client:
        log_thought("No OpenAI client available, using mock competitor extraction...")
        # Extract potential company names using simple heuristics
        words = text.split()
        potential_names = []
        for i, word in enumerate(words):
            if word.istitle() and len(word) > 2:
                # Check if next word is also capitalized (likely company name)
                if i + 1 < len(words) and words[i + 1].istitle():
                    potential_names.append(f"{word} {words[i + 1]}")
                else:
                    potential_names.append(word)
        return clean_competitor_names(potential_names[:10])  # Return first 10
    
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
    """Finds the official website of a company using Serper API."""
    log_thought(f"Searching for official website of {company_name}...")
    query = f"{company_name} official website"
    try:
        from utils.serper_search import search_tool
        results = search_tool.search(query)
        if results:
            return results[0]["url"]
    except Exception as e:
        log_thought(f"Error searching for website: {e}")
    
    # Return a mock website for testing
    return f"https://www.{company_name.lower().replace(' ', '')}.com"


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
        try:
            from utils.serper_search import search_tool
            results = search_tool.search(query)
            if results:
                # Take the first result
                result = extract_company_info(results[0]["url"])
                if result:
                    data += result.get("description", "") + "\n"
        except Exception as e:
            log_thought(f"Error searching for query '{query}': {e}")
    return {"description": data}


def generate_competitor_analysis(
    client: openai.Client,
    company_name: str,
    company_data: Dict[str, str],
    external_data: Dict[str, str]
) -> str:
    """Generates a competitor analysis report using GPT-4o."""
    log_thought(f"Generating competitor analysis for: {company_name}...")
    
    # Handle missing keys safely
    website = company_data.get('website', f"https://www.{company_name.lower().replace(' ', '')}.com")
    title = company_data.get('title', company_name)
    description = company_data.get('description', f"Company information for {company_name}")
    external_desc = external_data.get('description', 'Limited external data available')
    
    prompt = f"""
    Analyze the following competitor:

    Company Name: {company_name}
    Website: {website}
    Title: {title}

    Description:
    {description}

    Additional Market Insights:
    {external_desc}

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
    
    if not client:
        log_thought("No OpenAI client available, generating mock analysis...")
        return f"""
# Competitor Analysis: {company_name}

## Company Overview
{company_name} is a major player in its industry, operating through their website at {website}.

## Market Position
Based on available data, {company_name} holds a significant position in the market with established brand recognition.

## Key Strengths
- Strong brand presence
- Established market position
- Professional online presence

## Areas for Monitoring
- Competitive pricing strategies
- Product innovation cycles
- Customer satisfaction trends

## Recommendations
- Monitor their pricing and promotional strategies
- Track their product launches and announcements
- Analyze their customer engagement approaches

*Note: This is a sample analysis. For detailed insights, configure your OpenAI API key.*
        """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a business analyst. Generate a competitor analysis report."},
                {"role": "user", "content": prompt}
            ]
        )
        log_thought("✅ Analysis generated successfully")
        return response.choices[0].message.content.strip()
    except Exception as e:
        log_thought(f"OpenAI API error: {e}")
        return f"Error generating analysis: {str(e)}"
