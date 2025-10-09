#!/usr/bin/env python3
"""
John Hardy Lovestruck Collection - AEO Launch Analysis
Billie Eilish Partnership | Lab-Grown Diamonds | Launched Sept 29, 2025

Focus: Assess AI citation visibility of new collection launch featuring:
- Billie Eilish & Finneas O'Connell partnership
- Lab-grown diamond positioning
- Sustainability narrative (renewable energy, reclaimed metals)
- Competitive standing vs Brilliant Earth and Vrai

35 queries × 4 platforms = 140 tests
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


class JohnHardyLovestruckAuditor:
    """
    Product launch-specific auditor for Lovestruck collection
    """
    
    def __init__(self, gemini_keys: List[str]):
        self.gemini_key_manager = GeminiKeyManager(gemini_keys)
        
        # Brand & collection tracking
        self.brand_name = "John Hardy"
        self.collection_name = "Lovestruck"
        self.launch_date = "September 29, 2025"
        
        # Celebrity partners
        self.celebrities = ["Billie Eilish", "Finneas O'Connell", "Finneas"]
        
        # Competitor tracking
        self.competitors = {
            "Brilliant Earth": ["brilliant earth", "brilliantearth"],
            "Vrai": ["vrai", "vrai.com"],
            "Mejuri": ["mejuri"],
            "Aurate": ["aurate"],
            "David Yurman": ["david yurman"]
        }
        
        # Define queries
        self.queries = self._define_lovestruck_queries()
        
        # Storage
        self.analysis_matrix_data = []
        self.citation_details_data = []
        self.media_influence_data = defaultdict(lambda: {
            'citation_count': 0,
            'lovestruck_citations': 0,
            'billie_eilish_citations': 0,
            'queries': set(),
            'engines': set()
        })
        
        # Gemini tracking
        self.gemini_attempts = 0
        self.gemini_successes = 0
        
        logger.info("John Hardy Lovestruck Launch Auditor initialized")
        logger.info(f"Collection: {self.collection_name} (Launched: {self.launch_date})")
    
    def _define_lovestruck_queries(self) -> List[Dict[str, Any]]:
        """Define 35 queries across 6 categories"""
        queries = []
        
        # CATEGORY 1: COLLECTION-SPECIFIC BRANDED (6 queries)
        collection_specific = [
            ("What is John Hardy Lovestruck?", "brand_knowledge"),
            ("John Hardy Lovestruck collection review", "research"),
            ("Where can I buy John Hardy Lovestruck jewelry?", "purchase_intent"),
            ("John Hardy lab-grown diamond collection", "research"),
            ("John Hardy Billie Eilish jewelry collection", "discovery"),
            ("John Hardy proprietary diamond cuts", "research")
        ]
        for text, intent in collection_specific:
            queries.append({
                "text": text,
                "type": "branded",
                "category": "collection_specific",
                "commercial_intent": intent
            })
        
        # CATEGORY 2: CELEBRITY PARTNERSHIP (5 queries)
        celebrity = [
            ("Billie Eilish jewelry collaboration", "discovery"),
            ("Billie Eilish sustainable jewelry", "research"),
            ("What jewelry does Billie Eilish wear?", "research"),
            ("Finneas O'Connell jewelry collaboration", "discovery"),
            ("Celebrity lab-grown diamond jewelry", "discovery")
        ]
        for text, intent in celebrity:
            queries.append({
                "text": text,
                "type": "celebrity",
                "category": "celebrity_partnership",
                "commercial_intent": intent
            })
        
        # CATEGORY 3: LAB-GROWN DIAMOND CATEGORY (8 queries)
        lab_grown = [
            ("Best lab-grown diamond jewelry brands 2025", "discovery"),
            ("Sustainable lab-created diamond jewelry", "research"),
            ("Lab-grown diamond rings for everyday wear", "purchase_intent"),
            ("Organic shaped lab-grown diamonds", "research"),
            ("Freeform diamond cuts and shapes", "research"),
            ("Lab-grown diamonds in reclaimed metals", "research"),
            ("Renewable energy jewelry production", "research"),
            ("Lab-grown vs natural diamond jewelry brands", "comparison")
        ]
        for text, intent in lab_grown:
            queries.append({
                "text": text,
                "type": "category",
                "category": "lab_grown",
                "commercial_intent": intent
            })
        
        # CATEGORY 4: SUSTAINABILITY NARRATIVE (7 queries)
        sustainability = [
            ("Most sustainable jewelry brands 2025", "discovery"),
            ("Ethical diamond jewelry with renewable energy", "research"),
            ("Recycled gold jewelry with lab-grown diamonds", "research"),
            ("Climate-conscious jewelry brands", "research"),
            ("Zero-waste jewelry production", "research"),
            ("Jewelry brands supporting climate initiatives", "research"),
            ("Sustainable luxury jewelry for Gen Z", "discovery")
        ]
        for text, intent in sustainability:
            queries.append({
                "text": text,
                "type": "category",
                "category": "sustainability",
                "commercial_intent": intent
            })
        
        # CATEGORY 5: PRODUCT DISCOVERY (5 queries)
        product = [
            ("Pebble-shaped diamond jewelry", "discovery"),
            ("Handmade lab-grown diamond jewelry", "research"),
            ("Everyday diamond jewelry for stacking", "purchase_intent"),
            ("Modern diamond ear cuffs", "discovery"),
            ("Surf chain necklace with diamonds", "discovery")
        ]
        for text, intent in product:
            queries.append({
                "text": text,
                "type": "product",
                "category": "product_discovery",
                "commercial_intent": intent
            })
        
        # CATEGORY 6: COMPETITIVE INTELLIGENCE (4 queries)
        competitive = [
            ("John Hardy vs Brilliant Earth lab-grown diamonds", "comparison"),
            ("Vrai vs John Hardy sustainable jewelry", "comparison"),
            ("Alternative to Brilliant Earth engagement rings", "discovery"),
            ("Lab-grown diamond jewelry besides Vrai", "discovery")
        ]
        for text, intent in competitive:
            queries.append({
                "text": text,
                "type": "competitive",
                "category": "competitive",
                "commercial_intent": intent
            })
        
        return queries
    
    def run_audit(self) -> Dict[str, str]:
        """Execute Lovestruck launch analysis"""
        logger.info(f"\n{'='*80}")
        logger.info("JOHN HARDY LOVESTRUCK COLLECTION - AEO LAUNCH ANALYSIS")
        logger.info(f"Collection Launch: {self.launch_date}")
        logger.info(f"{'='*80}")
        logger.info(f"Total Queries: {len(self.queries)}")
        logger.info(f"Platforms: 4 (ChatGPT, Claude, Perplexity, Gemini)")
        logger.info(f"Total Tests: {len(self.queries) * 4}")
        logger.info(f"FOCUS: Launch awareness, Billie Eilish partnership, Lab-grown category entry")
        logger.info(f"{'='*80}\n")
        
        # Execute all queries
        self._execute_queries()
        
        # Generate output files
        logger.info("\nGenerating Lovestruck Analysis Files...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_files = self._generate_output_files(timestamp)
        
        # Validate
        citation_count = len(self.citation_details_data)
        logger.info(f"\n{'='*80}")
        logger.info(f"LOVESTRUCK CITATION CAPTURE: {citation_count} URLs")
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
            system_prompt = "You are a helpful assistant specializing in jewelry and fashion. Please provide detailed citations with URLs for all information sources."
            
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
        """Claude with enhanced citation inference"""
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            
            # More explicit prompt requesting sources
            enhanced_query = f"""{query}

