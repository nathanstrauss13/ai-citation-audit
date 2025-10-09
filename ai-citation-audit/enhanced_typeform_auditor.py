#!/usr/bin/env python3
"""
Enhanced Typeform Auditor - PR-Focused Citation Analysis
Properly classifies sources into Editorial, Social, Informational, and Ecommerce
with weighted scoring for PR opportunity identification
"""

import os
import json
import csv
import logging
import requests
import time
import random
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
from urllib.parse import urlparse
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SourceClassifier:
    """Classifies domains into PR-relevant categories"""
    
    # Tier 1 Editorial - Premium publications
    EDITORIAL_TIER1 = {
        'wsj.com', 'nytimes.com', 'forbes.com', 'fortune.com', 'bloomberg.com',
        'techcrunch.com', 'theverge.com', 'wired.com', 'businessinsider.com',
        'ft.com', 'economist.com', 'reuters.com', 'apnews.com', 'bbc.com',
        'cnn.com', 'nbcnews.com', 'washingtonpost.com', 'usatoday.com',
        'time.com', 'newsweek.com', 'theatlantic.com', 'newyorker.com',
        'fastcompany.com', 'inc.com', 'entrepreneur.com', 'hbr.org'
    }
    
    # Tier 2 Editorial - Industry trades, regional, niche
    EDITORIAL_TIER2_PATTERNS = [
        'news', 'journal', 'times', 'post', 'tribune', 'herald', 'gazette',
        'chronicle', 'observer', 'report', 'daily', 'weekly', 'monthly',
        'magazine', 'review', 'digest', 'bulletin', 'wire', 'media'
    ]
    
    # Social/Community platforms
    SOCIAL_COMMUNITY = {
        'reddit.com', 'twitter.com', 'x.com', 'facebook.com', 'instagram.com',
        'linkedin.com', 'youtube.com', 'tiktok.com', 'pinterest.com',
        'quora.com', 'medium.com', 'substack.com', 'discord.com', 'slack.com',
        'tumblr.com', 'snapchat.com', 'twitch.tv', 'clubhouse.com'
    }
    
    # Informational/Reference sites
    INFORMATIONAL = {
        'wikipedia.org', 'wikimedia.org', 'britannica.com', 'dictionary.com',
        'merriam-webster.com', 'cambridge.org', 'oxford.com', 'howstuffworks.com',
        'khanacademy.org', 'coursera.org', 'edx.org', 'udemy.com'
    }
    
    # Ecommerce/Marketplace platforms
    ECOMMERCE = {
        'amazon.com', 'ebay.com', 'walmart.com', 'target.com', 'bestbuy.com',
        'costco.com', 'homedepot.com', 'lowes.com', 'wayfair.com', 'etsy.com',
        'alibaba.com', 'aliexpress.com', 'shopify.com', 'wish.com', 'newegg.com',
        'overstock.com', 'zappos.com', 'nordstrom.com', 'macys.com', 'sephora.com'
    }
    
    # PR Wire services (separate category)
    PR_WIRE = {
        'prnewswire.com', 'businesswire.com', 'globenewswire.com', 'prweb.com',
        'einpresswire.com', 'prlog.org', 'openpr.com', '24-7pressrelease.com'
    }
    
    @classmethod
    def classify(cls, domain: str) -> Tuple[str, int]:
        """
        Classify a domain and return (category, weight)
        
        Categories:
        - EDITORIAL_TIER1: Weight 10 (Premium editorial)
        - EDITORIAL_TIER2: Weight 7 (Industry/regional editorial)
        - SOCIAL_COMMUNITY: Weight 3 (Social platforms)
        - INFORMATIONAL: Weight 2 (Reference/educational)
        - ECOMMERCE: Weight 1 (Marketplaces)
        - PR_WIRE: Weight 0.5 (Press releases - lowest priority)
        - OTHER: Weight 4 (Unknown - moderate weight)
        """
        domain = domain.lower().strip()
        
        # Remove common subdomains
        if domain.startswith('www.'):
            domain = domain[4:]
        if domain.startswith('m.'):
            domain = domain[2:]
            
        # Check Tier 1 Editorial
        if domain in cls.EDITORIAL_TIER1:
            return ('EDITORIAL_TIER1', 10)
        
        # Check PR Wire (before Tier 2 to avoid false positives)
        if domain in cls.PR_WIRE:
            return ('PR_WIRE', 0.5)
        
        # Check Social/Community
        if domain in cls.SOCIAL_COMMUNITY:
            return ('SOCIAL_COMMUNITY', 3)
        
        # Check Informational
        if domain in cls.INFORMATIONAL or domain.endswith('.gov') or domain.endswith('.edu'):
            return ('INFORMATIONAL', 2)
        
        # Check Ecommerce
        if domain in cls.ECOMMERCE:
            return ('ECOMMERCE', 1)
        
        # Check Tier 2 Editorial patterns
        for pattern in cls.EDITORIAL_TIER2_PATTERNS:
            if pattern in domain:
                return ('EDITORIAL_TIER2', 7)
        
        # Default to OTHER with moderate weight
        return ('OTHER', 4)


