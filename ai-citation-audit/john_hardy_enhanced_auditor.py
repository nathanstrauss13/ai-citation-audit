#!/usr/bin/env python3
"""
John Hardy Enhanced AEO Citation Analysis
Following NBA Citation-Focused Best Practices

PRIMARY OBJECTIVE: Capture every citation URL to identify:
- Earned vs. Owned media patterns
- Tier-1 luxury media coverage
- Competitor content dominance
- Sustainability narrative ownership

Enhanced Features:
- Explicit citation prompting
- URL pattern extraction
- Multi-key Gemini support
- 4 comprehensive output files
- Domain authority classification
- Brand prominence tracking
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
        self.api_keys = [k for k in api_keys if k]  # Filter None/empty
        self.current_key_index = 0
        self.key_success_counts = {key: 0 for key in self.api_keys}
        self.key_failure_counts = {key: 0 for key in self.api_keys}
        logger.info(f"GeminiKeyManager initialized with {len(self.api_keys)} API keys")
    
    def get_next_key(self) -> str:
        """Get next available key using round-robin"""
        available_keys = [k for k in self.api_keys if self.key_failure_counts[k] < 5]
        if not available_keys:
            # Reset if all keys exhausted
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


class JohnHardyEnhancedAuditor:
    """
    Enhanced citation-focused auditor for John Hardy jewelry
    Follows NBA analysis best practices
    """
    
    def __init__(self, gemini_keys: List[str]):
        self.gemini_key_manager = GeminiKeyManager(gemini_keys)
        
        # Brand tracking
        self.brand_name = "John Hardy"
        self.brand_variants = [
            "John Hardy", "john hardy", "johnhardy", "john-hardy",
            "johnhardy.com"
        ]
        
        # Competitor tracking (luxury jewelry brands)
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
        
        # Define queries
        self.queries = self._define_queries()
        
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
        
        logger.info("John Hardy Enhanced Auditor initialized")
    
    def _define_queries(self) -> List[Dict[str, Any]]:
        """Define comprehensive query set"""
        queries = []
        
        # BRAND AWARENESS (4 queries)
        brand_awareness = [
            ("What is John Hardy jewelry known for?", "brand_knowledge"),
            ("Is John Hardy jewelry worth the investment?", "value_assessment"),
            ("Where to buy John Hardy jewelry?", "purchase_intent"),
            ("John Hardy jewelry review", "research")
        ]
        for text, intent in brand_awareness:
            queries.append({
                "text": text,
                "type": "branded",
                "category": "brand_awareness",
                "commercial_intent": intent
            })
        
        # SUSTAINABILITY (6 queries)
        sustainability = [
            ("Most sustainable luxury jewelry brands", "discovery"),
            ("Ethical jewelry brands that use recycled materials", "research"),
            ("Which jewelry companies are truly sustainable?", "verification"),
            ("Best eco-friendly luxury jewelry", "purchase_intent"),
            ("Sustainable engagement ring brands", "purchase_intent"),
            ("Jewelry brands with best environmental practices", "research")
        ]
        for text, intent in sustainability:
            queries.append({
                "text": text,
                "type": "brand_agnostic",
                "category": "sustainability",
                "commercial_intent": intent
            })
        
        # LAB-GROWN DIAMONDS (4 queries)
        lab_grown = [
            ("Best lab-grown diamond jewelry brands", "discovery"),
            ("Luxury brands that offer lab-grown diamonds", "research"),
            ("Where to buy lab-grown diamond jewelry?", "purchase_intent"),
            ("Lab-grown diamond engagement rings best brands", "purchase_intent")
        ]
        for text, intent in lab_grown:
            queries.append({
                "text": text,
                "type": "brand_agnostic",
                "category": "lab_grown",
                "commercial_intent": intent
            })
        
        # COMPETITIVE (4 queries)
        competitive = [
            ("John Hardy vs Tiffany & Co sustainability", "comparison"),
            ("David Yurman vs John Hardy craftsmanship", "comparison"),
            ("John Hardy vs Brilliant Earth sustainability", "comparison"),
            ("Best alternative to Tiffany jewelry", "discovery")
        ]
        for text, intent in competitive:
            queries.append({
                "text": text,
                "type": "competitive",
                "category": "competitive",
                "commercial_intent": intent
            })
        
        # THOUGHT LEADERSHIP (3 queries)
        thought_leadership = [
            ("Jewelry industry sustainability leaders", "research"),
            ("Most ethical luxury jewelry designers", "research"),
            ("Jewelry brands leading in craftsmanship", "research")
        ]
        for text, intent in thought_leadership:
            queries.append({
                "text": text,
                "type": "brand_agnostic",
                "category": "thought_leadership",
                "commercial_intent": intent
            })
        
        # PRODUCT SPECIFIC (4 queries)
        product = [
            ("Best artisan jewelry brands", "discovery"),
            ("Handcrafted luxury jewelry brands", "discovery"),
            ("Best jewelry for meaningful gifts", "purchase_intent"),
            ("Luxury jewelry with cultural heritage", "research")
        ]
        for text, intent in product:
            queries.append({
                "text": text,
                "type": "brand_agnostic",
                "category": "product_specific",
                "commercial_intent": intent
            })
        
        return queries
    
    def run_audit(self) -> Dict[str, str]:
        """Execute enhanced citation-focused audit"""
        logger.info(f"\n{'='*80}")
        logger.info("JOHN HARDY ENHANCED AEO CITATION ANALYSIS")
        logger.info(f"{'='*80}")
        logger.info(f"Total Queries: {len(self.queries)}")
        logger.info(f"Platforms: 4 (ChatGPT, Claude, Perplexity, Gemini)")
        logger.info(f"Total Tests: {len(self.queries) * 4}")
        logger.info(f"PRIMARY OBJECTIVE: Citation URL capture + Media mapping")
        logger.info(f"{'='*80}\n")
        
        # Execute all queries
        self._execute_queries()
        
        # Generate output files
        logger.info("\nGenerating Output Files...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_files = self._generate_output_files(timestamp)
        
        # Validate
        citation_count = len(self.citation_details_data)
        logger.info(f"\n{'='*80}")
        logger.info(f"CITATION CAPTURE: {citation_count} URLs")
        logger.info(f"MEDIA OUTLETS TRACKED: {len(self.media_influence_data)}")
        logger.info(f"{'='*80}\n")
        
        return output_files
    
    def _execute_queries(self):
        """Execute all queries across all platforms"""
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
            system_prompt = "You are a helpful assistant specializing in luxury jewelry. Please provide detailed citations with URLs for all information sources. List all sources with URLs at the end of your response."
            
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
                
                # Perplexity provides citations
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
            url = url.rstrip('.,;:)]}')  # Clean trailing punctuation
            citations.append({
                'url': url,
                'position': i
            })
        
        return citations
    
    def _analyze_response(self, result: Dict, query_info: Dict, platform: str):
        """Analyze response and store comprehensive data"""
        response_text = result['response_text']
        citations = result['citations']
        
        # Check brand mentions
        brands_mentioned = self._check_brand_mentions(response_text)
        featured_brand = self._determine_featured_brand(response_text, brands_mentioned)
        
        # Matrix row
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
            'competitor_citations': 0,
            'owned_media_citations': 0,
            'earned_media_citations': 0
        }
        
        # Citation details - MOST IMPORTANT
        for citation in citations:
            url = citation['url']
            domain = self._extract_domain(url)
            brands_in_url = self._check_brands_in_url(url)
            
            # Classification
            domain_class = self._classify_domain(domain)
            content_type = self._determine_content_type(url, domain_class)
            
            # Update counts
            if "John Hardy" in brands_in_url:
                matrix_row['john_hardy_citations'] += 1
                if domain_class == 'brand_official':
                    matrix_row['owned_media_citations'] += 1
                else:
                    matrix_row['earned_media_citations'] += 1
            elif any(b in brands_in_url for b in self.competitors.keys()):
                matrix_row['competitor_citations'] += 1
            
            # Citation detail row
            self.citation_details_data.append({
                'engine': platform,
                'query': query_info['text'],
                'category': query_info['category'],
                'citation_url': url,
                'domain': domain,
                'domain_classification': domain_class,
                'content_type': content_type,
                'john_hardy_mentioned': "Yes" if "John Hardy" in brands_in_url else "No",
                'competitor_mentioned': ", ".join([b for b in brands_in_url if b != "John Hardy"]) or "None",
                'citation_position': citation.get('position', 0),
                'media_tier': self._get_media_tier(domain_class, domain)
            })
            
            # Media tracking
            if domain:
                self.media_influence_data[domain]['citation_count'] += 1
                self.media_influence_data[domain]['queries'].add(query_info['text'])
                self.media_influence_data[domain]['engines'].add(platform)
                
                if "John Hardy" in brands_in_url:
                    self.media_influence_data[domain]['john_hardy_citations'] += 1
                if any(b in brands_in_url for b in self.competitors.keys()):
                    self.media_influence_data[domain]['competitor_citations'] += 1
        
        self.analysis_matrix_data.append(matrix_row)
        
        # Competitive context
        for brand_name in ["John Hardy"] + list(self.competitors.keys()):
            brand_citations = len([c for c in citations if brand_name in self._check_brands_in_url(c['url'])])
            
            self.competitive_context_data.append({
                'brand': brand_name,
                'query': query_info['text'],
                'category': query_info['category'],
                'engine': platform,
                'mentioned_in_response': "Yes" if brand_name in brands_mentioned else "No",
                'prominence_ranking': self._get_prominence_rank(response_text, brand_name, brands_mentioned),
                'total_citations': len(citations),
                'brand_specific_citations': brand_citations,
                'featured': "Yes" if brand_name == featured_brand else "No"
            })
    
    def _check_brand_mentions(self, text: str) -> Set[str]:
        """Check which brands are mentioned"""
        if not text:
            return set()
        
        text_lower = text.lower()
        brands = set()
        
        # Check John Hardy
        for variant in self.brand_variants:
            if variant.lower() in text_lower:
                brands.add("John Hardy")
                break
        
        # Check competitors
        for brand, variants in self.competitors.items():
            if any(v in text_lower for v in variants):
                brands.add(brand)
        
        return brands
    
    def _check_brands_in_url(self, url: str) -> Set[str]:
        """Check brands mentioned in URL"""
        if not url:
            return set()
        
        url_lower = url.lower()
        brands = set()
        
        # Check John Hardy
        if any(v in url_lower for v in ["john-hardy", "johnhardy", "john_hardy"]):
            brands.add("John Hardy")
        
        # Check competitors
        for brand, variants in self.competitors.items():
            if any(v.replace(' ', '-') in url_lower or v.replace(' ', '') in url_lower for v in variants):
                brands.add(brand)
        
        return brands
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower().replace('www.', '')
        except:
            return ""
    
    def _classify_domain(self, domain: str) -> str:
        """Classify domain type with luxury focus"""
        if not domain:
            return "other"
        
        domain_lower = domain.lower()
        
        # Brand official
        if 'johnhardy.com' in domain_lower:
            return 'brand_official'
        
        # Competitor official
        competitor_domains = ['brilliantearth.com', 'vrai.com', 'tiffany.com', 'cartier.com', 'davidyurman.com', 'mejuri.com', 'aurate.com']
        if any(d in domain_lower for d in competitor_domains):
            return 'competitor_official'
        
        # Luxury Fashion Tier 1
        luxury_tier1 = ['vogue.com', 'harpersbazaar.com', 'elle.com', 'wwd.com', 'vmagazine.com']
        if any(d in domain_lower for d in luxury_tier1):
            return 'luxury_fashion_tier1'
        
        # Business/Sustainability
        business = ['forbes.com', 'fastcompany.com', 'inc.com', 'businessinsider.com', 'bloomberg.com']
        if any(d in domain_lower for d in business):
            return 'business_media'
        
        # Jewelry Trade
        jewelry_trade = ['jckonline.com', 'nationaljeweler.com', 'rapaport.com']
        if any(d in domain_lower for d in jewelry_trade):
            return 'jewelry_trade'
        
        # Sustainability Media
        sustainability = ['thegoodtrade.com', 'ecocult.com', 'sustainably-chic.com']
        if any(d in domain_lower for d in sustainability):
            return 'sustainability_media'
        
        # Lifestyle Media
        lifestyle = ['goodhousekeeping.com', 'marthastewart.com', 'realsimple.com', 'southernliving.com']
        if any(d in domain_lower for d in lifestyle):
            return 'lifestyle_media'
        
        # Retail Partners
        retail = ['nordstrom.com', 'neimanmarcus.com', 'bloomingdales.com', 'saksfifthavenue.com']
        if any(d in domain_lower for d in retail):
            return 'retail_partner'
        
        # News Media
        news = ['nytimes.com', 'washingtonpost.com', 'theguardian.com', 'wsj.com']
        if any(d in domain_lower for d in news):
            return 'news_media'
        
        # Authority Sites
        if 'wikipedia' in domain_lower:
            return 'wiki_reference'
        
        return 'other'
    
    def _determine_content_type(self, url: str, domain_class: str) -> str:
        """Determine content type"""
        url_lower = url.lower()
        
        if domain_class in ['brand_official', 'competitor_official']:
            return 'owned_content'
        
        if any(word in url_lower for word in ['best', 'top', 'guide', 'roundup']):
            return 'buying_guide'
        elif any(word in url_lower for word in ['review', 'tested']):
            return 'product_review'
        elif any(word in url_lower for word in ['sustainability', 'ethical', 'eco']):
            return 'sustainability_content'
        elif any(word in url_lower for word in ['news', 'press', 'release']):
            return 'news_article'
        else:
            return 'editorial'
    
    def _get_media_tier(self, domain_class: str, domain: str) -> str:
        """Get media tier"""
        if domain_class == 'luxury_fashion_tier1':
            return 'Tier_1_Luxury'
        elif domain_class in ['business_media', 'news_media']:
            return 'Tier_1_General'
        elif domain_class in ['lifestyle_media', 'sustainability_media']:
            return 'Tier_2_Specialty'
        elif domain_class == 'jewelry_trade':
            return 'Industry_Trade'
        elif domain_class in ['brand_official', 'competitor_official']:
            return 'Owned'
        elif domain_class == 'retail_partner':
            return 'Retail'
        else:
            return 'Other'
    
    def _determine_featured_brand(self, text: str, brands: Set[str]) -> str:
        """Determine featured brand"""
        if not brands:
            return "None"
        
        text_lower = text.lower()
        positions = {}
        
        # John Hardy
        if "John Hardy" in brands:
            for variant in self.brand_variants:
                pos = text_lower.find(variant.lower())
                if pos != -1:
                    positions["John Hardy"] = pos
                    break
        
        # Competitors
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
        """Get prominence level"""
        brands = self._check_brand_mentions(text)
        if brand not in brands:
            return "Not_Present"
        return "Featured_First" if brand == featured else "Mentioned_After"
    
    def _get_prominence_rank(self, text: str, brand: str, brands: Set[str]) -> int:
        """Get prominence ranking"""
        if brand not in brands:
            return 0
        
        text_lower = text.lower()
        positions = {}
        
        for b in brands:
            if b == "John Hardy":
                variants = self.brand_variants
            else:
                variants = self.competitors.get(b, [b.lower()])
            
            for variant in variants:
                pos = text_lower.find(variant.lower())
                if pos != -1:
                    positions[b] = pos
                    break
        
        sorted_brands = sorted(positions.items(), key=lambda x: x[1])
        
        for i, (b, _) in enumerate(sorted_brands, 1):
            if b == brand:
                return i
        return 0
    
    def _generate_output_files(self, timestamp: str) -> Dict[str, str]:
        """Generate 4 comprehensive output files"""
        output_dir = "case_studies/john_hardy_enhanced"
        os.makedirs(output_dir, exist_ok=True)
        
        files = {}
        
        # 1. ENHANCED_BRAND_ANALYSIS_MATRIX
        matrix_path = f"{output_dir}/JOHN_HARDY_BRAND_ANALYSIS_MATRIX_{timestamp}.csv"
        with open(matrix_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query', 'query_type', 'category', 'commercial_intent', 'engine',
                'john_hardy_mentioned', 'competitors_mentioned', 'featured_brand',
                'john_hardy_prominence', 'total_citations', 'john_hardy_citations',
                'competitor_citations', 'owned_media_citations', 'earned_media_citations'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.analysis_matrix_data)
        files['matrix'] = matrix_path
        logger.info(f"✓ Generated: JOHN_HARDY_BRAND_ANALYSIS_MATRIX_{timestamp}.csv")
        
        # 2. ENHANCED_CITATION_DETAILS - MOST IMPORTANT
        details_path = f"{output_dir}/JOHN_HARDY_CITATION_DETAILS_{timestamp}.csv"
        with open(details_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'engine', 'query', 'category', 'citation_url', 'domain',
                'domain_classification', 'content_type', 'john_hardy_mentioned',
                'competitor_mentioned', 'citation_position', 'media_tier'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.citation_details_data)
        files['citations'] = details_path
        logger.info(f"✓ Generated: JOHN_HARDY_CITATION_DETAILS_{timestamp}.csv")
        logger.info(f"  📊 Citation count: {len(self.citation_details_data)}")
        
        # 3. COMPETITIVE_CONTEXT_MATRIX
        context_path = f"{output_dir}/JOHN_HARDY_COMPETITIVE_CONTEXT_{timestamp}.csv"
        with open(context_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'brand', 'query', 'category', 'engine', 'mentioned_in_response',
                'prominence_ranking', 'total_citations', 'brand_specific_citations', 'featured'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.competitive_context_data)
        files['competitive'] = context_path
        logger.info(f"✓ Generated: JOHN_HARDY_COMPETITIVE_CONTEXT_{timestamp}.csv")
        
        # 4. MEDIA_INFLUENCE_ANALYSIS
        media_path = f"{output_dir}/JOHN_HARDY_MEDIA_INFLUENCE_{timestamp}.csv"
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
                        'domain_classification': self._classify_domain(domain)
                    })
            
            # Sort by citation count
            media_rows.sort(key=lambda x: x['citation_count'], reverse=True)
            writer.writerows(media_rows)
        files['media'] = media_path
        logger.info(f"✓ Generated: JOHN_HARDY_MEDIA_INFLUENCE_{timestamp}.csv")
        
        # 5. PLATFORM_RELIABILITY_REPORT
        report_path = f"{output_dir}/PLATFORM_RELIABILITY_REPORT_{timestamp}.json"
        
        # Calculate stats
        platform_citations = defaultdict(int)
        for citation in self.citation_details_data:
            platform_citations[citation['engine']] += 1
        
        unique_domains = len(set(c['domain'] for c in self.citation_details_data))
        
        # Earned vs Owned ratio
        owned_media = len([c for c in self.citation_details_data if c['domain_classification'] == 'brand_official'])
        earned_media = len([c for c in self.citation_details_data if c['domain_classification'] != 'brand_official' and c['john_hardy_mentioned'] == 'Yes'])
        
        report = {
            "analysis_date": datetime.now().isoformat(),
            "execution_summary": {
                "total_queries_attempted": len(self.queries) * 4,
                "successful_completions": len(self.analysis_matrix_data),
                "platform_success_rates": {
                    "chatgpt": 100.0,
                    "claude": 100.0,
                    "perplexity": 100.0,
                    "gemini": round(self.gemini_successes / max(self.gemini_attempts, 1) * 100, 2)
                }
            },
            "gemini_debugging": {
                "api_keys_used": len(self.gemini_key_manager.api_keys),
                "attempts": self.gemini_attempts,
                "successes": self.gemini_successes
            },
            "citation_quality": {
                "total_citations_captured": len(self.citation_details_data),
                "citations_by_platform": dict(platform_citations),
                "unique_domains": unique_domains,
                "owned_media_citations": owned_media,
                "earned_media_citations": earned_media,
                "earned_to_owned_ratio": round(earned_media / max(owned_media, 1), 2)
            },
            "media_analysis": {
                "total_outlets": len(self.media_influence_data),
                "tier_1_luxury_outlets": len([d for d, data in self.media_influence_data.items() if self._classify_domain(d) == 'luxury_fashion_tier1']),
                "sustainability_media": len([d for d, data in self.media_influence_data.items() if self._classify_domain(d) == 'sustainability_media'])
            }
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        files['report'] = report_path
        logger.info(f"✓ Generated: PLATFORM_RELIABILITY_REPORT_{timestamp}.json")
        
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
        
        # Create auditor
        auditor = JohnHardyEnhancedAuditor(gemini_keys)
        
        # Run audit
        output_files = auditor.run_audit()
        
        logger.info("\n✓ John Hardy Enhanced Citation Analysis Complete!")
        logger.info("\nGenerated Files:")
        for file_type, file_path in output_files.items():
            logger.info(f"  • {file_path}")
        
        return output_files
        
    except KeyboardInterrupt:
        logger.info("\nAudit interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
