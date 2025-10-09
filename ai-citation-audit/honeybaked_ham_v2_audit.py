#!/usr/bin/env python3
"""
HoneyBaked Ham - Programmatic API Data Collection V2
Precision Methodology for AI Citation Analysis

Tests 15 queries across 4 AI platforms (60 total prompts)
Distinguishes between:
1. Brand mention in LLM response text
2. Total citations provided
3. Brand mentions within cited sources
"""

import os
import sys
import json
import csv
import logging
import requests
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
from urllib.parse import urlparse
from bs4 import BeautifulSoup

# Import platform adapters
from platforms.chatgpt import ChatGPTPlatform
from platforms.claude import ClaudePlatform
from platforms.perplexity import PerplexityPlatform
from platforms.gemini import GeminiPlatform

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HoneyBakedAuditor:
    """
    Comprehensive auditor for HoneyBaked Ham AI visibility
    Follows V2 precision methodology
    """
    
    def __init__(self):
        self.brand_name = "HoneyBaked"
        self.brand_variants = [
            "HoneyBaked", "HoneyBaked Ham", "Honey Baked", "Honey Baked Ham",
            "honeybaked.com", "HoneyBaked.com"
        ]
        
        self.chef_tim_variants = [
            "Tim Ziga", "Chef Tim", "Timothy Ziga", "Chef Timothy Ziga"
        ]
        
        # Initialize platforms
        self.platforms = {
            'chatgpt': ChatGPTPlatform(),
            'claude': ClaudePlatform(),
            'perplexity': PerplexityPlatform(),
            'gemini': GeminiPlatform()
        }
        
        # Competitor tracking list
        self.competitors = [
            "Omaha Steaks", "Whole Foods", "Costco", "Harry & David",
            "Williams Sonoma", "D'Artagnan", "Smithfield", "Spiral Ham Store",
            "Glazier Ham", "Sam's Club", "Walmart", "Kroger", "Publix"
        ]
        
        # Query definitions
        self.queries = self._define_queries()
        
        # Storage for results
        self.query_response_data = []
        self.citation_details_data = []
        self.competitive_mentions_data = []
        
        logger.info("HoneyBaked V2 Auditor initialized")
    
    def _define_queries(self) -> List[Dict[str, str]]:
        """Define the 15 test queries"""
        queries = []
        
        # BRANDED QUERIES (3 queries)
        branded = [
            "Compare HoneyBaked Ham to Omaha Steaks for holiday meals",
            "What makes HoneyBaked Ham different from other spiral hams?",
            "Where can I find HoneyBaked Ham stores near me?"
        ]
        for q in branded:
            queries.append({"text": q, "type": "branded", "category": "branded"})
        
        # BRAND-AGNOSTIC QUERIES (12 queries)
        
        # Category: Holiday Ham (4)
        holiday_ham = [
            "What is the best ham for Thanksgiving dinner?",
            "What is the best ham for Christmas dinner?",
            "Best spiral cut ham brands",
            "Best mail-order hams for holidays"
        ]
        for q in holiday_ham:
            queries.append({"text": q, "type": "brand_agnostic", "category": "holiday_ham"})
        
        # Category: Convenience/Ordering (4)
        convenience = [
            "What should I serve for Christmas dinner if I don't want to cook?",
            "What is the easiest holiday meal to order online?",
            "Last-minute Thanksgiving dinner options",
            "Where can I order a complete holiday meal?"
        ]
        for q in convenience:
            queries.append({"text": q, "type": "brand_agnostic", "category": "convenience"})
        
        # Category: Gifting (3)
        gifting = [
            "Best holiday food gifts to ship",
            "What's the best food gift for the holidays?",
            "Premium food gifts for corporate clients"
        ]
        for q in gifting:
            queries.append({"text": q, "type": "brand_agnostic", "category": "gifting"})
        
        # Category: Thought Leadership (1)
        thought_leadership = [
            "Who are the top chefs in the holiday catering industry?"
        ]
        for q in thought_leadership:
            queries.append({"text": q, "type": "brand_agnostic", "category": "thought_leadership"})
        
        return queries
    
    def run_audit(self) -> Dict[str, str]:
        """
        Execute complete audit across all queries and platforms
        Returns paths to generated CSV files
        """
        logger.info(f"Starting HoneyBaked V2 Audit - {len(self.queries)} queries × {len(self.platforms)} platforms = {len(self.queries) * len(self.platforms)} total tests")
        
        total_tests = len(self.queries) * len(self.platforms)
        completed = 0
        
        for query_info in self.queries:
            query_text = query_info["text"]
            query_type = query_info["type"]
            query_category = query_info["category"]
            
            logger.info(f"\n{'='*80}")
            logger.info(f"Query: {query_text}")
            logger.info(f"Type: {query_type} | Category: {query_category}")
            logger.info(f"{'='*80}")
            
            for platform_name, platform in self.platforms.items():
                completed += 1
                logger.info(f"\n[{completed}/{total_tests}] Testing on {platform_name}...")
                
                try:
                    # Get response and citations from platform
                    result = self._query_platform(platform, platform_name, query_text)
                    
                    if result:
                        # Analyze response for brand mentions
                        analysis = self._analyze_response(
                            result['response_text'],
                            result['citations'],
                            query_text,
                            query_type,
                            platform_name
                        )
                        
                        # Store in appropriate data structures
                        self.query_response_data.append(analysis['query_matrix_row'])
                        self.citation_details_data.extend(analysis['citation_details'])
                        self.competitive_mentions_data.extend(analysis['competitive_mentions'])
                    
                    # Rate limiting
                    time.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Error testing {query_text} on {platform_name}: {e}")
                    continue
        
        # Generate CSV files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_files = self._generate_csv_files(timestamp)
        
        logger.info(f"\n{'='*80}")
        logger.info("Audit Complete!")
        logger.info(f"Generated files:")
        for key, path in output_files.items():
            logger.info(f"  - {key}: {path}")
        logger.info(f"{'='*80}\n")
        
        return output_files
    
    def _query_platform(self, platform, platform_name: str, query: str) -> Dict[str, Any]:
        """Query a platform and return structured results"""
        try:
            # Get citations from platform
            citations = platform.get_citations(query)
            
            # Get full response text (we need to modify platform adapters to return this)
            # For now, we'll make a separate call to get the full response
            response_text = self._get_full_response(platform, platform_name, query)
            
            return {
                'response_text': response_text,
                'citations': citations,
                'platform': platform_name
            }
            
        except Exception as e:
            logger.error(f"Error querying {platform_name}: {e}")
            return None
    
    def _get_full_response(self, platform, platform_name: str, query: str) -> str:
        """
        Get full response text from platform
        This is needed to analyze brand mentions in the response
        """
        try:
            if platform_name == 'chatgpt':
                return self._get_chatgpt_response_text(query)
            elif platform_name == 'claude':
                return self._get_claude_response_text(query)
            elif platform_name == 'perplexity':
                return self._get_perplexity_response_text(query)
            elif platform_name == 'gemini':
                return self._get_gemini_response_text(query)
            else:
                return ""
        except Exception as e:
            logger.error(f"Error getting full response from {platform_name}: {e}")
            return ""
    
    def _get_chatgpt_response_text(self, query: str) -> str:
        """Get full ChatGPT response text"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": query}],
                    "max_tokens": 1500,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            return ""
        except Exception as e:
            logger.error(f"ChatGPT response error: {e}")
            return ""
    
    def _get_claude_response_text(self, query: str) -> str:
        """Get full Claude response text"""
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-5-sonnet-20241022",
                    "max_tokens": 1500,
                    "messages": [{"role": "user", "content": query}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                text = ""
                for block in data.get('content', []):
                    if block.get('type') == 'text':
                        text += block.get('text', '')
                return text
            return ""
        except Exception as e:
            logger.error(f"Claude response error: {e}")
            return ""
    
    def _get_perplexity_response_text(self, query: str) -> str:
        """Get full Perplexity response text"""
        try:
            api_key = os.getenv('PERPLEXITY_API_KEY')
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": query}],
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            return ""
        except Exception as e:
            logger.error(f"Perplexity response error: {e}")
            return ""
    
    def _get_gemini_response_text(self, query: str) -> str:
        """Get full Gemini response text"""
        try:
            api_key = os.getenv('GOOGLE_API_KEY')
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": query}]}],
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    return data['candidates'][0]['content']['parts'][0]['text']
            return ""
        except Exception as e:
            logger.error(f"Gemini response error: {e}")
            return ""
    
    def _analyze_response(
        self,
        response_text: str,
        citations: List[Dict],
        query: str,
        query_type: str,
        platform: str
    ) -> Dict[str, Any]:
        """
        Analyze response and citations for brand mentions
        Returns data for all three CSV files
        """
        
        # 1. Check if brand mentioned in response text
        brand_mentioned_in_response = self._check_brand_mention(response_text)
        
        # 2. Count total citations
        total_citations = len(citations)
        
        # 3. Check citations for brand mentions
        citations_mentioning_brand = 0
        brand_citation_urls = []
        citation_details = []
        
        for citation in citations:
            url = citation.get('url', '')
            
            # Check if brand mentioned in this citation's source
            brand_in_source = self._check_url_for_brand(url)
            
            if brand_in_source:
                citations_mentioning_brand += 1
                brand_citation_urls.append(url)
            
            # Build citation detail row
            citation_details.append({
                'engine': platform,
                'query': query,
                'query_type': query_type,
                'citation_url': url,
                'domain': self._extract_domain(url),
                'domain_classification': self._classify_domain(url),
                'honeybaked_mentioned_in_source': "Yes" if brand_in_source else "No",
                'content_type': self._classify_content_type(url)
            })
        
        # 4. Determine response prominence
        response_prominence = self._determine_prominence(response_text, brand_mentioned_in_response)
        
        # 5. Check for Chef Tim mentions
        chef_tim_mentioned = self._check_chef_tim_mention(response_text, citations)
        
        # 6. Track competitor mentions
        competitive_mentions = self._track_competitors(response_text, citations, query, query_type, platform)
        
        # Build query matrix row
        query_matrix_row = {
            'query': query,
            'query_type': query_type,
            'engine': platform,
            'brand_mentioned_in_response': "Yes" if brand_mentioned_in_response else "No",
            'total_citations': total_citations,
            'citations_mentioning_brand': citations_mentioning_brand,
            'response_prominence': response_prominence,
            'chef_tim_mentioned': "Yes" if chef_tim_mentioned else "No"
        }
        
        return {
            'query_matrix_row': query_matrix_row,
            'citation_details': citation_details,
            'competitive_mentions': competitive_mentions
        }
    
    def _check_brand_mention(self, text: str) -> bool:
        """Check if any brand variant is mentioned in text"""
        if not text:
            return False
        
        text_lower = text.lower()
        for variant in self.brand_variants:
            if variant.lower() in text_lower:
                return True
        return False
    
    def _check_chef_tim_mention(self, text: str, citations: List[Dict]) -> bool:
        """Check if Chef Tim Ziga is mentioned"""
        # Check response text
        if text:
            text_lower = text.lower()
            for variant in self.chef_tim_variants:
                if variant.lower() in text_lower:
                    return True
        
        # Check citation URLs and content
        for citation in citations:
            url = citation.get('url', '').lower()
            if 'tim' in url and 'ziga' in url:
                return True
        
        return False
    
    def _check_url_for_brand(self, url: str) -> bool:
        """
        Check if a URL mentions HoneyBaked
        Returns True if brand found, False otherwise
        """
        if not url:
            return False
        
        # Check if it's the official site
        if 'honeybaked.com' in url.lower():
            return True
        
        # Try to fetch and analyze the page content
        try:
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; HoneyBakedAudit/1.0)'
            })
            
            if response.status_code == 200:
                # Check both raw text and HTML
                content = response.text.lower()
                
                for variant in self.brand_variants:
                    if variant.lower() in content:
                        return True
                
                # Also check with BeautifulSoup for cleaner text
                try:
                    soup = BeautifulSoup(content, 'html.parser')
                    text = soup.get_text().lower()
                    
                    for variant in self.brand_variants:
                        if variant.lower() in text:
                            return True
                except:
                    pass
            
            return False
            
        except Exception as e:
            logger.debug(f"Could not fetch {url}: {e}")
            return False
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    def _classify_domain(self, url: str) -> str:
        """Classify domain type"""
        domain = self._extract_domain(url).lower()
        
        # Tier 1 News
        tier1_news = ['nytimes.com', 'wsj.com', 'washingtonpost.com', 'theguardian.com']
        if any(d in domain for d in tier1_news):
            return 'tier1_news'
        
        # Tier 2 News
        tier2_news = ['usatoday.com', 'latimes.com', 'chicagotribune.com']
        if any(d in domain for d in tier2_news):
            return 'tier2_news'
        
        # Food Media
        food_media = ['seriouseats.com', 'bonappetit.com', 'foodnetwork.com', 
                      'allrecipes.com', 'eater.com', 'thespruceeats.com', 'tasty.co']
        if any(d in domain for d in food_media):
            return 'food_media'
        
        # Lifestyle Media
        lifestyle_media = ['goodhousekeeping.com', 'marthastewart.com', 'realsimple.com',
                          'southernliving.com', 'tasteofhome.com']
        if any(d in domain for d in lifestyle_media):
            return 'lifestyle_media'
        
        # Business Media
        business_media = ['businessinsider.com', 'forbes.com', 'inc.com', 'fastcompany.com',
                         'bloomberg.com', 'cnbc.com']
        if any(d in domain for d in business_media):
            return 'business_media'
        
        # Authority
        authority = ['consumerreports.org', 'wirecutter.com', 'thewirecutter.com']
        if any(d in domain for d in authority):
            return 'authority'
        
        # Brand Official
        if 'honeybaked.com' in domain:
            return 'brand_official'
        
        # Retail
        retail = ['amazon.com', 'walmart.com', 'target.com', 'costco.com', 'kroger.com']
        if any(d in domain for d in retail):
            return 'retail'
        
        return 'other'
    
    def _classify_content_type(self, url: str) -> str:
        """Classify content type based on URL"""
        url_lower = url.lower()
        
        if any(word in url_lower for word in ['best', 'top', 'roundup', 'comparison', 'vs']):
            return 'buying_guide'
        elif any(word in url_lower for word in ['review', 'tested', 'rating']):
            return 'product_review'
        elif any(word in url_lower for word in ['news', 'article', 'report']):
            return 'news_article'
        elif any(word in url_lower for word in ['recipe', 'how-to', 'guide', 'tutorial']):
            return 'how_to'
        elif any(word in url_lower for word in ['about', 'company', 'product']):
            return 'company_page'
        elif any(word in url_lower for word in ['opinion', 'editorial', 'commentary']):
            return 'opinion'
        else:
            return 'other'
    
    def _determine_prominence(self, text: str, brand_mentioned: bool) -> str:
        """Determine how prominently the brand was mentioned"""
        if not brand_mentioned:
            return "Not Present"
        
        if not text:
            return "Not Present"
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        
        # Check first few sentences for brand
        first_sentences = sentences[:3]
        for sentence in first_sentences:
            if self._check_brand_mention(sentence):
                # Check if it's a primary recommendation
                if any(word in sentence.lower() for word in ['recommend', 'best', 'top', 'leading', 'premier']):
                    return "Featured First"
                else:
                    return "Listed Among Options"
        
        # Brand mentioned but not in first sentences
        return "Mentioned in Passing"
    
    def _track_competitors(
        self,
        response_text: str,
        citations: List[Dict],
        query: str,
        query_type: str,
        platform: str
    ) -> List[Dict]:
        """Track competitor mentions and compare to HoneyBaked"""
        competitor_rows = []
        
        honeybaked_in_response = self._check_brand_mention(response_text)
        honeybaked_in_citations = any(
            self._check_url_for_brand(c.get('url', '')) for c in citations
        )
        
        for competitor in self.competitors:
            # Check if competitor mentioned in response
            comp_in_response = competitor.lower() in response_text.lower() if response_text else False
            
            # Check if competitor in citations
            comp_in_citations = False
            for citation in citations:
                url = citation.get('url', '').lower()
                if competitor.lower().replace(' ', '') in url.replace(' ', ''):
                    comp_in_citations = True
                    break
            
            # Only add row if competitor was mentioned
            if comp_in_response or comp_in_citations:
                # Determine prominence vs HoneyBaked
                prominence = self._compare_prominence(
                    response_text,
                    competitor,
                    honeybaked_in_response
                )
                
                competitor_rows.append({
                    'query': query,
                    'query_type': query_type,
                    'engine': platform,
                    'competitor_mentioned': competitor,
                    'mentioned_in_response': "Yes" if comp_in_response else "No",
                    'mentioned_in_citations': "Yes" if comp_in_citations else "No",
                    'prominence_vs_honeybaked': prominence
                })
        
        # Always add HoneyBaked row for context
        honeybaked_prominence = "Not Present"
        if honeybaked_in_response:
            honeybaked_prominence = self._determine_prominence(response_text, True)
        
        competitor_rows.append({
            'query': query,
            'query_type': query_type,
            'engine': platform,
            'competitor_mentioned': 'HoneyBaked',
            'mentioned_in_response': "Yes" if honeybaked_in_response else "No",
            'mentioned_in_citations': "Yes" if honeybaked_in_citations else "No",
            'prominence_vs_honeybaked': honeybaked_prominence
        })
        
        return competitor_rows
    
    def _compare_prominence(
        self,
        text: str,
        competitor: str,
        honeybaked_present: bool
    ) -> str:
        """Compare competitor prominence to HoneyBaked"""
        if not text:
            return "Both Absent"
        
        # Find positions in text
        comp_pos = text.lower().find(competitor.lower())
        hb_positions = [text.lower().find(v.lower()) for v in self.brand_variants]
        hb_pos = min([p for p in hb_positions if p != -1], default=-1)
        
        comp_present = comp_pos != -1
        hb_present = hb_pos != -1
        
        if not comp_present and not hb_present:
            return "Both Absent"
        elif comp_present and not hb_present:
            return "Present, HoneyBaked Absent"
        elif not comp_present and hb_present:
            return "HoneyBaked Present, Competitor Absent"
        else:
            # Both present - check order
            if comp_pos < hb_pos:
                return "Higher - Featured First"
            elif comp_pos > hb_pos:
                return "Lower - Mentioned After"
            else:
                return "Equal - Listed Together"
    
    def _generate_csv_files(self, timestamp: str) -> Dict[str, str]:
        """Generate all three CSV files"""
        output_dir = "case_studies/honeybaked_ham/v2_audit"
        os.makedirs(output_dir, exist_ok=True)
        
        files = {}
        
        # 1. QUERY_RESPONSE_MATRIX.csv
        matrix_path = f"{output_dir}/HONEYBAKED_QUERY_RESPONSE_MATRIX_{timestamp}.csv"
        with open(matrix_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query', 'query_type', 'engine', 'brand_mentioned_in_response',
                'total_citations', 'citations_mentioning_brand', 
                'response_prominence', 'chef_tim_mentioned'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.query_response_data)
        files['query_matrix'] = matrix_path
        logger.info(f"Generated: {matrix_path}")
        
        # 2. CITATION_DETAILS.csv
        details_path = f"{output_dir}/HONEYBAKED_CITATION_DETAILS_{timestamp}.csv"
        with open(details_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'engine', 'query', 'query_type', 'citation_url', 'domain',
                'domain_classification', 'honeybaked_mentioned_in_source', 'content_type'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.citation_details_data)
        files['citation_details'] = details_path
        logger.info(f"Generated: {details_path}")
        
        # 3. COMPETITIVE_MENTIONS.csv
        competitive_path = f"{output_dir}/HONEYBAKED_COMPETITIVE_MENTIONS_{timestamp}.csv"
        with open(competitive_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query', 'query_type', 'engine', 'competitor_mentioned',
                'mentioned_in_response', 'mentioned_in_citations', 'prominence_vs_honeybaked'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.competitive_mentions_data)
        files['competitive_mentions'] = competitive_path
        logger.info(f"Generated: {competitive_path}")
        
        # 4. Generate summary JSON
        summary_path = f"{output_dir}/HONEYBAKED_AUDIT_SUMMARY_{timestamp}.json"
        summary = self._generate_summary()
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        files['summary'] = summary_path
        logger.info(f"Generated: {summary_path}")
        
        return files
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary statistics"""
        total_queries = len(self.query_response_data)
        
        # Brand mention statistics
        brand_mentions = sum(1 for row in self.query_response_data 
                           if row['brand_mentioned_in_response'] == 'Yes')
        brand_mention_rate = (brand_mentions / total_queries * 100) if total_queries > 0 else 0
        
        # Citation statistics
        total_citations = sum(row['total_citations'] for row in self.query_response_data)
        citations_with_brand = sum(row['citations_mentioning_brand'] 
                                  for row in self.query_response_data)
        citation_authority_score = (citations_with_brand / total_citations * 100) if total_citations > 0 else 0
        
        # By query type
        branded_queries = [r for r in self.query_response_data if r['query_type'] == 'branded']
        agnostic_queries = [r for r in self.query_response_data if r['query_type'] == 'brand_agnostic']
        
        branded_mentions = sum(1 for r in branded_queries if r['brand_mentioned_in_response'] == 'Yes')
        agnostic_mentions = sum(1 for r in agnostic_queries if r['brand_mentioned_in_response'] == 'Yes')
        
        # By platform
        platform_stats = {}
        for platform in ['chatgpt', 'claude', 'perplexity', 'gemini']:
            platform_queries = [r for r in self.query_response_data if r['engine'] == platform]
            platform_mentions = sum(1 for r in platform_queries if r['brand_mentioned_in_response'] == 'Yes')
            platform_stats[platform] = {
                'total_queries': len(platform_queries),
                'brand_mentions': platform_mentions,
                'mention_rate': (platform_mentions / len(platform_queries) * 100) if len(platform_queries) > 0 else 0
            }
        
        return {
            'audit_date': datetime.now().isoformat(),
            'total_queries_tested': total_queries,
            'total_platforms': len(self.platforms),
            'total_tests_conducted': len(self.queries) * len(self.platforms),
            'overall_metrics': {
                'brand_mention_rate': round(brand_mention_rate, 2),
                'total_brand_mentions': brand_mentions,
                'total_citations': total_citations,
                'citations_with_brand': citations_with_brand,
                'citation_authority_score': round(citation_authority_score, 2)
            },
            'by_query_type': {
                'branded': {
                    'total': len(branded_queries),
                    'mentions': branded_mentions,
                    'rate': round((branded_mentions / len(branded_queries) * 100) if len(branded_queries) > 0 else 0, 2)
                },
                'brand_agnostic': {
                    'total': len(agnostic_queries),
                    'mentions': agnostic_mentions,
                    'rate': round((agnostic_mentions / len(agnostic_queries) * 100) if len(agnostic_queries) > 0 else 0, 2)
                }
            },
            'by_platform': platform_stats,
            'competitive_landscape': {
                'total_competitor_mentions': len([r for r in self.competitive_mentions_data if r['competitor_mentioned'] != 'HoneyBaked']),
                'unique_competitors_found': len(set(r['competitor_mentioned'] for r in self.competitive_mentions_data if r['competitor_mentioned'] != 'HoneyBaked'))
            }
        }


def main():
    """Main execution function"""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Verify API keys
        required_keys = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'PERPLEXITY_API_KEY', 'GOOGLE_API_KEY']
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        
        if missing_keys:
            logger.error(f"Missing required API keys: {', '.join(missing_keys)}")
            logger.error("Please set these in your .env file")
            sys.exit(1)
        
        # Create auditor and run
        auditor = HoneyBakedAuditor()
        output_files = auditor.run_audit()
        
        logger.info("\n" + "="*80)
        logger.info("HoneyBaked Ham V2 Audit Complete!")
        logger.info("="*80)
        logger.info("\nGenerated Files:")
        for file_type, file_path in output_files.items():
            logger.info(f"  {file_type}: {file_path}")
        
        return output_files
        
    except KeyboardInterrupt:
        logger.info("\n\nAudit interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