class DomainNormalizer:
    """Normalizes and deduplicates domains"""
    
    @staticmethod
    def normalize(url: str) -> str:
        """Extract and normalize domain from URL"""
        if not url:
            return ''
        
        # Handle URLs without protocol
        if not url.startswith(('http://', 'https://', '//')):
            url = 'https://' + url
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path.split('/')[0]
            
            # Remove common subdomains
            domain = domain.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            if domain.startswith('m.'):
                domain = domain[2:]
            
            # Remove port if present
            domain = domain.split(':')[0]
            
            return domain
        except Exception as e:
            logger.error(f"Error normalizing URL {url}: {e}")
            return url.lower()
    
    @staticmethod
    def extract_from_text(text: str) -> List[str]:
        """Extract all URLs from text"""
        # Comprehensive URL regex
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+|www\.[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        
        # Also look for domain mentions without protocol
        domain_pattern = r'\b([a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]\.(?:com|org|net|edu|gov|io|co|uk|ca|au|de|fr|jp|cn|in|br|mx))\b'
        domains = re.findall(domain_pattern, text)
        
        all_urls = urls + ['https://' + d for d in domains]
        return list(set(all_urls))


class PROpportunityScorer:
    """Calculates PR opportunity scores for outlets"""
    
    @staticmethod
    def calculate_score(
        outlet_data: Dict[str, Any],
        brand_name: str,
        tier_weight: int
    ) -> float:
        """
        Calculate PR opportunity score
        
        Factors:
        - Citation frequency (how often cited)
        - Platform breadth (how many platforms cite it)
        - Recommendation weight (explicitly recommended vs just cited)
        - Tier weight (editorial > social > informational > ecommerce)
        - Brand gap (inverse of current brand presence)
        """
        
        # Base citations score
        total_citations = outlet_data.get('total_citations', 0)
        
        # Platform breadth bonus (cited by multiple platforms is better)
        platforms_citing = len(outlet_data.get('platforms', []))
        platform_multiplier = 1 + (platforms_citing - 1) * 0.25  # +25% per additional platform
        
        # Recommendation bonus (explicitly recommended is 2x value)
        recommended_count = outlet_data.get('recommended_count', 0)
        recommendation_bonus = 1 + min(recommended_count * 0.5, 2)  # Up to 3x for heavily recommended
        
        # Brand gap factor (no mentions = full opportunity, has mentions = reduced opportunity)
        brand_mentions = outlet_data.get('brand_mentions', 0)
        brand_gap = 1.0 if brand_mentions == 0 else 0.3
        
        # Calculate final score
        score = (
            total_citations *
            tier_weight *
            platform_multiplier *
            recommendation_bonus *
            brand_gap
        )
        
        return round(score, 2)


class EnhancedTypeformAuditor:
    """Enhanced auditor with proper classification and scoring"""
    
    def __init__(self, brand: str, competitors: List[str], prompts: List[str]):
        self.brand = brand
        self.competitors = competitors
        self.prompts = prompts
        self.results = []
        self.outlet_aggregates = defaultdict(lambda: {
            'total_citations': 0,
            'platforms': set(),
            'brand_mentions': 0,
            'competitor_mentions': defaultdict(int),
            'actual_urls': set(),
            'inferred_sources': set(),
            'recommended_count': 0,
            'sample_contexts': []
        })
    
    def run_audit(self) -> Dict[str, Any]:
        """Run enhanced audit with better citation extraction"""
        platforms = ['ChatGPT', 'Claude', 'Perplexity', 'Gemini']
        
        logger.info(f"Starting enhanced audit for {self.brand}")
        logger.info(f"Testing {len(self.prompts)} queries across {len(platforms)} platforms")
        
        total = len(self.prompts) * len(platforms)
        completed = 0
        
        for prompt in self.prompts:
            # Handle both string and dict formats
            if isinstance(prompt, dict):
                prompt_text = prompt.get('query', str(prompt))
            else:
                prompt_text = prompt
                
            for platform in platforms:
                completed += 1
                logger.info(f"[{completed}/{total}] {platform}: {prompt_text[:50]}...")
                
                try:
                    # Query with enhanced prompting
                    result = self._query_platform_enhanced(platform, prompt)
                    
                    if result:
                        # Analyze with better extraction
                        analysis = self._analyze_response_enhanced(result, prompt, platform)
                        self.results.append(analysis)
                        
                        # Aggregate outlet data
                        self._aggregate_outlets(analysis, platform)
                    
                    # Rate limiting
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    logger.error(f"Error querying {platform}: {e}")
                    self.results.append({
                        'query': prompt,
                        'platform': platform,
                        'error': str(e)
                    })
        
        # Calculate opportunity scores
        return self._compile_analysis()
    
    def _query_platform_enhanced(self, platform: str, query: str) -> Dict:
        """Query platform with enhanced citation prompting"""
        
        # Handle both string and dict formats for query
        if isinstance(query, dict):
            query_text = query.get('query', str(query))
        else:
            query_text = query
        
        # Enhanced system prompt for better citations
        citation_prompt = """
You MUST include citations and sources in your response.
At the end of your response, add a section titled "Sources and References:" 
listing at least 3 credible websites with full URLs.
Also add a section titled "Recommended Resources:" listing websites 
users should visit for more information.
"""
        
        enhanced_query = f"{query_text}\n\n{citation_prompt}"
        
        if platform == 'ChatGPT':
            return self._query_chatgpt(enhanced_query)
        elif platform == 'Claude':
            return self._query_claude(enhanced_query)
        elif platform == 'Perplexity':
            return self._query_perplexity(query_text)  # Already returns citations
        elif platform == 'Gemini':
            return self._query_gemini(enhanced_query)
    
    def _query_chatgpt(self, query: str) -> Dict:
        """Query ChatGPT with citation enhancement"""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            return None
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that always cites credible sources."},
                    {"role": "user", "content": query}
                ],
                "max_tokens": 1500,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            text = response.json()['choices'][0]['message']['content']
            
            # Extract URLs from response
            urls = DomainNormalizer.extract_from_text(text)
            
            return {'text': text, 'citations': urls}
        return None
    
    def _query_claude(self, query: str) -> Dict:
        """Query Claude with citation enhancement"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return None
        
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
                "messages": [
                    {"role": "user", "content": query}
                ],
                "system": "You are a helpful assistant that always cites credible sources with URLs."
            },
            timeout=30
        )
        
        if response.status_code == 200:
            text = ""
            for block in response.json().get('content', []):
                if block.get('type') == 'text':
                    text += block.get('text', '')
            
            # Extract URLs
            urls = DomainNormalizer.extract_from_text(text)
            
            return {'text': text, 'citations': urls}
        return None
    
    def _query_perplexity(self, query: str) -> Dict:
        """Query Perplexity (already returns good citations)"""
        api_key = os.getenv('PERPLEXITY_API_KEY') or os.getenv('PPLX_API_KEY')
        if not api_key:
            return None
        
        try:
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "sonar-pro",
                    "messages": [{"role": "user", "content": query}],
                    "max_tokens": 1000,
                    "temperature": 0.1,
                    "return_citations": True
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                text = data['choices'][0]['message']['content']
                
                # Get citations from response
                citations = []
                if isinstance(data.get('citations'), list):
                    citations = data['citations']
                
                # Also extract any URLs from text
                text_urls = DomainNormalizer.extract_from_text(text)
                all_citations = list(set(citations + text_urls))
                
                return {'text': text, 'citations': all_citations}
                
        except Exception as e:
            logger.error(f"Perplexity error: {e}")
        
        return None
    
    def _query_gemini(self, query: str) -> Dict:
        """Query Gemini with citation enhancement"""
        api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
        if not api_key:
            return None
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={api_key}"
        
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "parts": [{
                        "text": query
                    }]
                }],
                "generationConfig": {
                    "maxOutputTokens": 1500,
                    "temperature": 0.7
                }
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                text = data['candidates'][0]['content']['parts'][0]['text']
                
                # Extract URLs
                urls = DomainNormalizer.extract_from_text(text)
                
                return {'text': text, 'citations': urls}
        return None
    
    def _analyze_response_enhanced(self, result: Dict, query: str, platform: str) -> Dict:
        """Enhanced response analysis with better extraction"""
        text = result.get('text', '')
        citations = result.get('citations', [])
        
        text_lower = text.lower()
        
        # Brand and competitor detection (improved)
        brand_mentioned = self._detect_entity(self.brand, text_lower)
        competitors_mentioned = [
            comp for comp in self.competitors 
            if self._detect_entity(comp, text_lower)
        ]
        
        # Extract all types of citations
        actual_urls = [DomainNormalizer.normalize(url) for url in citations if url]
        
        # Extract inferred sources
        inferred_sources = self._extract_inferred_sources(text)
        
        # Extract recommended resources
        recommended = self._extract_recommended_resources(text)
        
        # Get sample context for citations
        sample_context = self._extract_citation_context(text, self.brand)
        
        return {
            'query': query,
            'platform': platform,
            'brand_mentioned': brand_mentioned,
            'competitors_mentioned': competitors_mentioned,
            'actual_urls': actual_urls,
            'inferred_sources': inferred_sources,
            'recommended_resources': recommended,
            'sample_context': sample_context,
            'full_response': text
        }
    
    def _detect_entity(self, entity: str, text: str) -> bool:
        """Improved entity detection with word boundaries"""
        entity_lower = entity.lower()
        # Use word boundaries to avoid false positives
        pattern = r'\b' + re.escape(entity_lower) + r'\b'
        return bool(re.search(pattern, text))
    
    def _extract_inferred_sources(self, text: str) -> List[str]:
        """Extract inferred sources from text"""
        sources = []
        
        patterns = [
            r'[Aa]ccording to ([A-Z][a-zA-Z\s&]+?)(?:[,\.]|\s+(?:reports|states|notes))',
            r'([A-Z][a-zA-Z\s&]+?) (?:reports|states|notes|says|claims)',
            r'[Aa]s (?:reported|stated|noted) by ([A-Z][a-zA-Z\s&]+?)(?:[,\.])',
            r'[Ss]ource:\s*([A-Z][a-zA-Z\s&]+?)(?:[,\.\n])',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            sources.extend([m.strip() for m in matches if len(m.strip()) < 50])
        
        return list(set(sources))
    
    def _extract_recommended_resources(self, text: str) -> List[str]:
        """Extract explicitly recommended resources"""
        resources = []
        
        # Look for recommendation patterns
        patterns = [
            r'(?:[Vv]isit|[Cc]heck out?|[Gg]o to|[Tt]ry|[Uu]se|[Ee]xplore)\s+([A-Za-z0-9\-\.]+(?:\.com|\.org|\.net|\.io))',
            r'([A-Z][a-zA-Z0-9\-\.]+(?:\.com|\.org|\.net))\s+(?:is recommended|is great for|is excellent for)',
            r'[Rr]ecommended [Rr]esources?:([^\.]+)',
            r'[Uu]seful [Ww]ebsites?:([^\.]+)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            if isinstance(matches, list):
                for match in matches:
                    if isinstance(match, str):
                        # Extract domains from the match
                        domains = DomainNormalizer.extract_from_text(match)
                        resources.extend(domains)
        
        # Normalize and deduplicate
        normalized = [DomainNormalizer.normalize(r) for r in resources if r]
        return list(set(normalized))
    
    def _extract_citation_context(self, text: str, brand: str) -> str:
        """Extract context around brand mentions or key recommendations"""
        sentences = text.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            if brand.lower() in sentence.lower() or 'recommend' in sentence.lower():
                relevant_sentences.append(sentence.strip())
                if len(relevant_sentences) >= 2:
                    break
        
        return '. '.join(relevant_sentences)[:300] if relevant_sentences else ''
    
    def _aggregate_outlets(self, analysis: Dict, platform: str):
        """Aggregate outlet data across queries and platforms"""
        # Process actual URLs
        for url in analysis.get('actual_urls', []):
            if url:
                self.outlet_aggregates[url]['total_citations'] += 1
                self.outlet_aggregates[url]['platforms'].add(platform)
                if analysis.get('brand_mentioned'):
                    self.outlet_aggregates[url]['brand_mentions'] += 1
                for comp in analysis.get('competitors_mentioned', []):
                    self.outlet_aggregates[url]['competitor_mentions'][comp] += 1
                self.outlet_aggregates[url]['actual_urls'].add(url)
                if analysis.get('sample_context'):
                    self.outlet_aggregates[url]['sample_contexts'].append(analysis['sample_context'])
        
        # Process recommended resources with higher weight
        for resource in analysis.get('recommended_resources', []):
            if resource:
                self.outlet_aggregates[resource]['total_citations'] += 1
                self.outlet_aggregates[resource]['recommended_count'] += 1
                self.outlet_aggregates[resource]['platforms'].add(platform)
                if analysis.get('brand_mentioned'):
                    self.outlet_aggregates[resource]['brand_mentions'] += 1
    
    def _compile_analysis(self) -> Dict[str, Any]:
        """Compile final analysis with PR opportunity scores"""
        
        # Calculate scores for each outlet
        scored_outlets = []
        
        for domain, data in self.outlet_aggregates.items():
            # Classify the outlet
            category, tier_weight = SourceClassifier.classify(domain)
            
            # Calculate PR opportunity score
            score = PROpportunityScorer.calculate_score(data, self.brand, tier_weight)
            
            scored_outlets.append({
                'domain': domain,
                'category': category,
                'tier_weight': tier_weight,
                'pr_opportunity_score': score,
                'total_citations': data['total_citations'],
                'platforms_citing': list(data['platforms']),
                'platform_count': len(data['platforms']),
                'brand_mentions': data['brand_mentions'],
                'competitor_mentions': dict(data['competitor_mentions']),
                'recommended_count': data['recommended_count'],
                'sample_context': data['sample_contexts'][0] if data['sample_contexts'] else '',
                'is_pr_target': category in ['EDITORIAL_TIER1', 'EDITORIAL_TIER2'] and data['brand_mentions'] == 0
            })
        
        # Sort by PR opportunity score
        scored_outlets.sort(key=lambda x: x['pr_opportunity_score'], reverse=True)
        
        # Group by category
        outlets_by_category = defaultdict(list)
        for outlet in scored_outlets:
            outlets_by_category[outlet['category']].append(outlet)
        
        # Calculate summary statistics
        total_queries = len(self.prompts)
        total_results = len(self.results)
        brand_mentions = sum(1 for r in self.results if r.get('brand_mentioned'))
        
        # Identify top PR targets
        pr_targets = [
            o for o in scored_outlets 
            if o['category'] in ['EDITORIAL_TIER1', 'EDITORIAL_TIER2'] 
            and o['brand_mentions'] == 0
            and o['total_citations'] >= 2
        ][:10]
        
        return {
            'brand': self.brand,
            'competitors': self.competitors,
            'total_queries': total_queries,
            'total_results': total_results,
            'brand_mention_rate': round(brand_mentions / total_results * 100, 1) if total_results > 0 else 0,
            'outlets_by_category': dict(outlets_by_category),
            'all_outlets': scored_outlets,
            'top_pr_targets': pr_targets,
            'top_editorial': outlets_by_category['EDITORIAL_TIER1'][:5] + outlets_by_category['EDITORIAL_TIER2'][:5],
            'top_social': outlets_by_category['SOCIAL_COMMUNITY'][:5],
            'top_informational': outlets_by_category['INFORMATIONAL'][:5],
            'top_ecommerce': outlets_by_category['ECOMMERCE'][:5],
            'raw_results': self.results,
            'analysis_timestamp': datetime.now().isoformat(),
            'methodology': {
                'platforms_tested': ['ChatGPT', 'Claude', 'Perplexity', 'Gemini'],
                'citation_extraction': 'Enhanced with URL extraction and recommendation detection',
                'scoring_factors': 'Tier weight × Citation frequency × Platform breadth × Recommendation bonus × Brand gap',
                'classification': 'Editorial Tier 1/2, Social, Informational, Ecommerce, PR Wire'
            }
        }
    
    def save_analysis(self, filepath: str):
        """Save complete analysis to JSON"""
        analysis = self._compile_analysis()
        with open(filepath, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        logger.info(f"Analysis saved to {filepath}")
        return filepath
    
    def export_pr_targets_csv(self, filepath: str):
        """Export PR target list as CSV"""
        analysis = self._compile_analysis()
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            fieldnames = [
                'rank', 'outlet', 'category', 'pr_opportunity_score',
                'total_citations', 'platforms_citing', 'recommended_count',
                'brand_mentions', 'action_required', 'sample_context'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for i, target in enumerate(analysis['top_pr_targets'], 1):
                writer.writerow({
                    'rank': i,
                    'outlet': target['domain'],
                    'category': target['category'],
                    'pr_opportunity_score': target['pr_opportunity_score'],
                    'total_citations': target['total_citations'],
                    'platforms_citing': ', '.join(target['platforms_citing']),
                    'recommended_count': target['recommended_count'],
                    'brand_mentions': target['brand_mentions'],
                    'action_required': 'High Priority - No current coverage' if target['brand_mentions'] == 0 else 'Monitor',
                    'sample_context': target['sample_context'][:200]
                })
        
        logger.info(f"PR targets exported to {filepath}")
        return filepath


# Utility functions for web integration
def run_enhanced_audit(brand: str, competitors: List[str], prompts: List[str]) -> Dict[str, Any]:
    """Run enhanced audit and return analysis"""
    auditor = EnhancedTypeformAuditor(brand, competitors, prompts)
    return auditor.run_audit()


def generate_pr_focused_queries(brand: str, general_query: str, competitors: List[str], openai_key: str) -> List[str]:
    """Generate PR-focused test queries"""
    if not openai_key:
        # Fallback queries
        return [
            general_query,
            f"What are the best {brand.lower()} alternatives?",
            f"Top recommendations for {general_query.replace('?', '').lower()}",
            f"Expert reviews of {brand.lower()} products",
            f"Where to find quality {general_query.replace('What are the best ', '').replace('?', '').lower()}"
        ]
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {openai_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o-mini",
                "messages": [{
                    "role": "user",
                    "content": f"""Generate 5 queries to test {brand}'s visibility in AI recommendations.
                    
Brand: {brand}
User's query: {general_query}
Competitors: {', '.join(competitors) if competitors else 'None specified'}

Create a mix of:
1. The original query
2. Unbiased category queries (don't mention brands)
3. Comparison queries
4. "Where to buy" queries
5. Expert recommendation queries

Return as JSON array of 5 queries."""
                }],
                "max_tokens": 500,
                "temperature": 0.7
            },
            timeout=30
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            queries = json.loads(content)
            return queries[:5]
            
    except Exception as e:
        logger.error(f"Error generating queries: {e}")
    
    # Return fallback queries
    return [
        general_query,
        f"What are the best {brand.lower()} alternatives?",
        f"Top recommendations for {general_query.replace('?', '').lower()}",
        f"Expert reviews of {brand.lower()} products",
        f"Where to find quality {general_query.replace('What are the best ', '').replace('?', '').lower()}"
    ]
