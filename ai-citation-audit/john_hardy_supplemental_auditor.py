#!/usr/bin/env python3
"""
John Hardy Supplemental AEO Citation Analysis
Social Media & Trade Publications Focus

15 Supplemental Queries:
- 10 Social Media queries (Reddit, TikTok, Instagram, YouTube)
- 5 Trade/Industry queries (WWD, BOF, JCK)

Purpose: Supplement existing 25-query baseline with social/trade citation patterns
"""

import os
import sys
import json
import csv
import logging
import requests
import time
import re
import random
from datetime import datetime
from typing import List, Dict, Any, Set, Optional
from urllib.parse import urlparse
from collections import defaultdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GeminiKeyManager:
    """Manages multiple Gemini API keys with load balancing"""
    
    def __init__(self, api_keys: List[str]):
        self.api_keys = [k for k in api_keys if k]
        self.current_key_index = 0
        self.key_success_counts = {key: 0 for key in self.api_keys}
        self.key_failure_counts = {key: 0 for key in self.api_keys}
        logger.info(f"GeminiKeyManager initialized with {len(self.api_keys)} API keys")
    
    def get_next_key(self) -> str:
        available_keys = [k for k in self.api_keys if self.key_failure_counts[k] < 5]
        if not available_keys:
            self.key_failure_counts = {key: 0 for key in self.api_keys}
            available_keys = self.api_keys
        
        key = available_keys[self.current_key_index % len(available_keys)]
        self.current_key_index += 1
        return key
    
    def mark_success(self, key: str):
        self.key_success_counts[key] += 1
        if self.key_failure_counts[key] > 0:
            self.key_failure_counts[key] -= 1
    
    def mark_failure(self, key: str):
        self.key_failure_counts[key] += 1


