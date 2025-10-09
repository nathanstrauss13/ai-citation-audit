#!/usr/bin/env python3
"""
Anthropic Claude Platform Integration
Handles citation extraction from Claude responses
"""

import os
import requests
import json
import logging
import re
from urllib.parse import urlparse
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ClaudePlatform:
    """Anthropic Claude platform integration for citation extraction"""
    
    def __init__(self):
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.model = "claude-3-5-sonnet-20241022"
        self.timeout = 30
        
        logger.info(f"Claude platform initialized with model: {self.model}")
    
    def get_citations(self, prompt: str) -> List[Dict[str, Any]]:
        """Extract citations from Claude response"""
        try:
            logger.info("Claude API call attempt 1")
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            # Enhanced prompt to encourage citation-rich responses
            enhanced_prompt = f"""Please provide a comprehensive and well-researched response to this query. Include specific sources, citations, references, and URLs where possible. When mentioning companies, publications, or studies, please include their official websites or relevant links.

Query: {prompt}

Please structure your response with clear references and authoritative sources."""
            
            payload = {
                "model": self.model,
                "max_tokens": 1500,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "user",
                        "content": enhanced_prompt
                    }
                ],
                "system": "You are a knowledgeable research assistant that provides detailed, well-sourced responses with citations and references. Always include specific URLs, publication names, and authoritative sources when discussing topics. Format your responses with clear citations and include web links when available."
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
                logger.info(f"Claude returned {len(citations)} citations")
                return citations
            else:
                logger.error(f"Claude API error: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("Claude API timeout")
            return []
        except Exception as e:
            logger.error(f"Claude API exception: {e}")
            return []
    
    def _extract_citations_from_response(self, response_data: Dict[str, Any], prompt: str) -> List[Dict[str, Any]]:
        """Extract citations from Claude response data"""
        citations = []
        
        try:
            if 'content' in response_data and response_data['content']:
                # Claude returns content as a list of content blocks
                content = ""
                for block in response_data['content']:
                    if block.get('type') == 'text':
                        content += block.get('text', '')
                
                # Extract URLs from content using multiple patterns
                url_patterns = [
                    r'https?://[^\s\]\)\,\n]+(?:[^\s\]\)\,.,;!?\n])',  # Standard URLs
                    r'(?:Source:|Reference:|See:|Visit:|Website:)\s*(https?://[^\s\]\)\,\n]+)',  # Labeled sources
                    r'\[([^\]]*)\]\((https?://[^\)\n]+)\)',  # Markdown links
                    r'<(https?://[^>\n]+)>',  # Angle bracket URLs
                    r'(?:Available at|Found at|Link:)\s*(https?://[^\s\]\)\,\n]+)',  # Additional patterns
                ]
                
                for pattern in url_patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
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
                                'platform': 'claude',
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
            
            logger.info(f"Extracted {len(unique_citations)} citations from Claude response")
            return unique_citations
            
        except Exception as e:
            logger.error(f"Error extracting citations from Claude response: {e}")
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
            invalid_domains = ['example.com', 'test.com', 'localhost', 'domain.com', 'website.com', 'company.com']
            if parsed.netloc.lower() in invalid_domains:
                return False
            
            # Must have valid TLD
            valid_tlds = ['.com', '.org', '.net', '.edu', '.gov', '.co.uk', '.io', '.ai', '.co', '.us', '.de', '.fr']
            if not any(parsed.netloc.lower().endswith(tld) for tld in valid_tlds):
                return False
            
            return True
        except:
            return False
