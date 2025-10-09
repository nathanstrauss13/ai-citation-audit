#!/usr/bin/env python3
"""
Perplexity AI Platform Integration
Handles citation extraction from Perplexity AI responses
"""

import os
import requests
import json
import logging
import re
from urllib.parse import urlparse
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class PerplexityPlatform:
    """Perplexity AI platform integration for citation extraction"""
    
    def __init__(self):
        self.api_key = os.getenv('PERPLEXITY_API_KEY')
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY not found in environment variables")
        
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.model = "sonar-pro"
        self.timeout = 30
        
        logger.info(f"Perplexity platform initialized with model: {self.model}")
    
    def get_citations(self, prompt: str) -> List[Dict[str, Any]]:
        """Extract citations from Perplexity AI response"""
        try:
            logger.info("Perplexity API call attempt 1")
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that provides detailed responses with citations and sources."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.2,
                "return_citations": True,
                "return_images": False
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
                logger.info(f"Perplexity returned {len(citations)} citations")
                return citations
            else:
                logger.error(f"Perplexity API error: {response.status_code} - {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error("Perplexity API timeout")
            return []
        except Exception as e:
            logger.error(f"Perplexity API exception: {e}")
            return []
    
    def _extract_citations_from_response(self, response_data: Dict[str, Any], prompt: str) -> List[Dict[str, Any]]:
        """Extract citations from Perplexity response data"""
        citations = []
        
        try:
            # Extract from citations field if available
            if 'citations' in response_data:
                for citation in response_data['citations']:
                    if isinstance(citation, str) and citation.startswith('http'):
                        citations.append({
                            'url': citation,
                            'type': 'citation',
                            'platform': 'perplexity',
                            'prompt': prompt,
                            'domain': self._extract_domain(citation)
                        })
            
            # Also extract nested citations under choices/message if present
            try:
                choices = response_data.get('choices', [])
                if choices:
                    first = choices[0] or {}
                    msg = first.get('message', {}) or {}
                    nested = msg.get('citations') or first.get('citations') or []
                    for citation in nested:
                        if isinstance(citation, str) and citation.startswith('http'):
                            citations.append({
                                'url': citation,
                                'type': 'citation',
                                'platform': 'perplexity',
                                'prompt': prompt,
                                'domain': self._extract_domain(citation)
                            })
            except Exception:
                pass

            # Extract from message content
            if 'choices' in response_data and response_data['choices']:
                content = response_data['choices'][0].get('message', {}).get('content', '')
                
                # Extract URLs from content using regex
                url_pattern = r'https?://[^\s\]\)]+(?:[^\s\]\).,;!?])'
                urls = re.findall(url_pattern, content)
                
                for url in urls:
                    # Clean up URL
                    url = url.rstrip('.,;!?')
                    if self._is_valid_url(url):
                        citations.append({
                            'url': url,
                            'type': 'inline',
                            'platform': 'perplexity',
                            'prompt': prompt,
                            'domain': self._extract_domain(url)
                        })
            
            # Normalize, validate, and dedupe
            seen_urls = set()
            unique_citations = []
            for citation in citations:
                nu = self._normalize_url(citation.get('url', ''))
                if not nu or not self._is_valid_url(nu):
                    continue
                if nu in seen_urls:
                    continue
                citation['url'] = nu
                citation['domain'] = self._extract_domain(nu)
                seen_urls.add(nu)
                unique_citations.append(citation)

            # Basic link verification (HEAD) for top URLs; non-blocking fallback
            try:
                valid_set = self._verify_urls([c['url'] for c in unique_citations])
                if valid_set:
                    unique_citations = [c for c in unique_citations if c['url'] in valid_set]
            except Exception as _:
                pass
            
            logger.info(f"Extracted {len(unique_citations)} citations from Perplexity response")
            return unique_citations
            
        except Exception as e:
            logger.error(f"Error extracting citations from Perplexity response: {e}")
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
            invalid_domains = ['example.com', 'test.com', 'localhost']
            if parsed.netloc.lower() in invalid_domains:
                return False
            
            return True
        except:
            return False

    def _normalize_url(self, url: str) -> str:
        try:
            if not url:
                return ""
            if url.startswith("data:") or url.startswith("#"):
                return ""
            from urllib.parse import urlparse
            p = urlparse(url)
            netloc = p.netloc.lower()
            if netloc.startswith("www."):
                netloc = netloc[4:]
            path = (p.path or "").rstrip("/")
            return f"{p.scheme}://{netloc}{path}"
        except Exception:
            return url or ""

    def _verify_urls(self, urls: List[str]) -> set:
        """
        Basic HEAD verification for top N URLs. Returns set of URLs passing 2xx/3xx.
        """
        valid = set()
        try:
            session = requests.Session()
            session.headers.update({"User-Agent": "InnateC3-CiteAudit/0.1"})
            for u in urls[:10]:  # cap to avoid latency
                try:
                    r = session.head(u, timeout=3, allow_redirects=True)
                    if 200 <= r.status_code < 400:
                        valid.add(u)
                except Exception:
                    continue
        except Exception:
            # Non-fatal: return empty to indicate fallback
            return set()
        return valid
