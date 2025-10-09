import requests
import os
import time
import re
import json
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class GeminiPlatform:
    """Gemini AI platform for citation extraction using direct REST API"""
    
    def __init__(self):
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # Use direct REST API to bypass library routing issues
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model_name = "gemini-2.5-flash"  # Confirmed working model
        self.rate_limit_delay = 4.0  # 15 RPM = 4 seconds between requests
        self.max_retries = 2
        logger.info(f"Using direct REST API with {self.model_name} model")
        
    def get_citations(self, prompt: str) -> List[Dict]:
        """Get citations from Gemini with enhanced prompting using direct REST API"""
        
        # Enhanced prompt to encourage citations
        enhanced_prompt = f"""
        {prompt}
        
        When providing information, please include specific sources and references.
        Format any sources as:
        - Reference: [Source Name] - URL
        - Or include URLs inline in your response
        Include authoritative sources like news sites, company websites, industry reports, etc.
        """
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Gemini API call attempt {attempt + 1}")
                
                # Direct REST API call
                url = f"{self.base_url}/models/{self.model_name}:generateContent"
                
                headers = {
                    "Content-Type": "application/json"
                }
                
                data = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": enhanced_prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 4096,
                        "topP": 0.8,
                        "topK": 40
                    }
                }
                
                # Make the request with API key as query parameter
                response = requests.post(
                    f"{url}?key={self.api_key}",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                # Rate limiting
                time.sleep(self.rate_limit_delay)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        text = result['candidates'][0]['content']['parts'][0]['text']
                        
                        # Extract citations from response
                        citations = self.extract_citations(text)
                        logger.info(f"Gemini returned {len(citations)} citations")
                        
                        return citations
                    else:
                        logger.warning(f"No candidates in response: {result}")
                        return []
                else:
                    error_data = response.json() if response.content else {}
                    error_str = str(error_data).lower()
                    logger.error(f"Gemini API error (attempt {attempt + 1}): {response.status_code} - {error_data}")
                    
                    # Handle specific errors
                    if "quota" in error_str or "rate" in error_str or response.status_code == 429:
                        wait_time = 60 if "quota" in error_str else 10
                        logger.warning(f"Rate limit hit, waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                    elif "api_key" in error_str or response.status_code == 401:
                        logger.error("Invalid API key")
                        return []
                    else:
                        if attempt < self.max_retries - 1:
                            time.sleep(5)
                            continue
                
            except Exception as e:
                logger.error(f"Gemini API exception (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
                    continue
                    
        return []
    
    def extract_citations(self, text: str) -> List[Dict]:
        """Multi-strategy extraction for Gemini responses"""
        citations = []
        seen_urls = set()
        
        # Strategy 1: Reference format with URLs
        ref_patterns = [
            r'(?:Reference|Source|Citation):\s*(?:\[?([^\]]+)\]?)?\s*[-–]\s*(https?://[^\s\]]+)',
            r'\[(\d+)\][^\n]*?(https?://[^\s\]]+)',
            r'(?:From|Via|According to)[:\s]+([^\n]*?)(https?://[^\s\]]+)'
        ]
        
        for pattern in ref_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                url = match[-1] if isinstance(match, tuple) else match
                if url not in seen_urls:
                    seen_urls.add(url)
                    citations.append({
                        'url': url,
                        'type': 'reference',
                        'engine': 'gemini'
                    })
        
        # Strategy 2: Direct URLs in text
        url_pattern = r'https?://[^\s\)\]<"\']+'
        urls = re.findall(url_pattern, text)
        for url in urls:
            # Clean up URL
            url = url.rstrip('.,;:')
            if url not in seen_urls:
                seen_urls.add(url)
                citations.append({
                    'url': url,
                    'type': 'inline',
                    'engine': 'gemini'
                })
        
        # Strategy 3: Domain mentions (convert to URLs)
        domain_patterns = [
            r'(?:from|via|source:|according to)\s+([a-zA-Z0-9\-]+\.(?:com|org|net|edu|gov|io))',
            r'([A-Z][a-zA-Z0-9\-]+\.com)\s+(?:reports|states|announces)',
            r'visit\s+([a-zA-Z0-9\-]+\.[a-z]{2,4})'
        ]
        
        for pattern in domain_patterns:
            domains = re.findall(pattern, text, re.IGNORECASE)
            for domain in domains:
                url = f"https://{domain.lower()}"
                if url not in seen_urls:
                    seen_urls.add(url)
                    citations.append({
                        'url': url,
                        'type': 'domain_mention',
                        'engine': 'gemini'
                    })
        
        # Strategy 4: News organizations and publications
        news_orgs = {
            'Forbes': 'https://www.forbes.com',
            'Bloomberg': 'https://www.bloomberg.com',
            'Reuters': 'https://www.reuters.com',
            'Business Insider': 'https://www.businessinsider.com',
            'Wall Street Journal': 'https://www.wsj.com',
            'New York Times': 'https://www.nytimes.com',
            'Financial Times': 'https://www.ft.com',
            'CNBC': 'https://www.cnbc.com',
            'CNN Business': 'https://www.cnn.com/business',
            'MarketWatch': 'https://www.marketwatch.com'
        }
        
        for org, url in news_orgs.items():
            if org.lower() in text.lower() and url not in seen_urls:
                # Check if this org is mentioned in citation context
                patterns = [
                    f'according to {org}',
                    f'{org} reports',
                    f'per {org}',
                    f'via {org}',
                    f'source: {org}'
                ]
                if any(p.lower() in text.lower() for p in patterns):
                    seen_urls.add(url)
                    citations.append({
                        'url': url,
                        'type': 'news_org',
                        'engine': 'gemini'
                    })
        
        logger.info(f"Extracted {len(citations)} citations from Gemini response")
        return citations

    def test_connection(self) -> bool:
        """Test if Gemini API is working using direct REST API"""
        try:
            # Direct REST API call for testing
            url = f"{self.base_url}/models/{self.model_name}:generateContent"
            
            headers = {
                "Content-Type": "application/json"
            }
            
            data = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "Hello, please respond with 'OK'"
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 100
                }
            }
            
            response = requests.post(
                f"{url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Gemini response structure: {json.dumps(result, indent=2)}")
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        text = candidate['content']['parts'][0]['text']
                        return "OK" in text.upper()
                    else:
                        logger.error(f"Unexpected response structure: {candidate}")
                        return False
                else:
                    logger.error(f"No candidates in response: {result}")
                    return False
            
            logger.error(f"Gemini connection test failed: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False