Please provide your answer with specific sources. For each major point or fact, indicate where the information comes from (e.g., "According to Vogue...", "John Hardy's website states...", "As reported by Forbes..."). Include URLs when possible."""
            
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
                    "messages": [{"role": "user", "content": enhanced_query}]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                text = ""
                for block in data.get('content', []):
                    if block.get('type') == 'text':
                        text += block.get('text', '')
                
                # First try to extract explicit URLs
                citations = self._extract_urls_from_text(text)
                
                # If no URLs found, infer sources from text mentions
                if not citations:
                    citations = self._infer_sources_from_text(text)
                
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
    
    def _infer_sources_from_text(self, text: str) -> List[Dict]:
        """Infer sources from text mentions when URLs aren't provided (for Claude)"""
        if not text:
            return []
        
        inferred_citations = []
        position = 1
        
        # Patterns to detect source mentions
        source_patterns = [
            # "According to [Source]" or "As [Source] reports"
            r'(?:according to|as reported by|as stated by|per|via)\s+([A-Z][A-Za-z\s&\.\']+?)(?:,|\.|\'s|reports|states|notes)',
            # "[Source] reports/states/notes that"
            r'([A-Z][A-Za-z\s&\.\']+?)\s+(?:reports|states|notes|writes|says|indicates|confirms|announced)\s+that',
            # On [Source] or At [Source]
            r'(?:on|at|from)\s+([A-Z][A-Za-z\s&\.\']+?)(?:,|\.|\'s|website)',
        ]
        
        # Known sources to look for (with their likely domains)
        source_mapping = {
            'Vogue': 'vogue.com',
            'Elle': 'elle.com',
            'Harper\'s Bazaar': 'harpersbazaar.com',
            'Harpers Bazaar': 'harpersbazaar.com',
            'Forbes': 'forbes.com',
            'WWD': 'wwd.com',
            'Women\'s Wear Daily': 'wwd.com',
            'John Hardy': 'johnhardy.com',
            'Brilliant Earth': 'brilliantearth.com',
            'Vrai': 'vrai.com',
            'JCK': 'jckonline.com',
            'National Jeweler': 'nationaljeweler.com',
            'Business of Fashion': 'businessoffashion.com',
            'BOF': 'businessoffashion.com',
            'The Good Trade': 'thegoodtrade.com',
            'Nordstrom': 'nordstrom.com',
            'Neiman Marcus': 'neimanmarcus.com',
            'Billboard': 'billboard.com',
            'Rolling Stone': 'rollingstone.com',
            'Variety': 'variety.com',
            'People': 'people.com',
            'E! News': 'eonline.com',
            'Instagram': 'instagram.com',
            'TikTok': 'tiktok.com',
        }
        
        # Search for pattern matches
        found_sources = set()
        for pattern in source_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                source_name = match.group(1).strip()
                
                # Clean up source name
                source_name = re.sub(r'\s+', ' ', source_name)
                source_name = source_name.rstrip('.,;:')
                
                # Check if it matches a known source
                for known_source, domain in source_mapping.items():
                    if known_source.lower() in source_name.lower():
                        if domain not in found_sources:
                            inferred_citations.append({
                                'url': f'https://{domain}',
                                'position': position,
                                'inferred': True,
                                'source_mention': source_name
                            })
                            found_sources.add(domain)
                            position += 1
                        break
        
        # Also look for direct brand/outlet mentions even without attribution phrases
        for known_source, domain in source_mapping.items():
            if known_source in text and domain not in found_sources:
                inferred_citations.append({
                    'url': f'https://{domain}',
                    'position': position,
                    'inferred': True,
                    'source_mention': known_source
                })
                found_sources.add(domain)
                position += 1
        
        if inferred_citations:
            logger.info(f"  ⚡ Inferred {len(inferred_citations)} source(s) from text")
        
        return inferred_citations
    
    def _analyze_response(self, result: Dict, query_info: Dict, platform: str):
        """Analyze response with Lovestruck-specific tracking"""
        response_text = result['response_text']
        citations = result['citations']
        
        # Check for launch awareness
        launch_aware = self._check_launch_awareness(response_text)
        
        # Check for Lovestruck mentions
        lovestruck_mentioned = 'lovestruck' in response_text.lower()
        
        # Check for celebrity mentions
        billie_mentioned = any(name.lower() in response_text.lower() for name in self.celebrities)
        
        # Check brand mentions
        john_hardy_mentioned = any(variant.lower() in response_text.lower() 
                                   for variant in ["john hardy", "johnhardy"])
        
        # Check competitor mentions
        competitors_mentioned = []
        for comp_name, variants in self.competitors.items():
            if any(v.lower() in response_text.lower() for v in variants):
                competitors_mentioned.append(comp_name)
        
        # Matrix row
        matrix_row = {
            'query': query_info['text'],
            'query_type': query_info['type'],
            'category': query_info['category'],
            'commercial_intent': query_info['commercial_intent'],
            'launch_awareness': "Yes" if launch_aware else "No",
            'engine': platform,
            'john_hardy_mentioned': "Yes" if john_hardy_mentioned else "No",
            'lovestruck_mentioned': "Yes" if lovestruck_mentioned else "No",
            'billie_eilish_mentioned': "Yes" if billie_mentioned else "No",
            'competitors_mentioned': ", ".join(competitors_mentioned) if competitors_mentioned else "None",
            'featured_brand': self._determine_featured_brand(response_text, competitors_mentioned, john_hardy_mentioned),
            'total_citations': len(citations),
            'john_hardy_citations': 0,
            'lovestruck_citations': 0,
            'competitor_citations': 0,
            'owned_media_citations': 0,
            'earned_media_citations': 0
        }
        
        # Citation details
        for citation in citations:
            url = citation['url']
            domain = self._extract_domain(url)
            
            # Check mentions in URL
            jh_in_url = any(v in url.lower() for v in ["john-hardy", "johnhardy"])
            lovestruck_in_url = 'lovestruck' in url.lower()
            billie_in_url = any(name.lower().replace(' ', '-') in url.lower() for name in self.celebrities)
            competitor_in_url = any(comp for comp_name, variants in self.competitors.items() 
                                   for comp in variants if comp.replace(' ', '-') in url.lower() or comp.replace(' ', '') in url.lower())
            
            # Update counts
            if jh_in_url or lovestruck_in_url:
                matrix_row['john_hardy_citations'] += 1
                if lovestruck_in_url:
                    matrix_row['lovestruck_citations'] += 1
            if competitor_in_url:
                matrix_row['competitor_citations'] += 1
            
            # Classify domain
            domain_class = self._classify_domain_lovestruck(domain, url)
            
            if domain_class == 'brand_official':
                matrix_row['owned_media_citations'] += 1
            elif jh_in_url or lovestruck_in_url:
                matrix_row['earned_media_citations'] += 1
            
            # Store citation details
            self.citation_details_data.append({
                'engine': platform,
                'query': query_info['text'],
                'category': query_info['category'],
                'citation_url': url,
                'domain': domain,
                'domain_classification': domain_class,
                'john_hardy_mentioned': "Yes" if jh_in_url or lovestruck_in_url else "No",
                'lovestruck_mentioned': "Yes" if lovestruck_in_url else "No",
                'billie_eilish_mentioned': "Yes" if billie_in_url else "No",
                'competitor_mentioned': ", ".join([c for c, v in self.competitors.items() 
                                                   for var in v if var.replace(' ', '-') in url.lower() or var.replace(' ', '') in url.lower()]) or "None",
                'citation_position': citation.get('position', 0),
                'content_freshness': self._estimate_content_freshness(url, response_text)
            })
            
            # Media tracking
            if domain:
                self.media_influence_data[domain]['citation_count'] += 1
                self.media_influence_data[domain]['queries'].add(query_info['text'])
                self.media_influence_data[domain]['engines'].add(platform)
                
                if lovestruck_in_url:
                    self.media_influence_data[domain]['lovestruck_citations'] += 1
                if billie_in_url:
                    self.media_influence_data[domain]['billie_eilish_citations'] += 1
        
        self.analysis_matrix_data.append(matrix_row)
    
    def _check_launch_awareness(self, text: str) -> bool:
        """Check if response shows awareness of Sept 2025 launch"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for Lovestruck collection mention
        if 'lovestruck' not in text_lower:
            return False
        
        # Check for 2025 or September mention
        if '2025' in text_lower or 'september' in text_lower or 'sept' in text_lower:
            return True
        
        # Check for "new" or "launched" or "recently" near Lovestruck
        launch_terms = ['new collection', 'launched', 'recently', 'latest', 'newest', 'just released']
        return any(term in text_lower for term in launch_terms)
    
    def _classify_domain_lovestruck(self, domain: str, url: str) -> str:
        """Classify domain with launch-specific categories"""
        if not domain:
            return "other"
        
        domain_lower = domain.lower()
        url_lower = url.lower()
        
        # Brand official
        if 'johnhardy.com' in domain_lower:
            return 'brand_official'
        
        # Competitor official
        if any(c in domain_lower for c in ['brilliantearth', 'vrai.com', 'mejuri', 'aurate']):
            return 'competitor_official'
        
        # Entertainment/Celebrity media
        if any(m in domain_lower for m in ['billboard', 'rollingstone', 'variety', 'eonline', 'people', 'tmz', 'pagesix']):
            return 'entertainment_media'
        
        # Luxury Fashion Tier 1
        if any(m in domain_lower for m in ['vogue', 'elle', 'harpersbazaar', 'wwd']):
            return 'luxury_fashion_tier1'
        
        # Sustainability Media
        if any(s in domain_lower for s in ['sustainablebrands', 'greenbiz', 'treehugger', 'thegoodtrade', 'ecocult']):
            return 'sustainability_media'
        
        # Business Media
        if any(b in domain_lower for b in ['forbes', 'bloomberg', 'cnbc', 'businessinsider']):
            return 'business_media'
        
        # Jewelry Trade
        if any(j in domain_lower for j in ['jck', 'nationaljeweler', 'rapaport']):
            return 'jewelry_trade'
        
        # Retail Partners
        if any(r in domain_lower for r in ['nordstrom', 'neimanmarcus', 'bloomingdales', 'saks']):
            return 'retail_partner'
        
        # Social Media
        if 'reddit.com' in domain_lower:
            return 'social_reddit'
        elif 'instagram.com' in domain_lower:
            return 'social_instagram'
        elif 'tiktok.com' in domain_lower:
            return 'social_tiktok'
        elif 'youtube.com' in domain_lower or 'youtu.be' in domain_lower:
            return 'social_youtube'
        
        # Celebrity/Lifestyle
        if any(l in domain_lower for l in ['gq.com', 'esquire', 'complex', 'refinery29']):
            return 'lifestyle_media'
        
        # Philanthropic (Support+Feed partnership)
        if 'supportandfeed' in domain_lower or 'support+feed' in domain_lower:
            return 'philanthropic'
        
        # News Media
        if any(n in domain_lower for n in ['nytimes', 'wsj', 'washingtonpost', 'reuters', 'apnews']):
            return 'news_media'
        
        # Wikipedia
        if 'wikipedia' in domain_lower:
            return 'wiki_reference'
        
        return 'other'
    
    def _estimate_content_freshness(self, url: str, text: str) -> str:
        """Estimate if content is from 2025 (post-launch)"""
        url_lower = url.lower()
        text_lower = text.lower()
        
        if '2025' in url_lower or '/2025/' in url_lower:
            return '2025'
        elif '2024' in url_lower or '/2024/' in url_lower:
            return '2024'
        elif any(year in url_lower for year in ['2023', '2022', '2021', '2020']):
            return 'older'
        
        # Check text for date references
        if '2025' in text_lower:
            return '2025'
        elif '2024' in text_lower:
            return '2024'
        
        return 'unknown'
    
    def _extract_domain(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower().replace('www.', '')
        except:
            return ""
    
    def _determine_featured_brand(self, text: str, competitors: List[str], jh_mentioned: bool) -> str:
        """Determine which brand is featured most prominently"""
        if not competitors and not jh_mentioned:
            return "None"
        
        text_lower = text.lower()
        positions = {}
        
        if jh_mentioned:
            for variant in ["john hardy", "johnhardy"]:
                pos = text_lower.find(variant)
                if pos != -1:
                    positions["John Hardy"] = pos
                    break
        
        for comp in competitors:
            comp_lower = comp.lower()
            pos = text_lower.find(comp_lower)
            if pos != -1:
                positions[comp] = pos
        
        return min(positions.items(), key=lambda x: x[1])[0] if positions else "None"
    
    def _generate_output_files(self, timestamp: str) -> Dict[str, str]:
        """Generate Lovestruck-specific output files"""
        output_dir = "case_studies/john_hardy_lovestruck"
        os.makedirs(output_dir, exist_ok=True)
        
        files = {}
        
        # 1. Lovestruck Launch Analysis Matrix
        matrix_path = f"{output_dir}/LOVESTRUCK_LAUNCH_ANALYSIS_MATRIX_{timestamp}.csv"
        with open(matrix_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'query', 'query_type', 'category', 'commercial_intent', 'launch_awareness',
                'engine', 'john_hardy_mentioned', 'lovestruck_mentioned', 'billie_eilish_mentioned',
                'competitors_mentioned', 'featured_brand', 'total_citations', 'john_hardy_citations',
                'lovestruck_citations', 'competitor_citations', 'owned_media_citations', 'earned_media_citations'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.analysis_matrix_data)
        files['matrix'] = matrix_path
        logger.info(f"✓ Generated: LOVESTRUCK_LAUNCH_ANALYSIS_MATRIX_{timestamp}.csv")
        
        # 2. Lovestruck Citation Details
        details_path = f"{output_dir}/LOVESTRUCK_CITATION_DETAILS_{timestamp}.csv"
        with open(details_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'engine', 'query', 'category', 'citation_url', 'domain',
                'domain_classification', 'john_hardy_mentioned', 'lovestruck_mentioned',
                'billie_eilish_mentioned', 'competitor_mentioned', 'citation_position',
                'content_freshness'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.citation_details_data)
        files['details'] = details_path
        logger.info(f"✓ Generated: LOVESTRUCK_CITATION_DETAILS_{timestamp}.csv")
        logger.info(f"  📊 Citation count: {len(self.citation_details_data)}")
        
        # 3. Lovestruck Media Influence
        media_path = f"{output_dir}/LOVESTRUCK_MEDIA_INFLUENCE_{timestamp}.csv"
        with open(media_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'media_outlet', 'citation_count', 'lovestruck_citations',
                'billie_eilish_citations', 'top_queries', 'engines', 'domain_classification'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            media_rows = []
            for domain, data in self.media_influence_data.items():
                if data['citation_count'] > 0:
                    media_rows.append({
                        'media_outlet': domain,
                        'citation_count': data['citation_count'],
                        'lovestruck_citations': data['lovestruck_citations'],
                        'billie_eilish_citations': data['billie_eilish_citations'],
                        'top_queries': '; '.join(list(data['queries'])[:3]),
                        'engines': ', '.join(sorted(data['engines'])),
                        'domain_classification': self._classify_domain_lovestruck(domain, '')
                    })
            
            media_rows.sort(key=lambda x: x['citation_count'], reverse=True)
            writer.writerows(media_rows)
        files['media'] = media_path
        logger.info(f"✓ Generated: LOVESTRUCK_MEDIA_INFLUENCE_{timestamp}.csv")
        
        # 4. Lovestruck Launch Summary
        summary_path = f"{output_dir}/LOVESTRUCK_LAUNCH_SUMMARY_{timestamp}.json"
        
        # Calculate launch metrics
        total_queries = len(self.analysis_matrix_data)
        launch_aware_count = len([r for r in self.analysis_matrix_data if r['launch_awareness'] == 'Yes'])
        lovestruck_mention_count = len([r for r in self.analysis_matrix_data if r['lovestruck_mentioned'] == 'Yes'])
        billie_mention_count = len([r for r in self.analysis_matrix_data if r['billie_eilish_mentioned'] == 'Yes'])
        
        # Category-specific metrics
        collection_queries = [r for r in self.analysis_matrix_data if r['category'] == 'collection_specific']
        celebrity_queries = [r for r in self.analysis_matrix_data if r['category'] == 'celebrity_partnership']
        lab_grown_queries = [r for r in self.analysis_matrix_data if r['category'] == 'lab_grown']
        
        # Citation freshness
        fresh_2025 = len([c for c in self.citation_details_data if c['content_freshness'] == '2025'])
        
        summary = {
            "launch_date": self.launch_date,
            "analysis_date": datetime.now().isoformat(),
            "execution_summary": {
                "total_tests": total_queries,
                "launch_awareness_rate": round(launch_aware_count / max(total_queries, 1) * 100, 2),
                "lovestruck_mention_rate": round(lovestruck_mention_count / max(total_queries, 1) * 100, 2),
                "billie_eilish_association_rate": round(billie_mention_count / max(total_queries, 1) * 100, 2)
            },
            "category_performance": {
                "collection_specific": {
                    "queries": len(collection_queries),
                    "lovestruck_mentions": len([r for r in collection_queries if r['lovestruck_mentioned'] == 'Yes']),
                    "launch_awareness": len([r for r in collection_queries if r['launch_awareness'] == 'Yes'])
                },
                "celebrity_partnership": {
                    "queries": len(celebrity_queries),
                    "billie_eilish_mentions": len([r for r in celebrity_queries if r['billie_eilish_mentioned'] == 'Yes']),
                    "john_hardy_association": len([r for r in celebrity_queries if r['john_hardy_mentioned'] == 'Yes'])
                },
                "lab_grown_category": {
                    "queries": len(lab_grown_queries),
                    "john_hardy_mentions": len([r for r in lab_grown_queries if r['john_hardy_mentioned'] == 'Yes']),
                    "lovestruck_mentions": len([r for r in lab_grown_queries if r['lovestruck_mentioned'] == 'Yes'])
                }
            },
            "citation_analysis": {
                "total_citations": len(self.citation_details_data),
                "owned_media_citations": sum(r['owned_media_citations'] for r in self.analysis_matrix_data),
                "earned_media_citations": sum(r['earned_media_citations'] for r in self.analysis_matrix_data),
                "fresh_2025_content": fresh_2025,
                "lovestruck_specific_citations": sum(r['lovestruck_citations'] for r in self.analysis_matrix_data)
            },
            "competitive_position": {
                "total_competitor_citations": sum(r['competitor_citations'] for r in self.analysis_matrix_data),
                "john_hardy_citations": sum(r['john_hardy_citations'] for r in self.analysis_matrix_data),
                "competitive_ratio": round(sum(r['john_hardy_citations'] for r in self.analysis_matrix_data) / 
                                          max(sum(r['competitor_citations'] for r in self.analysis_matrix_data), 1), 2)
            },
            "media_coverage": {
                "total_outlets": len(self.media_influence_data),
                "entertainment_media_outlets": len([d for d in self.media_influence_data.keys() 
                                                    if self._classify_domain_lovestruck(d, '') == 'entertainment_media']),
                "luxury_fashion_outlets": len([d for d in self.media_influence_data.keys() 
                                              if self._classify_domain_lovestruck(d, '') == 'luxury_fashion_tier1'])
            }
        }
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        files['summary'] = summary_path
        logger.info(f"✓ Generated: LOVESTRUCK_LAUNCH_SUMMARY_{timestamp}.json")
        
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
        
        # Create Lovestruck auditor
        auditor = JohnHardyLovestruckAuditor(gemini_keys)
        
        # Run audit
        output_files = auditor.run_audit()
        
        logger.info("\n✓ John Hardy Lovestruck Launch Analysis Complete!")
        logger.info("\nGenerated Files:")
        for file_type, file_path in output_files.items():
            logger.info(f"  • {file_path}")
        
        return output_files
        
    except KeyboardInterrupt:
        logger.info("\nLaunch analysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