class JohnHardySupplementalAuditor:
    """
    Supplemental auditor focusing on social media and trade publications
    """
    
    def __init__(self, gemini_keys: List[str]):
        self.gemini_key_manager = GeminiKeyManager(gemini_keys)
        
        # Brand tracking
        self.brand_name = "John Hardy"
        self.brand_variants = [
            "John Hardy", "john hardy", "johnhardy", "john-hardy",
            "johnhardy.com"
        ]
        
        # Competitor tracking
        self.competitors = {
            "Brilliant Earth": ["brilliant earth", "brilliantearth"],
            "Vrai": ["vrai", "vrai.com"],
            "Mejuri": ["mejuri"],
            "Aurate": ["aurate"],
            "Tiffany & Co": ["tiffany", "tiffany & co", "tiffany and co"],
            "Cartier": ["cartier"],
            "David Yurman": ["david yurman"],
            "Pandora": ["pandora"],
            "Lagos": ["lagos"],
            "Chopard": ["chopard"],
            "Bario Neal": ["bario neal"],
            "Catbird": ["catbird"]
        }
        
        # Define supplemental queries
        self.queries = self._define_supplemental_queries()
        
        # Storage
        self.analysis_matrix_data = []
        self.citation_details_data = []
        self.competitive_context_data = []
        self.media_influence_data = defaultdict(lambda: {
            'citation_count': 0,
            'john_hardy_citations': 0,
            'competitor_citations': 0,
            'queries': set(),
            'engines': set()
        })
        
        # Gemini tracking
        self.gemini_attempts = 0
        self.gemini_successes = 0
        
        logger.info("John Hardy Supplemental Auditor initialized - Social Media & Trade Focus")
    
    def _define_supplemental_queries(self) -> List[Dict[str, Any]]:
        """Define 15 supplemental queries for social/trade analysis"""
        queries = []
        
        # SOCIAL MEDIA - REDDIT (4 queries)
        reddit = [
            ("What jewelry brands does Reddit recommend for sustainability?", "research"),
            ("Reddit recommendations for ethical engagement rings", "research"),
            ("Best luxury jewelry brands according to Reddit users", "discovery"),
            ("What do people on Reddit say about lab-grown diamonds?", "research")
        ]
        for text, intent in reddit:
            queries.append({
                "text": text,
                "type": "social_media",
                "category": "social_reddit",
                "commercial_intent": intent
            })
        
        # SOCIAL MEDIA - TIKTOK/INSTAGRAM (3 queries)
        tiktok_instagram = [
            ("Viral jewelry trends on TikTok 2025", "discovery"),
            ("Most popular jewelry influencers on Instagram", "research"),
            ("TikTok recommendations for affordable luxury jewelry", "discovery")
        ]
        for text, intent in tiktok_instagram:
            queries.append({
                "text": text,
                "type": "social_media",
                "category": "social_tiktok_instagram",
                "commercial_intent": intent
            })
        
        # SOCIAL MEDIA - GENERAL (3 queries)
        social_general = [
            ("What are people saying on social media about sustainable jewelry?", "research"),
            ("Customer reviews and experiences with John Hardy on social media", "research"),
            ("Most talked about jewelry brands on social media", "discovery")
        ]
        for text, intent in social_general:
            queries.append({
                "text": text,
                "type": "social_media",
                "category": "social_general",
                "commercial_intent": intent
            })
        
        # TRADE PUBLICATIONS - DIRECT (2 queries)
        trade_direct = [
            ("Women's Wear Daily jewelry industry coverage", "research"),
            ("Business of Fashion luxury jewelry trends", "research")
        ]
        for text, intent in trade_direct:
            queries.append({
                "text": text,
                "type": "trade_publication",
                "category": "trade_direct",
                "commercial_intent": intent
            })
        
        # TRADE PUBLICATIONS - INDUSTRY (3 queries)
        industry = [
            ("Jewelry industry market analysis and trends 2025", "research"),
            ("Fashion industry coverage of sustainable jewelry brands", "research"),
            ("Jewelry designer profiles and interviews in fashion media", "research")
        ]
        for text, intent in industry:
            queries.append({
                "text": text,
                "type": "trade_publication",
                "category": "trade_industry",
                "commercial_intent": intent
            })
        
        return queries
    
    def run_audit(self) -> Dict[str, str]:
        """Execute supplemental citation audit"""
        logger.info(f"\n{'='*80}")
        logger.info("JOHN HARDY SUPPLEMENTAL AEO CITATION ANALYSIS")
        logger.info("Social Media & Trade Publications Focus")
        logger.info(f"{'='*80}")
        logger.info(f"Total Queries: {len(self.queries)}")
        logger.info(f"Platforms: 4 (ChatGPT, Claude, Perplexity, Gemini)")
        logger.info(f"Total Tests: {len(self.queries) * 4}")
        logger.info(f"FOCUS: Social media accessibility + Trade publication coverage")
        logger.info(f"{'='*80}\n")
        
        # Execute all queries
        self._execute_queries()
        
        # Generate output files
        logger.info("\nGenerating Supplemental Output Files...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_files = self._generate_output_files(timestamp)
        
        # Validate
        citation_count = len(self.citation_details_data)
        social_citations = len([c for c in self.citation_details_data if 'social' in c.get('domain_classification', '').lower()])
        trade_citations = len([c for c in self.citation_details_data if 'trade' in c.get('domain_classification', '').lower()])
        
        logger.info(f"\n{'='*80}")
        logger.info(f"SUPPLEMENTAL CITATION CAPTURE: {citation_count} URLs")
        logger.info(f"Social Media Citations: {social_citations}")
        logger.info(f"Trade Publication Citations: {trade_citations}")
        logger.info(f"MEDIA OUTLETS TRACKED: {len(self.media_influence_data)}")
        logger.info(f"{'='*80}\n")
        
        return output_files
    
    def _execute_queries(self):
        """Execute all supplemental queries"""
        total = len(self.queries) * 4
        completed = 0
        
        for query_info in self.queries:
            query_text = query_info["text"]
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Query: {query_text}")
            logger.info(f"Category: {query_info['category']}")
            logger.info(f"{'='*60}")
            
            for platform in ['ChatGPT', 'Claude', 'Perplexity', 'Gemini']:
                completed += 1
                logger.info(f"[{completed}/{total}] {platform}...")
                
                try:
                    result = self._query_platform(platform, query_text)
                    
                    if result:
                        self._analyze_response(result, query_info, platform)
                        logger.info(f"  ✓ Citations: {len(result.get('citations', []))}")
                    
                    time.sleep(random.uniform(2, 4))
                    
                except Exception as e:
                    logger.error(f"Error: {e}")
                    continue
    
    def _query_platform(self, platform: str, query: str) -> Optional[Dict]:
        """Query platform with citation-focused prompting"""
        if platform == 'ChatGPT':
            return self._query_chatgpt(query)
        elif platform == 'Claude':
            return self._query_claude(query)
        elif platform == 'Perplexity':
            return self._query_perplexity(query)
        elif platform == 'Gemini':
            return self._query_gemini(query)
        return None
    
    def _query_chatgpt(self, query: str) -> Optional[Dict]:
        """ChatGPT with explicit citation request"""
        try:
            api_key = os.getenv('OPENAI_API_KEY')
            system_prompt = "You are a helpful assistant. Please provide detailed citations with URLs for all information sources. List all sources with URLs at the end of your response."
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"{query} Please provide sources with URLs."}
                    ],
                    "max_tokens": 1500,
                    "temperature": 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                text = response.json()['choices'][0]['message']['content']
                citations = self._extract_urls_from_text(text)
                return {
                    'response_text': text,
                    'citations': citations,
                    'platform': 'ChatGPT'
                }
        except Exception as e:
            logger.error(f"ChatGPT error: {e}")
        return None
    
    def _query_claude(self, query: str) -> Optional[Dict]:
        """Claude with native citations"""
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
                    "messages": [{"role": "user", "content": f"{query} Please include sources and citations."}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                text = ""
                for block in data.get('content', []):
                    if block.get('type') == 'text':
                        text += block.get('text', '')
                
                citations = self._extract_urls_from_text(text)
                return {
                    'response_text': text,
                    'citations': citations,
                    'platform': 'Claude'
                }
        except Exception as e:
            logger.error(f"Claude error: {e}")
        return None
    
    def _query_perplexity(self, query: str) -> Optional[Dict]:
        """Perplexity with automatic citations"""
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
                text = data['choices'][0]['message']['content']
                
                citations_data = data.get('citations', [])
                if not citations_data:
                    citations_data = self._extract_urls_from_text(text)
                else:
                    citations_data = [{'url': c} for c in citations_data]
                
                return {
                    'response_text': text,
                    'citations': citations_data,
                    'platform': 'Perplexity'
                }
        except Exception as e:
            logger.error(f"Perplexity error: {e}")
        return None
    
    def _query_gemini(self, query: str) -> Optional[Dict]:
        """Gemini with multi-key support"""
        self.gemini_attempts += 1
        
        for attempt in range(len(self.gemini_key_manager.api_keys)):
            key = self.gemini_key_manager.get_next_key()
            
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={key}"
                
                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": f"{query} Please provide sources and links."}]}],
                        "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096}
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if 'candidates' in data:
                        text = data['candidates'][0]['content']['parts'][0]['text']
                        self.gemini_key_manager.mark_success(key)
                        self.gemini_successes += 1
                        
                        citations = self._extract_urls_from_text(text)
                        
                        return {
                            'response_text': text,
                            'citations': citations,
                            'platform': 'Gemini'
                        }
            except Exception as e:
                self.gemini_key_manager.mark_failure(key)
                time.sleep(2)
                continue
        
        return None
    
    def _extract_urls_from_text(self, text: str) -> List[Dict]:
        """Extract all URLs from text"""
        if not text:
            return []
        
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, text)
        
        citations = []
        for i, url in enumerate(urls, 1):
            url = url.rstrip('.,;:)]}')
            citations.append({
                'url': url,
                'position': i
            })
        
        return citations
    
    def _analyze_response(self, result: Dict, query_info: Dict, platform: str):
        """Analyze response and store data"""
        response_text = result['response_text']
        citations = result['citations']
        
        brands_mentioned = self._check_brand_mentions(response_text)
        featured_brand = self._determine_featured_brand(response_text, brands_mentioned)
        
        matrix_row = {
            'query': query_info['text'],
            'query_type': query_info['type'],
            'category': query_info['category'],
            'commercial_intent': query_info['commercial_intent'],
            'engine': platform,
            'john_hardy_mentioned': "Yes" if "John Hardy" in brands_mentioned else "No",
            'competitors_mentioned': ", ".join([b for b in brands_mentioned if b != "John Hardy"]),
            'featured_brand': featured_brand,
            'john_hardy_prominence': self._get_prominence(response_text, "John Hardy", featured_brand),
            'total_citations': len(citations),
            'john_hardy_citations': 0,
            'competitor_citations': 0
        }
        
        for citation in citations:
            url = citation['url']
            domain = self._extract_domain(url)
            brands_in_url = self._check_brands_in_url(url)
            
            domain_class = self._classify_domain_supplemental(domain, url)
            
            if "John Hardy" in brands_in_url:
                matrix_row['john_hardy_citations'] += 1
            elif any(b in brands_in_url for b in self.competitors.keys()):
                matrix_row['competitor_citations'] += 1
            
            self.citation_details_data.append({
                'engine': platform,
                'query': query_info['text'],
                'category': query_info['category'],
                'citation_url': url,
                'domain': domain,
                'domain_classification': domain_class,
                'john_hardy_mentioned': "Yes" if "John Hardy" in brands_in_url else "No",
                'competitor_mentioned': ", ".join([b for b in brands_in_url if b != "John Hardy"]) or "None",
                'citation_position': citation.get('position', 0)
            })
            
            if domain:
                self.media_influence_data[domain]['citation_count'] += 1
                self.media_influence_data[domain]['queries'].add(query_info['text'])
                self.media_influence_data[domain]['engines'].add(platform)
                
                if "John Hardy" in brands_in_url:
                    self.media_influence_data[domain]['john_hardy_citations'] += 1
                if any(b in brands_in_url for b in self.competitors.keys()):
                    self.media_influence_data[domain]['competitor_citations'] += 1
        
        self.analysis_matrix_data.append(matrix_row)
        
        for brand_name in ["John Hardy"] + list(self.competitors.keys()):
            brand_citations = len([c for c in citations if brand_name in self._check_brands_in_url(c['url'])])
            
            self.competitive_context_data.append({
                'brand': brand_name,
                'query': query_info['text'],
                'category': query_info['category'],
                'engine': platform,
                'mentioned_in_response': "Yes" if brand_name in brands_mentioned else "No",
                'total_citations': len(citations),
                'brand_specific_citations': brand_citations
            })
    
    def _classify_domain_supplemental(self, domain: str, url: str) -> str:
        """Classify with focus on social/trade sources"""
        if not domain:
            return "other"
        
        domain_lower = domain.lower()
        url_lower = url.lower()
        
        # Social Media
        if 'reddit.com' in domain_lower:
            return 'social_reddit'
        elif 'youtube.com' in domain_lower or 'youtu.be' in domain_lower:
            return 'social_youtube'
        elif 'tiktok.com' in domain_lower:
            return 'social_tiktok'
        elif 'instagram.com' in domain_lower:
            return 'social_instagram'
        elif any(s in domain_lower for s in ['twitter.com', 'x.com']):
            return 'social_twitter'
        elif any(s in domain_lower for s in ['pinterest.com', 'facebook.com']):
            return 'social_other'
        
        # Trade Publications
        elif 'wwd.com' in domain_lower:
            return 'trade_fashion_wwd'
        elif 'businessoffashion.com' in domain_lower:
            return 'trade_fashion_bof'
        elif 'vogue.com' in domain_lower and ('business' in url_lower):
            return 'trade_fashion_vogue_business'
        elif 'jckonline.com' in domain_lower:
            return 'trade_jewelry_jck'
        elif 'nationaljeweler.com' in domain_lower:
            return 'trade_jewelry_national'
        elif 'rapaport.com' in domain_lower:
            return 'trade_jewelry_rapaport'
        
        # Standard classifications
        elif 'johnhardy.com' in domain_lower:
            return 'brand_official'
        elif any(c in domain_lower for c in ['brilliantearth', 'vrai.com', 'tiffany', 'cartier']):
            return 'competitor_official'
        elif any(m in domain_lower for m in ['vogue', 'elle', 'harpersbazaar']):
            return 'luxury_fashion_tier1'
        elif any(b in domain_lower for b in ['forbes', 'bloomberg', 'businessinsider']):
            return 'business_media'
        else:
            return 'other'
    
    def _check_brand_mentions(self, text: str) -> Set[str]:
        if not text:
            return set()
        
        text_lower = text.lower()
        brands = set()
        
        for variant in self.brand_variants:
            if variant.lower() in text_lower:
                brands.add("John Hardy")
                break
        
        for brand, variants in self.competitors.items():
            if any(v in text_lower for v in variants):
                brands.add(brand)
        
        return brands
    
    def _check_brands_in_url(self, url: str) -> Set[str]:
        if not url:
            return set()
        
        url_lower = url.lower()
        brands = set()
        
        if any(v in url_lower for v in ["john-hardy", "johnhardy", "john_hardy"]):
            brands.add("John Hardy")
        
        for brand, variants in self.competitors.items():
            if any(v.replace(' ', '-') in url_lower or v.replace(' ', '') in url_lower for v in variants):
                brands.add(brand)
        
        return brands
    
    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower().replace('www.', '')
        except:
            return ""
    
    def _determine_featured_brand(self, text: str, brands: Set[str]) -> str:
        if not brands:
            return "None"
        
        text_lower = text.lower()
        positions = {}
        
        if "John Hardy" in brands:
            for variant in self.brand_variants:
                pos = text_lower.find(variant.lower())
                if pos != -1:
                    positions["John Hardy"] = pos
                    break
        
        for brand in brands:
            if brand != "John Hardy":
                variants = self.competitors.get(brand, [brand.lower()])
                for variant in variants:
                    pos = text_lower.find(variant.lower())
                    if pos != -1:
                        positions[brand] = pos
                        break
        
        return min(positions.items(), key=lambda x: x[1])[0] if positions else "None"
    
    def _get_prominence(self, text: str, brand: str, featured: str) -> str:
        brands = self._check_brand_mentions(text)
        if brand not in brands:
            return "Not_Present"
        return "Featured_First" if brand == featured else "Mentioned_After"
    
    def _generate_output_files(self, timestamp: str) -> Dict[str, str]:
        """Generate supplemental output files"""
        output_dir = "case_studies/john_hardy_supplemental"
        os.makedirs(output_dir, exist_ok=True)
        
        files = {}
        
        # 1. Supplemental Analysis Matrix
        matrix_path = f"{output_dir}/JOHN_HARDY_SUPPLEMENTAL_MATRIX_{timestamp}.csv"
        with open(matrix_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query', 'query_type', 'category', 'commercial_intent', 'engine',
                'john_hardy_mentioned', 'competitors_mentioned', 'featured_brand',
                'john_hardy_prominence', 'total_citations', 'john_hardy_citations',
                'competitor_citations'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.analysis_matrix_data)
        files['matrix'] = matrix_path
        logger.info(f"✓ Generated: JOHN_HARDY_SUPPLEMENTAL_MATRIX_{timestamp}.csv")
        
        # 2. Supplemental Citation Details
        details_path = f"{output_dir}/JOHN_HARDY_SUPPLEMENTAL_CITATIONS_{timestamp}.csv"
        with open(details_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'engine', 'query', 'category', 'citation_url', 'domain',
                'domain_classification', 'john_hardy_mentioned',
                'competitor_mentioned', 'citation_position'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.citation_details_data)
        files['citations'] = details_path
        logger.info(f"✓ Generated: JOHN_HARDY_SUPPLEMENTAL_CITATIONS_{timestamp}.csv")
        logger.info(f"  📊 Supplemental citation count: {len(self.citation_details_data)}")
        
        # 3. Supplemental Media Influence
        media_path = f"{output_dir}/JOHN_HARDY_SUPPLEMENTAL_MEDIA_{timestamp}.csv"
        with open(media_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'media_outlet', 'citation_count', 'john_hardy_citations',
                'competitor_citations', 'top_queries', 'engines', 'domain_classification'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            media_rows = []
            for domain, data in self.media_influence_data.items():
                if data['citation_count'] > 0:
                    media_rows.append({
                        'media_outlet': domain,
                        'citation_count': data['citation_count'],
                        'john_hardy_citations': data['john_hardy_citations'],
                        'competitor_citations': data['competitor_citations'],
                        'top_queries': '; '.join(list(data['queries'])[:3]),
                        'engines': ', '.join(sorted(data['engines'])),
                        'domain_classification': self._classify_domain_supplemental(domain, '')
                    })
            
            media_rows.sort(key=lambda x: x['citation_count'], reverse=True)
            writer.writerows(media_rows)
        files['media'] = media_path
        logger.info(f"✓ Generated: JOHN_HARDY_SUPPLEMENTAL_MEDIA_{timestamp}.csv")
        
        # 4. Supplemental Summary Report
        report_path = f"{output_dir}/SUPPLEMENTAL_SUMMARY_{timestamp}.json"
        
        platform_citations = defaultdict(int)
        for citation in self.citation_details_data:
            platform_citations[citation['engine']] += 1
        
        social_citations = len([c for c in self.citation_details_data if 'social' in c['domain_classification']])
        trade_citations = len([c for c in self.citation_details_data if 'trade' in c['domain_classification']])
        reddit_citations = len([c for c in self.citation_details_data if c['domain_classification'] == 'social_reddit'])
        youtube_citations = len([c for c in self.citation_details_data if c['domain_classification'] == 'social_youtube'])
        
        report = {
            "analysis_date": datetime.now().isoformat(),
            "supplemental_focus": "Social Media & Trade Publications",
            "execution_summary": {
                "total_queries": 15,
                "queries_by_category": {
                    "social_reddit": 4,
                    "social_tiktok_instagram": 3,
                    "social_general": 3,
                    "trade_direct": 2,
                    "trade_industry": 3
                },
                "total_tests_attempted": len(self.queries) * 4,
                "successful_completions": len(self.analysis_matrix_data)
            },
            "citation_analysis": {
                "total_citations": len(self.citation_details_data),
                "citations_by_platform": dict(platform_citations),
                "social_media_citations": social_citations,
                "trade_publication_citations": trade_citations,
                "reddit_citations": reddit_citations,
                "youtube_citations": youtube_citations
            },
            "key_findings": {
                "social_media_accessible": social_citations > 0,
                "trade_publications_accessible": trade_citations > 0,
                "reddit_citation_rate": round(reddit_citations / max(len(self.citation_details_data), 1) * 100, 2),
                "social_vs_trade_ratio": round(social_citations / max(trade_citations, 1), 2) if trade_citations > 0 else 0
            }
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        files['report'] = report_path
        logger.info(f"✓ Generated: SUPPLEMENTAL_SUMMARY_{timestamp}.json")
        
        return files


def main():
    """Main execution"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Get Gemini keys
        gemini_keys = [
            os.getenv('GOOGLE_API_KEY'),
            "AIzaSyAjyRcAwv1zEv0GvgVE18Aelqo_f5E-23A",
            "AIzaSyDvHaUxZrE7xvvvUuqsDUkKUGzWf-nGxa8"
        ]
        
        # Verify all keys
        required = ['OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'PERPLEXITY_API_KEY']
        missing = [k for k in required if not os.getenv(k)]
        if missing:
            logger.error(f"Missing keys: {', '.join(missing)}")
            sys.exit(1)
        
        # Create supplemental auditor
        auditor = JohnHardySupplementalAuditor(gemini_keys)
        
        # Run supplemental audit
        output_files = auditor.run_audit()
        
        logger.info("\n✓ John Hardy Supplemental Citation Analysis Complete!")
        logger.info("\nGenerated Files:")
        for file_type, file_path in output_files.items():
            logger.info(f"  • {file_path}")
        
        return output_files
        
    except KeyboardInterrupt:
        logger.info("\nSupplemental audit interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
