"""
Serper API integration for reliable web search in competitor analysis.
This replaces the unreliable Google Search library with a professional API.
"""

import os
import requests
from typing import List, Dict, Any
from config.config import settings
from utils.agent_utils import log_thought


class SerperSearchTool:
    """Professional web search using Serper API."""
    
    ENDPOINT = "https://google.serper.dev/search"
    
    def __init__(self, k: int = 5):
        self.k = k
        key = settings.SERPER_API_KEY
        if not key or key == "your_serper_api_key_here":
            log_thought("⚠️ SERPER_API_KEY not configured, using mock data")
            self.api_available = False
        else:
            self.headers = {"X-API-KEY": key, "Content-Type": "application/json"}
            self.api_available = True
    
    def search(self, query: str) -> List[Dict[str, str]]:
        """
        Search using Serper API and return structured results.
        
        Args:
            query: Search query string
            
        Returns:
            List of search results with title, url, and snippet
        """
        log_thought(f"🔍 Serper search: {query}")
        
        if not self.api_available:
            return self._get_mock_results(query)
        
        try:
            payload = {"q": query, "num": self.k}
            response = requests.post(
                self.ENDPOINT, 
                headers=self.headers, 
                json=payload, 
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic", [])[:self.k]:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "snippet": item.get("snippet", ""),
                    "content": item.get("snippet", "")  # Alias for compatibility
                })
            
            log_thought(f"✅ Found {len(results)} results")
            return results
            
        except Exception as e:
            log_thought(f"❌ Serper API error: {e}")
            return self._get_mock_results(query)
    
    def _get_mock_results(self, query: str) -> List[Dict[str, str]]:
        """Generate mock search results when API is unavailable."""
        log_thought("📝 Using mock search results")
        
        # Mock competitor data based on query
        mock_data = {
            "tesla": [
                {"title": "BMW - Luxury Electric Vehicles", "url": "https://www.bmw.com", "snippet": "BMW offers premium electric vehicles competing with Tesla"},
                {"title": "Mercedes-Benz Electric Cars", "url": "https://www.mercedes-benz.com", "snippet": "Mercedes-Benz EQS and electric vehicle lineup"},
                {"title": "Audi e-tron Electric Vehicles", "url": "https://www.audi.com", "snippet": "Audi's electric vehicle technology and models"}
            ],
            "apple": [
                {"title": "Samsung Galaxy Smartphones", "url": "https://www.samsung.com", "snippet": "Samsung Galaxy series competing with iPhone"},
                {"title": "Google Pixel Phones", "url": "https://store.google.com", "snippet": "Google Pixel smartphones with advanced AI features"},
                {"title": "Microsoft Surface Devices", "url": "https://www.microsoft.com", "snippet": "Microsoft Surface laptops and tablets"}
            ],
            "microsoft": [
                {"title": "Google Workspace", "url": "https://workspace.google.com", "snippet": "Google's productivity suite competing with Microsoft Office"},
                {"title": "Apple Business Solutions", "url": "https://www.apple.com/business", "snippet": "Apple's enterprise and business solutions"},
                {"title": "Amazon Web Services", "url": "https://aws.amazon.com", "snippet": "AWS cloud services competing with Microsoft Azure"}
            ]
        }
        
        # Find relevant mock data
        query_lower = query.lower()
        for key, data in mock_data.items():
            if key in query_lower:
                return [{"title": item["title"], "url": item["url"], "snippet": item["snippet"], "content": item["snippet"]} for item in data]
        
        # Default mock results
        return [
            {"title": f"Competitor Analysis for {query}", "url": "https://example.com/competitor1", "snippet": f"Mock competitor data for {query}", "content": f"Mock competitor data for {query}"},
            {"title": f"Market Research - {query}", "url": "https://example.com/competitor2", "snippet": f"Market analysis for {query} industry", "content": f"Market analysis for {query} industry"},
            {"title": f"Industry Report - {query}", "url": "https://example.com/competitor3", "snippet": f"Industry insights for {query} sector", "content": f"Industry insights for {query} sector"}
        ]


# Global instance
search_tool = SerperSearchTool(k=5)
