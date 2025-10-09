#!/usr/bin/env python3
"""
OpenAI ChatGPT Platform Integration
Handles citation extraction from ChatGPT responses
"""

import os
import requests
import json
import logging
import re
from urllib.parse import urlparse
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ChatGPTPlatform:
    """OpenAI ChatGPT platform integration for citation extraction"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.base_url = "https://api.openai.com/v1/chat/completions"
        self.model = "gpt-4o-mini"
        self.timeout = 30
        
        logger.info(f"ChatGPT platform initialized with model: {self.model}")
    
    def get_citations(self, prompt: str) -> List[Dict[str, Any]]:
        """Extract citations from ChatGPT response"""
        try:
            logger.info("ChatGPT API call attempt 1")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Enhanced prompt to encourage citation-rich responses
            enhanced_prompt = f"""Please provide a comprehensive response to this query with specific sources, citations, and references where possible. Include URLs and publication names when mentioning information.

Query: {prompt}

Please structure your response with clear references and sources."""
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful research assistant that provides detailed responses with citations, sources, and references. Always include specific URLs, publication names, and authoritative sources when discussing topics. Format citations clearly and include web links when available."
                    },
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                "max_tokens": 1500,
                "temperature": 0.3
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                citations = self._extract_citations_from_response(data, prompt)
                logger.info(f"ChatGPT returned {len(citations)} citations")
                return citations
            else:
                logger.error(f"ChatGPT API error: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("ChatGPT API timeout")
            return []
        except Exception as e:
            logger.error(f"ChatGPT API exception: {e}")
            return []
    
    def _extract_citations_from_response(self, response_data: Dict[str, Any], prompt: str) -> List[Dict[str, Any]]:
        """Extract citations from ChatGPT response data"""
        citations = []
        
        try:
            if 'choices' in response_data and response_data['choices']:
                content = response_data['choices'][0].get('message', {}).get('content', '')
                
                # Extract URLs from content using multiple patterns
                url_patterns = [
                    r'https?://[^\s\]\)\,]+(?:[^\s\]\)\,.,;!?])',  # Standard URLs
                    r'(?:Source:|Reference:|See:|Visit:)\s*(https?://[^\s\]\)\,]+)',  # Labeled sources
                    r'\[([^\]]*)\]\((https?://[^\)]+)\)',  # Markdown links
                    r'<(https?://[^>]+)>',  # Angle bracket URLs
                ]
                
                for pattern in url_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    for match in matches:
                        if isinstance(match, tuple):
                            # Handle tuple results from capturing groups
                            url = match[1] if len(match) > 1 else match[0]
                        else:
                            url = match
                        
                        # Clean up URL
                        url = url.rstrip('.,;!?')
                        if self._is_valid_url(url):
                            citations.append({
                                'url': url,
                                'type': 'inline',
                                'platform': 'chatgpt',
                                'prompt': prompt,
                                'domain': self._extract_domain(url)
                            })
                
            
            # Remove duplicates
            seen_urls = set()
            unique_citations = []
            for citation in citations:
                if citation['url'] not in seen_urls:
                    seen_urls.add(citation['url'])
                    unique_citations.append(citation)
            
            logger.info(f"Extracted {len(unique_citations)} citations from ChatGPT response")
            return unique_citations
            
        except Exception as e:
            logger.error(f"Error extracting citations from ChatGPT response: {e}")
            return []
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and not a common false positive"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            
            # Filter out common false positives
            invalid_domains = ['example.com', 'test.com', 'localhost', 'domain.com', 'website.com']
            if parsed.netloc.lower() in invalid_domains:
                return False
            
            # Must have valid TLD
            valid_tlds = ['.com', '.org', '.net', '.edu', '.gov', '.co.uk', '.io', '.ai', '.co', '.us']
            if not any(parsed.netloc.lower().endswith(tld) for tld in valid_tlds):
                return False
            
            return True
        except:
            return False
